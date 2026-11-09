#!/usr/bin/env python3
"""Regenera el gemelo `emotes/aoe-yolo/` con el dibujo del set base.

Mismo aldeano, misma tabla de escenas y exactamente los mismos nombres de
archivo que `emotes/aoe/`. La marca YOLO vive en los estados `yolo` y
`super-yolo` (vincha magenta en la frente + cohete de madera a la espalda,
`frame_yolo` de `gen_aldeano.py`), asi que el gemelo se dibuja con el mismo
generador cambiando solo el set de destino:

    python3 gentle-emote-arcade/scripts/sprites/gen_aoe_yolo.py

No duplica codigo de dibujo ni parchea fuentes: ejecuta
`gen_aldeano.py --set aoe-yolo`. La version anterior leia `gen_aoe_final.py`
(el generador viejo, aldeano con sombrero de paja) y escribia una copia
parcheada en `/tmp`; ese generador ya no es la fuente del set.
"""
import os
import runpy
import sys

BASE = os.path.dirname(os.path.abspath(__file__))


def main():
    sys.argv = ["gen_aldeano.py", "--set", "aoe-yolo"]
    runpy.run_path(os.path.join(BASE, "gen_aldeano.py"), run_name="__main__")


if __name__ == "__main__":
    main()
