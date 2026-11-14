import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const EXT = join(import.meta.dirname, "..", "extensions", "game-select", "index.ts");

const EVENTOS = [
  "session.started", "agent.started", "agent.completed", "agent.failed",
  "agent.cancelled", "agent.attention", "subagent.queued", "subagent.running",
  "subagent.waiting", "subagent.completed", "subagent.failed", "subagent.cancelled",
  "subagent.timed_out", "context.high",
];

interface Sandbox {
  cwd: string;
  arcade: string;
  agentConfig: string;
  projectConfig: string;
  live: string;
}

function crearSandbox(juegos: string[]): Sandbox {
  const cwd = mkdtempSync(join(tmpdir(), "game-select-"));
  const home = join(cwd, "home");
  const arcade = join(cwd, "gentle-emote-arcade");
  mkdirSync(join(arcade, "emotes"), { recursive: true });
  mkdirSync(join(arcade, "sounds"), { recursive: true });
  for (const juego of juegos) {
    const dir = join(arcade, "sounds", juego);
    mkdirSync(dir, { recursive: true });
    const choices: Record<string, string> = {};
    for (const evento of EVENTOS) {
      const archivo = `${evento.replace(/\./g, "-")}.wav`;
      writeFileSync(join(dir, archivo), "RIFF");
      choices[evento] = archivo;
    }
    writeFileSync(join(dir, "seleccion.json"), JSON.stringify({ choices }, null, 2));
  }
  const agentConfig = join(home, ".gentle-shell", "agent", "extensions", "gentle-emote", "config.json");
  mkdirSync(join(home, ".gentle-shell", "agent", "extensions", "gentle-emote"), { recursive: true });
  writeFileSync(agentConfig, JSON.stringify({ emotes: [{ model: "*", "emote-set": "gentleman" }], debug: true }, null, 2));
  const projectConfig = join(home, ".pi", "extensions", "gentle-emote", "config.json");
  mkdirSync(join(home, ".pi", "extensions", "gentle-emote"), { recursive: true });
  writeFileSync(projectConfig, JSON.stringify({ emotes: [{ model: "*", "emote-set": "gentleman" }], debug: true }, null, 2));
  const live = join(home, ".gentle-shell", "config", "gentle-ai", "notifications.json");
  mkdirSync(join(home, ".gentle-shell", "config", "gentle-ai"), { recursive: true });
  writeFileSync(live, JSON.stringify({ enabled: true, audio: { events: { "agent.failed": "builtin:error" } } }, null, 2));
  return { cwd: home, arcade, agentConfig, projectConfig, live };
}

/** Importa la extension fresca: lee cwd y env en el init del modulo. */
async function cargarExtension(agentDir: string) {
  // La extension resuelve HOME y cwd al importarse: se aisla el sandbox completo
  // para que ningun test escriba en la config real del usuario.
  const home = join(agentDir, "..", "..");
  process.env.HOME = home;
  process.env.USERPROFILE = home;
  process.env.PI_CODING_AGENT_DIR = agentDir;
  process.chdir(home);
  const mod = await import(`${pathToFileURL(EXT).href}?v=${Math.random()}`);
  const registro: { name: string; comando: any }[] = [];
  mod.default({ registerCommand: (name: string, comando: any) => registro.push({ name, comando }) });
  assert.equal(registro.length, 1, "debe registrar exactamente un comando");
  return { mod, nombre: registro[0].name, comando: registro[0].comando };
}

function ctxFalso(seleccion: string | undefined) {
  const avisos: { mensaje: string; tipo: string }[] = [];
  const titulos: string[] = [];
  return {
    avisos,
    titulos,
    ctx: {
      ui: {
        select: async (titulo: string, opciones: string[]) => {
          titulos.push(titulo);
          return opciones.includes(seleccion ?? "") ? seleccion : undefined;
        },
        notify: (mensaje: string, tipo: string) => avisos.push({ mensaje, tipo }),
      },
    },
  };
}

test("listarJuegos ordena los packs y esconde los ocultos", async () => {
  const sb = crearSandbox(["aoe", "minecraft", "cs16"]);
  mkdirSync(join(sb.arcade, "sounds", "abuela"), { recursive: true });
  writeFileSync(join(sb.arcade, "sounds", "suelto.txt"), "");
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  assert.deepEqual(mod.listarJuegos(sb.arcade), ["aoe", "cs16", "minecraft"]);
});

test("resolverJuego entiende nombre, numero, prefijo y alias abuela", async () => {
  const sb = crearSandbox(["aoe", "cs16", "gentle", "minecraft"]);
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const juegos = mod.listarJuegos(sb.arcade);
  assert.equal(mod.resolverJuego("aoe", juegos), "aoe");
  assert.equal(mod.resolverJuego("2", juegos), "cs16");
  assert.equal(mod.resolverJuego("mine", juegos), "minecraft");
  assert.equal(mod.resolverJuego("abuela", juegos), "gentle");
  assert.equal(mod.resolverJuego("zzz", juegos), "");
  assert.equal(mod.resolverJuego("", juegos), "");
});

test("parseArgs separa flags, proyecto e invasividad", async () => {
  const sb = crearSandbox(["aoe"]);
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const ops = mod.parseArgs("minecraft --invasividad guardia --proyecto /tmp/x --dry-run", "/base");
  assert.deepEqual(ops, {
    juego: "minecraft",
    invasividad: "guardia",
    proyecto: "/tmp/x",
    dryRun: true,
  });
  assert.equal(mod.parseArgs("", "/base").proyecto, "/base");
  assert.equal(mod.parseArgs("-n", "/base").dryRun, true);
});

test("sin argumentos abre el menu y aplica el juego elegido", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos, titulos } = ctxFalso("minecraft");

  await comando.handler("", ctx);

  assert.equal(titulos.length, 1, "debe abrir un unico menu");
  assert.match(titulos[0], /Elegí juego/);
  const agent = JSON.parse(readFileSync(sb.agentConfig, "utf-8"));
  const project = JSON.parse(readFileSync(sb.projectConfig, "utf-8"));
  assert.equal(agent.emotes[0]["emote-set"], "minecraft");
  assert.equal(project.emotes[0]["emote-set"], "minecraft");
  assert.equal(agent.debug, true, "no debe perder el resto de la config");

  const live = JSON.parse(readFileSync(sb.live, "utf-8"));
  assert.match(live.audio.events["agent.failed"], /minecraft\/agent-failed\.wav$/);
  assert.match(live.audio.events["context.high"], /minecraft\/context-high\.wav$/);
  assert.match(live.audio.events["subagent.queued"], /minecraft\/subagent-queued\.wav$/);
  assert.equal(live.audio.events["session.shutdown"], null, "shutdown nunca suena");
  assert.equal(avisos.at(-1)?.mensaje.includes("/reload"), true, "debe avisar del /reload");
  const backups = readdirSync(join(sb.cwd, ".gentle-shell", "config", "gentle-ai"))
    .filter((f) => f.startsWith("notifications.json.bak-"));
  assert.equal(backups.length, 1, "debe dejar backup antes de escribir");
});

test("el menu cancelado no escribe nada y cae en la lista numerada", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos } = ctxFalso(undefined);
  const antes = readFileSync(sb.live, "utf-8");

  await comando.handler("", ctx);

  assert.equal(readFileSync(sb.live, "utf-8"), antes);
  assert.equal(JSON.parse(readFileSync(sb.agentConfig, "utf-8")).emotes[0]["emote-set"], "gentleman");
  assert.match(avisos.at(-1)?.mensaje ?? "", /elegí número/);
});

test("--dry-run no toca config ni notifications.json", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos } = ctxFalso(undefined);
  const antesLive = readFileSync(sb.live, "utf-8");
  const antesAgent = readFileSync(sb.agentConfig, "utf-8");
  const dirLive = join(sb.cwd, ".gentle-shell", "config", "gentle-ai");
  const backupsAntes = readdirSync(dirLive).filter((f) => f.includes(".bak-")).length;

  await comando.handler("minecraft --dry-run", ctx);

  assert.equal(readFileSync(sb.live, "utf-8"), antesLive);
  assert.equal(readFileSync(sb.agentConfig, "utf-8"), antesAgent);
  const backupsDespues = readdirSync(dirLive).filter((f) => f.includes(".bak-")).length;
  assert.equal(backupsDespues, backupsAntes, "dry-run no debe crear backups");
  assert.match(avisos.at(-1)?.mensaje ?? "", /dry-run: minecraft/);
});

test("el argumento directo sigue funcionando (aoe, invasividad guardia)", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos } = ctxFalso(undefined);

  await comando.handler("aoe --invasividad guardia", ctx);

  assert.equal(JSON.parse(readFileSync(sb.agentConfig, "utf-8")).emotes[0]["emote-set"], "aoe");
  const live = JSON.parse(readFileSync(sb.live, "utf-8"));
  assert.match(live.audio.events["agent.failed"], /aoe\/agent-failed\.wav$/);
  assert.equal(live.audio.events["agent.started"], null, "guardia no incluye agent.started");
  assert.match(avisos.at(-1)?.mensaje ?? "", /6 sonidos, guardia/);
});

test("resolverArchivo acepta nombre, pack/stem y builtin", async () => {
  const sb = crearSandbox(["aoe"]);
  mkdirSync(join(sb.arcade, "sounds", "misc"), { recursive: true });
  writeFileSync(join(sb.arcade, "sounds", "misc", "coin.wav"), "RIFF");
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  assert.match(mod.resolverArchivo(sb.arcade, "aoe", "agent-failed"), /aoe\/agent-failed\.wav$/);
  assert.match(mod.resolverArchivo(sb.arcade, "aoe", "misc/coin"), /misc\/coin\.wav$/);
  assert.equal(mod.resolverArchivo(sb.arcade, "aoe", "builtin:error"), "builtin:error");
  assert.equal(mod.resolverArchivo(sb.arcade, "aoe", "no-existe"), null);
});
