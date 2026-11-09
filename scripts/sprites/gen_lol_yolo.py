#!/usr/bin/env python3
"""Gemelo YOLO de lol: emotes/lol-yolo (24 estados x 48x40 RGBA).

No dibuja arte nuevo ni toca el set base: carga `gen_lol.py` como modulo, le
apunta la salida a `emotes/lol-yolo` y le agrega al bruto armado la marca YOLO
del set: una banda de gafas toxicas sobre los ojos (marco INK, lente TOX_D,
reflejos TOX / TOX_L). Son los colores que el propio set ya usa para el modo
YOLO (`TOX`, `TOX_L`, `TOX_D`), con la misma geometria que las gafas del set
cs16 y la misma idea que la franja magenta de `aoe-yolo`: dos filas sobre la
linea de ojos, sin ningun color nuevo.

Regla de marcado (igual en los tres gemelos): se marca el actor que
protagoniza los estados `yolo` / `super-yolo` del set. En lol es el bruto
armado (hi, success, failure, yolo, super-yolo, bye); el mago, el arquero, el
yordle y las escenas de props quedan como en el base, y en las vistas de
espaldas (bye 02) no se dibuja la banda.

`emotes.json` no se toca: sigue siendo byte-identico al de `lol`.

Uso (sirve desde cualquier cwd):
  python3 gentle-emote-arcade/scripts/sprites/gen_lol_yolo.py
"""
import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
GENERADOR = os.path.join(AQUI, "gen_lol.py")
SET_BASE = os.path.normpath(os.path.join(AQUI, "..", "..", "emotes", "lol"))
DESTINO = os.path.normpath(os.path.join(AQUI, "..", "..", "emotes",
                                        "lol-yolo"))


def cargar(ruta, nombre):
    sys.dont_write_bytecode = True  # no dejar __pycache__ junto al base
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def marcar(mod):
    """Banda toxica sobre los ojos del bruto armado (cara al frente)."""
    original = mod.bruiser_head

    def bruiser_head(buf, look="fwd", mouth="line", back=False):
        original(buf, look=look, mouth=mouth, back=back)
        if back:
            return
        mod.rect(buf, 20, 9, 27, 10, mod.INK)     # marco
        mod.rect(buf, 21, 9, 26, 10, mod.TOX_D)   # lente
        mod.setpx(buf, 21, 9, mod.TOX)            # reflejo
        mod.setpx(buf, 26, 10, mod.TOX_L)

    mod.bruiser_head = bruiser_head


def limpiar(mod):
    """Borra PNG del gemelo que no esten en el plan: dos corridas dan lo mismo.

    Solo mira dentro de `emotes/lol-yolo/<estado>/`; no toca el set base ni
    los `.json`.
    """
    if not os.path.isdir(DESTINO):
        return []
    esperados = {(estado, nombre)
                 for estado, frames in mod.FRAMES
                 for nombre, _construir in frames}
    sobran = []
    for estado in sorted(os.listdir(DESTINO)):
        carpeta = os.path.join(DESTINO, estado)
        if not os.path.isdir(carpeta):
            continue
        for archivo in sorted(os.listdir(carpeta)):
            if not archivo.endswith(".png"):
                continue
            if (estado, archivo) not in esperados:
                os.remove(os.path.join(carpeta, archivo))
                sobran.append("%s/%s" % (estado, archivo))
    return sobran


def comparar(mod):
    """Separa los frames marcados de los que salieron iguales al set base."""
    marcados, iguales, faltan = [], [], []
    for estado, frames in mod.FRAMES:
        for nombre, _construir in frames:
            etiqueta = "%s/%s" % (estado, nombre)
            gemelo = os.path.join(DESTINO, estado, nombre)
            base = os.path.join(SET_BASE, estado, nombre)
            if not (os.path.isfile(gemelo) and os.path.isfile(base)):
                faltan.append(etiqueta)
                continue
            with open(gemelo, "rb") as fh:
                a = fh.read()
            with open(base, "rb") as fh:
                b = fh.read()
            (iguales if a == b else marcados).append(etiqueta)
    return marcados, iguales, faltan


def main():
    mod = cargar(GENERADOR, "gen_lol")
    if os.path.normpath(mod.BASE) != SET_BASE:
        sys.exit("gen_lol.py cambio de salida: %s" % mod.BASE)
    marcar(mod)
    mod.BASE = DESTINO
    sobran = limpiar(mod)
    if sobran:
        print("fuera del plan (borrados): %s" % ", ".join(sobran))
    mod.main()

    marcados, iguales, faltan = comparar(mod)
    print("\ngemelo lol-yolo: %d frames con marca YOLO, %d identicos al base"
          % (len(marcados), len(iguales)))
    if iguales:
        print("  identicos al base: %s" % ", ".join(iguales))
    if faltan:
        sys.exit("faltan frames: %s" % ", ".join(faltan))
    if not marcados:
        sys.exit("la marca YOLO no se aplico a ningun frame")
    print("  -> %s" % DESTINO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
