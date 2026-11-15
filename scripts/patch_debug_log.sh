#!/bin/bash
# Pone un techo duro al debug.log del paquete npm gentle-emote.
# Uso: ./scripts/patch_debug_log.sh [--check]
#
# El paquete upstream escribe con appendFileSync en cada frame del avatar y no
# rota nunca: con debug=true llegó a 558 MB. Este patch rota el archivo a
# `debug.log.1` (un solo backup) cuando pasa de 2 MB, así ni con debug prendido
# puede llenar el disco.
#
# Es idempotente y verifica el sha256 del archivo original, para no aplicar
# sobre una versión distinta. Se pierde si `pi update` reinstala el paquete:
# volvé a correrlo (check_install.sh avisa cuando falta).
set -euo pipefail

AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.gentle-shell/agent}"
LOG_TS="$AGENT_DIR/npm/node_modules/gentle-emote/src/log.ts"
# sha256 de src/log.ts tal como viene en gentle-emote 0.1.4
ORIGINAL="e22d4f46e549d7f63020157ea00aac5455d4a60e9b1c40654805275a8192474f"

check_only=0
[ "${1:-}" = "--check" ] && check_only=1

if [ ! -f "$LOG_TS" ]; then
    echo "no está el paquete: $LOG_TS" >&2
    exit 2
fi

cuerpo_parcheado() {
    cat <<'EOF'
import { appendFileSync, renameSync, statSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const LOG_FILE = join(dirname(fileURLToPath(import.meta.url)), "..", "debug.log");
// gentle-emote-arcade: cap local. Upstream no rota nunca (llegó a 558 MB).
const MAX_LOG_BYTES = 2 * 1024 * 1024;

let debugEnabled = false;

export function setDebug(enabled: boolean) {
  debugEnabled = enabled;
}

export function log(msg: string) {
  if (!debugEnabled) return;
  try {
    if (statSync(LOG_FILE).size > MAX_LOG_BYTES) renameSync(LOG_FILE, `${LOG_FILE}.1`);
  } catch {
    /* todavía no existe: lo crea el append */
  }
  appendFileSync(LOG_FILE, `[${new Date().toISOString()}] ${msg}\n`);
}
EOF
}

if grep -q "MAX_LOG_BYTES" "$LOG_TS" 2>/dev/null; then
    [ "$check_only" = 0 ] && echo "ya parcheado (cap 2 MB) en $LOG_TS"
    exit 0
fi

if [ "$check_only" = 1 ]; then
    echo "FALTA el cap de debug.log: corré scripts/patch_debug_log.sh" >&2
    exit 1
fi

ACTUAL="$(sha256sum "$LOG_TS" | cut -d' ' -f1)"
if [ "$ACTUAL" != "$ORIGINAL" ]; then
    echo "log.ts no es el original 0.1.4 (sha256 $ACTUAL)." >&2
    echo "Revisalo a mano: el paquete cambió de versión." >&2
    exit 1
fi

cp "$LOG_TS" "$LOG_TS.orig-$(date +%Y%m%d-%H%M%S)"
cuerpo_parcheado > "$LOG_TS"
echo "parcheado: $LOG_TS (cap 2 MB, rotación a debug.log.1)"
