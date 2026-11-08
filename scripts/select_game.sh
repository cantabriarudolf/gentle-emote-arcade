#!/bin/bash
# Selector de juego: cambia sprites Y sonidos juntos.
# Uso: ./scripts/select_game.sh aoe|minecraft|cs16
# Requiere: sounds/<juego>/seleccion.json (portable, solo nombres) y
# emotes/<juego>/ (si aún no tiene arte, el plugin usa lo que haya).
set -e
JUEGO="${1:-aoe}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SEL="$REPO/sounds/$JUEGO/seleccion.json"
[ -f "$SEL" ] || { echo "No existe $SEL"; exit 1; }

echo "=== Sprites -> $JUEGO ==="
python3 - "$JUEGO" "$REPO" <<'PY'
import json,sys,os
juego=sys.argv[1]
repo=sys.argv[2]
paths=[
 os.path.expanduser("~/.gentle-shell/agent/extensions/gentle-emote/config.json"),
 os.path.join(os.path.dirname(repo),".pi","extensions","gentle-emote","config.json"),
]
for p in paths:
  if os.path.isfile(p):
    d=json.load(open(p))
    d["emotes"]=[{"model":"*","emote-set":juego}]
    json.dump(d,open(p,"w"),indent=2); open(p,"a").write("\n")
    print("sprites:",p)
PY

echo "=== Sonidos -> $JUEGO (con backup) ==="
LIVE="$HOME/.gentle-shell/config/gentle-ai/notifications.json"
cp -p "$LIVE" "$LIVE.bak-$(date +%Y%m%d-%H%M%S)"
python3 - "$SEL" "$LIVE" <<'PY'
import json,sys,os
sel=json.load(open(sys.argv[1]))
live=json.load(open(sys.argv[2]))
base=os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])))
ev=live.setdefault("audio",{}).setdefault("events",{})
import glob as _g
for event,name in sel["choices"].items():
    cand=os.path.join(base,name)
    if not os.path.isfile(cand):
        hits=sorted(_g.glob(cand+".*"))
        cand=hits[0] if hits else cand
    ev[event]=f"file:{cand}"
ev["session.shutdown"]=None
json.dump(live,open(sys.argv[2],"w"),indent=2,ensure_ascii=False)
print("sonidos:",len(sel["choices"]),"eventos desde",base)
PY
echo "Listo: /reload en herdr para ver+oir $JUEGO"
