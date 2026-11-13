#!/bin/bash
# Selector de juego: cambia sprites Y sonidos juntos.
# Uso: ./scripts/select_game.sh [juego] [--proyecto RUTA] [--invasividad NIVEL] [--dry-run]
#       juego: aoe (default) | minecraft | cs16 | starcraft | lol | misc | gentle | abuela
#       --proyecto RUTA: lee el mapa .pi/extensions/game-select/projects.json
#       --invasividad NIVEL: todo | esencial | guardia
#       -n, --dry-run: no escribe ninguna config (sprites ni sonidos).
# Requiere: sounds/<juego>/seleccion.json (portable, solo nombres) y
# emotes/<juego>/ (si aún no tiene arte, el plugin usa lo que haya).
set -euo pipefail
JUEGO=""
DRY=0
PROYECTO=""
INVASIVIDAD=""
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--dry-run) DRY=1; shift ;;
        -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
        --proyecto) PROYECTO="$2"; shift 2 ;;
        --invasividad) INVASIVIDAD="$2"; shift 2 ;;
        -*) echo "opción desconocida: $1" >&2; exit 2 ;;
        *)
            if [ -n "$JUEGO" ]; then
                echo "juego de más: $1" >&2; exit 2
            fi
            JUEGO="$1"; shift
            ;;
    esac
done

case "$JUEGO" in
    abuela) JUEGO="gentle" ;;
esac

REPO="$(cd "$(dirname "$0")/.." && pwd)"

if [ -n "$PROYECTO" ]; then
    PROJECT_ROOT="$(cd "$REPO/.." && pwd)"
    MAP="$PROJECT_ROOT/.pi/extensions/game-select/projects.json"
    if [ -f "$MAP" ]; then
        info="$(python3 - "$MAP" "$PROYECTO" <<'PY'
import json, os, sys
map_path, proj = sys.argv[1], sys.argv[2]
try:
    data = json.load(open(map_path, encoding="utf-8"))
except Exception:
    data = {}
entry = None
for key in (proj, os.path.abspath(proj), os.path.realpath(proj)):
    if key in data:
        entry = data[key]; break
if not isinstance(entry, dict):
    entry = {}
print(entry.get("juego", ""))
print(entry.get("invasividad", ""))
PY
)"
        proj_juego="$(printf '%s\n' "$info" | sed -n '1p')"
        proj_inv="$(printf '%s\n' "$info" | sed -n '2p')"
        [ -n "$JUEGO" ] || JUEGO="$proj_juego"
        [ -n "$INVASIVIDAD" ] || INVASIVIDAD="$proj_inv"
    fi
fi

JUEGO="${JUEGO:-aoe}"
INVASIVIDAD="${INVASIVIDAD:-todo}"
case "$INVASIVIDAD" in
    todo|esencial|guardia) ;;
    *) echo "invasividad desconocida: $INVASIVIDAD" >&2; exit 2 ;;
esac
SEL="$REPO/sounds/$JUEGO/seleccion.json"
[ -f "$SEL" ] || { echo "No existe $SEL" >&2; exit 1; }

echo "=== Sprites -> $JUEGO ==="
if [ "$DRY" -eq 1 ]; then
    echo "(dry-run: no toco la config de sprites)"
else
    # gentle usa sprites de aoe (easter egg sin arte propio).
    SPRITES_JUEGO="$JUEGO"
    if [ "$JUEGO" = "gentle" ] || [ "$JUEGO" = "misc" ]; then
        SPRITES_JUEGO="aoe"
    fi
    python3 - "$SPRITES_JUEGO" "$REPO" <<'PY'
import json, os, shutil, stat, sys, time

juego, repo = sys.argv[1], sys.argv[2]
paths = [
    os.path.expanduser("~/.gentle-shell/agent/extensions/gentle-emote/config.json"),
    os.path.join(os.path.dirname(repo), ".pi", "extensions", "gentle-emote", "config.json"),
]
deseado = [{"model": "*", "emote-set": juego}]
sello = time.strftime("%Y%m%d-%H%M%S")
for p in paths:
    if not os.path.isfile(p):
        continue
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    if d.get("emotes") == deseado:
        print("sprites: ya en %s (%s)" % (juego, p))
        continue
    respaldo = p + ".bak-" + sello
    n = 1
    while os.path.exists(respaldo):
        respaldo = "%s.bak-%s-%d" % (p, sello, n)
        n += 1
    shutil.copy2(p, respaldo)
    d["emotes"] = deseado
    modo = stat.S_IMODE(os.stat(p).st_mode)
    tmp = "%s.tmp-%d" % (p, os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, modo)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print("sprites:", p, "(backup: %s)" % os.path.basename(respaldo))
PY
fi

echo "=== Sonidos -> $JUEGO (valida + backup) ==="
ARGS=("$JUEGO" --invasividad "$INVASIVIDAD")
if [ -n "$PROYECTO" ]; then
    ARGS+=(--proyecto "$PROYECTO")
fi
if [ "$DRY" -eq 1 ]; then
    ARGS+=(--dry-run)
fi
"$REPO/scripts/apply_sounds.sh" "${ARGS[@]}"
if [ "$DRY" -eq 0 ]; then
    echo "Listo: /reload en herdr para ver+oir $JUEGO"
fi