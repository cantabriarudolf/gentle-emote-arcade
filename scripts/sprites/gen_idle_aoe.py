#!/usr/bin/env python3
"""Regenera solo el par `idle` de `emotes/aoe/`.

Reusa el dibujo de `gen_aldeano.py` (el aldeano musculoso: torso desnudo,
pantalon azul, cinturon trenzado y brazaletes) en vez de tener su propia copia
del personaje: antes este script dibujaba el aldeano viejo con sombrero de
paja y, al correrlo, borraba el arte nuevo del parpadeo.

    python3 gentle-emote-arcade/scripts/sprites/gen_idle_aoe.py

Escribe unicamente `emotes/aoe/idle/idle.png` e `idle_blink.png`.
"""
import importlib.util
import os

BASE = os.path.dirname(os.path.abspath(__file__))
GENERADOR = os.path.join(BASE, "gen_aldeano.py")


def cargar_generador():
    """Carga `gen_aldeano.py` como modulo (no ejecuta su `main`)."""
    especificacion = importlib.util.spec_from_file_location(
        "gen_aldeano", GENERADOR
    )
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def main():
    gen = cargar_generador()
    carpeta = os.path.join(gen.SET_DIR, "idle")
    os.makedirs(carpeta, exist_ok=True)
    for nombre, pose in (("idle.png", 1), ("idle_blink.png", 2)):
        buf = gen.frame_idle(pose)
        with open(os.path.join(carpeta, nombre), "wb") as fh:
            fh.write(gen.encode_png(gen.W, gen.H, buf))
    print("idle regenerado en emotes/%s/idle/ (2 PNG)" % gen.SET_NAME)


if __name__ == "__main__":
    main()
