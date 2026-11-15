/**
 * Devuelve `notifications.json` a los sonidos que trae Gentle Shell de fábrica.
 *
 * Es lo que corresponde al desinstalar el arcade: el pack `gentle` escribe
 * `agent.started: null` para que la frase del Enter la reproduzca la extensión, y
 * si la extensión se va sin restaurar, ese `null` deja el Enter mudo para siempre.
 *
 * Los valores replican `DEFAULT_NOTIFICATION_SETTINGS` de Gentle Shell
 * (`gentle-pi/lib/notification-policy.ts:39-45`): prioridad 3 → `builtin:error`,
 * 2 → `builtin:attention`, 1 → `builtin:success`, 0 → `null`.
 *
 *   node scripts/restore_notifications.ts [ruta-a-notifications.json]
 */
import { copyFileSync, existsSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

export const SONIDOS_POR_DEFECTO: Readonly<Record<string, string | null>> = Object.freeze({
  "session.started": null,
  "session.shutdown": null,
  "agent.started": null,
  "agent.completed": "builtin:success",
  "agent.failed": "builtin:error",
  "agent.cancelled": null,
  "agent.attention": "builtin:attention",
  "subagent.queued": null,
  "subagent.running": null,
  "subagent.waiting": null,
  "subagent.completed": "builtin:success",
  "subagent.failed": "builtin:error",
  "subagent.cancelled": null,
  "subagent.timed_out": "builtin:error",
  "context.high": "builtin:attention",
});

export interface ResumenRestauracion {
  archivo: string;
  restaurados: number;
  backup: string;
  cambiados: string[];
}

/**
 * Reescribe sólo `audio.events`, dejando `enabled`, `backend` y los límites de
 * tiempo como estaban: desinstalar el arcade no es apagar las notificaciones.
 */
export function restaurarPorDefecto(livePath: string): ResumenRestauracion {
  if (!existsSync(livePath)) throw new Error(`no existe ${livePath}`);
  const stamp = new Date().toISOString().replace(/[:.]/g, "").slice(0, 15);
  const backup = `${livePath}.bak-${stamp}`;
  copyFileSync(livePath, backup);

  const data = JSON.parse(readFileSync(livePath, "utf-8"));
  data.audio = data.audio ?? {};
  const eventos = (data.audio.events = data.audio.events ?? {});
  const cambiados: string[] = [];
  for (const [evento, valor] of Object.entries(SONIDOS_POR_DEFECTO)) {
    if (eventos[evento] !== valor) cambiados.push(evento);
    eventos[evento] = valor;
  }
  writeFileSync(livePath, JSON.stringify(data, null, 2));
  return { archivo: livePath, restaurados: Object.keys(SONIDOS_POR_DEFECTO).length, backup, cambiados };
}

const esCli = process.argv[1] != null && pathToFileURL(process.argv[1]).href === import.meta.url;
if (esCli) {
  const live = process.argv[2] ?? join(homedir(), ".gentle-shell", "config", "gentle-ai", "notifications.json");
  try {
    const r = restaurarPorDefecto(live);
    console.log(`sonidos de fábrica restaurados en ${r.archivo}`);
    console.log(`eventos reescritos: ${r.restaurados} · cambiados: ${r.cambiados.length}`);
    if (r.cambiados.length) console.log(`  ${r.cambiados.join(", ")}`);
    console.log(`backup: ${r.backup}`);
  } catch (error) {
    console.error(`no pude restaurar: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}
