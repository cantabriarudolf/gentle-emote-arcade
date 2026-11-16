import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, readdirSync, cpSync, rmSync } from "node:fs";
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
  const manejadores = new Map<string, any>();
  mod.default({
    registerCommand: (name: string, comando: any) => registro.push({ name, comando }),
    on: (nombre: string, fn: any) => manejadores.set(nombre, fn),
  });
  assert.equal(registro.length, 1, "debe registrar exactamente un comando");
  return { mod, nombre: registro[0].name, comando: registro[0].comando, manejadores };
}

/**
 * Simula la UI de seleccion: una respuesta por llamada, en orden. Cada respuesta
 * matchea una opcion exacta o un prefijo unico (asi `c` elige `c — guardia ...`).
 */
function ctxFalso(...selecciones: (string | undefined)[]) {
  const avisos: { mensaje: string; tipo: string }[] = [];
  const titulos: string[] = [];
  const menus: string[][] = [];
  let recargas = 0;
  let i = 0;
  return {
    avisos,
    titulos,
    menus,
    recargas: () => recargas,
    ctx: {
      reload: async () => {
        recargas += 1;
      },
      ui: {
        select: async (titulo: string, opciones: string[]) => {
          titulos.push(titulo);
          menus.push(opciones);
          const pedido = selecciones[i++];
          if (pedido === undefined) return undefined;
          if (opciones.includes(pedido)) return pedido;
          const hits = opciones.filter((o) => o.startsWith(pedido));
          return hits.length === 1 ? hits[0] : undefined;
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
  assert.equal(mod.parseArgs("aoe c", "/base").invasividad, "c", "el set tambien va como segundo token");
  assert.equal(mod.parseArgs("", "/base").proyecto, "/base");
  assert.equal(mod.parseArgs("-n", "/base").dryRun, true);
});

test("sin argumentos abre el menu y aplica el juego elegido", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos, titulos, recargas } = ctxFalso("minecraft", "a");
  const antesLive = readFileSync(sb.live, "utf-8");

  await comando.handler("", ctx);

  assert.equal(recargas(), 1, "una recarga automatica por aplicacion");

  assert.equal(titulos.length, 2, "debe abrir los dos menus: juego y set");
  assert.match(titulos[0], /Elegí juego/);
  const agent = JSON.parse(readFileSync(sb.agentConfig, "utf-8"));
  const project = JSON.parse(readFileSync(sb.projectConfig, "utf-8"));
  assert.equal(agent.emotes[0]["emote-set"], "gentleman", "el sprite global no se toca");
  assert.equal(project.emotes[0]["emote-set"], "minecraft", "el sprite es del proyecto");
  assert.equal(agent.debug, true, "no debe perder el resto de la config");

  assert.equal(readFileSync(sb.live, "utf-8"), antesLive, "el audio global no se toca: el hook lo aplica al abrir sesion");
  assert.match(avisos.at(-1)?.mensaje ?? "", /Recargado/, "debe recargar solo, sin /reload manual");
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

test("el menu pregunta el juego y despues el set de sonidos a/b/c", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos, titulos, menus } = ctxFalso("minecraft", "c");

  await comando.handler("", ctx);

  assert.equal(titulos.length, 2, "debe preguntar juego y despues set de sonidos");
  assert.match(titulos[0], /Elegí juego/);
  assert.match(titulos[1], /auditivas/i);
  assert.equal(menus[1].length, 3, "el segundo menu ofrece a, b y c");
  assert.match(menus[1][0], /^a\b/);
  assert.match(menus[1][1], /^b\b/);
  assert.match(menus[1][2], /^c\b/);

  const mapa = JSON.parse(readFileSync(join(sb.cwd, ".pi", "extensions", "game-select", "projects.json"), "utf-8"));
  assert.deepEqual(mapa[sb.cwd], { juego: "minecraft", invasividad: "guardia" }, "el set queda en el mapa del proyecto");
  assert.match(avisos.at(-1)?.mensaje ?? "", /guardia/);
  assert.match(avisos.at(-1)?.mensaje ?? "", /6 sonidos/);
});

test("a, b y c son los tres sets: todo, esencial y guardia", async () => {
  const sb = crearSandbox(["aoe"]);
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  assert.equal(mod.resolverNivel("a"), "todo");
  assert.equal(mod.resolverNivel("B"), "esencial");
  assert.equal(mod.resolverNivel("c"), "guardia");
  assert.equal(mod.resolverNivel("guardia"), "guardia");
  assert.equal(mod.resolverNivel(""), "");
  assert.equal(mod.resolverNivel("zzz"), "");
  assert.equal(mod.planSonidos(sb.arcade, "aoe", "todo").asignados, 14);
  assert.equal(mod.planSonidos(sb.arcade, "aoe", "esencial").asignados, 12);
  assert.equal(mod.planSonidos(sb.arcade, "aoe", "guardia").asignados, 6);
});

test("el menu guarda juego y set por proyecto y los reusa la proxima vez", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  await comando.handler("", ctxFalso("minecraft", "b").ctx);

  const mapa = JSON.parse(readFileSync(join(sb.cwd, ".pi", "extensions", "game-select", "projects.json"), "utf-8"));
  assert.deepEqual(mapa[sb.cwd], { juego: "minecraft", invasividad: "esencial" });

  // El set guardado es el default para usos sin UI (dry-run del script).
  const segunda = ctxFalso(undefined);
  await comando.handler("minecraft --dry-run", segunda.ctx);

  assert.equal(segunda.titulos.length, 0, "dry-run no pregunta nada");
  assert.match(segunda.avisos.at(-1)?.mensaje ?? "", /dry-run: minecraft \(12 sonidos, esencial\)/);
});

test("cambiar de juego por argumento vuelve a preguntar el set", async () => {
  const sb = crearSandbox(["aoe", "minecraft", "lol"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  await comando.handler("", ctxFalso("minecraft", "a").ctx);
  const mapaPath = join(sb.cwd, ".pi", "extensions", "game-select", "projects.json");
  assert.equal(JSON.parse(readFileSync(mapaPath, "utf-8"))[sb.cwd].invasividad, "todo");

  const segunda = ctxFalso("c");
  await comando.handler("lol", segunda.ctx);

  assert.equal(segunda.titulos.length, 1, "con el juego por argumento igual pregunta el set");
  assert.match(segunda.titulos[0], /auditivas/i);
  assert.deepEqual(JSON.parse(readFileSync(mapaPath, "utf-8"))[sb.cwd], { juego: "lol", invasividad: "guardia" });
  assert.match(segunda.avisos.at(-1)?.mensaje ?? "", /6 sonidos, guardia/);
});

test("sin menu, con el set por argumento, igual recarga solo", async () => {
  const sb = crearSandbox(["aoe"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos, recargas } = ctxFalso(undefined);

  await comando.handler("aoe --invasividad c", ctx);

  assert.equal(recargas(), 1, "debe recargar aunque no haya menu");
  assert.match(avisos.at(-1)?.mensaje ?? "", /Recargado/);
});

test("cancelar el set de sonidos no escribe nada", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const antesLive = readFileSync(sb.live, "utf-8");
  const antesAgent = readFileSync(sb.agentConfig, "utf-8");
  const { ctx, avisos } = ctxFalso("minecraft", undefined);

  await comando.handler("", ctx);

  assert.equal(readFileSync(sb.live, "utf-8"), antesLive);
  assert.equal(readFileSync(sb.agentConfig, "utf-8"), antesAgent);
  assert.equal(existsSync(join(sb.cwd, ".pi", "extensions", "game-select", "projects.json")), false);
  assert.match(avisos.at(-1)?.mensaje ?? "", /sin cambios/i);
});

test("el set se puede elegir por argumento con a, b o c", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos, titulos } = ctxFalso(undefined);

  await comando.handler("aoe --invasividad c", ctx);

  assert.equal(titulos.length, 0, "con el set en el argumento no hay menu");
  const mapaPath = join(sb.cwd, ".pi", "extensions", "game-select", "projects.json");
  assert.deepEqual(JSON.parse(readFileSync(mapaPath, "utf-8"))[sb.cwd], { juego: "aoe", invasividad: "guardia" });
  assert.match(avisos.at(-1)?.mensaje ?? "", /6 sonidos, guardia/);
});

test("sin UI de seleccion el respaldo numérico tambien dice los sets", async () => {
  const sb = crearSandbox(["aoe", "minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const avisos: { mensaje: string; tipo: string }[] = [];
  const ctx = { ui: { notify: (mensaje: string, tipo: string) => avisos.push({ mensaje, tipo }) } };

  await comando.handler("", ctx);

  const mensaje = avisos.at(-1)?.mensaje ?? "";
  assert.match(mensaje, /elegí número/);
  assert.match(mensaje, /--invasividad a\|b\|c/);
});

test("gentle usa sus propias escenas y misc sigue con el arte de aoe", async () => {
  const sb = crearSandbox(["gentle", "misc"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx } = ctxFalso(undefined);

  await comando.handler("gentle --invasividad a", ctx);
  assert.equal(JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"], "gentle");

  await comando.handler("misc --invasividad a", ctx);
  assert.equal(
    JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"],
    "aoe",
    "misc no tiene arte propio: sigue usando aoe",
  );
});

test("planSonidos elige al azar entre el principal y sus variantes", async () => {
  const sb = crearSandbox(["aoe"]);
  const selPath = join(sb.arcade, "sounds", "aoe", "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  writeFileSync(join(sb.arcade, "sounds", "aoe", "agent-failed-2.wav"), "RIFF");
  sel.variantes = { "agent.failed": ["agent-failed-2"] };
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  assert.match(mod.planSonidos(sb.arcade, "aoe", "todo", () => 0).eventos["agent.failed"], /agent-failed\.wav$/);
  assert.match(mod.planSonidos(sb.arcade, "aoe", "todo", () => 0.99).eventos["agent.failed"], /agent-failed-2\.wav$/);
  assert.equal(mod.planSonidos(sb.arcade, "aoe", "guardia", () => 0).asignados, 6,
    "el set recorta igual con variantes");
});

test("la activacion de gentle elige entre las variantes de abuela y cae al coin", async () => {
  const sb = crearSandbox(["gentle"]);
  const dir = join(sb.arcade, "sounds", "gentle");
  writeFileSync(join(dir, "coin.wav"), "RIFF");
  writeFileSync(join(dir, "abuela-1.wav"), "RIFF");
  const selPath = join(dir, "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  sel.activacionVariantes = ["coin", "abuela-1"];
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod, comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  assert.match(mod.resolverActivacion(sb.arcade, "gentle", () => 0), /gentle\/coin\.wav$/);
  assert.match(mod.resolverActivacion(sb.arcade, "gentle", () => 0.99), /gentle\/abuela-1\.wav$/);

  // sin la clave, el fallback sigue siendo el coin de siempre
  const sinAbuela = JSON.parse(readFileSync(selPath, "utf-8"));
  delete sinAbuela.activacionVariantes;
  writeFileSync(selPath, JSON.stringify(sinAbuela, null, 2));
  assert.match(mod.resolverActivacion(sb.arcade, "gentle", () => 0.99), /gentle\/coin\.wav$/);

  // y el comando la usa al activar el easter egg
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };
  await comando.handler("gentle --invasividad a", ctxFalso(undefined).ctx);
  assert.match(jugados[0], /gentle\/coin\.wav$/);
});

test("con una sola toma de abuela el coin ya no suena", async () => {
  const sb = crearSandbox(["gentle"]);
  const dir = join(sb.arcade, "sounds", "gentle");
  writeFileSync(join(dir, "coin.wav"), "RIFF");
  writeFileSync(join(dir, "abuela-1.wav"), "RIFF");
  const selPath = join(dir, "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  sel.activacionVariantes = ["abuela-1"];
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod, comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  for (const tirada of [0, 0.5, 0.99]) {
    assert.match(mod.resolverActivacion(sb.arcade, "gentle", () => tirada), /gentle\/abuela-1\.wav$/,
      "con una sola toma no hay sorteo: siempre la misma");
  }

  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };
  await comando.handler("gentle --invasividad a", ctxFalso(undefined).ctx);
  assert.match(jugados[0], /gentle\/abuela-1\.wav$/, "la activación usa abuela, no el coin");
});

test("sonidoNuevaSesion prefiere la clave propia y cae a session.started", async () => {
  const sb = crearSandbox(["gentle", "aoe"]);
  const dir = join(sb.arcade, "sounds", "gentle");
  writeFileSync(join(dir, "esto-es-una-locura.wav"), "RIFF");
  const selPath = join(dir, "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  sel.nuevaSesion = ["esto-es-una-locura"];
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  assert.match(String(mod.sonidoNuevaSesion(sb.arcade, "gentle")), /gentle\/esto-es-una-locura\.wav$/,
    "el pack que trae su propia frase la conserva");
  assert.match(String(mod.sonidoNuevaSesion(sb.arcade, "aoe")), /aoe\/session-started\.wav$/,
    "sin la clave cae al session.started del pack: ningún pack queda mudo");
});

test("sin nuevaSesion ni session.started el pack no rompe: devuelve null", async () => {
  const sb = crearSandbox(["aoe"]);
  const selPath = join(sb.arcade, "sounds", "aoe", "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  delete sel.choices["session.started"];
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  assert.equal(mod.sonidoNuevaSesion(sb.arcade, "aoe"), null);
  assert.equal(mod.sonidoNuevaSesion(sb.arcade, "no-existe"), null);
});

test("sesion nueva suena tambien en un pack sin clave propia", async () => {
  const sb = crearSandbox(["aoe"]);
  const config = JSON.parse(readFileSync(sb.projectConfig, "utf-8"));
  config.emotes = [{ model: "*", "emote-set": "aoe" }];
  writeFileSync(sb.projectConfig, JSON.stringify(config, null, 2));
  const { mod, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };

  await manejadores.get("session_start")({ reason: "new" }, {});
  assert.match(jugados.at(-1) ?? "", /aoe\/session-started\.wav$/,
    "`/new` no puede quedar en silencio en ningún pack");
});

test("sesion nueva suena, reload y startup no", async () => {
  const sb = crearSandbox(["gentle"]);
  const dir = join(sb.arcade, "sounds", "gentle");
  writeFileSync(join(dir, "esto-es-una-locura.wav"), "RIFF");
  const selPath = join(dir, "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  sel.nuevaSesion = ["esto-es-una-locura"];
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  // El config de proyecto es el que gana en la resolución del pack.
  const config = JSON.parse(readFileSync(sb.projectConfig, "utf-8"));
  config.emotes = [{ model: "*", "emote-set": "gentle" }];
  writeFileSync(sb.projectConfig, JSON.stringify(config, null, 2));

  const { mod, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };
  const sesionNueva = manejadores.get("session_start");
  assert.equal(typeof sesionNueva, "function", "debe escuchar session_start");

  await sesionNueva({ reason: "new" }, {});
  assert.match(jugados.at(-1) ?? "", /gentle\/esto-es-una-locura\.wav$/);

  jugados.length = 0;
  for (const reason of ["reload", "startup", "resume", "fork"]) {
    await sesionNueva({ reason }, {});
  }
  assert.deepEqual(jugados, [], "sólo la sesión nueva suena");
});

test("reproducir informa el motivo cuando no puede sonar", async () => {
  const sb = crearSandbox(["aoe"]);
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const r = await mod.reproducir(join(sb.cwd, "no-existe.wav"));
  assert.equal(r.ok, false);
  assert.match(String(r.error), /no existe/i);
});

test("si el sonido de confirmacion falla, el comando lo avisa", async () => {
  const sb = crearSandbox(["aoe"]);
  const { comando, mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  mod.reproductor.play = async () => ({ ok: false, error: "paplay: sin servidor de audio" });
  const { ctx, avisos } = ctxFalso(undefined);

  await comando.handler("aoe --invasividad a", ctx);

  const aviso = avisos.find((a) => /sin servidor de audio/.test(a.mensaje));
  assert.ok(aviso, "debe avisar por qué no sonó");
  assert.equal(aviso?.tipo, "warning");
  assert.equal(JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"], "aoe",
    "igual aplica el cambio aunque el sonido falle");
});

test("sonidoConfirmacion prefiere session.started y cae a attention", async () => {
  const sb = crearSandbox(["aoe"]);
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  assert.equal(mod.sonidoConfirmacion({ "session.started": "/x/a.wav", "agent.attention": "/x/b.wav" }), "/x/a.wav");
  assert.equal(mod.sonidoConfirmacion({ "session.started": null, "agent.attention": "/x/b.wav" }), "/x/b.wav");
  assert.equal(mod.sonidoConfirmacion({ "session.started": "builtin:success", "agent.attention": null }), null);
});

test("al aplicar suena la confirmacion del pack nuevo", async () => {
  const sb = crearSandbox(["aoe"]);
  const { comando, mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };

  await comando.handler("", ctxFalso("aoe", "a").ctx);
  assert.deepEqual(jugados, [join(sb.arcade, "sounds", "aoe", "session-started.wav")]);

  jugados.length = 0;
  await comando.handler("", ctxFalso("aoe", "c").ctx);
  assert.deepEqual(jugados, [join(sb.arcade, "sounds", "aoe", "agent-attention.wav")], "guardia no tiene session.started");
});

test("dry-run y cancelar no suenan", async () => {
  const sb = crearSandbox(["aoe"]);
  const { comando, mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };

  await comando.handler("aoe --dry-run", ctxFalso(undefined).ctx);
  await comando.handler("", ctxFalso("aoe", undefined).ctx);
  assert.deepEqual(jugados, [], "no debe sonar si no se aplicó nada");
});

test("gentle suena el coin y no la confirmacion", async () => {
  const sb = crearSandbox(["gentle"]);
  writeFileSync(join(sb.arcade, "sounds", "gentle", "coin.wav"), "RIFF");
  const { comando, mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };

  await comando.handler("gentle --invasividad a", ctxFalso(undefined).ctx);
  assert.deepEqual(jugados, [join(sb.arcade, "sounds", "gentle", "coin.wav")]);
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

  assert.equal(JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"], "aoe");
  const mapaPath = join(sb.cwd, ".pi", "extensions", "game-select", "projects.json");
  assert.deepEqual(JSON.parse(readFileSync(mapaPath, "utf-8"))[sb.cwd], { juego: "aoe", invasividad: "guardia" });
  assert.match(avisos.at(-1)?.mensaje ?? "", /6 sonidos, guardia/);
});

test("integracion: el menu aplica un pack real del repo con el set c", async () => {
  // Copia el pack real de aoe al sandbox: datos de verdad, sin tocar la config
  // ni el mapa de proyectos del usuario.
  const sb = crearSandbox([]);
  const repo = join(import.meta.dirname, "..");
  cpSync(join(repo, "sounds", "aoe"), join(sb.arcade, "sounds", "aoe"), { recursive: true });
  const { comando, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const { ctx, avisos, menus } = ctxFalso("aoe", "c");

  await comando.handler("", ctx);

  assert.deepEqual(menus[0], ["aoe"], "solo el pack que existe en el sandbox");
  assert.equal(JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"], "aoe");
  await abrirSesion(manejadores);
  const live = JSON.parse(readFileSync(sb.live, "utf-8"));
  const esperado = join(sb.arcade, "sounds", "aoe", "attack.wav");
  assert.equal(live.audio.events["agent.attention"], `file:${esperado}`);
  assert.equal(live.audio.events["agent.started"], null, "guardia no incluye agent.started");
  assert.match(avisos.at(-1)?.mensaje ?? "", /aoe .*6 sonidos, guardia/);
  assert.deepEqual(
    JSON.parse(readFileSync(join(sb.cwd, ".pi", "extensions", "game-select", "projects.json"), "utf-8"))[sb.cwd],
    { juego: "aoe", invasividad: "guardia" },
  );
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

test("sonidoRotativo sortea en cada llamada entre principal y variantes", async () => {
  const sb = crearSandbox(["gentle"]);
  const dir = join(sb.arcade, "sounds", "gentle");
  for (const nombre of ["a-ver", "a-ver-2", "locura"]) writeFileSync(join(dir, `${nombre}.wav`), "RIFF");
  const selPath = join(dir, "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  sel.choices["agent.started"] = "a-ver";
  sel.variantes = { "agent.started": ["a-ver-2", "locura"] };
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  assert.match(String(mod.sonidoRotativo(sb.arcade, "gentle", "agent.started", () => 0)), /gentle\/a-ver\.wav$/);
  assert.match(String(mod.sonidoRotativo(sb.arcade, "gentle", "agent.started", () => 0.5)), /gentle\/a-ver-2\.wav$/);
  assert.match(String(mod.sonidoRotativo(sb.arcade, "gentle", "agent.started", () => 0.99)), /gentle\/locura\.wav$/);
  assert.equal(mod.sonidoRotativo(sb.arcade, "gentle", "no-existe", () => 0), null);
});

test("aplicar gentle deja el Enter a cargo de la extension, no del scheduler", async () => {
  const sb = crearSandbox(["aoe", "gentle"]);
  const { comando, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  await comando.handler("gentle --invasividad a", ctxFalso(undefined).ctx);
  await abrirSesion(manejadores);
  assert.equal(JSON.parse(readFileSync(sb.live, "utf-8")).audio.events["agent.started"], null,
    "gentle rota: si el scheduler también dispara, suenan dos frases");

  await comando.handler("aoe --invasividad a", ctxFalso(undefined).ctx);
  await abrirSesion(manejadores);
  assert.match(JSON.parse(readFileSync(sb.live, "utf-8")).audio.events["agent.started"], /aoe\/agent-started\.wav$/,
    "el resto de los packs sigue como estaba");
});

test("el Enter rota solo con el pack gentle", async () => {
  const sb = crearSandbox(["aoe", "gentle"]);
  const dir = join(sb.arcade, "sounds", "gentle");
  writeFileSync(join(dir, "a-ver.wav"), "RIFF");
  const selPath = join(dir, "seleccion.json");
  const sel = JSON.parse(readFileSync(selPath, "utf-8"));
  sel.choices["agent.started"] = "a-ver";
  writeFileSync(selPath, JSON.stringify(sel, null, 2));
  const { mod, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const jugados: string[] = [];
  mod.reproductor.play = async (archivo: string) => {
    jugados.push(archivo);
    return { ok: true };
  };
  const turno = manejadores.get("turn_start");
  assert.equal(typeof turno, "function", "debe escuchar turn_start");

  const config = JSON.parse(readFileSync(sb.projectConfig, "utf-8"));
  config.emotes = [{ model: "*", "emote-set": "aoe" }];
  writeFileSync(sb.projectConfig, JSON.stringify(config, null, 2));
  await turno({}, {});
  assert.deepEqual(jugados, [], "con aoe el Enter lo sigue sonando el scheduler");

  config.emotes = [{ model: "*", "emote-set": "gentle" }];
  writeFileSync(sb.projectConfig, JSON.stringify(config, null, 2));
  await turno({}, {});
  assert.match(jugados.at(-1) ?? "", /gentle\/a-ver\.wav$/);
});

/** Dispara el hook de inicio de sesion sin audio: `startup` no saluda. */
async function abrirSesion(manejadores: Map<string, any>) {
  const hook = manejadores.get("session_start");
  assert.equal(typeof hook, "function", "la extension debe escuchar session_start");
  await hook({ reason: "startup" }, { ui: { notify: () => {} } });
}

const MAPA = (cwd: string) => join(cwd, ".pi", "extensions", "game-select", "projects.json");
const respaldos = (cwd: string) =>
  readdirSync(join(cwd, ".gentle-shell", "config", "gentle-ai"))
    .filter((f) => f.startsWith("notifications.json.bak-")).length;

test("elegir juego no toca el audio ni los sprites globales", async () => {
  const sb = crearSandbox(["minecraft"]);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const antesLive = readFileSync(sb.live, "utf-8");
  const antesAgent = readFileSync(sb.agentConfig, "utf-8");

  await comando.handler("", ctxFalso("minecraft", "a").ctx);

  assert.equal(readFileSync(sb.live, "utf-8"), antesLive, "el audio global es de todos los proyectos: no se toca");
  assert.equal(readFileSync(sb.agentConfig, "utf-8"), antesAgent, "los sprites globales tampoco");
  assert.equal(JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"], "minecraft");
  assert.deepEqual(JSON.parse(readFileSync(MAPA(sb.cwd), "utf-8"))[sb.cwd], { juego: "minecraft", invasividad: "todo" });
});

test("abrir sesion aplica el juego del proyecto con backup", async () => {
  const sb = crearSandbox(["minecraft"]);
  const { comando, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  await comando.handler("minecraft --invasividad b", ctxFalso(undefined).ctx);

  await abrirSesion(manejadores);

  const live = JSON.parse(readFileSync(sb.live, "utf-8"));
  assert.match(live.audio.events["agent.failed"], /minecraft\/agent-failed\.wav$/);
  assert.equal(live.audio.events["subagent.queued"], null, "esencial no incluye queued");
  assert.equal(live.audio.events["session.shutdown"], null, "shutdown nunca suena");
  assert.equal(respaldos(sb.cwd), 1, "un backup antes de escribir");
});

test("abrir sesion dos veces no vuelve a escribir ni a respaldar", async () => {
  const sb = crearSandbox(["minecraft"]);
  const { comando, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  await comando.handler("minecraft --invasividad a", ctxFalso(undefined).ctx);

  await abrirSesion(manejadores);
  const primero = readFileSync(sb.live, "utf-8");
  await abrirSesion(manejadores);

  assert.equal(readFileSync(sb.live, "utf-8"), primero, "idempotente");
  assert.equal(respaldos(sb.cwd), 1, "no acumula un backup por sesion");
});

test("un proyecto sin entrada en el mapa vuelve al audio previo", async () => {
  const sb = crearSandbox(["minecraft"]);
  const { comando, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const fabrica = readFileSync(sb.live, "utf-8");
  await comando.handler("minecraft --invasividad a", ctxFalso(undefined).ctx);
  await abrirSesion(manejadores);
  assert.notEqual(readFileSync(sb.live, "utf-8"), fabrica, "primero aplica el pack del proyecto");

  // El mapa existe pero no tiene entrada para este cwd: otro proyecto cualquiera.
  const mapa = JSON.parse(readFileSync(MAPA(sb.cwd), "utf-8"));
  delete mapa[sb.cwd];
  mapa["/tmp/otro-proyecto"] = { juego: "minecraft", invasividad: "todo" };
  writeFileSync(MAPA(sb.cwd), JSON.stringify(mapa, null, 2));

  await abrirSesion(manejadores);

  assert.deepEqual(JSON.parse(readFileSync(sb.live, "utf-8")), JSON.parse(fabrica), "sin entrada se restaura el baseline");
});

test("el baseline guarda el audio previo y no se pisa con un pack", async () => {
  const sb = crearSandbox(["minecraft"]);
  const { comando, manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const fabrica = readFileSync(sb.live, "utf-8");
  const baseline = join(sb.cwd, ".gentle-shell", "config", "gentle-ai", "notifications.baseline.json");
  await comando.handler("minecraft --invasividad a", ctxFalso(undefined).ctx);
  await abrirSesion(manejadores);

  assert.equal(readFileSync(baseline, "utf-8"), fabrica, "el baseline es el audio previo, no el pack");

  await comando.handler("minecraft --invasividad c", ctxFalso(undefined).ctx);
  await abrirSesion(manejadores);
  assert.equal(readFileSync(baseline, "utf-8"), fabrica, "un pack nuevo no reescribe el baseline");
});

test("elegir juego crea el config del proyecto y copia el pack de sprites", async () => {
  const sb = crearSandbox(["minecraft"]);
  mkdirSync(join(sb.arcade, "emotes", "minecraft", "idle"), { recursive: true });
  writeFileSync(join(sb.arcade, "emotes", "minecraft", "emotes.json"), "{}");
  rmSync(sb.projectConfig);
  const { comando } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));

  await comando.handler("minecraft --invasividad a", ctxFalso(undefined).ctx);

  assert.equal(JSON.parse(readFileSync(sb.projectConfig, "utf-8")).emotes[0]["emote-set"], "minecraft",
    "crea el config del proyecto si falta");
  assert.equal(
    existsSync(join(sb.cwd, ".pi", "extensions", "gentle-emote", "emotes", "minecraft", "emotes.json")),
    true,
    "el pack viaja con el proyecto: se resuelve sin el dir global",
  );
});

test("un pack que no existe no deja la sesion muda por accidente", async () => {
  const sb = crearSandbox(["minecraft"]);
  const { manejadores } = await cargarExtension(join(sb.cwd, ".gentle-shell", "agent"));
  const mapa = { [sb.cwd]: { juego: "starcraft", invasividad: "todo" } };
  mkdirSync(join(sb.cwd, ".pi", "extensions", "game-select"), { recursive: true });
  writeFileSync(MAPA(sb.cwd), JSON.stringify(mapa, null, 2));
  const antes = readFileSync(sb.live, "utf-8");

  await abrirSesion(manejadores);

  assert.equal(readFileSync(sb.live, "utf-8"), antes, "sin pack no se toca el audio global");
  assert.equal(respaldos(sb.cwd), 0, "y no deja backup de algo que no aplicó");
});
