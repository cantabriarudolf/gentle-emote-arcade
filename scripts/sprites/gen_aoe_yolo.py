#!/usr/bin/env python3
"""Regenera los estados del gemelo `emotes/aoe-yolo/` que salen de
`gen_aldeano.py` y `gen_build_aoe.py`.

Misma tabla de escenas y exactamente los mismos nombres de archivo que
`emotes/aoe/`: el gemelo se dibuja con los mismos generadores cambiando solo
el set de destino, sin duplicar codigo de dibujo ni parchear fuentes.

    python3 gentle-emote-arcade/scripts/sprites/gen_aoe_yolo.py

**No cubre el set completo.** Estos estados los dibujan generadores que
todavia no aceptan `--set`, asi que se espejan copiando el PNG del set base
(ver `emotes/aoe-yolo/README.md`):

    delegate, judge, remember, compact, verify   gen_monje.py
    explore                                     gen_explore_aoe.py
    yolo, super-yolo                            gen_yolo_aoe.py

La version anterior leia `gen_aoe_final.py` (el generador viejo, aldeano con
sombrero de paja) y escribia una copia parcheada en `/tmp`; ese generador ya
no es la fuente del set.
"""
import os
import runpy
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def main():
    # Aldeano: hi, idle, talk, ask, success, failure, bye, jobs, grandma, write.
    sys.argv = ["gen_aldeano.py", "--set", "aoe-yolo"]
    runpy.run_path(os.path.join(BASE, "gen_aldeano.py"), run_name="__main__")
    # Estructuras: build, jira, review.
    sys.argv = ["gen_build_aoe.py", "--set", "aoe-yolo"]
    runpy.run_path(os.path.join(BASE, "gen_build_aoe.py"), run_name="__main__")


if __name__ == "__main__":
    main()
