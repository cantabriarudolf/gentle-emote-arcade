#!/bin/bash
# Verifica que lo instalado sea igual a lo que hay en el repo.
# Uso: ./scripts/check_install.sh [--quiet]
# Sale 0 si todo coincide, 1 si hay drift. No escribe nada.
#
#   - emotes/: repo vs ~/.gentle-shell/agent/extensions/gentle-emote/emotes
#     y vs <proyecto>/.pi/extensions/gentle-emote/emotes
#   - extensions/game-select/index.ts vs la copia instalada (sigue symlinks)
#   - cableado de sonidos en ~/.gentle-shell/config/gentle-ai/notifications.json
#   - debug.log gigante del paquete npm y flags debug en los config.json
set -uo pipefail

QUIET=0
[ "${1:-}" = "--quiet" ] && QUIET=1

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PROYECTO="$(cd "$REPO/.." && pwd)"
AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.gentle-shell/agent}"
LIVE="${HOME:-/root}/.gentle-shell/config/gentle-ai/notifications.json"
NPM_LOG="$AGENT_DIR/npm/node_modules/gentle-emote/debug.log"

WARN=0
FALLAS=0
drift() { echo "DRIFT: $*"; FALLAS=$((FALLAS + 1)); }
ok() { [ "$QUIET" = 1 ] || echo "ok: $*"; }

echo "== repo =="
cd "$REPO" || exit 2
SUCIO="$(git status --porcelain 2>/dev/null | wc -l)"
RAMA="$(git rev-parse --abbrev-ref HEAD 2>/dev/null)"
AHEAD="$(git rev-list --count "@{u}..HEAD" 2>/dev/null || echo "?")"
BEHIND="$(git rev-list --count "HEAD..@{u}" 2>/dev/null || echo "?")"
[ "$QUIET" = 1 ] || echo "rama=$RAMA  sin commitear=$SUCIO  adelante=$AHEAD  atras=$BEHIND"
[ "$SUCIO" != "0" ] && drift "$SUCIO archivo(s) sin commitear en $REPO"
[ "$AHEAD" != "0" ] && drift "$AHEAD commit(s) locales sin pushear"
[ "$BEHIND" != "0" ] && drift "$BEHIND commit(s) atrás de origin"

echo "== emotes =="
for DESTINO in \
    "$AGENT_DIR/extensions/gentle-emote/emotes" \
    "$PROYECTO/.pi/extensions/gentle-emote/emotes"; do
    if [ ! -d "$DESTINO" ]; then
        drift "no existe $DESTINO"
        continue
    fi
    for SET in "$REPO"/emotes/*/; do
        NOMBRE="$(basename "$SET")"
        case "$NOMBRE" in *.bak) continue ;; esac
        if ! diff -rq "$SET" "$DESTINO/$NOMBRE" >/dev/null 2>&1; then
            drift "set $NOMBRE distinto en $DESTINO"
        fi
    done
    PNGS=$(find "$DESTINO" -name '*.png' 2>/dev/null | wc -l)
    ok "$DESTINO ($PNGS PNG)"
done

echo "== extension game-select =="
INSTALADA="$PROYECTO/.pi/extensions/game-select/index.ts"
if [ ! -e "$INSTALADA" ]; then
    drift "no está instalada en $INSTALADA"
elif [ ! -L "$INSTALADA" ]; then
    drift "$INSTALADA es una copia, no un symlink: puede desincronizarse"
    if ! diff -q "$REPO/extensions/game-select/index.ts" "$INSTALADA" >/dev/null 2>&1; then
        drift "la copia instalada difiere del repo"
    fi
else
    [ "$(readlink -f "$INSTALADA")" = "$REPO/extensions/game-select/index.ts" ] \
        && ok "symlink -> repo" \
        || drift "el symlink apunta a $(readlink -f "$INSTALADA"), no al repo"
fi

echo "== sonidos =="
if [ ! -f "$LIVE" ]; then
    drift "no existe $LIVE"
else
    EVENTOS=$(grep -c '"file:' "$LIVE" 2>/dev/null || echo 0)
    if [ "$EVENTOS" = "0" ]; then
        drift "ningún evento con sonido de pack (solo builtin): corré scripts/select_game.sh <juego>"
    else
        ROTAS=0
        while IFS= read -r RUTA; do
            [ -f "$RUTA" ] || { drift "evento apunta a un archivo que no existe: $RUTA"; ROTAS=$((ROTAS + 1)); }
        done < <(grep -o '"file:[^"]*"' "$LIVE" | tr -d '"' | sed 's/^file://')
        [ "$ROTAS" = "0" ] && ok "$EVENTOS eventos cableados, todos los archivos existen"
    fi
fi

echo "== higiene =="
LOG_TS="$AGENT_DIR/npm/node_modules/gentle-emote/src/log.ts"
if [ -f "$LOG_TS" ] && ! grep -q "MAX_LOG_BYTES" "$LOG_TS" 2>/dev/null; then
    drift "falta el cap de debug.log: corré scripts/patch_debug_log.sh (pi update lo borra)"
else
    ok "cap de debug.log presente (rota a 2 MB)"
fi
if [ -f "$NPM_LOG" ]; then
    BYTES=$(stat -c%s "$NPM_LOG" 2>/dev/null || echo 0)
    if [ "$BYTES" -gt 4194304 ]; then
        drift "debug.log de $(($BYTES / 1048576)) MB en el paquete npm"
    else
        ok "debug.log en $BYTES bytes"
    fi
fi
if [ -f "$NPM_LOG.1" ]; then
    ROTADO=$(stat -c%s "$NPM_LOG.1" 2>/dev/null || echo 0)
    ok "debug.log.1 (rotación) en $((ROTADO / 1024)) KB"
fi
TRACE=/tmp/game-select.log
if [ -f "$TRACE" ]; then
    TRACE_BYTES=$(stat -c%s "$TRACE" 2>/dev/null || echo 0)
    if [ "$TRACE_BYTES" -gt 200000 ]; then
        drift "traza de game-select en $((TRACE_BYTES / 1024)) KB: revisá el cap en traza()"
    else
        ok "traza game-select chica ($TRACE_BYTES bytes)"
    fi
fi
for CFG in \
    "$AGENT_DIR/extensions/gentle-emote/config.json" \
    "$PROYECTO/.pi/extensions/gentle-emote/config.json"; do
    [ -f "$CFG" ] || continue
    if grep -q '"debug": *true' "$CFG"; then
        WARN=$((WARN + 1))
        echo "WARN: debug activo en $CFG (crece debug.log en cada frame)"
    fi
done
SOLO_ROOT=$(find "$PROYECTO/.pi" -not -user "$(id -un)" 2>/dev/null | wc -l)
[ "$SOLO_ROOT" != "0" ] && echo "WARN: $SOLO_ROOT archivo(s) en .pi/ que no son tuyos (root): sudo rm -rf para limpiar"

echo
if [ "$FALLAS" = "0" ]; then
    echo "resultado: instalación igual al repo ($WARN aviso(s))."
    exit 0
fi
echo "resultado: $FALLAS problema(s) de sincronización, $WARN aviso(s)."
exit 1
