#!/usr/bin/env python3
"""Dibuja los estados de obra de AoE: `build`, `jira` y `review` (48x40).

Los tres son estructuras, no personajes, y van juntos aca porque comparten las
mismas primitivas de piedra, madera y tierra:

    build/build_01..03.png    obra progresiva por etapas
    jira/jira_01..03.png      maravilla: coliseo de piedra con velas azules
    review/review_01..03.png  torre de piedra abajo y madera arriba, con techo

Etapas de `build` (progresivas, de menos a mas obra):

    build_01  25%: el terreno marcado con postes y cuerda, el cartel "25"
                  clavado y el aldeano de espaldas martillando (referencia del
                  cerco con troncos y cartel).
    build_02  cerco de troncos entre los postes, pila de materiales y el
                  elefante adentro de la faena (referencia del cerco con
                  elefante).
    build_03  casi terminado: muro de troncos completo, techo de tablas y el
                  aldeano de espaldas dando el ultimo martillazo.

`jira` reemplaza el cohete de madera por el coliseo: ovalo de piedra con vanos
en sombra, tres velas azules arriba y pasto abajo; la segunda pose suma la
marca (banderin y vanos encendidos). `review` reemplaza al monje con pergamino
por la torre: base de piedra gris, cuerpo alto de madera con techo de tejas y
hiedra verde trepando; la segunda pose enciende la ventana.

El aldeano de espaldas no se duplica: sale de `cuerpo(..., cara=False,
espalda=True)` de `gen_aldeano.py`, con las mismas primitivas (`box`, `line`,
`ell`, `pegar`) y la misma guarda de sets. Uso:

    python3 gentle-emote-arcade/scripts/sprites/gen_build_aoe.py
    python3 gentle-emote-arcade/scripts/sprites/gen_build_aoe.py --set aoe-yolo

`--set` lo resuelve `gen_aldeano.py` (sets validos: `aoe` y `aoe-yolo`). El
script escribe solo los nueve PNG de `build`, `jira` y `review`: no agrega ni
borra archivos del set.
"""

import importlib.util
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(AQUI, "gen_aldeano.py")

# ── Piedra, madera, tierra y pasto ─────────────────────────────────────────
PIEDRA = (170, 168, 156)
PIEDRA_L = (206, 204, 190)
PIEDRA_D = (128, 126, 114)
VANO = (56, 54, 50)           # hueco de los arcos en sombra
MADERA = (148, 104, 58)
MADERA_L = (190, 148, 96)
MADERA_D = (104, 72, 40)
MADERA_DD = (72, 48, 26)
TEJA = (168, 78, 54)
TEJA_L = (208, 112, 78)
TEJA_D = (116, 46, 34)
HIEDRA = (74, 142, 62)
HIEDRA_L = (116, 184, 92)
PASTO = (86, 158, 64)
PASTO_L = (124, 192, 96)
PASTO_D = (56, 112, 42)
TIERRA = (178, 146, 104)
TIERRA_L = (204, 174, 130)
TIERRA_D = (140, 110, 74)
TABLA = (176, 138, 88)
TABLA_D = (128, 96, 56)
CUERDA = (216, 202, 164)
CARTEL = (224, 198, 150)
CARTEL_D = (176, 148, 104)
TINTA = (62, 46, 32)
VELA = (54, 96, 190)          # velas azules del coliseo
VELA_L = (108, 150, 228)
VELA_D = (30, 58, 138)
ELEFANTE = (152, 152, 160)
ELEFANTE_L = (188, 188, 196)
ELEFANTE_D = (108, 108, 118)
COLMILLO = (238, 236, 218)
FUEGO = (250, 208, 96)

# Digitos 3x5 del cartel de obra (mismo estilo que el resto de la UI).
FONT_DIG = {
    "2": ("###", "..#", "###", "#..", "###"),
    "5": ("###", "#..", "###", "..#", "###"),
}


def cargar_base():
    """Carga `gen_aldeano.py` como modulo, sin dejar `__pycache__`."""
    sys.dont_write_bytecode = True
    especificacion = importlib.util.spec_from_file_location("gen_aldeano", BASE)
    modulo = importlib.util.module_from_spec(especificacion)
    especificacion.loader.exec_module(modulo)
    return modulo


# ── Piezas compartidas ─────────────────────────────────────────────────────
def terreno(g, c, y0=35, y1=37):
    """Franja de tierra apisonada donde se apoya la obra."""
    g.box(c, 2, y0, 45, y1, TIERRA)
    g.box(c, 2, y0, 45, y0, TIERRA_L)
    g.box(c, 2, y1, 45, y1, TIERRA_D)
    for x in (6, 13, 21, 30, 38, 43):
        g.px(c, x, y0 + 1, TIERRA_D)


def pasto(g, c, y0=33, y1=37):
    """Franja de pasto del coliseo, con matas claras y oscuras."""
    g.box(c, 2, y0, 45, y1, PASTO)
    g.box(c, 2, y0, 45, y0, PASTO_L)
    g.box(c, 2, y1, 45, y1, PASTO_D)
    for x in (4, 9, 16, 24, 31, 39, 44):
        g.px(c, x, y0 + 1, PASTO_L)
    for x in (7, 12, 20, 27, 35, 42):
        g.px(c, x, y0 + 3, PASTO_D)


def poste(g, c, x, y0, y1):
    """Poste vertical de madera con punta tallada."""
    g.box(c, x, y0 + 1, x + 1, y1, MADERA)
    g.box(c, x, y0 + 1, x, y1, MADERA_L)
    g.box(c, x + 1, y0 + 2, x + 1, y1, MADERA_D)
    g.px(c, x, y0, MADERA_L)                 # punta
    g.px(c, x + 1, y0, MADERA_D)


def tronco(g, c, x0, x1, y):
    """Tronco horizontal: dos filas, con la veta marcada."""
    g.box(c, x0, y, x1, y, MADERA)
    g.box(c, x0, y + 1, x1, y + 1, MADERA_D)
    g.box(c, x0, y, x0, y + 1, MADERA_DD)    # punta cortada
    g.px(c, x1, y, MADERA_L)
    g.px(c, x1, y + 1, MADERA_D)


def cartel_25(g, c, x, y, y_estaca):
    """Cartel de obra con el progreso "25" y su estaca hasta el piso."""
    g.box(c, x, y, x + 9, y + 7, CARTEL)
    g.box(c, x, y, x + 9, y, CARTEL_D)
    g.box(c, x, y + 7, x + 9, y + 7, CARTEL_D)
    for dx, ch in ((1, "2"), (5, "5")):
        for dy, fila in enumerate(FONT_DIG[ch]):
            for i, p in enumerate(fila):
                if p == "#":
                    g.px(c, x + dx + i, y + 1 + dy, TINTA)
    g.box(c, x + 4, y + 8, x + 5, y_estaca, MADERA)
    g.box(c, x + 5, y + 8, x + 5, y_estaca, MADERA_D)


def aldeano_de_espaldas(g, c, dx):
    """Aldeano musculoso de espaldas con el martillo en alto."""
    g.cuerpo(c, dx=dx, cara=False, espalda=True, mouth=0)
    manos = (30 + dx, 17)
    g.dib_brazo(c, [(28 + dx, 19), (30 + dx, 18), (30 + dx, 17)],
                manos, lado=+1)
    g.dib_martillo(c, manos[0], manos[1] + 3, arriba=True)
    g.dib_brazo(c, [(19 + dx, 19), (18 + dx, 23), (18 + dx, 26)],
                (18 + dx, 27), lado=-1)


# ── build: obra progresiva ─────────────────────────────────────────────────
def frame_build_1(g):
    """25%: postes y cuerda, cartel "25" y el aldeano de espaldas."""
    b = g.canvas()
    c = g.canvas()
    terreno(g, c)
    for x in (2, 20, 42):
        poste(g, c, x, 23, 35)
    g.line(c, 3, 26, 21, 27, CUERDA, 1)      # cuerda floja entre postes
    g.line(c, 21, 27, 43, 26, CUERDA, 1)
    cartel_25(g, c, 30, 11, 26)
    aldeano_de_espaldas(g, c, -7)
    g.pegar(b, c)
    return b


def frame_build_2(g):
    """Cerco de troncos, pila de materiales y el elefante en la faena."""
    b = g.canvas()
    c = g.canvas()
    terreno(g, c)
    for x in (2, 41):
        poste(g, c, x, 21, 35)
    # el elefante va primero: los troncos del cerco le pasan por delante y se
    # lee que esta adentro de la faena, no afuera
    dib_elefante(g, c, 12, 18)
    for y in (27, 31):
        tronco(g, c, 4, 40, y)
    g.line(c, 3, 24, 42, 24, CUERDA, 1)      # cuerda del cerco
    # materiales: troncos cortados apilados contra el poste de la izquierda
    tronco(g, c, 4, 12, 34)
    for x in (5, 8, 11):
        g.px(c, x, 34, MADERA_L)
    g.pegar(b, c)
    return b


def frame_build_3(g):
    """Casi terminado: galpon de troncos con techo y el ultimo martillazo."""
    b = g.canvas()
    c = g.canvas()
    terreno(g, c)
    # galpon de troncos ya levantado, con techo de tablas
    for x in (2, 25):
        poste(g, c, x, 17, 35)
    for y in (24, 27, 30, 33):
        tronco(g, c, 4, 25, y)
    techo = ((16, 12, 19), (17, 10, 21), (18, 8, 23),
             (19, 6, 25), (20, 4, 27), (21, 2, 29))
    for y, x0, x1 in techo:
        g.box(c, x0, y, x1, y, TABLA)
        for x in range(x0, x1 + 1, 2):
            g.px(c, x, y, TABLA_D)           # tablas del techo
        g.px(c, x1, y, MADERA_D)
    g.box(c, 14, 15, 17, 15, MADERA_DD)      # cabio de cumbrera
    g.box(c, 8, 28, 13, 35, VANO)            # puerta del galpon
    g.px(c, 7, 29, VANO)
    g.px(c, 14, 29, VANO)
    g.box(c, 18, 26, 22, 33, VANO)           # ventana
    # aldeano de espaldas dando el ultimo martillazo en el poste del frente
    aldeano_de_espaldas(g, c, 8)
    g.pegar(b, c)
    # polvillo del martillazo
    g.px(b, 43, 12, FUEGO)
    g.px(b, 44, 14, (198, 156, 52))
    return b


def dib_elefante(g, c, x, y):
    """Elefante gris de perfil, con oreja grande, colmillo y trompa."""
    # cuerpo
    g.box(c, x + 3, y + 3, x + 16, y + 11, ELEFANTE)
    g.box(c, x + 3, y + 3, x + 16, y + 3, ELEFANTE_L)
    g.box(c, x + 3, y + 11, x + 16, y + 11, ELEFANTE_D)
    # patas
    for px_ in (x + 4, x + 7, x + 12, x + 15):
        g.box(c, px_, y + 12, px_ + 1, y + 16, ELEFANTE_D)
        g.box(c, px_, y + 16, px_ + 2, y + 17, ELEFANTE)
    # cabeza, oreja y trompa
    g.box(c, x + 13, y + 1, x + 18, y + 8, ELEFANTE)
    g.box(c, x + 13, y + 1, x + 17, y + 1, ELEFANTE_L)
    g.box(c, x + 12, y + 2, x + 15, y + 7, ELEFANTE_D)   # oreja
    g.px(c, x + 15, y + 4, (32, 32, 38))                 # ojo
    g.box(c, x + 17, y + 8, x + 18, y + 13, ELEFANTE)    # trompa
    g.px(c, x + 17, y + 14, ELEFANTE_D)
    g.px(c, x + 16, y + 9, COLMILLO)                     # colmillo
    g.px(c, x + 16, y + 8, COLMILLO)
    # cola
    g.px(c, x + 2, y + 6, ELEFANTE_D)
    g.px(c, x + 2, y + 7, ELEFANTE_D)


# ── jira: coliseo maravilla ────────────────────────────────────────────────
def dib_velas(g, c):
    """Velas azules colgadas de un palo, con sus cuerdas."""
    g.box(c, 12, 7, 36, 8, VELA_D)           # palo
    g.box(c, 13, 7, 35, 7, VELA)
    g.line(c, 13, 8, 11, 15, CUERDA, 1)      # cuerdas a la piedra
    g.line(c, 35, 8, 37, 15, CUERDA, 1)
    for x0, x1, punta in ((14, 19, 16), (21, 26, 23), (28, 33, 30)):
        for i in range(punta - x0 + 1):
            g.box(c, x0 + i, 9 + i, x1 - i, 9 + i, VELA)
        for i in range(punta - x0):
            g.px(c, x0 + i, 9 + i, VELA_L)
        g.px(c, punta, 9 + punta - x0, VELA_D)


def dib_coliseo(g, c):
    """Ovalo de piedra en cuatro niveles con vanos en sombra."""
    # niveles, de arriba hacia abajo: (y0, y1, x0, x1)
    for y0, y1, x0, x1 in ((14, 15, 13, 34), (16, 19, 11, 36),
                           (20, 25, 8, 39), (26, 33, 5, 42)):
        g.box(c, x0, y0, x1, y1, PIEDRA)
        g.box(c, x0, y0, x1, y0, PIEDRA_L)   # cornisa iluminada
        g.box(c, x0, y1, x1, y1, PIEDRA_D)   # cornisa en sombra
        for x in (x0, x1):                   # cantos redondeados
            g.px(c, x, y0, PIEDRA)
            g.px(c, x, y1, PIEDRA)
    # esquinas comidas: cada nivel termina redondeado y el conjunto se lee
    # como ovalo, no como piramide escalonada
    for x0, y0, x1, y1 in ((13, 14, 34, 15), (11, 16, 36, 19),
                           (8, 20, 39, 25), (5, 26, 42, 33)):
        for x, y in ((x0, y0), (x0 + 1, y0), (x0 + 2, y0), (x0, y0 + 1),
                     (x0 + 1, y0 + 1), (x0, y0 + 2), (x0, y1), (x0 + 1, y1),
                     (x1, y0), (x1 - 1, y0), (x1 - 2, y0), (x1, y0 + 1),
                     (x1 - 1, y0 + 1), (x1, y0 + 2), (x1, y1), (x1 - 1, y1)):
            g.borrar(c, x, y)
    # vanos en sombra de cada nivel, con el arco de medio punto claro
    for x, y in ((15, 16), (22, 16), (29, 16),
                 (11, 21), (18, 21), (25, 21), (32, 21),
                 (7, 27), (14, 27), (21, 27), (28, 27), (35, 27)):
        g.box(c, x, y, x + 1, y + 3, VANO)
        g.px(c, x, y, PIEDRA_L)              # arco de medio punto
        g.px(c, x + 1, y, PIEDRA_L)
    # ladrillos marcados en el nivel de abajo
    for x in (8, 12, 16, 20, 24, 28, 32, 36, 40):
        g.px(c, x, 30, PIEDRA_D)
    g.px(c, 10, 23, PIEDRA_D)
    g.px(c, 20, 23, PIEDRA_D)
    g.px(c, 30, 23, PIEDRA_D)


def frame_jira(g, n):
    b = g.canvas()
    c = g.canvas()
    pasto(g, c)
    dib_coliseo(g, c)
    dib_velas(g, c)
    g.pegar(b, c)
    if n == 2:                               # marca: banderin y vanos activos
        g.box(b, 17, 3, 22, 6, (212, 72, 60))
        g.box(b, 17, 3, 22, 3, (238, 116, 96))
        g.px(b, 16, 2, CUERDA)
        g.px(b, 16, 4, CUERDA)
        for x in (18, 25):
            g.box(b, x, 22, x + 1, 24, FUEGO)    # vanos encendidos
        g.px(b, 32, 28, FUEGO)
        g.px(b, 14, 28, FUEGO)
    return b


# ── review: torre de piedra y madera ──────────────────────────────────────
def frame_review(g, n):
    b = g.canvas()
    c = g.canvas()
    # base de piedra gris con zocalo ancho
    g.box(c, 12, 23, 35, 37, PIEDRA)
    g.box(c, 12, 23, 35, 23, PIEDRA_L)
    g.box(c, 12, 37, 35, 37, PIEDRA_D)
    g.box(c, 10, 34, 37, 37, PIEDRA)         # plinto
    g.box(c, 10, 34, 37, 34, PIEDRA_L)
    g.box(c, 10, 37, 37, 37, PIEDRA_D)
    for y in (27, 31):
        g.box(c, 12, y, 35, y, PIEDRA_D)     # hiladas de piedra
        g.px(c, 18, y + 1, PIEDRA_D)
        g.px(c, 26, y + 1, PIEDRA_D)
        g.px(c, 30, y + 2, PIEDRA_D)
    # puerta en arco y ventanas en sombra
    g.box(c, 20, 30, 27, 37, VANO)
    g.box(c, 21, 29, 26, 29, VANO)
    g.borrar(c, 21, 29)
    g.borrar(c, 26, 29)
    g.px(c, 22, 29, VANO)
    g.px(c, 25, 29, VANO)
    g.box(c, 21, 28, 26, 28, PIEDRA_D)
    for x, y in ((15, 28), (31, 28)):
        g.box(c, x, y, x + 1, y + 2, VANO)
    # cuerpo de madera con vigas
    g.box(c, 15, 11, 32, 23, MADERA)
    for x in range(16, 32, 3):
        g.box(c, x, 12, x, 23, MADERA_D)     # tablas verticales
    g.box(c, 15, 11, 32, 12, MADERA_L)
    g.box(c, 14, 22, 33, 23, MADERA_D)       # viga de apoyo
    g.box(c, 14, 11, 14, 23, MADERA_L)
    g.box(c, 33, 11, 33, 23, MADERA_D)
    # ventana de la torre
    g.box(c, 21, 15, 26, 19, VANO)
    g.box(c, 21, 15, 26, 15, MADERA_DD)
    g.box(c, 23, 15, 23, 19, MADERA_DD)      # parteluz
    # techo de tejas a cuatro aguas
    for i, (x0, x1) in enumerate(((19, 28), (17, 30), (15, 32),
                                  (13, 34), (11, 36), (10, 37))):
        y = 5 + i
        g.box(c, x0, y, x1, y, TEJA)
        for x in range(x0 + (i % 2), x1, 2):
            g.px(c, x, y, TEJA_D)            # tejas
        g.px(c, x0, y, TEJA_L)
    g.box(c, 18, 4, 29, 4, TEJA_L)           # caballete
    g.box(c, 19, 3, 28, 3, TEJA_D)
    # hiedra trepando por la piedra: tallo continuo y hojas cada tres filas
    tallo = ((33, 32), (32, 31), (33, 30), (32, 29), (33, 28), (32, 27),
             (33, 26), (32, 25), (33, 24), (32, 23), (31, 22), (31, 21))
    for x, y in tallo:
        g.px(c, x, y, HIEDRA)
    for x, y in ((31, 31), (34, 30), (31, 28), (34, 27), (30, 25),
                 (34, 24), (29, 22), (30, 20)):
        g.px(c, x, y, HIEDRA_L)
        g.px(c, x + 1, y, HIEDRA)
    g.px(c, 32, 19, HIEDRA)
    g.px(c, 33, 19, HIEDRA_L)
    g.pegar(b, c)
    if n == 2:                               # marca: torre encendida
        g.box(b, 22, 16, 25, 18, FUEGO)
        g.px(b, 23, 17, (252, 240, 176))
        g.box(b, 20, 30, 27, 34, (128, 96, 62))   # puerta abierta
        g.px(b, 21, 31, FUEGO)
        g.px(b, 26, 31, FUEGO)
    return b


FRAMES = (
    ("build", [("build_01.png", frame_build_1),
               ("build_02.png", frame_build_2),
               ("build_03.png", frame_build_3)]),
    ("jira", [("jira_01.png", lambda g: frame_jira(g, 1)),
              ("jira_02.png", lambda g: frame_jira(g, 2)),
              ("jira_03.png", lambda g: frame_jira(g, 1))]),
    ("review", [("review_01.png", lambda g: frame_review(g, 1)),
                ("review_02.png", lambda g: frame_review(g, 2)),
                ("review_03.png", lambda g: frame_review(g, 1))]),
)


def verificar(g, escritos, buffers):
    """Contrato PNG, alfa, contorno entero y progreso de la obra."""
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
    for estado in ("jira", "review"):
        frames = escritos[estado]
        assert buffers[frames[0][1]] != buffers[frames[1][1]], \
            "%s: las dos poses son el mismo bitmap" % estado
        assert buffers[frames[0][1]] == buffers[frames[2][1]], \
            "%s: _03 deberia repetir la pose 1" % estado
    # las tres etapas de la obra son bitmaps distintos (ninguna repite otra)
    vistas = [buffers[ruta] for _nombre, ruta in escritos["build"]]
    assert len(set(bytes(v) for v in vistas)) == 3, \
        "build: alguna etapa repite el bitmap de otra"


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
    print("build/jira/review regenerados en emotes/%s/ (%d PNG)"
          % (g.SET_NAME, sum(len(f) for f in escritos.values())))
    for estado, frames in escritos.items():
        for nombre, ruta in frames:
            print("  %-16s %dB" % (nombre, os.path.getsize(ruta)))


if __name__ == "__main__":
    main()
