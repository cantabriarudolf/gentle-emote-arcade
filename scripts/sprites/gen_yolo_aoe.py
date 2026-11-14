#!/usr/bin/env python3
"""Dibuja los estados `yolo` y `super-yolo` de AoE: el auto cobra (48x40).

Reemplaza al aldeano con cohete de madera que dibujaba el generador viejo. La
referencia del usuario es un deportivo azul con franjas blancas dobles, vista
3/4, sin fondo. La unica diferencia entre los dos estados es la barra:

    yolo/        yolo_01.png, yolo_02.png, yolo_03.png   auto, SIN barra
    super-yolo/  super-yolo_01.png, ... _03.png          mismo auto + barra
                                                         verde neon de 3 px
                                                         encima

Poses: `_01` con el auto plantado y la estela limpia, `_02` con estela de
velocidad y las llantas giradas, `_03` repite la pose 1 (frame que ya estaba en
el ciclo). La barra se dibuja despues del auto y solo en `super-yolo`, asi que
la diferencia entre los dos estados queda acotada a esas tres filas: el
generador lo verifica comparando los pixeles de afuera de la barra.

Reusa las primitivas de `gen_aldeano.py` (mismo `pegar` con contorno de 1 px y
la misma guarda de sets) y escribe solo estos seis PNG, sin agregar ni borrar
archivos del set:

    python3 gentle-emote-arcade/scripts/sprites/gen_yolo_aoe.py
    python3 gentle-emote-arcade/scripts/sprites/gen_yolo_aoe.py --set aoe-yolo

`--set` lo resuelve `gen_aldeano.py`: los sets validos son `aoe` y `aoe-yolo`.
"""

import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "gen_aldeano.py")

# ── Paleta del auto cobra ──────────────────────────────────────────────────
AZUL = (46, 96, 204)          # carroceria azul
AZUL_L = (102, 152, 244)
AZUL_D = (26, 58, 142)
AZUL_DD = (14, 34, 92)
BLANCO = (238, 242, 250)      # franjas dobles
BLANCO_D = (188, 200, 220)
VIDRIO = (30, 48, 82)         # parabrisas y ventanilla
VIDRIO_L = (96, 132, 184)
GOMA = (32, 32, 38)           # neumatico
LLANTA = (176, 184, 200)      # llanta de aleacion
FARO = (250, 238, 156)
NEON = (92, 252, 122)         # barra verde neon de super-yolo
NEON_L = (196, 255, 206)
NEON_D = (34, 162, 74)

# Filas de la barra de super-yolo: 3 px de alto, por encima del techo.
BARRA_Y0, BARRA_Y1 = 6, 8


def cargar_base():
    """Carga `gen_aldeano.py` como modulo, sin dejar `__pycache__`."""
    sys.dont_write_bytecode = True
    especificacion = importlib.util.spec_from_file_location("gen_aldeano", BASE)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def dib_rueda(g, c, cx, giro):
    """Neumatico con llanta de aleacion; el brillo cambia con el giro.

    Las ruedas se dibujan despues de la carroceria: el neumatico tapa las
    filas bajas del flanco y asi queda el paso de rueda sin recortar nada.
    """
    cy = 28
    g.ell(c, cx, cy, 4, 4, GOMA)
    g.ell(c, cx, cy, 2, 2, LLANTA)
    g.px(c, cx, cy, AZUL_DD)                     # buje
    if giro:
        g.px(c, cx + 1, cy + 1, (232, 236, 244))
        g.px(c, cx - 1, cy + 2, BLANCO_D)
    else:
        g.px(c, cx - 1, cy - 1, (232, 236, 244))
        g.px(c, cx + 1, cy - 2, BLANCO_D)
    g.px(c, cx - 2, cy - 1, GOMA)
    g.px(c, cx + 2, cy + 1, GOMA)
    g.px(c, cx - 2, cy + 2, GOMA)


def dib_carroceria(g, c):
    """Silueta estilizada: techo bajo, trompa larga y franjas anchas."""
    # techo y cabina baja
    g.box(c, 23, 12, 27, 12, AZUL_L)
    g.box(c, 21, 13, 29, 13, AZUL)
    g.box(c, 20, 14, 30, 16, VIDRIO)
    g.box(c, 21, 14, 29, 14, VIDRIO_L)
    g.box(c, 19, 15, 19, 16, AZUL_D)             # parante trasero
    g.box(c, 30, 15, 30, 16, AZUL_L)             # parante delantero
    # cintura y capot largo
    g.box(c, 14, 17, 36, 17, AZUL_L)             # cintura iluminada
    g.box(c, 13, 18, 38, 18, AZUL)
    g.box(c, 12, 19, 40, 19, AZUL)
    g.box(c, 12, 19, 40, 19, AZUL_L)
    g.box(c, 11, 20, 40, 20, AZUL)
    # franjas blancas anchas a lo largo del flanco
    g.box(c, 9, 21, 41, 21, BLANCO)
    g.box(c, 9, 22, 41, 22, AZUL)
    g.box(c, 9, 23, 41, 23, BLANCO)
    g.px(c, 41, 21, BLANCO_D)
    g.px(c, 41, 23, BLANCO_D)
    # bajos
    g.box(c, 10, 24, 40, 24, AZUL)
    g.box(c, 11, 25, 39, 25, AZUL)
    g.box(c, 13, 26, 37, 26, AZUL_D)
    # cola corta: aleron, optica y doble escape
    g.box(c, 8, 16, 12, 17, AZUL_D)
    g.box(c, 8, 16, 12, 16, AZUL_L)
    g.box(c, 8, 19, 8, 21, AZUL_DD)
    g.box(c, 8, 21, 9, 22, (196, 72, 58))        # optica trasera
    g.box(c, 6, 25, 7, 25, AZUL_DD)              # escapes
    g.box(c, 6, 26, 7, 26, AZUL_DD)
    g.px(c, 6, 25, (128, 128, 138))
    g.px(c, 6, 26, (128, 128, 138))
    # marca YOLO del set (calcomania magenta en la puerta)
    g.px(c, 25, 20, g.MAGENTA)
    g.px(c, 26, 20, g.MAGENTA_D)


def dib_detalles(g, c):
    """Faro, parrilla y linea de puerta, por delante de las ruedas."""
    g.box(c, 39, 20, 40, 21, FARO)               # faro delantero
    g.px(c, 40, 20, (255, 252, 200))
    g.box(c, 40, 24, 41, 25, AZUL_DD)            # parrilla
    g.box(c, 12, 19, 40, 19, AZUL_L)             # filo del capot
    g.box(c, 26, 19, 26, 24, AZUL_D)             # linea de puerta
    g.px(c, 27, 19, LLANTA)                      # manija
    g.px(c, 36, 24, AZUL_D)                      # toma de aire


def dib_barra(g, b):
    """Barra verde neon de 3 px por encima del auto (solo super-yolo)."""
    g.box(b, 6, BARRA_Y0, 42, BARRA_Y1, NEON)
    g.box(b, 6, BARRA_Y0, 42, BARRA_Y0, NEON_L)
    g.box(b, 6, BARRA_Y1, 42, BARRA_Y1, NEON_D)
    g.px(b, 5, BARRA_Y0 + 1, NEON_D)
    g.px(b, 43, BARRA_Y0 + 1, NEON_D)


def frame_yolo(g, n, superyolo=False):
    b = g.canvas()
    c = g.canvas()
    giro = (n == 2)
    dib_carroceria(g, c)
    dib_rueda(g, c, 15, giro)
    dib_rueda(g, c, 33, giro)
    dib_detalles(g, c)
    g.pegar(b, c)
    if giro:                                     # estela de velocidad
        for x0, x1, y in ((1, 3, 21), (1, 4, 23), (1, 2, 26)):
            g.box(b, x0, y, x1, y, BLANCO_D)
        g.px(b, 2, 31, (150, 172, 198))
    if superyolo:
        dib_barra(g, b)
    return b


FRAMES = (
    ("yolo", [("yolo_01.png", lambda g: frame_yolo(g, 1)),
              ("yolo_02.png", lambda g: frame_yolo(g, 2)),
              ("yolo_03.png", lambda g: frame_yolo(g, 1))]),
    ("super-yolo", [("super-yolo_01.png", lambda g: frame_yolo(g, 1, True)),
                    ("super-yolo_02.png", lambda g: frame_yolo(g, 2, True)),
                    ("super-yolo_03.png", lambda g: frame_yolo(g, 1, True))]),
)


def verificar(g, escritos, buffers):
    """Contrato PNG, alfa, contorno entero y barra como unica diferencia."""
    for estado, frames in escritos.items():
        for nombre, ruta in frames:
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
        simple = escritos["yolo"]
        doble = escritos["super-yolo"]
        for (nombre, ruta), (_nombre2, ruta2) in zip(simple, doble):
            a, b = buffers[ruta], buffers[ruta2]
            assert a != b, "%s: super-yolo no tiene la barra" % nombre
            for y in range(g.H):
                if BARRA_Y0 <= y <= BARRA_Y1:
                    continue
                fila = g.W * 4
                assert a[y * fila:(y + 1) * fila] == b[y * fila:(y + 1) * fila], \
                    "%s: super-yolo cambia algo ademas de la barra (y=%d)" % (
                        nombre, y)


def main():
    g = cargar_base()
    escritos = {}
    buffers = {}
    for estado, frames in FRAMES:
        carpeta = os.path.join(g.SET_DIR, estado)
        os.makedirs(carpeta, exist_ok=True)
        for nombre, constructor in frames:
            buf = constructor(g)
            ruta = os.path.join(carpeta, nombre)
            with open(ruta, "wb") as fh:
                fh.write(g.encode_png(g.W, g.H, buf))
            escritos.setdefault(estado, []).append((nombre, ruta))
            buffers[ruta] = buf
    verificar(g, escritos, buffers)
    print("yolo/super-yolo regenerados en emotes/%s/ (%d PNG)"
          % (g.SET_NAME, sum(len(f) for f in escritos.values())))
    for estado, frames in escritos.items():
        for nombre, ruta in frames:
            print("  %-18s %dB" % (nombre, os.path.getsize(ruta)))


if __name__ == "__main__":
    main()
