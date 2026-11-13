import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync, readFileSync, writeFileSync, readdirSync, appendFileSync } from "node:fs";
import { join, dirname } from "node:path";

const OCULTOS = new Set(["gentle", "abuela"]);

function setEmoteSet(path: string, juego: string): boolean {
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

function findArcade(cwd: string): string | null {
  const cands = [
    join(cwd, "gentle-emote-arcade"),
    join(dirname(cwd), "gentle-emote-arcade"),
  ];
  for (const c of cands) {
    if (existsSync(join(c, "sounds")) && existsSync(join(c, "emotes"))) return c;
  }
  return null;
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

function resolverArchivo(arcade: string, juego: string, nombre: string): string | null {
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

export default function (pi: ExtensionAPI) {
  traza(`cargo extension cwd=${process.cwd()}`);
  const home = process.env.HOME ?? process.env.USERPROFILE ?? "";
  const agentDir =
    process.env.PI_CODING_AGENT_DIR || join(home, ".gentle-shell", "agent");
  const cwd = process.cwd();

  const comando = {
    description:
      "Cambiar de juego (sprites + sonidos): /emote:juego aoe|minecraft|cs16|starcraft|lol|misc|gentle(abuela)",
    getArgumentCompletions: (prefix: string) => {
      traza(`completions prefix=${JSON.stringify(prefix)}`);
      const arcade = findArcade(cwd);
      let juegos = ["aoe", "minecraft", "cs16", "starcraft", "lol", "misc"];
      if (arcade) {
        try {
          juegos = readdirSync(join(arcade, "sounds"), { withFileTypes: true })
            .filter((d) => d.isDirectory())
            .map((d) => d.name)
            .filter((j) => !OCULTOS.has(j));
        } catch {
          /* usa la lista fija */
        }
      }
      return juegos
        .filter((j) => j.startsWith(prefix.trim()))
        .map((j) => ({ value: j, label: j, description: `Pack ${j}` }));
    },
    handler: async (args: string, ctx: any) => {
      traza(`handler args=${JSON.stringify(args)}`);
      const arcade = findArcade(cwd);
      const mapPath = findProjectMap(cwd, arcade);

      // Parse args.
      const tokens = args.trim().split(/\s+/).filter(Boolean);
      let juego = "";
      let invasividad = "";
      let proyecto = cwd;
      let i = 0;
      while (i < tokens.length) {
        const t = tokens[i];
        if (t === "--invasividad") { invasividad = tokens[i + 1] ?? ""; i += 2; continue; }
        if (t === "--proyecto") { proyecto = tokens[i + 1] ?? cwd; i += 2; continue; }
        if (t === "--dry-run") { i += 1; continue; }
        if (!juego) juego = t;
        else if (!invasividad && (t === "todo" || t === "esencial" || t === "guardia")) invasividad = t;
        i += 1;
      }

      // Project map defaults.
      const entry = readProjectEntry(mapPath, proyecto);
      if (!juego && entry.juego) juego = String(entry.juego);
      if (!invasividad && entry.invasividad) invasividad = String(entry.invasividad);

      let juegos: string[] = ["aoe", "minecraft", "cs16", "starcraft", "lol", "misc"];
      if (arcade) {
        try {
          juegos = readdirSync(join(arcade, "sounds"), { withFileTypes: true })
            .filter((d) => d.isDirectory())
            .map((d) => d.name)
            .filter((j) => !OCULTOS.has(j))
            .sort();
        } catch { /* lista fija */ }
      }
      juego = (juego || "").trim().toLowerCase();
      if (juego === "abuela") juego = "gentle";
      const porNum = /^(\d+)$/.exec(juego);
      if (porNum) juego = juegos[parseInt(porNum[1], 10) - 1] ?? "";
      if (!juego) {
        const hit = juegos.filter((j) => j.startsWith(args.trim().toLowerCase()));
        if (hit.length === 1) juego = hit[0];
      }
      if (!invasividad) invasividad = "todo";
      if (!["todo", "esencial", "guardia"].includes(invasividad)) invasividad = "todo";

      const selPath = arcade && juego
        ? join(arcade, "sounds", juego, "seleccion.json")
        : null;
      if (!juego || !selPath || !existsSync(selPath)) {
        const lista = juegos.map((j, i) => `${i + 1}=${j}`).join("  ");
        ctx.ui?.notify?.(
          `[juego] elegí número: /emote:juego <n> — ${lista}`,
          "info",
        );
        return;
      }

      // Sprites: gentle/misc usan arte de aoe.
      const spritesJuego = (juego === "gentle" || juego === "misc") ? "aoe" : juego;
      for (const p of [
        join(agentDir, "extensions", "gentle-emote", "config.json"),
        join(cwd, ".pi", "extensions", "gentle-emote", "config.json"),
      ]) {
        setEmoteSet(p, spritesJuego);
      }

      let eventos = 0;
      try {
        const sel = JSON.parse(readFileSync(selPath, "utf-8"));
        const base = join(arcade!, "sounds", juego);
        const livePath = join(
          home,
          ".gentle-shell",
          "config",
          "gentle-ai",
          "notifications.json",
        );
        if (existsSync(livePath)) {
          const stamp = new Date()
            .toISOString()
            .replace(/[:.]/g, "")
            .slice(0, 15);
          writeFileSync(
            `${livePath}.bak-${stamp}`,
            readFileSync(livePath, "utf-8"),
          );
          const live = JSON.parse(readFileSync(livePath, "utf-8"));
          live.audio = live.audio ?? {};
          live.audio.events = live.audio.events ?? {};
          const ev = live.audio.events;
          const permitidos = INV_PERMITIDOS[invasividad] ?? INV_PERMITIDOS.todo;

          const plan: Record<string, string | null> = {};
          for (const evento of EVENTOS) {
            const nombre = sel.choices?.[evento];
            if (nombre == null) { plan[evento] = null; continue; }
            const resuelto = resolverArchivo(arcade!, juego, String(nombre));
            plan[evento] = resuelto;
          }

          for (const evento of EVENTOS) {
            const val = plan[evento];
            if (!permitidos.has(evento) || val == null) {
              ev[evento] = null;
            } else if (val.startsWith("builtin:")) {
              ev[evento] = val;
              eventos += 1;
            } else {
              ev[evento] = `file:${val}`;
              eventos += 1;
            }
          }
          ev["session.shutdown"] = null;
          writeFileSync(livePath, JSON.stringify(live, null, 2));
        }
      } catch {
        /* sin pack de sonidos: quedan solo los sprites */
      }
      ctx.ui?.notify?.(
        `[juego] → ${juego} (sprites + ${eventos} sonidos, ${invasividad}). /reload para ver+oír.`,
        "info",
      );
    },
  };
  pi.registerCommand?.("emote:juego", comando);
}
