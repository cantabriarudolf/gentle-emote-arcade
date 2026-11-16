import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync, readFileSync, writeFileSync, readdirSync, appendFileSync, statSync, mkdirSync, cpSync, renameSync, unlinkSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { execFile } from "node:child_process";

const OCULTOS = new Set(["abuela"]);
const JUEGOS_FALLBACK = ["aoe", "minecraft", "cs16", "starcraft", "lol", "misc"];
const DEFAULT_INVASIVIDAD = "todo";

/** Los tres sets de notificaciones auditivas que ofrece el menu: a, b y c. */
export const SETS_SONIDO = [
  { id: "a", nivel: "todo", etiqueta: "a — todo (14 sonidos: todo lo que pasa)" },
  { id: "b", nivel: "esencial", etiqueta: "b — esencial (12: sin queued/running)" },
  { id: "c", nivel: "guardia", etiqueta: "c — guardia (6: sólo los que piden tu mano)" },
];

const HOME_DIR = process.env.HOME ?? process.env.USERPROFILE ?? "";

export interface Opciones {
  juego: string;
  invasividad: string;
  proyecto: string;
  dryRun: boolean;
}

export function setEmoteSet(path: string, juego: string): boolean {
  let data: any = {};
  if (existsSync(path)) {
    try {
      data = JSON.parse(readFileSync(path, "utf-8"));
    } catch {
      data = {};
    }
  } else {
    try {
      mkdirSync(dirname(path), { recursive: true });
    } catch {
      /* si no se puede crear, abajo falla la escritura */
    }
  }
  try {
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
    else if (!opciones.invasividad && resolverNivel(t)) opciones.invasividad = t;
    i += 1;
  }
  return opciones;
}

export function normalizarInvasividad(valor: string): string {
  return resolverNivel(valor) || DEFAULT_INVASIVIDAD;
}

/** Acepta el nivel (`todo`/`esencial`/`guardia`), la letra del menu (`a`/`b`/`c`) o un prefijo unico. */
export function resolverNivel(entrada: string): string {
  const limpio = String(entrada ?? "").trim().toLowerCase();
  if (!limpio) return "";
  const porNombre = SETS_SONIDO.find((s) => s.nivel === limpio);
  if (porNombre) return porNombre.nivel;
  const porLetra = /^([abc])\b/.exec(limpio);
  if (porLetra) return SETS_SONIDO.find((s) => s.id === porLetra[1])?.nivel ?? "";
  const porPrefijo = SETS_SONIDO.filter((s) => s.nivel.startsWith(limpio));
  return porPrefijo.length === 1 ? porPrefijo[0].nivel : "";
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

/** Ruta del mapa por proyecto: el archivo que ya existe o el del cwd. */
export function projectsPath(cwd: string, arcade: string | null): string {
  return findProjectMap(cwd, arcade) ?? join(cwd, ".pi", "extensions", "game-select", "projects.json");
}

/** Guarda juego y set elegidos para este proyecto, sin perder las otras entradas. */
export function guardarProyecto(
  mapPath: string,
  proyecto: string,
  datos: { juego: string; invasividad: string },
): boolean {
  try {
    let mapa: Record<string, unknown> = {};
    if (existsSync(mapPath)) {
      try {
        const leido = JSON.parse(readFileSync(mapPath, "utf-8"));
        if (leido && typeof leido === "object" && !Array.isArray(leido)) mapa = leido as Record<string, unknown>;
      } catch {
        mapa = {};
      }
    }
    mapa[proyecto] = { juego: datos.juego, invasividad: datos.invasividad };
    mkdirSync(dirname(mapPath), { recursive: true });
    writeFileSync(mapPath, JSON.stringify(mapa, null, 2) + "\n");
    return true;
  } catch {
    return false;
  }
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

export interface ResultadoAplicacion {
  aplicado: boolean;
  motivo: "sin-arcade" | "sin-pack" | "sin-cambio" | "pack" | "baseline";
  juego?: string;
  respaldo?: string;
}

/** Copia del audio previo al primer pack, al lado del archivo vivo. */
export function baselinePath(livePath: string): string {
  return join(dirname(livePath), "notifications.baseline.json");
}

/**
 * Copia el pack de sprites al proyecto. El resolver del avatar mira primero
 * `<proyecto>/.pi/extensions/gentle-emote/emotes/<set>`, así que el proyecto
 * queda autosuficiente y no depende del dir global ni de este repo.
 */
export function copiarPackSprites(arcade: string, proyecto: string, juego: string): string | null {
  if (!juego) return null;
  const origen = join(arcade, "emotes", juego);
  if (!existsSync(origen)) return null;
  const destino = join(proyecto, ".pi", "extensions", "gentle-emote", "emotes", juego);
  if (existsSync(destino)) return destino;
  try {
    mkdirSync(dirname(destino), { recursive: true });
    cpSync(origen, destino, { recursive: true });
    return destino;
  } catch {
    return null;
  }
}

/** Eventos tal como van al archivo vivo: `file:` absoluto, shutdown mudo y
 * `gentle` sin el Enter del scheduler (lo rota la extensión). */
export function eventosVivos(
  juego: string,
  eventos: Record<string, string | null>,
): Record<string, string | null> {
  const salida: Record<string, string | null> = {};
  for (const evento of EVENTOS) {
    const val = eventos[evento];
    salida[evento] = val == null ? null : val.startsWith("builtin:") ? val : `file:${val}`;
  }
  salida["session.shutdown"] = null;
  if (juego === "gentle") salida["agent.started"] = null;
  return salida;
}

function leerEventos(livePath: string): Record<string, unknown> {
  try {
    const data = JSON.parse(readFileSync(livePath, "utf-8"));
    return (data?.audio?.events ?? {}) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function normalizado(ev: Record<string, unknown>, claves: string[]): string {
  const salida: Record<string, unknown> = {};
  for (const clave of claves) salida[clave] = ev[clave] ?? null;
  return JSON.stringify(salida);
}

/**
 * Aplica al archivo vivo de Gentle Shell el juego que ESTE proyecto eligió.
 *
 * El audio no tiene capa por proyecto en Gentle Shell: hay un solo
 * `notifications.json` para todas las sesiones. Por eso elegir juego no lo
 * escribe; se aplica acá, al abrir sesión, y un proyecto sin selección vuelve
 * al audio previo (`notifications.baseline.json`). Es idempotente: si el
 * archivo ya está como debe, no escribe ni deja backup.
 */
export function aplicarJuegoDeProyecto(opciones: {
  cwd: string;
  arcade: string | null;
  livePath: string;
  dryRun?: boolean;
}): ResultadoAplicacion {
  const { cwd, arcade, livePath, dryRun = false } = opciones;
  if (!arcade) return { aplicado: false, motivo: "sin-arcade" };

  const entry = readProjectEntry(projectsPath(cwd, arcade), cwd);
  const juego = typeof entry.juego === "string" ? entry.juego : "";
  const invasividad = normalizarInvasividad(String(entry.invasividad ?? ""));
  const baseline = baselinePath(livePath);
  const antes = leerEventos(livePath);

  let objetivo: Record<string, string | null>;
  if (juego) {
    const { eventos, asignados } = planSonidos(arcade, juego, invasividad);
    // Un pack sin archivos dejaría la sesión muda: mejor no tocar nada.
    if (asignados === 0) return { aplicado: false, motivo: "sin-pack", juego };
    objetivo = eventosVivos(juego, eventos);
  } else {
    if (!existsSync(baseline)) return { aplicado: false, motivo: "sin-cambio" };
    objetivo = leerEventos(baseline) as Record<string, string | null>;
  }

  const claves = [...EVENTOS, "session.shutdown", ...Object.keys(objetivo)];
  if (normalizado(antes, claves) === normalizado(objetivo as Record<string, unknown>, claves)) {
    return { aplicado: false, motivo: "sin-cambio", juego };
  }
  if (dryRun) return { aplicado: false, motivo: juego ? "pack" : "baseline", juego };

  try {
    mkdirSync(dirname(livePath), { recursive: true });
    if (!existsSync(baseline) && existsSync(livePath)) {
      writeFileSync(baseline, readFileSync(livePath, "utf-8"));
    }
    let respaldo: string | undefined;
    if (existsSync(livePath)) {
      const sello = new Date().toISOString().replace(/[:.]/g, "").slice(0, 15);
      respaldo = `${livePath}.bak-${sello}`;
      writeFileSync(respaldo, readFileSync(livePath, "utf-8"));
    }
    let vivo: any = {};
    try {
      vivo = JSON.parse(readFileSync(livePath, "utf-8"));
    } catch {
      vivo = {};
    }
    vivo.audio = vivo.audio ?? {};
    vivo.audio.events = vivo.audio.events ?? {};
    if (juego) Object.assign(vivo.audio.events, objetivo);
    else vivo.audio.events = { ...objetivo };
    // Atómico: otra sesión puede estar leyendo este archivo mientras escribimos.
    const tmp = `${livePath}.tmp-${process.pid}`;
    try {
      writeFileSync(tmp, JSON.stringify(vivo, null, 2));
      renameSync(tmp, livePath);
    } finally {
      if (existsSync(tmp)) unlinkSync(tmp);
    }
    return { aplicado: true, motivo: juego ? "pack" : "baseline", juego, respaldo };
  } catch {
    return { aplicado: false, motivo: "sin-cambio", juego };
  }
}

const TRAZA_PATH = "/tmp/game-select.log";
const TRAZA_MAX_BYTES = 64 * 1024;
/** Se arranca desde el tamaño en disco y trunca al pasar el tope: nunca crece sin límite. */
let trazaBytes = (() => {
  try {
    const size = statSync(TRAZA_PATH).size;
    if (size > TRAZA_MAX_BYTES) {
      writeFileSync(TRAZA_PATH, "");
      return 0;
    }
    return size;
  } catch {
    return 0;
  }
})();

function traza(msg: string) {
  try {
    const line = `${new Date().toISOString()} ${msg}\n`;
    if (trazaBytes + line.length > TRAZA_MAX_BYTES) {
      writeFileSync(TRAZA_PATH, "");
      trazaBytes = 0;
    }
    appendFileSync(TRAZA_PATH, line);
    trazaBytes += line.length;
  } catch {
    /* sin fs: no hay traza */
  }
}

export interface ResultadoSonido { ok: boolean; player?: string; error?: string }

/** Reproduce un WAV con el primer player disponible y devuelve por qué falló si falló. */
export function reproducir(archivo: string): Promise<ResultadoSonido> {
  if (!archivo) return Promise.resolve({ ok: false, error: "ruta vacía" });
  if (!existsSync(archivo)) return Promise.resolve({ ok: false, error: `no existe: ${archivo}` });
  const players: string[][] =
    process.platform === "darwin"
      ? [["afplay", archivo]]
      : [["paplay", archivo], ["aplay", "-q", archivo]];
  return new Promise((resolve) => {
    let done = false;
    const errores: string[] = [];
    const fin = (resultado: ResultadoSonido) => {
      if (done) return;
      done = true;
      traza(`sonido ${resultado.ok ? `ok ${resultado.player}` : `fallo: ${resultado.error}`}`);
      resolve(resultado);
    };
    const to = setTimeout(() => fin({ ok: false, error: "timeout del player" }), 3000);
    const intentar = (i: number): void => {
      if (i >= players.length) {
        clearTimeout(to);
        fin({ ok: false, error: errores.join("; ") || "sin player disponible" });
        return;
      }
      execFile(players[i][0], players[i].slice(1), (err) => {
        if (!err) { clearTimeout(to); fin({ ok: true, player: players[i][0] }); }
        else { errores.push(`${players[i][0]}: ${err.message}`); intentar(i + 1); }
      });
    };
    intentar(0);
  });
}

/** Seam de reproducción: los tests lo reemplazan para no tocar el audio real. */
export const reproductor = { play: reproducir };

export function sonarCoin(arcade: string, juego = "gentle"): Promise<ResultadoSonido> {
  const archivo = resolverActivacion(arcade, juego);
  if (!archivo) return Promise.resolve({ ok: false, error: "el pack no define sonido de activación" });
  traza(`activacion -> ${basename(archivo)}`);
  return reproductor.play(archivo);
}

/**
 * Sonido de sesión nueva (`session_start` con `reason: "new"`). Un pack puede
 * traer su propia frase en `nuevaSesion`; si no la trae, o la trae pero no
 * resuelve a un archivo, cae al `session.started` del pack. Sin ese fallback
 * `/new` quedaba mudo en 6 de 7 packs: la ausencia de una clave opcional no
 * puede traducirse en silencio.
 */
export function sonidoNuevaSesion(
  arcade: string,
  juego: string,
  rnd: () => number = Math.random,
): string | null {
  let nombres: string[] = [];
  let arranque = "";
  try {
    const sel = JSON.parse(readFileSync(join(arcade, "sounds", juego, "seleccion.json"), "utf-8"));
    if (Array.isArray(sel?.nuevaSesion)) nombres = sel.nuevaSesion.map(String);
    const elegido = sel?.choices?.["session.started"];
    if (typeof elegido === "string") arranque = elegido;
  } catch {
    return null;
  }
  const resolver = (lista: string[]): string[] =>
    lista
      .map((nombre) => resolverArchivo(arcade, juego, nombre))
      .filter((ruta): ruta is string => ruta != null);
  let resueltos = resolver(nombres);
  if (resueltos.length === 0 && arranque) resueltos = resolver([arranque]);
  if (resueltos.length === 0) return null;
  const indice = Math.min(resueltos.length - 1, Math.floor(rnd() * resueltos.length));
  return resueltos[Math.max(0, indice)];
}

/**
 * Elige al azar entre el principal del evento y sus `variantes`, en el momento de
 * reproducir. Es la diferencia con `planSonidos`: aquél sortea una vez y escribe
 * un `file:` fijo, así que la frase se repite en cada mensaje.
 */
export function sonidoRotativo(
  arcade: string,
  juego: string,
  evento: string,
  rnd: () => number = Math.random,
): string | null {
  let nombres: string[] = [];
  try {
    const sel = JSON.parse(readFileSync(join(arcade, "sounds", juego, "seleccion.json"), "utf-8"));
    const principal = sel?.choices?.[evento];
    if (principal != null) nombres.push(String(principal));
    const extras = sel?.variantes?.[evento];
    if (Array.isArray(extras)) for (const extra of extras) nombres.push(String(extra));
  } catch {
    return null;
  }
  const resueltos = nombres
    .map((nombre) => resolverArchivo(arcade, juego, nombre))
    .filter((ruta): ruta is string => ruta != null);
  if (resueltos.length === 0) return null;
  const indice = Math.min(resueltos.length - 1, Math.floor(rnd() * resueltos.length));
  return resueltos[Math.max(0, indice)];
}

const ORDEN_CONFIRMACION = ["session.started", "agent.attention", "agent.completed", "subagent.completed"];

/**
 * Sonido que confirma que el pack nuevo quedó aplicado: el `session.started`
 * del propio pack (el mismo que suena al abrir sesión), y si ese set lo silencia
 * (guardia), el `agent.attention`, que está en los tres sets.
 */
export function sonidoConfirmacion(eventos: Record<string, string | null>): string | null {
  for (const evento of ORDEN_CONFIRMACION) {
    const valor = eventos[evento];
    if (valor && !valor.startsWith("builtin:")) return valor;
  }
  return null;
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

export const EVENTOS = [
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
  rnd: () => number = Math.random,
): { eventos: Record<string, string | null>; asignados: number } {
  const selPath = join(arcade, "sounds", juego, "seleccion.json");
  const permitidos = INV_PERMITIDOS[invasividad] ?? INV_PERMITIDOS.todo;
  const eventos: Record<string, string | null> = {};
  let asignados = 0;
  let choices: Record<string, unknown> = {};
  let variantes: Record<string, unknown> = {};
  try {
    const sel = JSON.parse(readFileSync(selPath, "utf-8"));
    choices = sel?.choices ?? {};
    variantes = sel?.variantes ?? {};
  } catch {
    /* sin seleccion.json: todo queda en null */
  }
  for (const evento of EVENTOS) {
    if (!permitidos.has(evento)) {
      eventos[evento] = null;
      continue;
    }
    // Candidatos: el principal del evento y las variantes del pack (si las hay).
    const nombres: string[] = [];
    if (choices[evento] != null) nombres.push(String(choices[evento]));
    const extras = variantes[evento];
    if (Array.isArray(extras)) for (const extra of extras) nombres.push(String(extra));
    const resueltos = nombres
      .map((nombre) => resolverArchivo(arcade, juego, nombre))
      .filter((ruta): ruta is string => ruta != null);
    if (resueltos.length === 0) {
      eventos[evento] = null;
      continue;
    }
    const indice = Math.min(resueltos.length - 1, Math.floor(rnd() * resueltos.length));
    eventos[evento] = resueltos[Math.max(0, indice)];
    asignados += 1;
  }
  return { eventos, asignados };
}

/**
 * Sonido de activación del pack (`activacionVariantes`, con `activation` y el
 * coin como fallbacks): es lo que suena al activar el easter egg `gentle`.
 */
export function resolverActivacion(
  arcade: string,
  juego: string,
  rnd: () => number = Math.random,
): string | null {
  let nombres: string[] = [];
  try {
    const sel = JSON.parse(readFileSync(join(arcade, "sounds", juego, "seleccion.json"), "utf-8"));
    if (Array.isArray(sel?.activacionVariantes)) nombres = sel.activacionVariantes.map(String);
    else if (typeof sel?.activation === "string") nombres = [sel.activation];
  } catch {
    /* sin pack: queda el coin */
  }
  if (nombres.length === 0) nombres = ["coin"];
  const resueltos = nombres
    .map((nombre) => resolverArchivo(arcade, juego, nombre))
    .filter((ruta): ruta is string => ruta != null);
  if (resueltos.length === 0) return null;
  const indice = Math.min(resueltos.length - 1, Math.floor(rnd() * resueltos.length));
  return resueltos[Math.max(0, indice)];
}

export default function (pi: ExtensionAPI) {
  traza(`cargo extension cwd=${process.cwd()}`);
  const home = process.env.HOME ?? process.env.USERPROFILE ?? "";
  const agentDir =
    process.env.PI_CODING_AGENT_DIR || join(home, ".gentle-shell", "agent");
  const cwd = process.cwd();
  const configs = [
    join(agentDir, "extensions", "gentle-emote", "config.json"),
    join(cwd, ".pi", "extensions", "gentle-emote", "config.json"),
  ];

  /** Pack activo: el `emote-set` del config de proyecto, si no el global. */
  const packActual = (): string => {
    for (const ruta of [configs[1], configs[0]]) {
      try {
        const set = JSON.parse(readFileSync(ruta, "utf-8"))?.emotes?.[0]?.["emote-set"];
        if (typeof set === "string" && set) return set;
      } catch {
        /* siguiente config */
      }
    }
    return "";
  };

  // "✓ New session started": frase icónica del pack, sólo en sesión nueva.
  pi.on?.("session_start", async (event: any) => {
    // El audio global es uno solo para todas las sesiones: al abrir se aplica el
    // juego de ESTE proyecto, o se vuelve al audio previo si no eligió ninguno.
    if (home) {
      const livePath = join(home, ".gentle-shell", "config", "gentle-ai", "notifications.json");
      const resultado = aplicarJuegoDeProyecto({ cwd, arcade: findArcade(cwd), livePath });
      traza(
        `hook audio -> ${resultado.motivo}${resultado.juego ? ` ${resultado.juego}` : ""}` +
          `${resultado.respaldo ? ` (backup ${basename(resultado.respaldo)})` : ""}`,
      );
    }
    const reason = event?.reason;
    if (reason !== "new") return;
    const arcade = findArcade(cwd);
    if (!arcade) return;
    const pack = packActual();
    const archivo = pack ? sonidoNuevaSesion(arcade, pack) : null;
    traza(`nueva sesion -> ${archivo ? basename(archivo) : "-"} (pack ${pack || "?"})`);
    if (archivo) await reproductor.play(archivo);
  });

  // El Enter con el pack `gentle`: frase distinta en cada mensaje. El resto de
  // los packs queda con el `agent.started` fijo que escribe `planSonidos`.
  let rotando = false;
  pi.on?.("turn_start", async () => {
    if (rotando) return;
    const arcade = findArcade(cwd);
    if (!arcade) return;
    const pack = packActual();
    if (pack !== "gentle") return;
    const archivo = sonidoRotativo(arcade, pack, "agent.started");
    traza(`turno gentle -> ${archivo ? basename(archivo) : "-"}`);
    if (!archivo) return;
    rotando = true;
    try {
      await reproductor.play(archivo);
    } finally {
      rotando = false;
    }
  });

  const comando = {
    description:
      "Elegir juego (sprites + sonidos): /emote:juego abre el menu; directo /emote:juego <juego|n> con --invasividad a|b|c",
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
      const mapPath = projectsPath(cwd, arcade);
      const entry = readProjectEntry(mapPath, opciones.proyecto);
      const juegos = listarJuegos(arcade);
      const hayUi = typeof ctx?.ui?.select === "function";
      const sinArgs = !opciones.juego && !opciones.invasividad;
      const menuCompleto = sinArgs && hayUi && !opciones.dryRun;
      const tituloJuego = arcade
        ? "Elegí juego (sprites + sonidos):"
        : "Elegí juego (arcade no encontrado, no se aplican sonidos):";
      const listaNumerada = () => {
        const lista = juegos.map((j, i) => `${i + 1}=${j}`).join("  ");
        ctx.ui?.notify?.(
          `[juego] elegí número: /emote:juego <n> — ${lista} ` +
            `(set: --invasividad a|b|c) (arcade: ${arcade ?? "no encontrado"})`,
          "info",
        );
      };
      const cancelar = () => ctx.ui?.notify?.("[juego] cancelado: sin cambios", "info");
      const preguntarSet = async (): Promise<string> => {
        const elegido = await ctx.ui.select(
          "Elegí set de notificaciones auditivas:",
          SETS_SONIDO.map((s) => s.etiqueta),
        );
        const nivel = resolverNivel(String(elegido ?? ""));
        traza(`menu sonido -> ${String(elegido ?? "cancelado")} (${nivel || "-"})`);
        return nivel;
      };

      let juego = "";
      let invasividad = "";

      if (menuCompleto) {
        // El menu pregunta siempre las dos cosas: juego y set a/b/c.
        juego = resolverJuego(String((await ctx.ui.select(tituloJuego, juegos)) ?? ""), juegos);
        traza(`menu juego -> ${juego || "cancelado"}`);
        if (!juego) {
          listaNumerada();
          return;
        }
        invasividad = await preguntarSet();
        if (!invasividad) {
          cancelar();
          return;
        }
      } else {
        juego = resolverJuego(opciones.juego, juegos);
        if (!juego && entry.juego) juego = resolverJuego(String(entry.juego), juegos);
        if (!juego) {
          listaNumerada();
          return;
        }
        invasividad = resolverNivel(opciones.invasividad);
        // El set se confirma siempre en vivo, aunque el juego venga por argumento
        // o haya uno guardado: el guardado es sólo el default sin UI (dry-run/script).
        if (!invasividad && hayUi && !opciones.dryRun) {
          invasividad = await preguntarSet();
          if (!invasividad) {
            cancelar();
            return;
          }
        }
        invasividad = invasividad || resolverNivel(entry.invasividad ? String(entry.invasividad) : "") || DEFAULT_INVASIVIDAD;
      }

      // Sprites: `gentle` trae sus propias escenas (fork upstream); `misc` es
      // sólo sonidos mezclados, así que hereda el arte de aoe. Se escribe sólo
      // en el proyecto: el global lo resuelve el hook al abrir sesión, así
      // elegir acá no le cambia el arte ni el audio a los demás proyectos.
      const spritesJuego = juego === "misc" ? "aoe" : juego;
      if (!opciones.dryRun) {
        setEmoteSet(configs[1], spritesJuego);
        if (arcade) copiarPackSprites(arcade, opciones.proyecto, spritesJuego);
        guardarProyecto(mapPath, opciones.proyecto, { juego, invasividad });
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

      let sonido: ResultadoSonido = { ok: true };
      if (juego === "gentle") {
        sonido = await sonarCoin(arcade);
      } else {
        // Confirmación audible: el session.started del pack recién aplicado.
        const confirmacion = sonidoConfirmacion(eventos);
        if (confirmacion) sonido = await reproductor.play(confirmacion);
      }
      if (!sonido.ok) {
        ctx.ui?.notify?.(
          `[juego] el pack quedó aplicado, pero no pude reproducir el sonido: ${sonido.error ?? "sin player"}`,
          "warning",
        );
      }
      const recargar = typeof ctx?.reload === "function";
      ctx.ui?.notify?.(
        `[juego] → ${juego} (${asignados} sonidos, ${invasividad}) en este proyecto; ` +
          `el audio global se aplica al abrir sesión. ` +
          (recargar ? "Recargado." : "/reload para ver+oir."),
        "info",
      );
      // El reload es terminal para este handler: recarga extensiones y config.
      if (recargar) {
        try {
          await ctx.reload();
        } catch {
          /* si el host no puede recargar, queda el aviso de /reload */
        }
        return;
      }
    },
  };
  pi.registerCommand?.("emote:juego", comando);
}
