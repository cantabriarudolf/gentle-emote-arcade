#!/bin/bash
# Aplica los 14 eventos v2 a la config viva de Gentle Shell con backup.
# El repo solo guarda nombres (sounds/aoe/seleccion.json -> sounds/*.wav);
# el absoluto file: se resuelve acá, en tu máquina, al aplicar.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SEL="$REPO/sounds/aoe/seleccion.json"
LIVE="$HOME/.gentle-shell/config/gentle-ai/notifications.json"
cp -p "$LIVE" "$LIVE.bak-$(date +%Y%m%d-%H%M%S)"
python3 - "$SEL" "$LIVE" <<'PY'
import os, glob as _g
sel=json.load(open(sys.argv[1]))
live=json.load(open(sys.argv[2]))
repo=os.path.dirname(os.path.abspath(sys.argv[1]))
base=repo
ev=live.setdefault("audio",{}).setdefault("events",{})
for event,name in sel["choices"].items():
    cand=os.path.join(base,name if os.path.splitext(name)[1] else name)
    if not os.path.isfile(cand):
        hits=sorted(_g.glob(os.path.join(base,os.path.splitext(name)[0]+ ".*")))
        cand=hits[0] if hits else os.path.join(base,name+".wav")
    ev[event]=f"file:{cand}"
ev["session.shutdown"]=None
json.dump(live,open(sys.argv[2],"w"),indent=2,ensure_ascii=False)
print("aplicados",len(sel["choices"]),"eventos desde",base)
PY
