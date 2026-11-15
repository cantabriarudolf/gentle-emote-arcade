#!/usr/bin/env bash
# Desinstala gentle-emote-arcade y devuelve las notificaciones a los sonidos que
# trae Gentle Shell de fábrica (`builtin:error`, `builtin:attention`,
# `builtin:success` según prioridad; el resto queda en null).
#
# Uso: scripts/uninstall.sh [--dry-run]
set -euo pipefail

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE="${HOME}/.gentle-shell/config/gentle-ai/notifications.json"
NODE="${NODE:-node}"

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "dry-run: no escribo nada."
  echo "  devolvería los sonidos de fábrica en  ${LIVE}"
  echo "  y quitaría el symlink               ${HOME}/.gentle-shell/agent/extensions/game-select/index.ts"
  exit 0
fi

if [[ -f "$LIVE" ]]; then
  "$NODE" "${AQUI}/scripts/restore_notifications.ts" "$LIVE"
else
  echo "aviso: no existe ${LIVE}, no hay nada que restaurar"
fi

# El config del avatar no lo tocamos sin que lo pidas: sólo se avisa.
echo
echo "Pendiente de hacer a mano (no lo hace este script):"
echo "  1. rm -f \"${HOME}/.gentle-shell/agent/extensions/game-select/index.ts\""
echo "  2. quitar el bloque \"emote-set\" de los config.json global y de proyecto"
echo "  3. volver a copiar los emotes originales si los querés de vuelta"
echo
echo "Los WAV de sounds/ y el mapa projects.json quedan como estaban."
