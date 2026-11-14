import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync, readFileSync, writeFileSync, readdirSync, appendFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { execFile } from "node:child_process";

const OCULTOS = new Set(["abuela"]);
const JUEGOS_FALLBACK = ["aoe", "minecraft", "cs16", "starcraft", "lol", "misc"];
const INVASIVIDADES = ["todo", "esencial", "guardia"];
const DEFAULT_INVASIVIDAD = "todo";

const HOME_DIR = process.env.HOME ?? process.env.USERPROFILE ?? "";

export interface Opciones {
  juego: string;
  invasividad: string;
  proyecto: string;
  dryRun: boolean;
}

export function setEmoteSet(path: string, juego: string): boolean {
  if (!existsSync(path)) return false;
  try {
    const data = JSON.parse(readFileSync(path, "utf-8"));
    data.emotes = [{ model: "*", "emote-set": juego }];
    writeFileSync(path, JSON.stringify(data, null, 2) + "\n");
    return true;
  } catch {
    return false;
  }
}

export function findArcade(cwd: string): string | null {
  const cands = [
    join(cwd, "gentle-emote-arcade"),
    join(dirname(cwd), "gentle-emote-arcade"),
    process.env.PI_ARCADE_DIR ?? "",
    join(HOME_DIR, "Documentos", "Proyectos", "AoE", "gentle-emote-arcade"),
  ].filter((c) => c.length > 0);
  for (const c of cands) {
    if (existsSync(join(c, "sounds")) && existsSync(join(c, "emotes"))) return c;
  }
  return null;
}

/** Juegos disponibles: los packs con carpeta en `sounds/`, o la lista fija sin arcade. */
export function listarJuegos(arcade: string | null): string[] {
  if (!arcade) return [...JUEGOS_FALLBACK];
  try {
    const juegos = readdirSync(join(arcade, "sounds"), { withFileTypes: true })
      .filter((d) => d.isDirectory())
      .map((d) => d.name)
      .filter((j) => !OCULTOS.has(j))
      .sort();
    return juegos.length > 0 ? juegos : [...JUEGOS_FALLBACK];
  } catch {
    return [...JUEGOS_FALLBACK];
  }
}

/** Acepta nombre, prefijo unico, numero de la lista o el alias `abuela`. */
export function resolverJuego(entrada: string, juegos: string[]): string {
  const limpio = (entrada ?? "").trim().toLowerCase();
  if (!limpio) return "";
  const porNum = /^(\d+)$/.exec(limpio);
  if (porNum) return juegos[parseInt(porNum[1], 10) - 1] ?? "";
  const nombre = limpio === "abuela" ? "gentle" : limpio;
  if (juegos.includes(nombre)) return nombre;
  const hits = juegos.filter((j) => j.startsWith(nombre));
  return hits.length === 1 ? hits[0] : "";
}

export function parseArgs(args: string, cwd: string): Opciones {
  const tokens = (args ?? "").trim().split(/\s+/).filter(Boolean);
  const opciones: Opciones = { juego: "", invasividad: "", proyecto: cwd, dryRun: false };
  let i = 0;
  while (i < tokens.length) {
    const t = tokens[i];
    if (t === "--invasividad") {
      opciones.invasividad = tokens[i + 1] ?? "";
      i += 2;
      continue;
    }
    if (t === "--proyecto") {
      opciones.proyecto = tokens[i + 1] ?? cwd;
      i += 2;
      continue;
    }
    if (t === "--dry-run" || t === "-n") {
      opciones.dryRun = true;
      i += 1;
      continue;
    }
    if (!opciones.juego) opciones.juego = t;
    else if (!opciones.invasividad && INVASIVIDADES.includes(t)) opciones.invasividad = t;
    i += 1;
  }
  return opciones;
}

export function normalizarInvasividad(valor: string): string {
  return INVASIVIDADES.includes(valor) ? valor : DEFAULT_INVASIVIDAD;
}

function findProjectMap(cwd: string, arcade: string | null): string | null {
  const cands = [
    join(cwd, ".pi", "extensions", "game-select", "projects.json"),
    arcade ? join(dirname(arcade), ".pi", "extensions", "game-select", "projects.json") : "",
    join(dirname(cwd), ".pi", "extensions", "game-select", "projects.json"),
  ];
  for (const c of cands) {
    if (c && existsSync(c)) return c;
  }
  return null;
}

function readProjectEntry(mapPath: string | null, proyecto: string): { juego?: string; invasividad?: string } {
  if (!mapPath || !existsSync(mapPath)) return {};
  try {
    const data = JSON.parse(readFileSync(mapPath, "utf-8"));
    const entry = data[proyecto] ?? data[proyecto.replace(/\/$/, "")];
    if (entry && typeof entry === "object") return entry as any;
  } catch {
    /* ignore */
  }
  return {};
}

function traza(msg: string) {
  try {
    appendFileSync("/tmp/game-select.log", `${new Date().toISOString()} ${msg}\n`);
  } catch {
    /* sin fs: no hay traza */
  }
}

export function sonarCoin(arcade: string): Promise<void> {
  const coin = join(arcade, "sounds", "gentle", "coin.wav");
  if (!existsSync(coin)) return Promise.resolve();
  const players: string[][] =
    process.platform === "darwin"
      ? [["afplay", coin]]
      : [["paplay", coin], ["aplay", "-q", coin]];
  return new Promise((resolve) => {
    let done = false;
    const fin = () => { if (!done) { done = true; resolve(); } };
    const to = setTimeout(fin, 3000);
    const intentar = (i: number): void => {
      if (i >= players.length) { clearTimeout(to); fin(); return; }
      execFile(players[i][0], players[i].slice(1), (err) => {
        if (!err) { clearTimeout(to); fin(); }
        else intentar(i + 1);
      });
    };
    intentar(0);
  });
}

const INV_PERMITIDOS: Record<string, Set<string>> = {
  todo: new Set([
    "session.started", "agent.started", "agent.completed", "agent.failed",
    "agent.cancelled", "agent.attention", "subagent.queued", "subagent.running",
    "subagent.waiting", "subagent.completed", "subagent.failed", "subagent.cancelled",
    "subagent.timed_out", "context.high",
  ]),
  esencial: new Set([
    "session.started", "agent.started", "agent.completed", "agent.failed",
    "agent.cancelled", "agent.attention", "subagent.waiting", "subagent.completed",
    "subagent.failed", "subagent.cancelled", "subagent.timed_out", "context.high",
  ]),
  guardia: new Set([
    "agent.attention", "agent.failed", "subagent.waiting", "subagent.failed",
    "subagent.timed_out", "context.high",
  ]),
};

const EVENTOS = [
  "session.started", "agent.started", "agent.completed", "agent.failed",
  "agent.cancelled", "agent.attention", "subagent.queued", "subagent.running",
  "subagent.waiting", "subagent.completed", "subagent.failed", "subagent.cancelled",
  "subagent.timed_out", "context.high",
];

export function resolverArchivo(arcade: string, juego: string, nombre: string): string | null {
  // builtin
  if (nombre.startsWith("builtin:")) return nombre;
  // pack/stem
  if (nombre.includes("/")) {
    const [pack, tallo] = nombre.split("/", 2);
    const base = join(arcade, "sounds", pack);
    const exts = [".wav", ".ogg", ".flac", ".mp3"];
    for (const rel of [tallo, ...exts.map((e) => tallo + e)]) {
      const ruta = join(base, rel);
      if (existsSync(ruta)) return ruta;
    }
    try {
      const golpes = readdirSync(base).filter((f) => f === tallo || f.startsWith(tallo + "."));
      if (golpes.length) return join(base, golpes.sort()[0]);
    } catch {
      /* no-op */
    }
    return null;
  }
  const base = join(arcade, "sounds", juego);
  const exts = [".wav", ".ogg", ".flac", ".mp3"];
  for (const rel of [nombre, ...exts.map((e) => nombre + e)]) {
    const ruta = join(base, rel);
    if (existsSync(ruta)) return ruta;
  }
  try {
    const golpes = readdirSync(base).filter((f) => f === nombre || f.startsWith(nombre + "."));
    if (golpes.length) return join(base, golpes.sort()[0]);
  } catch {
    /* no-op */
  }
  return null;
}

/** Plan evento → archivo para un pack, sin tocar el disco. */
export function planSonidos(
  arcade: string,
  juego: string,
  invasividad: string,
): { eventos: Record<string, string | null>; asignados: number } {
  const selPath = join(arcade, "sounds", juego, "seleccion.json");
  const permitidos = INV_PERMITIDOS[invasividad] ?? INV_PERMITIDOS.todo;
  const eventos: Record<string, string | null> = {};
  let asignados = 0;
  let choices: Record<string, unknown> = {};
  try {
    const sel = JSON.parse(readFileSync(selPath, "utf-8"));
    choices = sel?.choices ?? {};
  } catch {
    /* sin seleccion.json: todo queda en null */
  }
  for (const evento of EVENTOS) {
    const nombre = choices[evento];
    const resuelto = nombre == null ? null : resolverArchivo(arcade, juego, String(nombre));
    if (!permitidos.has(evento) || resuelto == null) {
      eventos[evento] = null;
      continue;
    }
    eventos[evento] = resuelto;
    asignados += 1;
  }
  return { eventos, asignados };
}

export default function (pi: ExtensionAPI) {
  traza(`cargo extension cwd=${process.cwd()}`);
  const home = process.env.HOME ?? process.env.USERPROFILE ?? "";
  const agentDir =
    process.env.PI_CODING_AGENT_DIR || join(home, ".gentle-shell", "agent");
  const cwd = process.cwd();

  const comando = {
    description:
      "Elegir juego (sprites + sonidos): /emote:juego abre el menu, o /emote:juego <juego|n> directo",
    getArgumentCompletions: (prefix: string) => {
      traza(`completions prefix=${JSON.stringify(prefix)}`);
      return listarJuegos(findArcade(cwd))
        .filter((j) => j.startsWith(prefix.trim()))
        .map((j) => ({ value: j, label: j, description: `Pack ${j}` }));
    },
    handler: async (args: string, ctx: any) => {
      traza(`handler args=${JSON.stringify(args)}`);
      const arcade = findArcade(cwd);
      const opciones = parseArgs(args, cwd);
      const mapPath = findProjectMap(cwd, arcade);
      const entry = readProjectEntry(mapPath, opciones.proyecto);
      const juegos = listarJuegos(arcade);

      let juego = resolverJuego(opciones.juego, juegos);
      if (!juego && entry.juego) juego = resolverJuego(String(entry.juego), juegos);

      let invasividad = normalizarInvasividad(
        opciones.invasividad || (entry.invasividad ? String(entry.invasividad) : ""),
      );

      // Sin argumento: menu real; sin UI de seleccion, la lista numerada de siempre.
      if (!juego) {
        if (typeof ctx?.ui?.select === "function") {
          const titulo = arcade
            ? "Elegí juego (sprites + sonidos):"
            : "Elegí juego (arcade no encontrado, no se aplican sonidos):";
          const elegido = await ctx.ui.select(titulo, juegos);
          juego = resolverJuego(String(elegido ?? ""), juegos);
        }
        if (!juego) {
          const lista = juegos.map((j, i) => `${i + 1}=${j}`).join("  ");
          ctx.ui?.notify?.(
            `[juego] elegí número: /emote:juego <n> — ${lista} (arcade: ${arcade ?? "no encontrado"})`,
            "info",
          );
          return;
        }
      }

      // Sprites: gentle/misc usan arte de aoe.
      const spritesJuego = juego === "gentle" || juego === "misc" ? "aoe" : juego;
      const configs = [
        join(agentDir, "extensions", "gentle-emote", "config.json"),
        join(cwd, ".pi", "extensions", "gentle-emote", "config.json"),
      ];
      if (!opciones.dryRun) {
        for (const p of configs) setEmoteSet(p, spritesJuego);
      }

      if (!arcade) {
        ctx.ui?.notify?.(
          `[juego] → ${juego} (solo sprites: arcade no encontrado, sin sonidos)`,
          "warning",
        );
        return;
      }

      const { eventos, asignados } = planSonidos(arcade, juego, invasividad);

      if (opciones.dryRun) {
        ctx.ui?.notify?.(
          `[juego] dry-run: ${juego} (${asignados} sonidos, ${invasividad}). No escribí nada.`,
          "info",
        );
        return;
      }

      const livePath = join(home, ".gentle-shell", "config", "gentle-ai", "notifications.json");
      if (existsSync(livePath)) {
        try {
          const stamp = new Date().toISOString().replace(/[:.]/g, "").slice(0, 15);
          writeFileSync(`${livePath}.bak-${stamp}`, readFileSync(livePath, "utf-8"));
          const live = JSON.parse(readFileSync(livePath, "utf-8"));
          live.audio = live.audio ?? {};
          live.audio.events = live.audio.events ?? {};
          const ev = live.audio.events;
          for (const evento of EVENTOS) {
            const val = eventos[evento];
            ev[evento] = val == null ? null : val.startsWith("builtin:") ? val : `file:${val}`;
          }
          ev["session.shutdown"] = null;
          writeFileSync(livePath, JSON.stringify(live, null, 2));
        } catch {
          /* sin pack de sonidos: quedan solo los sprites */
        }
      }
      if (juego === "gentle") await sonarCoin(arcade);
      ctx.ui?.notify?.(
        `[juego] → ${juego} (sprites + ${asignados} sonidos, ${invasividad}). /reload para ver+oir.`,
        "info",
      );
    },
  };
  pi.registerCommand?.("emote:juego", comando);
}
