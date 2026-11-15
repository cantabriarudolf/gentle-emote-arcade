import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { EVENTOS } from "../extensions/game-select/index.ts";
import { auditarPack, auditarTodos } from "../scripts/check_packs.ts";
import { restaurarPorDefecto } from "../scripts/restore_notifications.ts";

const selPath = (arcade: string, pack = "aoe") => join(arcade, "sounds", pack, "seleccion.json");
const leerSel = (arcade: string, pack = "aoe") => JSON.parse(readFileSync(selPath(arcade, pack), "utf-8"));
const borrarEvento = (arcade: string, evento: string) => {
  const sel = leerSel(arcade);
  delete sel.choices[evento];
  writeFileSync(selPath(arcade), JSON.stringify(sel, null, 2));
};

/** Arma un arcade con un pack donde cada evento tiene su propio archivo. */
function arcadeFalso(choices: Record<string, string> = {}): string {
  const arcade = mkdtempSync(join(tmpdir(), "packs-"));
  const dir = join(arcade, "sounds", "aoe");
  mkdirSync(dir, { recursive: true });
  const completo: Record<string, string> = {};
  for (const evento of EVENTOS) {
    const archivo = `${evento.replace(/\./g, "-")}.wav`;
    writeFileSync(join(dir, archivo), "RIFF");
    completo[evento] = archivo;
  }
  writeFileSync(
    join(dir, "seleccion.json"),
    JSON.stringify(
      { schema: "gentle-emote-arcade.sounds/v1", soundsDir: "sounds/aoe", choices: { ...completo, ...choices } },
      null,
      2,
    ),
  );
  return arcade;
}

test("un pack completo y sin colisiones no tiene hallazgos", () => {
  assert.deepEqual(auditarPack(arcadeFalso(), "aoe"), []);
});

test("un evento canonico sin cablear es un hallazgo", () => {
  const arcade = arcadeFalso();
  borrarEvento(arcade, "context.high");
  const hallazgos = auditarPack(arcade, "aoe");
  assert.equal(hallazgos.length, 1);
  assert.match(hallazgos[0].detalle, /context\.high/);
});

test("un archivo referenciado que no existe es un hallazgo", () => {
  const hallazgos = auditarPack(arcadeFalso({ "agent.failed": "fantasma" }), "aoe");
  assert.equal(hallazgos.length, 1);
  assert.match(hallazgos[0].detalle, /agent\.failed/);
  assert.match(hallazgos[0].detalle, /fantasma/);
});

test("compartir archivo dentro de la misma familia esta permitido", () => {
  const arcade = arcadeFalso({
    "agent.completed": "agent-failed.wav",
    "agent.cancelled": "agent-failed.wav",
  });
  assert.deepEqual(auditarPack(arcade, "aoe"), []);
});

test("compartir archivo entre familias distintas es un hallazgo", () => {
  const hallazgos = auditarPack(arcadeFalso({ "subagent.completed": "agent-completed.wav" }), "aoe");
  assert.equal(hallazgos.length, 1);
  assert.equal(hallazgos[0].regla, "colision");
  assert.match(hallazgos[0].detalle, /agent\.completed/);
  assert.match(hallazgos[0].detalle, /subagent\.completed/);
});

test("sin nuevaSesion el session.started del pack alcanza: no es hallazgo", () => {
  const hallazgos = auditarPack(arcadeFalso(), "aoe").filter((h) => h.regla === "sesion-nueva");
  assert.deepEqual(hallazgos, []);
});

test("sin nuevaSesion ni session.started la sesion nueva queda muda: hallazgo", () => {
  const arcade = arcadeFalso();
  borrarEvento(arcade, "session.started");
  const hallazgos = auditarPack(arcade, "aoe");
  const muda = hallazgos.filter((h) => h.regla === "sesion-nueva");
  assert.equal(muda.length, 1);
  assert.equal(hallazgos.length, 2, "además queda session.started sin cablear");
});

test("nuevaSesion que apunta a un archivo inexistente tambien es hallazgo", () => {
  const arcade = arcadeFalso();
  const sel = leerSel(arcade);
  sel.nuevaSesion = ["no-existe"];
  delete sel.choices["session.started"];
  writeFileSync(selPath(arcade), JSON.stringify(sel, null, 2));
  const muda = auditarPack(arcade, "aoe").filter((h) => h.regla === "sesion-nueva");
  assert.equal(muda.length, 1);
});

test("auditarTodos recorre todos los packs del arcade", () => {
  const arcade = arcadeFalso();
  const otro = join(arcade, "sounds", "cs16");
  mkdirSync(otro, { recursive: true });
  writeFileSync(join(otro, "seleccion.json"), JSON.stringify({ choices: {} }, null, 2));
  const porPack = auditarTodos(arcade).map((h) => h.pack);
  assert.deepEqual([...new Set(porPack)], ["cs16"]);
  assert.ok(porPack.length >= EVENTOS.length, "el pack vacío deja un hallazgo por evento");
});

test("contrato: los packs del repo cumplen las reglas", () => {
  const repo = join(import.meta.dirname, "..");
  const hallazgos = auditarTodos(repo);
  const detalle = hallazgos.map((h) => `[${h.pack}] ${h.regla}: ${h.detalle}`).join("\n");
  assert.deepEqual(hallazgos, [], `los packs no cumplen el contrato:\n${detalle}`);
});

test("desinstalar devuelve los sonidos de fabrica de Gentle Shell", () => {
  const dir = mkdtempSync(join(tmpdir(), "restore-"));
  const live = join(dir, "notifications.json");
  writeFileSync(
    live,
    JSON.stringify(
      {
        schema: "gentle-shell.notifications/v1",
        enabled: true,
        audio: {
          backend: "auto",
          minimumIntervalMs: 1000,
          events: {
            "agent.started": null,
            "agent.failed": "file:/x/terwin.wav",
            "context.high": "file:/x/bombdef.wav",
          },
        },
      },
      null,
      2,
    ),
  );

  const resumen = restaurarPorDefecto(live);
  const data = JSON.parse(readFileSync(live, "utf-8"));

  assert.equal(data.audio.events["agent.failed"], "builtin:error", "prioridad 3 vuelve al error de fábrica");
  assert.equal(data.audio.events["context.high"], "builtin:attention", "prioridad 2 vuelve a attention");
  assert.equal(data.audio.events["agent.completed"], "builtin:success", "prioridad 1 vuelve a success");
  assert.equal(data.audio.events["agent.started"], null, "prioridad 0 ya venía en silencio");
  assert.equal(data.audio.events["session.shutdown"], null);
  assert.equal(data.enabled, true, "no apaga las notificaciones");
  assert.equal(data.audio.minimumIntervalMs, 1000, "no toca los límites de tiempo");
  assert.equal(resumen.restaurados, 15);
  assert.equal(readdirSync(dir).filter((f) => f.includes(".bak-")).length, 1, "deja backup antes de escribir");
});
