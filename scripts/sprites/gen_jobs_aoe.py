#!/usr/bin/env python3
"""Regenera el estado `jobs` de AoE: minero con veta de oro (48x40 RGBA).

Reusa el dibujo de `gen_aldeano.py` (`frame_jobs`): aldeano musculoso con
pico junto a la veta de oro, en tres poses de extraccion (pico arriba, golpe
con estrellitas, pepita). Escribe solo `jobs/jobs_01..03.png`:

    jobs/jobs_01.png   pico arriba
    jobs/jobs_02.png   golpe con estrellitas
    jobs/jobs_03.png   pepita extraida

Uso, desde la raiz del repo:

    python3 gentle-emote-arcade/scripts/sprites/gen_jobs_aoe.py
    python3 gentle-emote-arcade/scripts/sprites/gen_jobs_aoe.py --set aoe-yolo

`--set` lo resuelve `gen_aldeano.py` (sets validos: `aoe` y `aoe-yolo`), asi
el gemelo YOLO se replica con el mismo dibujo. El script no agrega ni borra
PNG del set y no toca ningun otro estado.
"""

import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "gen_aldeano.py")


def cargar_base():
    """Carga `gen_aldeano.py` como modulo, sin dejar `__pycache__`."""
    sys.dont_write_bytecode = True
    especificacion = importlib.util.spec_from_file_location("gen_aldeano", BASE)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def main():
    g = cargar_base()
    carpeta = os.path.join(g.SET_DIR, "jobs")
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    buffers = {}
    for nombre, n in (("jobs_01.png", 1), ("jobs_02.png", 2), ("jobs_03.png", 3)):
        buf = g.frame_jobs(n)
        ruta = os.path.join(carpeta, nombre)
        with open(ruta, "wb") as fh:
            fh.write(g.encode_png(g.W, g.H, buf))
        rutas.append((nombre, ruta))
        buffers[ruta] = buf

    # Autoverificacion: contrato PNG, alfa, contorno entero y poses distintas.
    for nombre, ruta in rutas:
        w, h, depth, ctype, _comp, _filt, inter = g.ihdr(ruta)
        assert (w, h) == (g.W, g.H), "%s: %dx%d" % (ruta, w, h)
        assert depth == 8, "%s: bit depth %d" % (ruta, depth)
        assert ctype == 6, "%s: color type %d" % (ruta, ctype)
        assert inter == 0, "%s: interlace %d" % (ruta, inter)
        buf = buffers[ruta]
        alfas = set(buf[i] for i in range(3, len(buf), 4))
        assert 0 in alfas, "%s: sin fondo transparente" % ruta
        assert 255 in alfas, "%s: sin pixeles opacos" % ruta
        for x in range(g.W):
            for y in (0, g.H - 1):
                assert not buf[(y * g.W + x) * 4 + 3], \
                    "%s: pixel opaco en el borde (y=%d)" % (ruta, y)
        for y in range(g.H):
            for x in (0, g.W - 1):
                assert not buf[(y * g.W + x) * 4 + 3], \
                    "%s: pixel opaco en el borde (x=%d)" % (ruta, x)
    assert buffers[rutas[0][1]] != buffers[rutas[1][1]], \
        "jobs: las poses 1 y 2 son el mismo bitmap"
    assert buffers[rutas[1][1]] != buffers[rutas[2][1]], \
        "jobs: las poses 2 y 3 son el mismo bitmap"
    assert buffers[rutas[0][1]] != buffers[rutas[2][1]], \
        "jobs: las poses 1 y 3 son el mismo bitmap"

    print("jobs regenerado en emotes/%s/jobs/ (%d PNG)"
          % (g.SET_NAME, len(rutas)))
    for nombre, ruta in rutas:
        print("  %-16s %dB" % (nombre, os.path.getsize(ruta)))


if __name__ == "__main__":
    main()
