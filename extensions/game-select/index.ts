import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync, readFileSync, writeFileSync, readdirSync, appendFileSync } from "node:fs";
import { join, dirname } from "node:path";

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

function traza(msg: string) {
  try {
    appendFileSync("/tmp/game-select.log", `${new Date().toISOString()} ${msg}\n`);
  } catch {
    /* sin fs: no hay traza */
  }
}

export default function (pi: ExtensionAPI) {
  traza(`cargo extension cwd=${process.cwd()}`);
  const home = process.env.HOME ?? process.env.USERPROFILE ?? "";
  const agentDir =
    process.env.PI_CODING_AGENT_DIR || join(home, ".gentle-shell", "agent");
  const cwd = process.cwd();

  const comando = {
    description:
      "Cambiar de juego (sprites + sonidos): /emote:juego aoe|minecraft|cs16|starcraft|lol",
    getArgumentCompletions: (prefix: string) => {
      traza(`completions prefix=${JSON.stringify(prefix)}`);
      const arcade = findArcade(cwd);
      let juegos = ["aoe", "minecraft", "cs16", "starcraft", "lol"];
      if (arcade) {
        try {
          juegos = readdirSync(join(arcade, "sounds"), { withFileTypes: true })
            .filter((d) => d.isDirectory())
            .map((d) => d.name);
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
      let juegos: string[] = ["aoe", "minecraft", "cs16", "starcraft", "lol"];
      if (arcade) {
        try {
          juegos = readdirSync(join(arcade, "sounds"), { withFileTypes: true })
            .filter((d) => d.isDirectory())
            .map((d) => d.name)
            .sort();
        } catch { /* lista fija */ }
      }
      let juego = args.trim().toLowerCase();
      const porNum = /^(\d+)$/.exec(juego);
      if (porNum) juego = juegos[parseInt(porNum[1], 10) - 1] ?? "";
      if (!juego) {
        const hit = juegos.filter((j) => j.startsWith(args.trim().toLowerCase()));
        if (hit.length === 1) juego = hit[0];
      }
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
      for (const p of [
        join(agentDir, "extensions", "gentle-emote", "config.json"),
        join(cwd, ".pi", "extensions", "gentle-emote", "config.json"),
      ]) {
        setEmoteSet(p, juego);
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
          const archivos = new Set(readdirSync(base));
          for (const [evento, nombre] of Object.entries<string>(sel.choices)) {
            let archivo = nombre as string;
            if (!archivos.has(archivo)) {
              const hit = [...archivos].find((f) => f === `${nombre}.wav` || f === `${nombre}.mp3` || f.startsWith(`${nombre}.`));
              if (hit) archivo = hit;
            }
            ev[evento] = `file:${join(base, archivo)}`;
          }
          ev["session.shutdown"] = null;
          writeFileSync(livePath, JSON.stringify(live, null, 2));
          eventos = Object.keys(sel.choices).length;
        }
      } catch {
        /* sin pack de sonidos: quedan solo los sprites */
      }
      ctx.ui?.notify?.(
        `[juego] → ${juego} (sprites + ${eventos} sonidos). /reload para ver+oír.`,
        "info",
      );
    },
  };
  pi.registerCommand?.("emote:juego", comando);
}
