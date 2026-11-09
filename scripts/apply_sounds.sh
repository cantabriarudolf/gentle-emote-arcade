#!/bin/bash
# Aplica un pack de sonidos (sounds/<juego>/seleccion.json) a la config viva de
# Gentle Shell. El repo solo guarda nombres; el absoluto file: se resuelve acá,
# en tu máquina, al aplicar. Orden: validar todo -> backup -> escribir.
#
# Uso: ./scripts/apply_sounds.sh [juego] [--dry-run]
#       juego: aoe (default) | minecraft | cs16 | starcraft | lol
#       -n, --dry-run: muestra el mapeo resuelto y NO toca la config viva.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LIVE="${GENTLE_NOTIFICATIONS_CONFIG:-$HOME/.gentle-shell/config/gentle-ai/notifications.json}"

JUEGO=""
DRY=0
for arg in "$@"; do
    case "$arg" in
        -n|--dry-run) DRY=1 ;;
        -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
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
SEL="$REPO/sounds/$JUEGO/seleccion.json"
[ -f "$SEL" ] || { echo "No existe $SEL" >&2; exit 1; }
if [ "$DRY" -eq 0 ] && [ ! -f "$LIVE" ]; then
    echo "No existe la config viva $LIVE" >&2
    exit 1
fi

python3 - "$SEL" "$LIVE" "$JUEGO" "$DRY" <<'PY'
import glob, json, os, shutil, stat, sys, time

sel_path, live_path, juego, dry = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1"
base = os.path.dirname(os.path.abspath(sel_path))

# Contrato de eventos de la suite (gentle-pi/docs/sound-notifications.md).
# Si falta uno, aplicar el pack dejaría eventos apuntando al juego anterior.
EVENTOS = (
    "session.started",
    "agent.started",
    "agent.completed",
    "agent.failed",
    "agent.cancelled",
    "agent.attention",
    "subagent.queued",
    "subagent.running",
    "subagent.waiting",
    "subagent.completed",
    "subagent.failed",
    "subagent.cancelled",
    "subagent.timed_out",
    "context.high",
)
EXTENSIONES = (".wav", ".ogg", ".flac", ".mp3")


def morir(msg, code=1):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def resolver(nombre):
    """Resuelve el tallo igual que el selector: literal, .wav, luego el resto."""
    for rel in (nombre,) + tuple(nombre + ext for ext in EXTENSIONES):
        ruta = os.path.join(base, rel)
        if os.path.isfile(ruta):
            return ruta
    golpes = sorted(
        g for g in glob.glob(os.path.join(base, nombre) + ".*") if os.path.isfile(g)
    )
    return golpes[0] if golpes else None


try:
    with open(sel_path, encoding="utf-8") as fh:
        sel = json.load(fh)
except (OSError, ValueError) as exc:
    morir("no pude leer %s: %s" % (sel_path, exc), 2)

choices = sel.get("choices") or {}
if not isinstance(choices, dict) or not choices:
    morir("%s no tiene 'choices'" % sel_path, 2)

declarado = sel.get("soundsDir")
esperado = "sounds/" + juego
if declarado and declarado != esperado:
    morir(
        "soundsDir=%r no coincide con %r (¿pasaste el juego equivocado?)"
        % (declarado, esperado),
        2,
    )

faltantes = [ev for ev in EVENTOS if ev not in choices]
if faltantes:
    morir(
        "faltan eventos en %s: %s" % (os.path.basename(sel_path), ", ".join(faltantes)),
        2,
    )
extras = sorted(set(choices) - set(EVENTOS) - {"session.shutdown"})
if extras:
    print("aviso: eventos desconocidos (no suenan): " + ", ".join(extras), file=sys.stderr)

plan = {}
rotos = []
for evento in EVENTOS:
    nombre = str(choices[evento])
    ruta = resolver(nombre)
    if ruta is None:
        rotos.append("%s -> %s" % (evento, nombre))
    else:
        plan[evento] = ruta
if rotos:
    morir(
        "sin archivo en %s para: %s" % (base, "; ".join(rotos)),
        2,
    )
mp3 = [ev for ev, ruta in plan.items() if not ruta.lower().endswith(".wav")]
if mp3:
    print(
        "aviso: la suite solo reproduce RIFF/WAVE PCM; revisá: %s" % ", ".join(mp3),
        file=sys.stderr,
    )

if dry:
    for evento in EVENTOS:
        print("%-20s %s" % (evento, os.path.basename(plan[evento])))
    print("DRY-RUN: no toqué %s (%d eventos de %s)" % (live_path, len(plan), juego))
    sys.exit(0)

try:
    with open(live_path, encoding="utf-8") as fh:
        live = json.load(fh)
except (OSError, ValueError) as exc:
    morir("config viva ilegible (%s): %s" % (live_path, exc), 2)

sello = time.strftime("%Y%m%d-%H%M%S")
backup = live_path + ".bak-" + sello
n = 1
while os.path.exists(backup):
    backup = "%s.bak-%s-%d" % (live_path, sello, n)
    n += 1
shutil.copy2(live_path, backup)

audio = live.setdefault("audio", {})
eventos = audio.setdefault("events", {})
for evento, ruta in plan.items():
    eventos[evento] = "file:" + ruta
eventos["session.shutdown"] = None

modo = stat.S_IMODE(os.stat(live_path).st_mode)
tmp = "%s.tmp-%d" % (live_path, os.getpid())
try:
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(live, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.chmod(tmp, modo)
    os.replace(tmp, live_path)
finally:
    if os.path.exists(tmp):
        os.unlink(tmp)

print("backup:", backup)
print("aplicados", len(plan), "eventos de", juego, "desde", base)
PY
