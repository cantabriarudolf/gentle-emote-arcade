import zlib, struct, os
# reuse final generator code by exec, but override base_dir and force yolo
src=open("gentle-emote-arcade/scripts/sprites/gen_aoe_final.py").read()
# change base_dir to aoe-yolo
src=src.replace('base_dir="gentle-emote-arcade/emotes/aoe"','base_dir="gentle-emote-arcade/emotes/aoe-yolo"')
# force yolo=True in the states dict usage: inject kw['yolo']=True before draw calls by replacing the loop header line
src=src.replace('for state,(pal,kw) in states.items():','for state,(pal,kw) in states.items():\n    kw=dict(kw); kw["yolo"]=True')
# talk loop
src=src.replace('for name,mw in [("talk_close",0),("talk_small",1),("talk_mid",2),("talk_wide",3)]:','for name,mw in [("talk_close",0),("talk_small",1),("talk_mid",2),("talk_wide",3)]:\n            pass')
# add yolo=True to talk draw call
src=src.replace('draw_villager(b,V,pose="talk",mouth=mw)','draw_villager(b,V,pose="talk",mouth=mw,yolo=True)')
# idle draws
src=src.replace('draw_villager(b,V,pose="idle",blink=False)','draw_villager(b,V,pose="idle",blink=False,yolo=True)')
src=src.replace('draw_villager(b,V,pose="idle",blink=True)','draw_villager(b,V,pose="idle",blink=True,yolo=True)')
open("/tmp/gen_yolo2.py","w").write(src)
