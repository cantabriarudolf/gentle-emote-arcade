#!/bin/bash
# Aplica los 14 eventos v2 a la config viva de Gentle Shell con backup.
# El repo solo guarda nombres (sounds/seleccion.json -> sounds/*.wav);
# el absoluto file: se resuelve acá, en tu máquina, al aplicar.
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SEL="$REPO/sounds/seleccion.json"
LIVE="$HOME/.gentle-shell/config/gentle-ai/notifications.json"
cp -p "$LIVE" "$LIVE.bak-$(date +%Y%m%d-%H%M%S)"
python3 - "$SEL" "$LIVE" <<'PY'
import json,sys
sel=json.load(open(sys.argv[1]))
live=json.load(open(sys.argv[2]))
import os
repo=os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[1])))
base=os.path.join(repo, sel.get("soundsDir","sounds"))
ev=live.setdefault("audio",{}).setdefault("events",{})
for event,name in sel["choices"].items():
    ev[event]=f"file:{base}/{name}.wav"
ev["session.shutdown"]=None
json.dump(live,open(sys.argv[2],"w"),indent=2,ensure_ascii=False)
print("aplicados",len(sel["choices"]),"eventos desde",base)
PY
