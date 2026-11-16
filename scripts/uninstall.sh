#!/usr/bin/env bash
# Desinstala gentle-emote-arcade y devuelve las notificaciones a como estaban
# antes del primer pack. Si hay `notifications.baseline.json` (lo crea el hook de
# `session_start` al aplicar el primer juego) restaura ese archivo tal cual; si
# no, vuelve a los sonidos de fábrica de Gentle Shell.
#
# Uso: scripts/uninstall.sh [--dry-run]
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE="${HOME}/.gentle-shell/config/gentle-ai/notifications.json"
BASELINE="${HOME}/.gentle-shell/config/gentle-ai/notifications.baseline.json"
NODE="${NODE:-node}"

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "dry-run: no escribo nada."
  if [[ -f "$BASELINE" ]]; then
    echo "  devolvería el audio previo desde        ${BASELINE}"
  else
    echo "  devolvería los sonidos de fábrica en    ${LIVE}"
  fi
  echo "  y quitaría el symlink                   ${HOME}/.gentle-shell/agent/extensions/game-select/index.ts"
  exit 0
fi

if [[ -f "$LIVE" ]]; then
  RESPALDO="${LIVE}.bak-$(date +%Y%m%d-%H%M%S)"
  cp -p "$LIVE" "$RESPALDO"
  if [[ -f "$BASELINE" ]]; then
    cp -p "$BASELINE" "$LIVE"
    echo "audio previo restaurado en ${LIVE} (backup: ${RESPALDO})"
  else
    "$NODE" "${AQUI}/scripts/restore_notifications.ts" "$LIVE"
  fi
else
  echo "aviso: no existe ${LIVE}, no hay nada que restaurar"
fi

# El config del avatar no lo tocamos sin que lo pidas: sólo se avisa.
echo
echo "Pendiente de hacer a mano (no lo hace este script):"
echo "  1. rm -f \"${HOME}/.gentle-shell/agent/extensions/game-select/index.ts\""
echo "  2. quitar \"emote-set\" de <proyecto>/.pi/extensions/gentle-emote/config.json"
echo "  3. el mapa <arcade>/../.pi/extensions/game-select/projects.json queda como estaba"
echo
echo "Los packs de sprites copiados dentro de cada proyecto quedan ahí: son del proyecto."
