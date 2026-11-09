#!/usr/bin/env python3
"""Gemelo YOLO de cs16: emotes/cs16-yolo (24 estados x 48x40 RGBA).

No dibuja arte nuevo ni toca el set base: carga `gen_cs16.py` como modulo, le
apunta la salida a `emotes/cs16-yolo` y fuerza en cada escena del CT la marca
YOLO del set, que es la que ya usa el estado `yolo`: gafas + panuelo rojo
(`ct_body_canvas(..., glasses=True, bandana=True)`). Paleta, geometria,
nombres de archivo y verificacion son los del generador base, asi que los dos
sets no se pueden desincronizar.

Regla de marcado (igual en los tres gemelos): se marca el actor que
protagoniza los estados `yolo` / `super-yolo` del set. En cs16 es el CT; el
rehen de `remember` y el pollo de `grandma` quedan como en el base.

Nombres: el set base guarda la escena `failure` como `down_01.png` /
`down_02.png`, no como `failure_0N.png` (deriva entre `gen_cs16.py` y los
bytes ya entregados). El gemelo respeta los nombres del base para que los dos
sets se instalen con la misma tabla de archivos.

`emotes.json` no se toca: sigue siendo byte-identico al de `cs16`.

Uso (sirve desde cualquier cwd):
  python3 gentle-emote-arcade/scripts/sprites/gen_cs16_yolo.py
"""
import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
GENERADOR = os.path.join(AQUI, "gen_cs16.py")
SET_BASE = os.path.normpath(os.path.join(AQUI, "..", "..", "emotes", "cs16"))
DESTINO = os.path.normpath(os.path.join(AQUI, "..", "..", "emotes",
                                        "cs16-yolo"))

# El set base entregado usa estos nombres para la escena `failure`.
NOMBRES = {"failure_01.png": "down_01.png",
           "failure_02.png": "down_02.png"}


def cargar(ruta, nombre):
    sys.dont_write_bytecode = True  # no dejar __pycache__ junto al base
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def marcar(mod):
    """Gafas + panuelo en todo cuerpo CT, sin tocar los demas personajes.

    Las escenas del CT pasan por `ct_body_canvas`; el rehen (`hostage`) llama a
    `head_ct` directo y por eso queda sin marca, igual que en el base.
    """
    original = mod.ct_body_canvas

    def ct_body_canvas(mode="stand", **opts):
        opts["glasses"] = True
        opts["bandana"] = True
        return original(mode, **opts)

    mod.ct_body_canvas = ct_body_canvas


def renombrar(mod):
    """Alinea la tabla de frames con los nombres que ya usa el set base."""
    mod.FRAMES = [(estado, [(NOMBRES.get(nombre, nombre), construir)
                            for nombre, construir in frames])
                  for estado, frames in mod.FRAMES]


def limpiar(mod):
    """Borra PNG del gemelo que no esten en el plan: dos corridas dan lo mismo.

    Solo mira dentro de `emotes/cs16-yolo/<estado>/`; no toca el set base ni
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
    mod = cargar(GENERADOR, "gen_cs16")
    if os.path.normpath(mod.BASE) != SET_BASE:
        sys.exit("gen_cs16.py cambio de salida: %s" % mod.BASE)
    marcar(mod)
    renombrar(mod)
    mod.BASE = DESTINO
    sobran = limpiar(mod)
    if sobran:
        print("fuera del plan (borrados): %s" % ", ".join(sobran))
    mod.main()

    marcados, iguales, faltan = comparar(mod)
    print("\ngemelo cs16-yolo: %d frames con marca YOLO, %d identicos al base"
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
