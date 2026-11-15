/**
 * Validador de packs de sonido. Reusa `resolverArchivo` de la extension en vez de
 * reimplementar la resolución `pack/tallo`: si el validador y el runtime
 * discreparan, el validador no vale nada.
 *
 *   node scripts/check_packs.ts [arcade]
 *
 * Sale con código 1 si hay hallazgos, así puede correr desde `check_install.sh`.
 */
import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

import { EVENTOS, resolverArchivo } from "../extensions/game-select/index.ts";

export type Regla = "evento-faltante" | "archivo-inexistente" | "colision" | "sesion-nueva";

export interface Hallazgo {
  pack: string;
  regla: Regla;
  detalle: string;
}

/** `agent.completed` → `agent`. Compartir archivo dentro de una familia es legítimo. */
const familia = (evento: string): string => evento.split(".")[0] ?? "";

function leerSeleccion(arcade: string, pack: string): Record<string, unknown> {
  try {
    const sel = JSON.parse(readFileSync(join(arcade, "sounds", pack, "seleccion.json"), "utf-8"));
    return sel && typeof sel === "object" ? (sel as Record<string, unknown>) : {};
  } catch {
    return {};
  }
}

/** Lista de nombres de una clave de sonido, ya sea string o array. */
function nombres(valor: unknown): string[] {
  if (Array.isArray(valor)) return valor.map(String);
  if (typeof valor === "string" && valor) return [valor];
  return [];
}

export function auditarPack(arcade: string, pack: string): Hallazgo[] {
  const sel = leerSeleccion(arcade, pack);
  const choices = (sel.choices ?? {}) as Record<string, unknown>;
  const hallazgos: Hallazgo[] = [];
  const reportar = (regla: Regla, detalle: string) => hallazgos.push({ pack, regla, detalle });

  // R1 — todo evento canónico cableado.
  for (const evento of EVENTOS) {
    if (choices[evento] == null) reportar("evento-faltante", `${evento} no está en choices`);
  }

  // R2 — todo archivo referenciado resuelve.
  const porArchivo = new Map<string, string[]>();
  for (const evento of EVENTOS) {
    const valor = choices[evento];
    if (valor == null) continue;
    const ruta = resolverArchivo(arcade, pack, String(valor));
    if (ruta == null) {
      reportar("archivo-inexistente", `${evento} apunta a ${String(valor)} y no resuelve`);
      continue;
    }
    if (ruta.startsWith("builtin:")) continue;
    const previos = porArchivo.get(ruta) ?? [];
    previos.push(evento);
    porArchivo.set(ruta, previos);
  }

  // R3 — dos familias distintas no pueden compartir archivo: el oído no las separa.
  for (const [ruta, eventos] of porArchivo) {
    const familias = new Set(eventos.map(familia));
    if (familias.size < 2) continue;
    reportar("colision", `${ruta.split("/").slice(-2).join("/")} compartido por ${eventos.join(", ")}`);
  }

  // R4 — `/new` no puede quedar mudo: o hay `nuevaSesion`, o cae a `session.started`.
  const propia = nombres(sel.nuevaSesion)
    .map((nombre) => resolverArchivo(arcade, pack, nombre))
    .filter((ruta): ruta is string => ruta != null);
  const arranque = choices["session.started"] == null
    ? null
    : resolverArchivo(arcade, pack, String(choices["session.started"]));
  if (propia.length === 0 && arranque == null) {
    reportar("sesion-nueva", "ni nuevaSesion ni session.started resuelven: `/new` queda mudo");
  }

  return hallazgos;
}

export function auditarTodos(arcade: string): Hallazgo[] {
  let packs: string[] = [];
  try {
    packs = readdirSync(join(arcade, "sounds"), { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .sort();
  } catch {
    return [{ pack: "-", regla: "evento-faltante", detalle: `no encuentro ${join(arcade, "sounds")}` }];
  }
  return packs.flatMap((pack) => auditarPack(arcade, pack));
}

const esCli = process.argv[1] != null && pathToFileURL(process.argv[1]).href === import.meta.url;
if (esCli) {
  const arcade = process.argv[2] ?? join(import.meta.dirname, "..");
  const hallazgos = auditarTodos(arcade);
  if (hallazgos.length === 0) {
    console.log(`packs ok · ${EVENTOS.length} eventos · sin colisiones entre familias · sesión nueva resuelta`);
    process.exit(0);
  }
  for (const h of hallazgos) console.log(`[${h.pack}] ${h.regla}: ${h.detalle}`);
  console.log(`\n${hallazgos.length} hallazgo(s) en ${arcade}`);
  process.exit(1);
}
