#!/usr/bin/env python3
"""Escenas CON UNIDADES del set AoE (gentle-emote-arcade).

Cinco estados, todos loop de poses chicas:

  read/     scout a caballo con antorcha ......... 2 poses (antorcha izq / der)
  explore/  caballeria con farol ................. 2 poses (paso 1 / paso 2)
  build/    herrero soldando el ariete ........... 2 poses (chispa / sin chispa)
  tool/     ariete de asalto empujado ............ 3 poses (atras / medio / adelante)
  jira/     castillo con cohete de madera ....... 2 poses (despegando / en el aire)

Solo stdlib: struct + zlib (PNG 48x40 RGBA escrito a mano, sin PIL, sin red).
Fondo transparente real, todo el dibujo adentro del cuadro.
Los demas estados del set no se tocan.

    python3 scripts/sprites/gen_unidades.py
"""
import os
import struct
import zlib

W, H = 48, 40


# --------------------------------------------------------------- PNG (stdlib)
def encode_png(w, h, pixels):
    def chunk(kind, body):
        full = kind + body
        return (struct.pack(">I", len(body)) + full
                + struct.pack(">I", zlib.crc32(full) & 0xFFFFFFFF))

    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def canvas():
    return bytearray(b"\x00\x00\x00\x00" * W * H)


def setpx(buf, x, y, col, a=255):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i:i + 4] = bytes((col[0], col[1], col[2], a))


def rect(buf, x0, y0, x1, y1, col, a=255):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            setpx(buf, x, y, col, a)


def hline(buf, x0, x1, y, col):
    rect(buf, x0, y, x1, y, col)


def vline(buf, x, y0, y1, col):
    rect(buf, x, y0, x, y1, col)


def line(buf, x0, y0, x1, y1, col):
    """Bresenham de 1 px (palos, varillas, ganchos)."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        setpx(buf, x0, y0, col)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ellipse(buf, cx, cy, rx, ry, col):
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            if (dx * dx) * (ry * ry) + (dy * dy) * (rx * rx) <= (rx * rx) * (ry * ry):
                setpx(buf, cx + dx, cy + dy, col)


def disc(buf, cx, cy, r, col):
    ellipse(buf, cx, cy, r, r, col)


# ------------------------------------------------------------------- paleta
ink = (26, 18, 8)
dark = (43, 31, 16)

horse = (152, 106, 60)
horseD = (114, 78, 42)
horseDD = (82, 55, 28)
mane = (62, 40, 20)
hoof = (46, 32, 16)
muzzle = (188, 150, 114)

blue = (52, 84, 164)
blueL = (98, 134, 208)
blueD = (34, 56, 118)

skin = (232, 176, 138)
skinD = (200, 140, 100)
shine = (246, 208, 172)

linen = (176, 150, 112)
linenD = (140, 116, 84)

iron = (126, 130, 138)
ironD = (86, 90, 98)
ironL = (176, 180, 188)
lens = (44, 52, 62)

wood = (139, 105, 60)
woodD = (100, 72, 38)
woodDD = (70, 50, 26)
woodL = (174, 140, 86)

leather = (112, 78, 44)
leatherD = (80, 54, 30)

cloth = (196, 178, 144)
clothD = (152, 134, 104)

stone = (148, 142, 130)
stoneD = (110, 104, 94)
stoneL = (182, 176, 162)

flameO = (216, 98, 32)
flame = (250, 168, 50)
flameC = (255, 234, 148)
ember = (255, 250, 210)

gold = (220, 180, 80)
goldD = (168, 130, 52)

smoke = (162, 160, 156)
smokeL = (206, 204, 200)


# ------------------------------------------------------------------ helpers
def flame_up(buf, cx, base, w=2, h=4, lean=0):
    """Llama: base en `base`, punta hacia arriba (`base - h`)."""
    for i in range(h):
        y = base - i
        half = w - (i * w) // (h + 1)
        off = (lean * i) // h
        rect(buf, cx - half + off, y, cx + half + off, y, flameO)
    for i in range(h - 1):
        y = base - 1 - i
        half = w - 1 - (i * (w - 1)) // (h + 1)
        off = (lean * (i + 1)) // h
        rect(buf, cx - half + off, y, cx + half + off, y, flame)
    setpx(buf, cx, base - 1, flameC)
    setpx(buf, cx, base - 2, flameC)
    setpx(buf, cx + 1, base - 2, flameC)


def exhaust(buf, cx, top, h, w, lean=0):
    """Chorro de cohete: sale de `top` hacia abajo."""
    for i in range(h):
        y = top + i
        half = w - (i * (w - 1)) // max(1, h - 1)
        off = (lean * i) // max(1, h)
        rect(buf, cx - half + off, y, cx + half + off, y, flameO)
    for i in range(h - 1):
        y = top + 1 + i
        half = max(0, w - 1 - (i * (w - 1)) // max(1, h - 1))
        off = (lean * (i + 1)) // max(1, h)
        rect(buf, cx - half + off, y, cx + half + off, y, flame)
    setpx(buf, cx, top, flameC)
    setpx(buf, cx, top + 1, flameC)
    setpx(buf, cx + 1, top + 1, flameC)


def torch(buf, hand, tip, h=4):
    """Antorcha: palo en diagonal de la mano a la punta y llama arriba."""
    line(buf, hand[0], hand[1], tip[0], tip[1], wood)
    line(buf, hand[0] + 1, hand[1], tip[0] + 1, tip[1], woodD)
    rect(buf, tip[0] - 1, tip[1], tip[0] + 2, tip[1] + 1, woodDD)   # atado
    setpx(buf, tip[0] - 1, tip[1], goldD)
    setpx(buf, tip[0] + 2, tip[1], goldD)
    flame_up(buf, tip[0], tip[1] - 1, w=2, h=h,
             lean=-1 if tip[0] < hand[0] else 1)


def lantern(buf, x, y, hook=None):
    """Farol de mano de 4 x 8 (x, y = marco de arriba)."""
    rect(buf, x, y, x + 3, y + 7, dark)
    rect(buf, x + 1, y + 2, x + 2, y + 5, flame)
    setpx(buf, x + 1, y + 3, flameC)
    setpx(buf, x + 2, y + 4, flameC)
    hline(buf, x, x + 3, y, goldD)
    hline(buf, x, x + 3, y + 7, goldD)
    vline(buf, x, y, y + 7, gold)
    vline(buf, x + 3, y, y + 7, gold)
    for (dx, dy) in ((-1, 3), (4, 3), (1, 8), (2, 8), (-1, 5), (4, 5)):
        setpx(buf, x + dx, y + dy, (252, 226, 160))
    if hook:
        line(buf, hook[0], hook[1], x + 2, y, goldD)


# ------------------------------------------------------------------- caballo
def draw_horse(buf, dy=0, gait=0, dust=None):
    """Caballo 3/4 mirando a la derecha. dy = bob del cuerpo, gait = paso."""
    # cola
    rect(buf, 11, 21 + dy, 12, 27 + dy, mane)
    rect(buf, 12, 28 + dy, 13, 30 + dy, horseDD)
    setpx(buf, 10, 24 + dy, mane)
    setpx(buf, 13, 31 + dy, horseDD)
    # barril, anca y pecho
    ellipse(buf, 22, 25 + dy, 8, 4, horse)
    ellipse(buf, 17, 24 + dy, 4, 4, horse)
    ellipse(buf, 28, 24 + dy, 4, 4, horse)
    hline(buf, 16, 31, 28 + dy, horseD)
    hline(buf, 18, 30, 29 + dy, horseD)
    setpx(buf, 15, 23 + dy, horseD)
    setpx(buf, 29, 22 + dy, horseD)
    # cuello
    for i in range(7):
        y = 22 + dy - i
        x0 = 27 + (i + 1) // 2
        rect(buf, x0, y, x0 + 4, y, horse)
        setpx(buf, x0, y, mane)
        setpx(buf, x0 + 1, y, horseD)
    # cabeza (baja, de caballo que va al trote)
    rect(buf, 30, 13 + dy, 37, 19 + dy, horse)
    rect(buf, 36, 15 + dy, 41, 18 + dy, horse)
    rect(buf, 38, 16 + dy, 41, 18 + dy, muzzle)
    hline(buf, 30, 33, 13 + dy, horseD)
    setpx(buf, 34, 15 + dy, ink)          # ojo
    setpx(buf, 40, 17 + dy, ink)          # ollar
    setpx(buf, 37, 19 + dy, horseD)       # quijada
    setpx(buf, 31, 18 + dy, horseD)       # mejilla
    # orejas
    rect(buf, 32, 10 + dy, 33, 13 + dy, horseD)
    rect(buf, 35, 9 + dy, 36, 13 + dy, horseD)
    setpx(buf, 32, 10 + dy, mane)
    setpx(buf, 35, 9 + dy, mane)
    setpx(buf, 31, 11 + dy, mane)         # copete
    setpx(buf, 31, 12 + dy, mane)
    # patas: dos tiempos de paso
    tras = -1 if gait else 1
    delan = 1 if gait else -1
    lift = -1 if gait else 0
    for x, dx, up in ((17, tras, 0), (21, -tras, lift),
                      (26, delan, lift), (30, -delan, 0)):
        y_end = 34 + up
        rect(buf, x + dx, 27 + dy, x + 1 + dx, y_end,
             horseD if x < 24 else horse)
        rect(buf, x + dx, y_end + 1, x + 1 + dx, y_end + 2, hoof)
    # polvo de los cascos
    if dust is not None:
        for (x, y) in dust:
            setpx(buf, x, y, clothD)


def rider(buf, dy=0, left="rest", right="rest"):
    """Jinete con tunica azul (color jugador) y yelmo de hierro."""
    # montura
    rect(buf, 17, 19 + dy, 27, 20 + dy, leather)
    hline(buf, 17, 27, 20 + dy, leatherD)
    setpx(buf, 26, 19 + dy, gold)
    # muslo, quijote y bota del lado visible
    rect(buf, 18, 16 + dy, 20, 19 + dy, blueD)
    rect(buf, 16, 19 + dy, 19, 22 + dy, leatherD)
    rect(buf, 17, 23 + dy, 19, 26 + dy, leatherD)
    hline(buf, 17, 19, 26 + dy, hoof)
    # torso
    rect(buf, 19, 10 + dy, 27, 18 + dy, blue)
    hline(buf, 19, 27, 10 + dy, blueL)
    vline(buf, 19, 10 + dy, 18 + dy, blueD)
    vline(buf, 27, 10 + dy, 18 + dy, blueD)
    rect(buf, 19, 17 + dy, 27, 18 + dy, (58, 42, 24))    # cinturon
    setpx(buf, 23, 17 + dy, gold)
    # cabeza
    rect(buf, 20, 3 + dy, 26, 9 + dy, skin)
    hline(buf, 20, 26, 9 + dy, skinD)
    setpx(buf, 20, 4 + dy, shine)
    setpx(buf, 22, 6 + dy, ink)
    setpx(buf, 24, 6 + dy, ink)
    setpx(buf, 23, 8 + dy, skinD)
    # yelmo con nasal
    rect(buf, 19, 2 + dy, 27, 3 + dy, iron)
    hline(buf, 19, 27, 2 + dy, ironL)
    hline(buf, 18, 28, 4 + dy, ironD)
    rect(buf, 23, 4 + dy, 23, 5 + dy, ironD)
    # brazos
    for side, pose in (("left", left), ("right", right)):
        if pose == "rest":
            if side == "left":
                rect(buf, 16, 11 + dy, 19, 13 + dy, blue)
                rect(buf, 14, 13 + dy, 17, 15 + dy, skin)
            else:
                rect(buf, 27, 11 + dy, 30, 13 + dy, blue)
                rect(buf, 29, 13 + dy, 32, 15 + dy, skin)
        elif pose == "out":
            if side == "left":
                rect(buf, 16, 12 + dy, 19, 14 + dy, blue)
                rect(buf, 14, 13 + dy, 16, 15 + dy, skin)
            else:
                rect(buf, 27, 11 + dy, 30, 13 + dy, blue)
                rect(buf, 30, 12 + dy, 32, 14 + dy, skin)
        elif pose == "up":
            if side == "left":
                rect(buf, 16, 9 + dy, 19, 11 + dy, blue)
                rect(buf, 14, 9 + dy, 16, 11 + dy, skin)
            else:
                rect(buf, 27, 9 + dy, 30, 11 + dy, blue)
                rect(buf, 29, 8 + dy, 31, 10 + dy, skin)


# ------------------------------------------------------------------ 1. read
def scene_read(pose):
    """Scout a caballo con antorcha: pose 1 antorcha izq, pose 2 antorcha der."""
    buf = canvas()
    dy = 0 if pose == 1 else -1
    gait = 0 if pose == 1 else 1
    draw_horse(buf, dy, gait)
    if pose == 1:
        rider(buf, dy, left="out", right="rest")
        torch(buf, (15, 14 + dy), (9, 8 + dy))
    else:
        rider(buf, dy, left="rest", right="up")
        torch(buf, (30, 9 + dy), (39, 6 + dy), h=3)
    return buf


# --------------------------------------------------------------- 2. explore
def scene_explore(pose):
    """Caballeria con farol: dos pasos del mismo loop."""
    buf = canvas()
    dy = 0 if pose == 1 else -1
    gait = 0 if pose == 1 else 1
    dust = [(12, 36), (13, 37), (11, 37)] if pose == 1 else [(9, 36), (8, 37), (10, 37)]
    draw_horse(buf, dy, gait, dust=dust)
    if pose == 1:
        rider(buf, dy, left="out", right="rest")
        lantern(buf, 5, 16 + dy, hook=(14, 14 + dy))
    else:
        rider(buf, dy, left="up", right="rest")
        lantern(buf, 4, 11 + dy, hook=(15, 9 + dy))
    # huellas del paso anterior
    for (x, y) in ((5, 38), (6, 38)) if pose == 1 else ((3, 38), (4, 38)):
        setpx(buf, x, y, clothD)
    return buf


# ----------------------------------------------------------------- 3. build
def scene_build(pose):
    """Herrero soldando la abrazadera del ariete: chispa prendida / apagada."""
    buf = canvas()
    spark = pose == 1

    # ---- tacon, yunque ----
    rect(buf, 31, 35, 38, 37, woodD)
    hline(buf, 31, 38, 35, wood)
    setpx(buf, 33, 36, woodDD)
    setpx(buf, 36, 37, woodDD)
    rect(buf, 30, 33, 39, 34, ironD)
    rect(buf, 32, 31, 37, 32, ironD)
    rect(buf, 30, 29, 40, 30, iron)
    hline(buf, 30, 40, 29, ironL)
    rect(buf, 40, 29, 42, 29, ironD)          # cuerno
    setpx(buf, 43, 29, ironD)

    # ---- viga del ariete apoyada en el yunque ----
    rect(buf, 24, 25, 44, 28, woodDD)
    rect(buf, 24, 25, 44, 27, wood)
    hline(buf, 24, 44, 25, woodL)
    hline(buf, 24, 44, 27, woodD)
    for x in (28, 32, 40, 43):
        vline(buf, x, 26, 26, woodD)
    # abrazadera metalica: foco del soldador
    rect(buf, 33, 25, 36, 28, flame if spark else iron)
    hline(buf, 33, 36, 25, ember if spark else ironL)
    hline(buf, 33, 36, 28, ironD)
    setpx(buf, 33, 26, ironD)
    setpx(buf, 36, 27, ironD)
    if spark:
        setpx(buf, 34, 26, flameC)
        setpx(buf, 35, 27, flameC)

    # ---- herrero ----
    # botas y piernas
    rect(buf, 12, 35, 15, 37, leatherD)
    rect(buf, 18, 35, 21, 37, leatherD)
    hline(buf, 12, 15, 37, hoof)
    hline(buf, 18, 21, 37, hoof)
    rect(buf, 13, 31, 15, 34, (74, 56, 32))
    rect(buf, 18, 31, 20, 34, (74, 56, 32))
    # camisa, brazo lejano y delantal de cuero
    rect(buf, 12, 16, 22, 30, linen)
    hline(buf, 12, 22, 16, (196, 172, 134))
    rect(buf, 10, 18, 12, 23, linenD)
    rect(buf, 9, 23, 12, 25, skinD)
    rect(buf, 11, 20, 21, 30, leather)
    rect(buf, 12, 21, 20, 29, (128, 92, 54))
    rect(buf, 11, 28, 21, 30, leatherD)
    vline(buf, 14, 17, 19, leatherD)          # tirantes
    vline(buf, 19, 17, 19, leatherD)
    setpx(buf, 16, 24, leatherD)
    setpx(buf, 16, 26, leatherD)
    # cabeza girada al yunque
    rect(buf, 14, 9, 21, 16, skin)
    hline(buf, 14, 21, 9, (208, 152, 114))
    setpx(buf, 14, 12, skinD)
    setpx(buf, 21, 13, skinD)
    setpx(buf, 19, 15, skinD)
    hline(buf, 17, 20, 15, skinD)
    rect(buf, 13, 7, 22, 9, dark)
    hline(buf, 14, 21, 7, (62, 46, 26))
    # antiparras de soldador
    rect(buf, 18, 11, 21, 13, ironD)
    hline(buf, 14, 22, 11, ironD)
    setpx(buf, 18, 12, flameC if spark else lens)
    setpx(buf, 21, 12, flameC if spark else lens)
    setpx(buf, 19, 12, iron)
    setpx(buf, 20, 12, iron)
    # brazo que trabaja, hacia la abrazadera
    rect(buf, 21, 17, 25, 20, linen)
    rect(buf, 25, 19, 29, 22, linen)
    rect(buf, 29, 21, 32, 24, leatherD)
    setpx(buf, 29, 21, leather)

    # ---- varilla y chispas ----
    if spark:
        line(buf, 31, 23, 35, 25, ironL)
        setpx(buf, 35, 25, ember)
        for (x, y) in ((33, 21), (36, 20), (38, 22), (39, 24), (40, 26),
                       (32, 23), (37, 17), (31, 20), (35, 16)):
            setpx(buf, x, y, flameC)
        for (x, y) in ((34, 22), (37, 23), (30, 22), (39, 26), (36, 18),
                       (38, 19)):
            setpx(buf, x, y, flame)
        for (x, y) in ((31, 17), (39, 20), (41, 23), (33, 27), (40, 16)):
            setpx(buf, x, y, flameO)
    else:
        line(buf, 31, 22, 34, 24, ironD)
        for (x, y) in ((35, 22), (34, 21), (36, 19), (35, 17), (37, 16)):
            setpx(buf, x, y, smoke if x % 2 else smokeL)
    return buf


# ------------------------------------------------------------------ 4. tool
def tool_wheel(buf, cx, cy, phase):
    """Rueda de 7 px con cuatro rayos que giran con la fase."""
    disc(buf, cx, cy, 3, woodDD)
    disc(buf, cx, cy, 2, wood)
    setpx(buf, cx, cy, ironD)
    spokes = {
        0: ((2, 1), (-2, -1), (1, -2), (-1, 2)),
        1: ((2, 0), (-2, 0), (0, 2), (0, -2)),
        2: ((1, 2), (-1, -2), (-2, 1), (2, -1)),
    }[phase]
    for (dx, dy) in spokes:
        line(buf, cx, cy, cx + dx, cy + dy, woodD)


def tool_villager(buf, phase):
    """Aldeano empujando el tronco del ariete desde atras."""
    step = 1 if phase % 2 else 0
    # botas y piernas
    rect(buf, 1, 35, 4, 36, (60, 40, 20))
    rect(buf, 5, 35, 8, 36, (60, 40, 20))
    rect(buf, 2 - step, 32, 4 - step, 34, (74, 56, 32))
    rect(buf, 5 + step, 32, 7 + step, 34, (74, 56, 32))
    # tunica
    rect(buf, 1, 23, 8, 31, (122, 90, 46))
    hline(buf, 1, 8, 23, (94, 68, 32))
    hline(buf, 1, 8, 29, (80, 55, 25))
    setpx(buf, 4, 29, (60, 40, 20))
    # cabeza y sombrero de paja
    rect(buf, 2, 17, 7, 22, skin)
    setpx(buf, 2, 19, skinD)
    setpx(buf, 6, 19, ink)
    setpx(buf, 3, 21, skinD)
    rect(buf, 2, 13, 8, 14, (138, 106, 59))     # copa del sombrero
    hline(buf, 2, 8, 13, (162, 128, 74))
    rect(buf, 1, 15, 9, 16, (107, 79, 38))      # ala
    setpx(buf, 2, 16, (138, 106, 59))
    setpx(buf, 1, 15, (138, 106, 59))


def scene_tool(pose):
    """Ariete de asalto empujado: pose 1 atras, 2 medio, 3 adelante."""
    buf = canvas()
    push = (0, 2, 4)[pose - 1]

    # ---- ruedas y eje ----
    tool_wheel(buf, 21, 33, (0, 1, 2)[pose - 1])
    tool_wheel(buf, 31, 33, (1, 2, 0)[pose - 1])
    rect(buf, 15, 28, 34, 28, woodDD)

    # ---- caja del ariete ----
    rect(buf, 14, 16, 36, 27, woodDD)
    rect(buf, 15, 17, 35, 26, woodD)
    for x in (19, 25, 31):
        vline(buf, x, 17, 26, woodDD)
    hline(buf, 15, 35, 17, (124, 92, 52))
    # techo a dos aguas
    for i in range(8):
        y = 8 + i
        half = 1 + (i * 11) // 7
        rect(buf, 25 - half, y, 25 + half, y, wood)
        setpx(buf, 25 - half, y, woodD)
        setpx(buf, 25 - half + 1, y, woodL)
        setpx(buf, 25 + half, y, woodD)
    hline(buf, 13, 37, 15, woodL)
    rect(buf, 15, 16, 16, 27, woodDD)          # poste trasero
    rect(buf, 34, 16, 35, 27, woodDD)          # poste delantero
    setpx(buf, 25, 7, goldD)

    # ---- tronco del ariete (lo mas claro del cuadro) ----
    tip = 37 + push
    rect(buf, 9, 19, tip, 25, woodDD)
    rect(buf, 9, 20, tip, 24, wood)
    hline(buf, 10, tip, 20, woodL)
    hline(buf, 10, tip, 23, woodD)
    hline(buf, 10, tip, 24, woodD)
    for x in (13, 19, 25, 31):
        if x < tip:
            vline(buf, x, 21, 22, woodD)
    # fleje de hierro en la mitad del tronco
    rect(buf, 28, 19, 29, 25, ironD)
    setpx(buf, 28, 20, iron)
    # cuerdas que lo atan a la caja
    for x in (17, 33):
        vline(buf, x, 19, 25, leatherD)
        setpx(buf, x, 20, leather)
    setpx(buf, 9, 21, leatherD)
    setpx(buf, 9, 23, leatherD)
    # punta de hierro
    rect(buf, tip - 1, 18, tip + 1, 26, ironD)
    rect(buf, tip, 19, tip + 1, 25, iron)
    hline(buf, tip - 1, tip + 1, 18, ironL)
    setpx(buf, tip - 1, 19, ironD)
    setpx(buf, tip - 1, 25, ironD)
    setpx(buf, tip + 1, 22, ironL)

    # ---- aldeano empujando ----
    tool_villager(buf, pose - 1)
    rect(buf, 7, 21, 9, 23, skin)              # manos contra el tronco
    setpx(buf, 7, 21, skinD)

    # ---- impacto ----
    if push:
        for (dx, dy) in ((2, -1), (3, 1), (3, 4), (4, 2), (1, 3)):
            setpx(buf, tip + dx, 22 + dy, clothD)
    if push >= 4:
        for (dx, dy) in ((4, -2), (4, 0), (4, 5), (2, -2), (3, 6)):
            setpx(buf, tip + dx, 22 + dy, smokeL)
        for (dx, dy) in ((3, -3), (4, -3), (4, 3), (3, 4)):
            setpx(buf, tip + dx, 22 + dy, flame)
    return buf


# ------------------------------------------------------------------ 5. jira
def castle(buf):
    """Muralla almenada con dos torres: la plataforma de lanzamiento."""
    # muralla
    rect(buf, 3, 34, 44, 38, stone)
    hline(buf, 3, 44, 34, stoneL)
    rect(buf, 3, 37, 44, 38, stoneD)
    for x in range(13, 38, 5):
        vline(buf, x, 35, 36, stoneD)
    hline(buf, 3, 44, 36, stoneD)
    for x in (11, 32):
        rect(buf, x, 32, x + 3, 33, stone)
        hline(buf, x, x + 3, 32, stoneL)
        setpx(buf, x + 3, 33, stoneD)
    # torres de los costados
    for x0, x1 in ((1, 9), (38, 46)):
        rect(buf, x0, 26, x1, 38, stone)
        vline(buf, x0, 26, 38, stoneD)
        vline(buf, x1, 26, 38, stoneD)
        hline(buf, x0, x1, 26, stoneL)
        hline(buf, x0, x1, 31, stoneD)
        for x in range(x0, x1, 4):
            rect(buf, x, 23, x + 2, 25, stone)
            hline(buf, x, x + 2, 23, stoneL)
    setpx(buf, 21, 35, stoneL)
    setpx(buf, 34, 37, stoneL)


def scene_jira(pose):
    """Cohete de madera despegando del castillo: 1 despegando, 2 en el aire."""
    buf = canvas()
    castle(buf)
    up = 0 if pose == 1 else 3
    base = 30 - up

    # ---- aletas (chicas y en punta) ----
    for i in range(5):
        y = 26 + up + i
        rect(buf, 18 - i, y, 21 - i, y, woodD)
        rect(buf, 27 + i, y, 30 + i, y, woodD)
        setpx(buf, 18 - i, y, woodL)
        setpx(buf, 30 + i, y, woodL)
    # ---- cuerpo (duelas) ----
    rect(buf, 19, 12 + up, 29, base, woodDD)
    rect(buf, 20, 12 + up, 28, base - 1, wood)
    vline(buf, 20, 13 + up, base - 1, woodL)
    vline(buf, 22, 13 + up, base - 1, woodD)
    vline(buf, 25, 13 + up, base - 1, woodD)
    vline(buf, 28, 13 + up, base - 1, woodD)
    # ---- punta conica ----
    for i in range(6):
        y = 11 + up - i
        half = 5 - i
        rect(buf, 24 - half, y, 24 + half, y, wood)
        setpx(buf, 24 - half, y, woodL)
        setpx(buf, 24 + half, y, woodD)
    setpx(buf, 24, 5 + up, woodD)
    setpx(buf, 24, 4 + up, woodL)            # regaton de madera
    hline(buf, 19, 29, 11 + up, woodL)
    # ---- flejes de hierro ----
    for y in (14, 21):
        hline(buf, 19, 29, y + up, ironD)
        hline(buf, 19, 29, y + 1 + up, iron)
        setpx(buf, 20, y + up, ironL)
    hline(buf, 19, 29, base - 1, ironD)
    # ---- portilla ----
    disc(buf, 24, 18 + up, 2, goldD)
    disc(buf, 24, 18 + up, 1, (48, 58, 74))
    setpx(buf, 23, 17 + up, (150, 186, 214))
    # ---- escape ----
    if pose == 1:
        exhaust(buf, 24, base + 1, 5, 3)
        for (x, y) in ((20, 32), (28, 32), (12, 28), (36, 28)):
            setpx(buf, x, y, smoke)
        for (x, y) in ((19, 33), (29, 33)):
            setpx(buf, x, y, smokeL)
    else:
        exhaust(buf, 24, base + 1, 9, 4)
        for (x, y) in ((20, 29), (28, 29), (16, 31), (32, 31), (12, 34),
                       (36, 34), (21, 33), (27, 34)):
            setpx(buf, x, y, smoke)
        for (x, y) in ((19, 30), (29, 30), (15, 33), (34, 33), (11, 32)):
            setpx(buf, x, y, smokeL)
    return buf


# ------------------------------------------------------------------- salida
BASE = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "emotes", "aoe"))

JOBS = [
    ("read", "read_01.png", scene_read, 1),
    ("read", "read_02.png", scene_read, 2),
    ("explore", "explore_01.png", scene_explore, 1),
    ("explore", "explore_02.png", scene_explore, 2),
    ("build", "build_01.png", scene_build, 1),
    ("build", "build_02.png", scene_build, 2),
    ("tool", "tool_01.png", scene_tool, 1),
    ("tool", "tool_02.png", scene_tool, 2),
    ("tool", "tool_03.png", scene_tool, 3),
    ("jira", "jira_01.png", scene_jira, 1),
    ("jira", "jira_02.png", scene_jira, 2),
]


def main():
    for state, name, draw, pose in JOBS:
        directory = os.path.join(BASE, state)
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, name)
        with open(path, "wb") as fh:
            fh.write(encode_png(W, H, draw(pose)))
        print("ok", os.path.join("emotes", "aoe", state, name))


if __name__ == "__main__":
    main()
