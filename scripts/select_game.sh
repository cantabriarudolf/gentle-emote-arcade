#!/bin/bash
# Selector de juego: cambia sprites Y sonidos juntos.
# Uso: ./scripts/select_game.sh [juego] [--dry-run]
#       juego: aoe (default) | minecraft | cs16 | starcraft | lol
#       -n, --dry-run: no escribe ninguna config (sprites ni sonidos).
# Requiere: sounds/<juego>/seleccion.json (portable, solo nombres) y
# emotes/<juego>/ (si aún no tiene arte, el plugin usa lo que haya).
set -euo pipefail
JUEGO=""
DRY=0
for arg in "$@"; do
    case "$arg" in
        -n|--dry-run) DRY=1 ;;
        -h|--help) sed -n '2,7p' "$0"; exit 0 ;;
        -*) echo "opción desconocida: $arg" >&2; exit 2 ;;
        *)
            if [ -n "$JUEGO" ]; then
                echo "juego de más: $arg" >&2
                exit 2
            fi
            JUEGO="$arg"
            ;;
    esac
done
JUEGO="${JUEGO:-aoe}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SEL="$REPO/sounds/$JUEGO/seleccion.json"
[ -f "$SEL" ] || { echo "No existe $SEL" >&2; exit 1; }

echo "=== Sprites -> $JUEGO ==="
if [ "$DRY" -eq 1 ]; then
    echo "(dry-run: no toco la config de sprites)"
else
    python3 - "$JUEGO" "$REPO" <<'PY'
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
ARGS=("$JUEGO")
if [ "$DRY" -eq 1 ]; then
    ARGS+=(--dry-run)
fi
"$REPO/scripts/apply_sounds.sh" "${ARGS[@]}"
if [ "$DRY" -eq 0 ]; then
    echo "Listo: /reload en herdr para ver+oir $JUEGO"
fi
