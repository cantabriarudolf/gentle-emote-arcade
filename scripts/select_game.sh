#!/bin/bash
# Selector de juego POR PROYECTO: escribe los sprites y el juego elegido en el
# proyecto, nunca en la config global de los demás proyectos. El audio de Gentle
# Shell es uno solo para todas las sesiones, así que lo aplica el hook
# `session_start` de game-select al abrir sesión (o /reload).
# Uso: ./scripts/select_game.sh [juego] [--proyecto RUTA] [--invasividad NIVEL] [--dry-run]
#       juego: aoe (default) | minecraft | cs16 | starcraft | lol | misc | gentle | abuela
#       --proyecto RUTA: proyecto destino (default: el directorio actual)
#       --invasividad NIVEL: todo|a (14) | esencial|b (12) | guardia|c (6)
#       -n, --dry-run: no escribe ninguna config (sprites, pack ni mapa).
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
        -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
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
# Un solo mapa, al lado del repo: guarda juego y set por proyecto (clave absoluta).
MAP="${PI_GAME_SELECT_MAP:-$(cd "$REPO/.." && pwd)/.pi/extensions/game-select/projects.json}"

if [ -n "$PROYECTO" ]; then
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
    if [ -d "$PROYECTO" ]; then
        PROYECTO="$(cd "$PROYECTO" && pwd)"
    else
        echo "no existe el proyecto: $PROYECTO" >&2
        exit 2
    fi
else
    PROYECTO="$PWD"
fi

JUEGO="${JUEGO:-aoe}"
# El menu llama a los sets a, b y c: se aceptan como alias del nivel.
case "$INVASIVIDAD" in
    a|A) INVASIVIDAD="todo" ;;
    b|B) INVASIVIDAD="esencial" ;;
    c|C) INVASIVIDAD="guardia" ;;
esac
INVASIVIDAD="${INVASIVIDAD:-todo}"
case "$INVASIVIDAD" in
    todo|esencial|guardia) ;;
    *) echo "invasividad desconocida: $INVASIVIDAD (usá a|b|c o todo|esencial|guardia)" >&2; exit 2 ;;
esac
SEL="$REPO/sounds/$JUEGO/seleccion.json"
[ -f "$SEL" ] || { echo "No existe $SEL" >&2; exit 1; }

echo "=== Sprites -> $JUEGO (sólo $PROYECTO) ==="
if [ "$DRY" -eq 1 ]; then
    echo "(dry-run: no toco la config del proyecto)"
else
    # `misc` es sólo sonidos mezclados: hereda el arte de aoe. `gentle` tiene
    # sus propias escenas (fork upstream).
    SPRITES_JUEGO="$JUEGO"
    if [ "$JUEGO" = "misc" ]; then
        SPRITES_JUEGO="aoe"
    fi
    python3 - "$SPRITES_JUEGO" "$JUEGO" "$REPO" "$PROYECTO" "$MAP" "$INVASIVIDAD" <<'PY'
import json, os, shutil, stat, sys, time

sprites, juego, repo, proyecto, mapa, invasividad = sys.argv[1:7]
ext = os.path.join(proyecto, ".pi", "extensions", "gentle-emote")
config = os.path.join(ext, "config.json")
os.makedirs(ext, exist_ok=True)

d = {}
if os.path.isfile(config):
    try:
        with open(config, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        d = {}
deseado = [{"model": "*", "emote-set": sprites}]
if d.get("emotes") == deseado:
    print("sprites: ya en %s (%s)" % (sprites, config))
else:
    modo = None
    if os.path.isfile(config):
        modo = stat.S_IMODE(os.stat(config).st_mode)
        respaldo = config + ".bak-" + time.strftime("%Y%m%d-%H%M%S")
        n = 1
        while os.path.exists(respaldo):
            respaldo = "%s.bak-%s-%d" % (config, time.strftime("%Y%m%d-%H%M%S"), n)
            n += 1
        shutil.copy2(config, respaldo)
        print("sprites: backup en %s" % os.path.basename(respaldo))
    d["emotes"] = deseado
    tmp = "%s.tmp-%d" % (config, os.getpid())
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(d, fh, indent=2)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        if modo is not None:
            os.chmod(tmp, modo)
        os.replace(tmp, config)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    print("sprites:", config)

# El pack de sprites viaja con el proyecto: el resolver del avatar mira primero
# `<proyecto>/.pi/extensions/gentle-emote/emotes/<set>`, así que el proyecto se
# resuelve solo, sin depender del dir global ni de este repo.
origen = os.path.join(repo, "emotes", sprites)
destino = os.path.join(ext, "emotes", sprites)
if os.path.isdir(origen) and not os.path.isdir(destino):
    shutil.copytree(origen, destino)
    print("pack:", destino)
elif os.path.isdir(destino):
    print("pack: ya en", destino)
else:
    print("pack: %s todavía no tiene arte; queda el que resuelva el plugin" % sprites)

# Mapa por proyecto: una entrada canónica, clave absoluta.
try:
    with open(mapa, encoding="utf-8") as fh:
        m = json.load(fh)
except Exception:
    m = {}
if not isinstance(m, dict):
    m = {}
m[proyecto] = {"juego": juego, "invasividad": invasividad}
os.makedirs(os.path.dirname(mapa), exist_ok=True)
modo = None
if os.path.isfile(mapa):
    modo = stat.S_IMODE(os.stat(mapa).st_mode)
tmp = "%s.tmp-%d" % (mapa, os.getpid())
try:
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    if modo is not None:
        os.chmod(tmp, modo)
    os.replace(tmp, mapa)
finally:
    if os.path.exists(tmp):
        os.unlink(tmp)
print("mapa:", mapa)
PY
fi

echo "=== Sonidos -> $JUEGO (se aplican al abrir sesión) ==="
# El audio de Gentle Shell es un único archivo global: si el selector lo
# escribiera acá, elegir en un proyecto le cambiaría el sonido a todos. El hook
# `session_start` de game-select lo aplica al abrir, con backup y baseline.
# Acá sólo se muestra el mapeo resuelto y se valida el pack.
"$REPO/scripts/apply_sounds.sh" "$JUEGO" --invasividad "$INVASIVIDAD" --dry-run
if [ "$DRY" -eq 0 ]; then
    # `gentle` (alias `abuela`) suena su activación al quedar elegido: la primera
    # toma de `activacionVariantes` del pack, con el coin como fallback.
    if [ "$JUEGO" = "gentle" ]; then
        ACTIVACION="$(python3 - "$REPO/sounds/gentle" <<'PY'
import json, os, sys
base = sys.argv[1]
nombres = []
try:
    sel = json.load(open(os.path.join(base, "seleccion.json"), encoding="utf-8"))
    if isinstance(sel.get("activacionVariantes"), list) and sel["activacionVariantes"]:
        nombres = [str(n) for n in sel["activacionVariantes"]]
    elif isinstance(sel.get("activation"), str):
        nombres = [sel["activation"]]
except Exception:
    pass
for nombre in nombres or ["coin"]:
    for rel in (nombre, nombre + ".wav"):
        ruta = os.path.join(base, rel)
        if os.path.isfile(ruta):
            print(ruta)
            raise SystemExit
PY
)"
        if [ -n "$ACTIVACION" ]; then
            { paplay "$ACTIVACION" || aplay -q "$ACTIVACION"; } >/dev/null 2>&1 ||
                echo "aviso: no pude reproducir $(basename "$ACTIVACION") (¿servidor de audio?)" >&2
        fi
    fi
    echo "Listo: $JUEGO queda elegido para $PROYECTO"
    echo "      el audio global se aplica al abrir sesión (en esta: /reload)"
fi
