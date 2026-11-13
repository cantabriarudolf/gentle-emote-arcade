#!/bin/bash
# Aplica un pack de sonidos (sounds/<juego>/seleccion.json) a la config viva de
# Gentle Shell. El repo solo guarda nombres; el absoluto file: se resuelve acá,
# en tu máquina, al aplicar. Orden: validar todo -> backup -> escribir.
#
# Uso: ./scripts/apply_sounds.sh [juego] [--proyecto RUTA] [--invasividad NIVEL] [--dry-run]
#       juego: aoe (default) | minecraft | cs16 | starcraft | lol | misc | gentle | abuela
#       --proyecto RUTA: lee el mapa .pi/extensions/game-select/projects.json
#       --invasividad NIVEL: todo (default) | esencial | guardia
#       -n, --dry-run: muestra el mapeo resuelto y NO toca la config viva.
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
LIVE="${GENTLE_NOTIFICATIONS_CONFIG:-$HOME/.gentle-shell/config/gentle-ai/notifications.json}"

JUEGO=""
DRY=0
PROYECTO=""
INVASIVIDAD=""
while [ $# -gt 0 ]; do
    case "$1" in
        -n|--dry-run) DRY=1; shift ;;
        -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
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

# Alias easter egg.
case "$JUEGO" in
    abuela) JUEGO="gentle" ;;
esac

# Mapa por proyecto (solo lectura; no se escribe en la config viva).
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
if [ "$DRY" -eq 0 ] && [ ! -f "$LIVE" ]; then
    echo "No existe la config viva $LIVE" >&2
    exit 1
fi

python3 - "$SEL" "$LIVE" "$JUEGO" "$DRY" "$INVASIVIDAD" "$REPO" <<'PY'
import glob, json, os, shutil, stat, sys, time

sel_path, live_path, juego, dry, invasividad, repo = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == "1", sys.argv[5], sys.argv[6]
base = os.path.dirname(os.path.abspath(sel_path))
sonidos_root = os.path.join(repo, "sounds")

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

PERMITIDOS = {
    "todo": set(EVENTOS),
    "esencial": set(EVENTOS) - {"subagent.queued", "subagent.running"},
    "guardia": {"agent.attention", "agent.failed", "subagent.waiting",
                "subagent.failed", "subagent.timed_out", "context.high"},
}


def morir(msg, code=1):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def resolver_builtin(nombre):
    # nombre: "builtin:success" -> token (el builtin lo resuelve la suite).
    return nombre


def resolver_pack_stem(valor):
    # "pack/tallo" -> ruta absoluta en sounds/<pack>/.
    if "/" not in valor:
        return None
    pack, tallo = valor.split("/", 1)
    base_pack = os.path.join(sonidos_root, pack)
    for rel in (tallo,) + tuple(tallo + ext for ext in EXTENSIONES):
        ruta = os.path.join(base_pack, rel)
        if os.path.isfile(ruta):
            return ruta
    golpes = sorted(g for g in glob.glob(os.path.join(base_pack, tallo) + ".*") if os.path.isfile(g))
    return golpes[0] if golpes else None


def resolver_local(base, nombre):
    for rel in (nombre,) + tuple(nombre + ext for ext in EXTENSIONES):
        ruta = os.path.join(base, rel)
        if os.path.isfile(ruta):
            return ruta
    golpes = sorted(g for g in glob.glob(os.path.join(base, nombre) + ".*") if os.path.isfile(g))
    return golpes[0] if golpes else None


def resolver(valor):
    if valor is None:
        return None
    if not isinstance(valor, str):
        return None
    if valor.startswith("builtin:"):
        return valor
    if "/" in valor:
        return resolver_pack_stem(valor)
    return resolver_local(base, valor)


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
    nombre = choices[evento]
    if nombre is None:
        plan[evento] = None
        continue
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
mp3 = [ev for ev, ruta in plan.items()
       if isinstance(ruta, str) and not ruta.startswith("builtin:")
       and not ruta.lower().endswith(".wav")]
if mp3:
    print(
        "aviso: la suite solo reproduce RIFF/WAVE PCM; revisá: %s" % ", ".join(mp3),
        file=sys.stderr,
    )

permitidos = PERMITIDOS[invasividad]

if dry:
    for evento in EVENTOS:
        val = plan[evento]
        if val is None:
            estado = "null (silencio)"
        elif evento not in permitidos:
            estado = "null (invasividad %s)" % invasividad
        else:
            estado = os.path.basename(val) if not val.startswith("builtin:") else val
        print("%-20s %s" % (evento, estado))
    print("DRY-RUN: no toqué %s (%s, %s)" % (live_path, juego, invasividad))
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
for evento in EVENTOS:
    val = plan[evento]
    if evento not in permitidos or val is None:
        eventos[evento] = None
    elif isinstance(val, str) and val.startswith("builtin:"):
        eventos[evento] = val
    else:
        eventos[evento] = "file:" + val
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
print("aplicados", sum(1 for e in EVENTOS if e in permitidos and plan[e] is not None), "eventos de", juego, "desde", base)
PY