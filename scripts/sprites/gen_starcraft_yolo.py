#!/usr/bin/env python3
"""Gemelo YOLO de starcraft: emotes/starcraft-yolo (24 estados x 48x40 RGBA).

No dibuja arte nuevo ni toca el set base: carga `gen_starcraft.py` como
modulo, le apunta la salida a `emotes/starcraft-yolo` y le repinta el visor al
marine terran con la marca YOLO del set: marco negro y lente ambar (INK /
AMBER_D / AMBER), los mismos dos pixeles de alto y la misma idea que las gafas
del gemelo cs16 y la franja de `aoe-yolo`. El ambar no es un color nuevo: es
el accent de luces y chispas que el set ya usa en `yolo` / `super-yolo`
(`glow(..., AMBER, ...)`, `spark(..., AMBER_D)`).

Regla de marcado (igual en los tres gemelos): se marca el actor que
protagoniza los estados `yolo` / `super-yolo` del set. En starcraft es el
marine (hi, success, bye, tool, write, yolo, super-yolo); el templario, el
zergling, el SCV, la abuela y las escenas de props quedan como en el base, y
las vistas de espaldas (bye 02) no dibujan visor.

`emotes.json` no se toca: sigue siendo byte-identico al de `starcraft`.

Uso (sirve desde cualquier cwd):
  python3 gentle-emote-arcade/scripts/sprites/gen_starcraft_yolo.py
"""
import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
GENERADOR = os.path.join(AQUI, "gen_starcraft.py")
SET_BASE = os.path.normpath(os.path.join(AQUI, "..", "..", "emotes",
                                         "starcraft"))
DESTINO = os.path.normpath(os.path.join(AQUI, "..", "..", "emotes",
                                        "starcraft-yolo"))


def cargar(ruta, nombre):
    sys.dont_write_bytecode = True  # no dejar __pycache__ junto al base
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def marcar(mod):
    """Visor ambar en todo marine, sin mover nada mas del frame.

    El visor cian del base ocupa dos filas (7-8); se repinta con marco INK y
    lente ambar sobre la misma geometria, asi que el resto del sprite queda
    pixel a pixel como en `starcraft`.
    """
    original = mod.marine_head

    def marine_head(b, oy=0, visor="on", back=False, lamp=True):
        original(b, oy=oy, visor=visor, back=back, lamp=lamp)
        if visor == "off" or back:
            return
        mod.rect(b, 20, 7 + oy, 27, 8 + oy, mod.INK)      # marco
        mod.rect(b, 21, 7 + oy, 26, 8 + oy, mod.AMBER_D)  # lente
        mod.hline(b, 21, 26, 7 + oy, mod.AMBER)           # brillo
        mod.setpx(b, 26, 8 + oy, mod.AMBER)

    mod.marine_head = marine_head


def limpiar(mod):
    """Borra PNG del gemelo que no esten en el plan: dos corridas dan lo mismo.

    Solo mira dentro de `emotes/starcraft-yolo/<estado>/`; no toca el set base
    ni los `.json`.
    """
    if not os.path.isdir(DESTINO):
        return []
    esperados = {(estado, nombre)
                 for estado, nombres, _dibujos in mod.PLAN
                 for nombre in nombres}
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
    for estado, nombres, _dibujos in mod.PLAN:
        for nombre in nombres:
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
    mod = cargar(GENERADOR, "gen_starcraft")
    if os.path.normpath(mod.BASE) != SET_BASE:
        sys.exit("gen_starcraft.py cambio de salida: %s" % mod.BASE)
    marcar(mod)
    mod.BASE = DESTINO
    sobran = limpiar(mod)
    if sobran:
        print("fuera del plan (borrados): %s" % ", ".join(sobran))
    mod.main()

    marcados, iguales, faltan = comparar(mod)
    print("\ngemelo starcraft-yolo: %d frames con marca YOLO, "
          "%d identicos al base" % (len(marcados), len(iguales)))
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
