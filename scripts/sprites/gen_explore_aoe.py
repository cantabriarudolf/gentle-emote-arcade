#!/usr/bin/env python3
"""Dibuja el estado `explore` de AoE: camello arquero (48x40 RGBA).

Reemplaza el jinete con antorcha que dibujaba el generador viejo. La referencia
del usuario es un camello marron claro de cuerpo entero con un jinete de
turbante, arco curvo y escudo redondo azul-blanco: entra completo en 48x40, al
contrario del jinete a caballo recortado que se descarto porque a este tamano
no se lee la silueta.

El dibujo se arma con las primitivas de `gen_aldeano.py` (misma paleta de
contorno, mismo `pegar` con contorno de 1 px) y se entrega en los nombres de
archivo que el set ya usa:

    explore/explore_01.png   pose 1: camello parado, arco bajo
    explore/explore_02.png   pose 2: paso, arco en alto y polvo en las patas
    explore/explore_03.png   repite la pose 1 (frame que ya estaba en el ciclo)

Uso, desde cualquier carpeta:

    python3 gentle-emote-arcade/scripts/sprites/gen_explore_aoe.py
    python3 gentle-emote-arcade/scripts/sprites/gen_explore_aoe.py --set aoe-yolo

El `--set` lo resuelve `gen_aldeano.py` (los sets validos son `aoe` y
`aoe-yolo`), asi el gemelo YOLO se replica con el mismo dibujo y sin codigo
duplicado. El script solo escribe los tres PNG de `explore/`: no toca ningun
otro estado del set.

La autoverificacion del final exige PNG 48x40 8-bit RGBA sin interlace, alfa
real, poses distintas entre si y que el contorno de 1 px no quede cortado por
el borde del lienzo.
"""

import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "gen_aldeano.py")

# ── Paleta del camello y del jinete ────────────────────────────────────────
CAMELLO = (198, 160, 110)     # pelo marron claro del camello
CAMELLO_L = (226, 192, 142)
CAMELLO_D = (160, 124, 80)
CAMELLO_DD = (120, 88, 54)
PEZUNA = (84, 62, 42)
MONTA = (168, 58, 52)         # manta de la montura
MONTA_D = (118, 36, 32)
TURBANTE = (238, 232, 210)    # turbante y tunica del jinete
TURBANTE_D = (196, 186, 158)
ARCO = (132, 88, 46)
CUERDA = (232, 232, 224)
ESCUDO = (58, 110, 196)       # escudo redondo azul
ESCUDO_L = (110, 156, 226)
ESCUDO_D = (34, 72, 146)
BLANCO = (242, 242, 236)


def cargar_base():
    """Carga `gen_aldeano.py` como modulo, sin dejar `__pycache__`."""
    sys.dont_write_bytecode = True
    especificacion = importlib.util.spec_from_file_location("gen_aldeano", BASE)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


def dib_patas(g, c, paso):
    """Cuatro patas de camello: dos pares, el del lado lejos en sombra."""
    if paso == 1:
        traseras = ((10, 12), (15, 16))     # (x0, x1) de cada par
        delanteras = ((27, 29), (32, 33))
        rodilla = 30
    else:                                   # paso: patas abiertas
        traseras = ((8, 10), (14, 15))
        delanteras = ((29, 31), (34, 35))
        rodilla = 31
    for x0, x1 in (traseras[1], delanteras[1]):
        g.box(c, x0, 27, x1, 34, CAMELLO_D)
        g.box(c, x0, 35, x1 + 1, 35, PEZUNA)
    for x0, x1 in (traseras[0], delanteras[0]):
        g.box(c, x0, 27, x1, 34, CAMELLO)
        g.box(c, x0, 27, x0, 34, CAMELLO_L)
        g.px(c, x0, rodilla, CAMELLO_D)        # rodilla marcada
        g.box(c, x0 - 1, 35, x1 + 1, 36, PEZUNA)
        g.box(c, x0 - 1, 35, x1 + 1, 35, CAMELLO_D)


def dib_cuerpo_camello(g, c, paso):
    """Cuerpo ovalado, joroba, cuello largo y cabeza con hocico."""
    # cola con penacho
    g.line(c, 9, 22, 7, 28, CAMELLO_D, 1)
    g.px(c, 7, 29, CAMELLO_DD)
    g.px(c, 8, 29, CAMELLO_D)
    # cuerpo: ovalo ancho apoyado sobre las patas
    g.ell(c, 20, 24, 12, 5, CAMELLO)
    g.box(c, 9, 20, 31, 22, CAMELLO)          # lomo recto entre joroba y anca
    g.box(c, 10, 20, 18, 20, CAMELLO_L)       # luz sobre el lomo
    g.box(c, 9, 28, 31, 29, CAMELLO_D)        # panza en sombra
    g.px(c, 27, 26, CAMELLO_D)                # costillar
    g.px(c, 28, 24, CAMELLO_D)
    g.px(c, 26, 27, CAMELLO_D)
    # joroba (dromedario): monticulo sobre el lomo
    g.ell(c, 22, 18, 6, 4, CAMELLO)
    g.box(c, 18, 15, 26, 15, CAMELLO_L)
    g.px(c, 16, 18, CAMELLO_D)
    g.px(c, 28, 18, CAMELLO_D)
    g.px(c, 17, 20, CAMELLO_D)
    # cuello: escalera de bloques del lomo a la cabeza (borde limpio)
    for x0, y0, x1, y1 in ((30, 21, 34, 23), (31, 18, 35, 21),
                           (32, 15, 36, 18), (33, 12, 37, 15)):
        g.box(c, x0, y0, x1, y1, CAMELLO)
        g.box(c, x0, y0, x0, y1, CAMELLO_D)
        g.px(c, x1, y0, CAMELLO_L)
    # cabeza: craneo, frente alta, hocico largo
    g.box(c, 36, 7, 41, 12, CAMELLO)
    g.box(c, 40, 10, 45, 14, CAMELLO)
    g.box(c, 41, 10, 44, 10, CAMELLO_L)
    g.box(c, 42, 14, 45, 14, CAMELLO_D)       # mandibula
    g.px(c, 44, 13, CAMELLO_DD)               # ollar
    g.px(c, 40, 10, CAMELLO_D)                # cuenca del ojo
    g.px(c, 39, 10, (32, 24, 16))             # ojo
    g.px(c, 38, 6, CAMELLO_D)                 # oreja
    g.px(c, 39, 6, CAMELLO_D)
    g.px(c, 37, 8, CAMELLO_L)


def dib_jinete(g, c, paso):
    """Jinete sentado en la joroba: tunica clara, turbante y arco curvo."""
    # manta de la montura sobre la joroba, con flecos
    g.box(c, 17, 15, 27, 17, MONTA)
    g.box(c, 17, 17, 27, 17, MONTA_D)
    for x in (17, 20, 23, 26, 27):
        g.px(c, x, 18, MONTA_D)
    g.px(c, 18, 15, (206, 96, 88))
    # pierna del jinete colgando por el lado visible, con bota
    g.box(c, 24, 18, 25, 23, TURBANTE_D)
    g.box(c, 24, 24, 25, 24, PEZUNA)
    # torso con faja roja
    g.box(c, 20, 10, 25, 18, TURBANTE)
    g.box(c, 25, 10, 25, 18, TURBANTE_D)
    g.box(c, 20, 16, 25, 17, MONTA)
    g.px(c, 21, 16, MONTA_D)
    g.px(c, 24, 16, MONTA_D)
    # brazo delantero extendido hacia la empunadura del arco
    g.line(c, 25, 12, 29, 10, TURBANTE, 2)
    g.px(c, 30, 9, (238, 196, 158))
    g.px(c, 30, 10, (198, 148, 112))
    # cabeza y turbante con cola colgando
    g.box(c, 20, 5, 24, 9, (238, 196, 158))
    g.px(c, 23, 7, (32, 24, 16))              # ojo
    g.px(c, 21, 8, (198, 148, 112))           # mejilla
    g.px(c, 22, 9, (168, 118, 86))            # boca
    g.box(c, 19, 2, 25, 4, TURBANTE)
    g.box(c, 19, 4, 25, 4, TURBANTE_D)
    g.px(c, 20, 2, BLANCO)
    g.px(c, 23, 3, BLANCO)
    g.box(c, 18, 5, 18, 7, TURBANTE_D)        # cola del turbante
    g.px(c, 18, 8, TURBANTE)


def dib_arco(g, c, alto):
    """Arco curvo con la cuerda tensa; `alto` lo sube junto con la mano."""
    dy = 0 if alto else 2
    puntos = ((30, 2 + dy), (33, 5 + dy), (34, 8 + dy),
              (33, 11 + dy), (30, 14 + dy))
    for a, b in zip(puntos, puntos[1:]):
        g.line(c, a[0], a[1], b[0], b[1], ARCO, 1)
    g.line(c, 30, 3 + dy, 30, 13 + dy, CUERDA, 1)     # cuerda
    g.px(c, 34, 8 + dy, (76, 50, 26))                 # empunadura


def dib_escudo(g, c):
    """Escudo redondo mitad azul/mitad blanco, colgado del hombro."""
    g.ell(c, 15, 15, 4, 4, ESCUDO)
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            if dx * dx + dy * dy > 17:
                continue
            if dx + dy <= 0:                  # mitad clara en diagonal
                g.px(c, 15 + dx, 15 + dy, BLANCO)
    g.px(c, 12, 13, ESCUDO_L)                 # brillo del borde azul
    g.px(c, 18, 17, ESCUDO_D)
    g.px(c, 13, 12, (252, 252, 250))


def frame_explore(g, n):
    b = g.canvas()
    c = g.canvas()
    paso = 1 if n == 1 else 2
    dib_patas(g, c, paso)
    dib_cuerpo_camello(g, c, paso)
    dib_escudo(g, c)
    dib_jinete(g, c, paso)
    dib_arco(g, c, alto=(n == 2))
    g.pegar(b, c)
    if n == 2:                              # polvo del paso
        for x, y in ((8, 37), (13, 38), (38, 38), (33, 37)):
            g.px(b, x, y, (206, 186, 152))
        g.px(b, 11, 38, (170, 148, 118))
        g.px(b, 36, 38, (170, 148, 118))
    return b


FRAMES = (
    ("explore_01.png", lambda g: frame_explore(g, 1)),
    ("explore_02.png", lambda g: frame_explore(g, 2)),
    ("explore_03.png", lambda g: frame_explore(g, 1)),
)


def verificar(g, rutas, buffers):
    """Autoverificacion: contrato PNG, alfa, poses distintas, contorno entero."""
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
        # el contorno de 1 px nunca queda cortado por el borde del lienzo
        for x in range(g.W):
            for y in (0, g.H - 1):
                assert not buf[(y * g.W + x) * 4 + 3], \
                    "%s: pixel opaco en el borde (y=%d)" % (ruta, y)
        for y in range(g.H):
            for x in (0, g.W - 1):
                assert not buf[(y * g.W + x) * 4 + 3], \
                    "%s: pixel opaco en el borde (x=%d)" % (ruta, x)
    assert buffers[rutas[0][1]] != buffers[rutas[1][1]], \
        "explore: las dos poses son el mismo bitmap"


def main():
    g = cargar_base()
    carpeta = os.path.join(g.SET_DIR, "explore")
    os.makedirs(carpeta, exist_ok=True)
    rutas, buffers = [], {}
    for nombre, constructor in FRAMES:
        buf = constructor(g)
        ruta = os.path.join(carpeta, nombre)
        with open(ruta, "wb") as fh:
            fh.write(g.encode_png(g.W, g.H, buf))
        rutas.append((nombre, ruta))
        buffers[ruta] = buf
    verificar(g, rutas, buffers)
    print("explore regenerado en emotes/%s/explore/ (%d PNG)"
          % (g.SET_NAME, len(rutas)))
    for nombre, ruta in rutas:
        print("  %-16s %dB" % (nombre, os.path.getsize(ruta)))


if __name__ == "__main__":
    main()
