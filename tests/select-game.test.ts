import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const REPO = join(import.meta.dirname, "..");
const SCRIPT = join(REPO, "scripts", "select_game.sh");

/** Proyecto vacío con mapa propio: el script no toca la config real del usuario. */
function sandbox() {
  const cwd = mkdtempSync(join(tmpdir(), "select-game-"));
  const proyecto = join(cwd, "proyecto");
  mkdirSync(proyecto, { recursive: true });
  const mapa = join(cwd, "projects.json");
  writeFileSync(mapa, "{}");
  return { cwd, proyecto, mapa };
}

function correr(args: string[], sb: { cwd: string; mapa: string }): string {
  return execFileSync("bash", [SCRIPT, ...args], {
    cwd: sb.cwd,
    encoding: "utf-8",
    env: { ...process.env, PI_GAME_SELECT_MAP: sb.mapa },
    stdio: ["ignore", "pipe", "pipe"],
  });
}

const configProyecto = (proyecto: string) =>
  JSON.parse(readFileSync(join(proyecto, ".pi", "extensions", "gentle-emote", "config.json"), "utf-8"));

test("el selector escribe sólo el proyecto: config, pack de sprites y mapa", () => {
  const sb = sandbox();

  const salida = correr(["minecraft", "--proyecto", sb.proyecto, "--invasividad", "b"], sb);

  assert.deepEqual(configProyecto(sb.proyecto).emotes, [{ model: "*", "emote-set": "minecraft" }]);
  assert.equal(
    existsSync(join(sb.proyecto, ".pi", "extensions", "gentle-emote", "emotes", "minecraft", "emotes.json")),
    true,
    "el pack de sprites viaja con el proyecto",
  );
  assert.deepEqual(JSON.parse(readFileSync(sb.mapa, "utf-8"))[sb.proyecto], {
    juego: "minecraft",
    invasividad: "esencial",
  });
  assert.match(salida, /DRY-RUN: no toqué/, "el audio global se muestra, no se escribe");
});

test("elegir en un proyecto no le cambia el sprite ni la entrada al otro", () => {
  const sb = sandbox();
  const otro = join(sb.cwd, "otro");
  mkdirSync(otro, { recursive: true });

  correr(["minecraft", "--proyecto", sb.proyecto], sb);
  correr(["aoe", "--proyecto", otro], sb);

  assert.deepEqual(configProyecto(sb.proyecto).emotes, [{ model: "*", "emote-set": "minecraft" }]);
  assert.deepEqual(configProyecto(otro).emotes, [{ model: "*", "emote-set": "aoe" }]);
  const mapa = JSON.parse(readFileSync(sb.mapa, "utf-8"));
  assert.equal(mapa[sb.proyecto].juego, "minecraft");
  assert.equal(mapa[otro].juego, "aoe");
});

test("--dry-run no escribe config, ni pack, ni mapa", () => {
  const sb = sandbox();

  correr(["minecraft", "--proyecto", sb.proyecto, "--dry-run"], sb);

  assert.equal(existsSync(join(sb.proyecto, ".pi")), false, "no crea el .pi del proyecto");
  assert.deepEqual(JSON.parse(readFileSync(sb.mapa, "utf-8")), {}, "no escribe el mapa");
});

test("un config del proyecto ilegible no se pisa", () => {
  const sb = sandbox();
  const dir = join(sb.proyecto, ".pi", "extensions", "gentle-emote");
  mkdirSync(dir, { recursive: true });
  const config = join(dir, "config.json");
  writeFileSync(config, "{ roto");

  assert.throws(() => correr(["minecraft", "--proyecto", sb.proyecto], sb), "el script tiene que fallar");

  assert.equal(readFileSync(config, "utf-8"), "{ roto");
  assert.deepEqual(JSON.parse(readFileSync(sb.mapa, "utf-8")), {}, "no escribe el mapa si no pudo escribir el config");
});
