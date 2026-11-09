#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set LEAGUE OF LEGENDS del fork gentle-emote-arcade (24 estados, 48x40 RGBA).

Estilo pixel art de Runeterra: silueta primero, contorno de 1 px y paleta
teal/navy con oro hextech, violeta magico, verde toxico y piel. Un mismo
campeon por arquetipo, objetos iconicos para el resto. El "reparto" respeta
el mapa de escenas:

  Mago encapuchado (capucha violeta, orbe, ribete dorado)
      think ..... 01 mano en la barbilla y orbe en la palma, 02 cabeza ladeada
      read ...... 01 tomo abierto, 02 pasa la pagina encendida
      write ..... 01 pluma escribiendo runas, 02 pluma alzada y runa nueva
      review .... 01 pergamino con marcas rojas, 02 sello verde estampado
      judge ..... 01 mazo arriba, 02 mazazo con onda de choque
      compact ... 01 entero con aura, 02 achicado y flechas de compresion
      remember .. 01 cristal al pecho, 02 cristal flotando con anillos

  Bruto armado (peto navy, hombreras doradas, espadon)
      hi ........ 01 saludo con la mano y espada al costado, 02 espada en alto
      success ... 01 punos arriba, 02 salto con espada arriba
      delegate .. 01 senala a la izquierda, 02 a la derecha (yordles chiquitos)
      bye ....... 01 saluda de frente, 02 se da vuelta y se va (espada al hombro)
      yolo ...... 01 carga con la espada adelante, 02 tajo bajo + lineas
      super-yolo  01 sol arriba a la derecha, 02 salto con estela toxica

  Tirador arquero (capucha teal, arco, carcaj)
      explore ... 01 arco bajo y ward rosa, 02 arco alto + pulso de vision
      verify .... 01 tilde verde en la mano, 02 sello grande estampado
      ask ....... 01 globo "?" arriba a la derecha, 02 globo a la izquierda
      jobs ...... 01 pocion al pecho con barra a 40%, 02 pocion alzada y 100%

  Yordle (sombreron enorme, cabeza grande, cuerpo chiquito)
      idle ...... idle.png + idle_blink.png (parpadeo)
      talk ...... 4 bocas (close / small / mid / wide) sobre la misma cara
      grandma ... 01 agujas arriba tejiendo, 02 agujas abajo y ovillo grande

  Objetos y props
      tool ...... 01 espadas cruzadas, 02 choque con chispas
      build ..... 01 torreta hextech cargando, 02 dispara el rayo
      jira ...... 01 Nexus de cristal cargando, 02 nexus encendido con rayos
      failure ... 01 campeon caido + espada clavada + polvo, 02 de rodillas

Solo stdlib: struct + zlib + math (PNG escrito a mano, sin PIL, sin red).
Escribe unicamente en emotes/lol/ y es idempotente: dos corridas dan los
mismos bytes.

    python3 gentle-emote-arcade/scripts/sprites/gen_lol.py
"""
import math
import os
import struct
import sys
import zlib

W, H = 48, 40
BASE = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "emotes", "lol"))

# ------------------------------------------------------------------- paleta
INK = (16, 20, 24)            # #101418 contorno
NAVY = (10, 50, 60)           # #0A323C peto / armadura
NAVY_L = (24, 74, 86)
NAVY_D = (6, 32, 40)
TEAL = (30, 91, 102)          # #1E5B66 placas y ropa
TEAL_L = (66, 138, 152)
TEAL_D = (14, 62, 70)
GOLD = (200, 170, 110)        # #C8AA6E hextech
GOLD_L = (238, 210, 156)
GOLD_D = (138, 110, 58)       # #8A6E3A
GOLD_DD = (96, 76, 40)
VIO = (107, 78, 155)          # #6B4E9B magia
VIO_L = (177, 143, 224)       # #B18FE0
VIO_LL = (216, 194, 246)
VIO_D = (66, 46, 100)
VIO_DD = (40, 28, 62)
SKIN = (232, 185, 138)        # #E8B98A
SKIN_L = (250, 216, 178)
SKIN_D = (196, 146, 104)
SKIN_DD = (160, 112, 80)
TOX = (127, 191, 63)          # #7FBF3F
TOX_L = (176, 224, 110)
TOX_D = (74, 128, 36)
WHITE = (246, 248, 244)
STEEL = (158, 170, 180)
STEEL_L = (212, 222, 230)
STEEL_D = (98, 110, 122)
STEEL_DD = (62, 72, 82)
WOOD = (150, 110, 64)
WOOD_L = (188, 144, 90)
WOOD_D = (110, 80, 44)
HAIR = (48, 38, 36)
HAIR_L = (74, 58, 52)
DUST = (146, 138, 126)
DUST_L = (196, 188, 174)
RED = (196, 66, 62)
RED_L = (232, 112, 104)
RED_D = (140, 42, 44)
PINK = (232, 120, 176)
PINK_L = (252, 182, 218)
PINK_D = (166, 62, 112)
PAPER = (238, 230, 206)
PAPER_D = (204, 194, 164)
PAPER_L = (250, 246, 228)
MOUTH = (122, 62, 58)
MOUTH_D = (86, 40, 44)
MOUTH_I = (196, 96, 92)
TEETH = (240, 238, 226)
EYE_D = (28, 36, 44)



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


def box(buf, x0, y0, x1, y1, fill, edge=None):
    """Rectangulo con contorno de 1 px (la casa lo usa para todo)."""
    rect(buf, x0, y0, x1, y1, INK if edge is None else edge)
    if x1 - x0 > 1 and y1 - y0 > 1:
        rect(buf, x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill)


def brush(buf, x, y, col, t):
    o = t // 2
    rect(buf, x - o, y - o, x - o + t - 1, y - o + t - 1, col)


def line_brush(buf, x0, y0, x1, y1, col, t):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        brush(buf, x0, y0, col, t)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def stroke(buf, pts, col, t=2):
    """Polilinea con contorno de 1 px: brazos, hoja de la espada, arco."""
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1], b[0], b[1], INK, t + 2)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1], b[0], b[1], col, t)


def line(buf, x0, y0, x1, y1, col):
    line_brush(buf, x0, y0, x1, y1, col, 1)


def circle(buf, cx, cy, r, col):
    for y in range(cy - r, cy + r + 1):
        d = r * r - (y - cy) * (y - cy)
        if d < 0:
            continue
        dx = int(math.sqrt(d))
        hline(buf, cx - dx, cx + dx, y, col)


def disc(buf, cx, cy, r, col):
    circle(buf, cx, cy, r, col)


def ellipse(buf, cx, cy, rx, ry, col):
    for y in range(cy - ry, cy + ry + 1):
        d = 1.0 - ((y - cy) / float(ry)) ** 2
        if d < 0:
            continue
        dx = int(rx * math.sqrt(d))
        hline(buf, cx - dx, cx + dx, y, col)


def ring(buf, cx, cy, r, col, thick=1):
    for y in range(cy - r, cy + r + 1):
        d = r * r - (y - cy) * (y - cy)
        if d < 0:
            continue
        dx = int(math.sqrt(d))
        di = r - thick
        d2 = di * di - (y - cy) * (y - cy)
        if d2 <= 0:
            hline(buf, cx - dx, cx + dx, y, col)
        else:
            dxi = int(math.sqrt(d2))
            hline(buf, cx - dx, cx - dxi - 1, y, col)
            hline(buf, cx + dxi + 1, cx + dx, y, col)


def blit(buf, src, dx=0, dy=0):
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3] and 0 <= x + dx < W and 0 <= y + dy < H:
                j = ((y + dy) * W + (x + dx)) * 4
                buf[j:j + 4] = src[i:i + 4]


def stamp(buf, draw, dx=0, dy=0):
    tmp = canvas()
    draw(tmp)
    blit(buf, tmp, dx, dy)


def flip_h(src):
    dst = canvas()
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3]:
                j = (y * W + (W - 1 - x)) * 4
                dst[j:j + 4] = src[i:i + 4]
    return dst


def bbox(src):
    minx, miny, maxx, maxy = W, H, -1, -1
    for y in range(H):
        for x in range(W):
            if src[(y * W + x) * 4 + 3]:
                minx = min(minx, x)
                maxx = max(maxx, x)
                miny = min(miny, y)
                maxy = max(maxy, y)
    return minx, miny, maxx, maxy


def scale_sprite(src, num, den, ground=38, cx=24):
    """Achica el recorte opaco de src (compact) y lo ancla al piso."""
    minx, miny, maxx, maxy = bbox(src)
    sw = (maxx - minx + 1) * num // den
    sh = (maxy - miny + 1) * num // den
    dst = canvas()
    ox = cx - sw // 2
    oy = ground - sh + 1
    for dy in range(sh):
        sy0 = miny + dy * den // num
        sy1 = max(sy0 + 1, miny + (dy + 1) * den // num)
        for dx in range(sw):
            sx0 = minx + dx * den // num
            sx1 = max(sx0 + 1, minx + (dx + 1) * den // num)
            best = None
            best_a = 0
            for sy in range(sy0, min(sy1, H)):
                for sx in range(sx0, min(sx1, W)):
                    i = (sy * W + sx) * 4
                    if src[i + 3] > best_a:
                        best_a = src[i + 3]
                        best = (src[i], src[i + 1], src[i + 2])
            if best is not None:
                setpx(dst, ox + dx, oy + dy, best)
    return dst


# ---------------------------------------------------------- tipografia 3x5
FONT = {
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#.."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
    "?": [".##.", "#..#", "..#.", "....", "..#."],
    "!": ["#", "#", "#", ".", "#"],
    "A": ["###", "#.#", "###", "#.#", "#.#"],
    "C": ["###", "#..", "#..", "#..", "###"],
    "G": [".##.", "#...", "#.##", "#..#", ".##."],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "J": ["..#", "..#", "..#", "#.#", ".#."],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": [".##", "#..", ".#.", "..#", "##."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "V": ["#.#", "#.#", "#.#", ".#.", ".#."],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["..#", "#.#", "#.#", "###", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "6": ["###", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", "..#", "..#", "..#"],
    "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "###"],
    ":": [".", "#", ".", "#", "."],
    "%": ["#.#", "..#", ".#.", "#..", "#.#"],
}


def text(buf, word, x0, y0, col, scale=1, outline=INK):
    x = x0
    for ch in word:
        g = FONT[ch]
        gw = len(g[0])
        if outline is not None:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                gx = x
                for ry, row in enumerate(g):
                    for i, c in enumerate(row):
                        if c == "#":
                            for sy in range(scale):
                                for sx in range(scale):
                                    setpx(buf, gx + i * scale + sx + dx,
                                          y0 + ry * scale + sy + dy, outline)
        for ry, row in enumerate(g):
            for i, c in enumerate(row):
                if c == "#":
                    for sy in range(scale):
                        for sx in range(scale):
                            setpx(buf, x + i * scale + sx,
                                  y0 + ry * scale + sy, col)
        x += (gw + 1) * scale


# ------------------------------------------------------------------ brillos
def spark(buf, x, y, col=GOLD):
    setpx(buf, x, y, col)
    setpx(buf, x - 1, y, col)
    setpx(buf, x + 1, y, col)
    setpx(buf, x, y - 1, col)
    setpx(buf, x, y + 1, col)


def star4(buf, x, y, col, core=WHITE):
    setpx(buf, x, y, core)
    setpx(buf, x - 1, y, col)
    setpx(buf, x + 1, y, col)
    setpx(buf, x, y - 1, col)
    setpx(buf, x, y + 1, col)


def burst(buf, cx, cy, r, col, core=WHITE):
    for k in range(0, 360, 45):
        rad = math.radians(k)
        line_brush(buf, cx, cy, cx + int(math.cos(rad) * r),
                   cy + int(math.sin(rad) * r), col, 1)
    circle(buf, cx, cy, max(1, r // 3), core)


def dust(buf, cx, cy, r=2):
    cx = min(max(cx, r + 1), W - 2 - r)
    cy = min(max(cy, r + 1), H - 2 - r)
    circle(buf, cx, cy, r, DUST)
    setpx(buf, cx - r, cy + 1, DUST_L)
    setpx(buf, cx + r, cy, DUST_L)
    setpx(buf, cx, cy - r, DUST_L)


def speed(buf, y, x0, x1):
    hline(buf, x0, x1, y, STEEL_D)
    hline(buf, x0, x1, y + 1, STEEL_L)


def rune(buf, cx, cy, col=VIO_L):
    setpx(buf, cx, cy - 2, col)
    setpx(buf, cx - 1, cy - 1, col)
    setpx(buf, cx + 1, cy - 1, col)
    setpx(buf, cx, cy, col)
    setpx(buf, cx, cy + 1, col)
    setpx(buf, cx - 1, cy + 2, col)
    setpx(buf, cx + 1, cy + 2, col)


ARROW = {
    "right": [(0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (1, -1), (1, 0),
              (1, 1), (2, 0)],
    "left": [(2, -2), (2, -1), (2, 0), (2, 1), (2, 2), (1, -1), (1, 0),
             (1, 1), (0, 0)],
    "up": [(-2, 2), (-1, 2), (0, 2), (1, 2), (2, 2), (-1, 1), (0, 1),
           (1, 1), (0, 0)],
    "down": [(-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (-1, 1), (0, 1),
             (1, 1), (0, 2)],
}


def arrow(buf, x, y, d, col=VIO_L):
    """Flecha de compresion (compact) de 5x3 px."""
    for (px, py) in ARROW[d]:
        setpx(buf, x + px, y + py, col)
    setpx(buf, x, y, VIO_LL)


def check(buf, x, y, size=1, col=TOX, edge=TOX_D):
    pts = [(0, 1), (0, 2), (1, 3), (2, 2), (3, 1), (4, 0)]
    for (px, py) in pts:
        for s in range(size):
            for t in range(size):
                setpx(buf, x + px * size + s, y + py * size + t, col)
    setpx(buf, x + 4 * size - 1, y, edge)


# ------------------------------------------------------------------ cuerpo
# Anclas del brazo derecho (lado pantalla derecha). El izquierdo se espeja.
ARMS = {
    "down":   [(30, 19), (32, 23), (31, 27)],
    "rest":   [(30, 19), (33, 23), (33, 27)],
    "out":    [(30, 19), (34, 22), (37, 23)],
    "out_up": [(30, 19), (34, 19), (38, 16)],
    "up":     [(30, 19), (33, 15), (34, 11)],
    "up_hi":  [(30, 19), (33, 14), (35, 8)],
    "sword":  [(30, 19), (33, 16), (34, 14)],
    "chin":   [(30, 19), (31, 16), (27, 16)],
    "chest":  [(30, 19), (29, 23), (25, 24)],
    "hold":   [(30, 19), (30, 23), (27, 26)],
    "point":  [(30, 19), (26, 21), (22, 21)],
    "fwd":    [(30, 19), (33, 22), (35, 24)],
    "swing":  [(30, 19), (33, 23), (35, 26)],
    "stamp":  [(30, 19), (34, 21), (37, 24)],
    "pen":    [(30, 19), (33, 21), (36, 19)],
    "bow":    [(30, 19), (33, 22), (37, 24)],
    "bow_hi": [(30, 19), (33, 20), (37, 19)],
    "low":    [(30, 19), (31, 23), (30, 27)],
}


def arm_pts(side, mode):
    pts = ARMS[mode]
    if side < 0:
        return [(W - 1 - x, y) for (x, y) in pts]
    return list(pts)


def arm(buf, side, mode, col, cuff, hand, t=3, edge=None):
    pts = arm_pts(side, mode)
    stroke(buf, pts, col, t)
    if edge:
        for a, b in zip(pts, pts[1:]):
            line_brush(buf, a[0], a[1] - 1, b[0], b[1] - 1, edge, 1)
    cuffs = [(a[0], a[1]) for a in pts[-2:-1]]
    for (x, y) in cuffs:
        box(buf, x - 1, y - 1, x + 1, y + 1, cuff)
    hx, hy = pts[-1]
    box(buf, hx - 2, hy - 2, hx + 2, hy + 2, hand)
    hline(buf, hx - 1, hx + 1, hy - 2, GOLD_L if hand == GOLD_D else hand)
    return (hx, hy)


# --------------------------------------------------------- bruto (Garen-like)
def bruiser_legs(buf, mode="stand"):
    if mode == "step1":
        spans = [(14, 19, 35), (26, 31, 35)]
        boots = [(12, 36, 20, 38), (25, 36, 32, 37)]
    elif mode == "step2":
        spans = [(16, 21, 35), (28, 33, 35)]
        boots = [(15, 36, 22, 37), (27, 36, 35, 38)]
    else:
        spans = [(17, 22, 35), (25, 30, 35)]
        boots = [(16, 36, 23, 38), (24, 36, 31, 38)]
    for (x0, x1, y1) in spans:
        box(buf, x0, 29, x1, y1, NAVY)
        hline(buf, x0 + 1, x1 - 1, 30, TEAL)
        vline(buf, x1 - 1, 31, y1 - 1, NAVY_D)
    for (x0, y0, x1, y1) in boots:
        box(buf, x0, y0, x1, y1, GOLD_D)
        hline(buf, x0 + 1, x1 - 1, y0 + 1, GOLD)
        hline(buf, x0 + 1, x1 - 1, y1 - 1, INK)
        setpx(buf, x0 + 1, y0 + 1, GOLD_L)


def bruiser_torso(buf, back=False):
    box(buf, 16, 16, 31, 28, NAVY)
    if back:
        rect(buf, 18, 18, 29, 25, NAVY_L)
        vline(buf, 23, 18, 24, NAVY)
        vline(buf, 24, 18, 24, NAVY)
        hline(buf, 18, 29, 18, TEAL)
    else:
        rect(buf, 19, 18, 28, 24, TEAL)
        hline(buf, 19, 28, 18, TEAL_L)
        vline(buf, 19, 18, 24, TEAL_L)
        vline(buf, 28, 18, 24, TEAL_D)
        hline(buf, 20, 27, 24, TEAL_D)
        # gema toxica del pecho
        rect(buf, 23, 20, 24, 21, TOX)
        setpx(buf, 23, 20, TOX_L)
        setpx(buf, 24, 21, TOX_D)
    hline(buf, 17, 30, 17, GOLD)
    rect(buf, 17, 26, 30, 27, GOLD_D)
    hline(buf, 17, 30, 26, GOLD)
    rect(buf, 23, 26, 24, 27, TEAL)
    setpx(buf, 23, 26, TEAL_L)


def pauldron(buf, x0):
    box(buf, x0, 15, x0 + 6, 21, GOLD)
    hline(buf, x0 + 1, x0 + 5, 16, GOLD_L)
    vline(buf, x0 + 1, 16, 19, GOLD_L)
    hline(buf, x0 + 1, x0 + 5, 20, GOLD_D)
    vline(buf, x0 + 5, 16, 20, GOLD_D)
    setpx(buf, x0 + 3, 18, TEAL)
    setpx(buf, x0 + 3, 17, TEAL_L)
    setpx(buf, x0 + 2, 19, NAVY_D)


def bruiser_head(buf, look="fwd", mouth="line", back=False):
    if back:
        box(buf, 19, 3, 28, 15, HAIR)
        rect(buf, 20, 4, 27, 12, HAIR)
        hline(buf, 20, 27, 4, HAIR_L)
        vline(buf, 20, 5, 12, HAIR_L)
        vline(buf, 27, 5, 12, (32, 26, 26))
        vline(buf, 23, 7, 11, (38, 30, 28))
        vline(buf, 24, 8, 10, (38, 30, 28))
        hline(buf, 21, 26, 12, (38, 30, 28))
        hline(buf, 20, 27, 6, GOLD)
        setpx(buf, 23, 6, TOX_D)
        rect(buf, 19, 13, 20, 15, SKIN_D)
        rect(buf, 27, 13, 28, 15, SKIN_D)
        setpx(buf, 21, 14, SKIN_D)
        setpx(buf, 26, 14, SKIN_D)
        return
    box(buf, 19, 3, 28, 15, SKIN)
    rect(buf, 20, 4, 27, 5, HAIR)
    hline(buf, 20, 27, 4, HAIR_L)
    rect(buf, 20, 6, 20, 8, HAIR)
    rect(buf, 27, 6, 27, 8, HAIR)
    hline(buf, 20, 27, 6, GOLD)
    setpx(buf, 23, 6, TOX)
    setpx(buf, 24, 6, TOX_D)
    hline(buf, 20, 22, 8, HAIR)
    hline(buf, 25, 27, 8, HAIR)
    for (x0, x1) in ((20, 22), (25, 27)):
        rect(buf, x0, 9, x1, 10, WHITE)
        setpx(buf, x0 + 1, 10, EYE_D)
        setpx(buf, x0 + 1, 9, EYE_D)
    if look == "right":
        for (x0, x1) in ((20, 22), (25, 27)):
            rect(buf, x0, 9, x1, 10, WHITE)
            setpx(buf, x1, 9, EYE_D)
            setpx(buf, x1, 10, EYE_D)
    elif look == "left":
        for (x0, x1) in ((20, 22), (25, 27)):
            rect(buf, x0, 9, x1, 10, WHITE)
            setpx(buf, x0, 9, EYE_D)
            setpx(buf, x0, 10, EYE_D)
    elif look == "up":
        for (x0, x1) in ((20, 22), (25, 27)):
            rect(buf, x0, 9, x1, 10, WHITE)
            setpx(buf, x0 + 1, 9, EYE_D)
            setpx(buf, x1 - 1, 9, EYE_D)
    setpx(buf, 23, 11, SKIN_D)
    setpx(buf, 24, 11, SKIN_D)
    setpx(buf, 23, 12, SKIN_D)
    if mouth == "line":
        hline(buf, 22, 25, 13, MOUTH_D)
    elif mouth == "smile":
        for (x, y) in ((21, 12), (22, 13), (23, 13), (24, 13), (25, 13),
                       (26, 12)):
            setpx(buf, x, y, MOUTH_D)
    elif mouth == "smirk":
        hline(buf, 22, 26, 13, MOUTH_D)
        setpx(buf, 26, 12, MOUTH_D)
    elif mouth == "open":
        rect(buf, 23, 12, 25, 13, MOUTH)
        hline(buf, 23, 25, 12, TEETH)
    elif mouth == "shout":
        rect(buf, 22, 12, 26, 14, MOUTH)
        hline(buf, 23, 25, 12, TEETH)
        setpx(buf, 23, 14, MOUTH_I)
        setpx(buf, 24, 14, MOUTH_I)
    hline(buf, 21, 26, 14, SKIN_D)


def bruiser(buf, arm_l="down", arm_r="down", legs="stand", look="fwd",
            mouth="line", back=False):
    bruiser_legs(buf, legs)
    bruiser_torso(buf, back=back)
    bruiser_head(buf, look=look, mouth=mouth, back=back)
    hl = arm(buf, -1, arm_l, NAVY_L, TEAL_L, GOLD_D, edge=TEAL_L)
    hr = arm(buf, +1, arm_r, NAVY_L, TEAL_L, GOLD_D, edge=TEAL_L)
    pauldron(buf, 12)
    pauldron(buf, 29)
    return {"lh": hl, "rh": hr}


# --------------------------------------------------------- mago encapuchado
HOOD = [(2, 23, 24), (3, 22, 25), (4, 21, 26), (5, 20, 27), (6, 19, 28),
        (7, 18, 29), (8, 18, 29), (9, 17, 30), (10, 17, 30), (11, 17, 30),
        (12, 16, 31), (13, 16, 31), (14, 16, 31), (15, 16, 31), (16, 16, 31)]
ROBE = [(17, 17, 30), (18, 16, 31), (19, 16, 31), (20, 15, 32), (21, 15, 32),
        (22, 15, 32), (23, 14, 33), (24, 14, 33), (25, 14, 33), (26, 13, 34),
        (27, 13, 34), (28, 13, 34), (29, 12, 35), (30, 12, 35), (31, 12, 35),
        (32, 11, 36), (33, 11, 36), (34, 11, 36), (35, 11, 36), (36, 11, 36)]


def mage_robe(buf, aura=False):
    for (y, x0, x1) in ROBE:
        hline(buf, x0, x1, y, INK)
    for (y, x0, x1) in ROBE[1:]:
        if x1 - x0 > 2:
            hline(buf, x0 + 1, x1 - 1, y, VIO)
    for (y, x0, x1) in ROBE[2:]:
        if x1 - x0 > 4:
            setpx(buf, x0 + 1, y, VIO_L)
            setpx(buf, x1 - 1, y, VIO_D)
    # pliegue central y cinto
    vline(buf, 23, 19, 25, VIO_D)
    vline(buf, 24, 19, 25, VIO_D)
    rect(buf, 15, 25, 31, 26, GOLD_D)
    hline(buf, 15, 31, 25, GOLD)
    rect(buf, 22, 25, 25, 26, GOLD)
    setpx(buf, 23, 25, VIO_LL)
    setpx(buf, 24, 26, GOLD_D)
    # ribete dorado del ruedo
    for y in (34, 35):
        for (yy, x0, x1) in ROBE:
            if yy == y:
                hline(buf, x0 + 1, x1 - 1, y, GOLD_D)
    hline(buf, 14, 33, 35, GOLD)
    # botas
    box(buf, 18, 37, 22, 38, VIO_DD)
    box(buf, 25, 37, 29, 38, VIO_DD)
    setpx(buf, 19, 37, VIO_D)
    setpx(buf, 26, 37, VIO_D)
    # broche del pecho
    rect(buf, 22, 18, 25, 20, GOLD_D)
    hline(buf, 22, 25, 18, GOLD)
    setpx(buf, 23, 19, VIO_LL)


def mage_head(buf, look="fwd", tilt=0, trim=True):
    dx = tilt
    for (y, x0, x1) in HOOD:
        hline(buf, x0 + dx, x1 + dx, y, INK)
    for (y, x0, x1) in HOOD[1:]:
        if x1 - x0 > 2:
            hline(buf, x0 + dx + 1, x1 + dx - 1, y, VIO)
    for (y, x0, x1) in HOOD[2:]:
        if x1 - x0 > 4:
            setpx(buf, x0 + dx + 1, y, VIO_L)
            setpx(buf, x1 + dx - 1, y, VIO_D)
    setpx(buf, 24 + dx, 3, VIO_L)
    setpx(buf, 23 + dx, 4, VIO_L)
    # abertura de la cara
    rect(buf, 19 + dx, 9, 28 + dx, 15, INK)
    rect(buf, 20 + dx, 10, 27 + dx, 14, VIO_DD)
    if trim:
        hline(buf, 20 + dx, 27 + dx, 9, GOLD_D)
        vline(buf, 19 + dx, 10, 14, GOLD_D)
        vline(buf, 28 + dx, 10, 14, GOLD_D)
    ey = 12 if look == "down" else 11
    rect(buf, 21 + dx, ey, 22 + dx, ey + 1, VIO_L)
    rect(buf, 25 + dx, ey, 26 + dx, ey + 1, VIO_L)
    setpx(buf, 21 + dx, ey, VIO_LL)
    setpx(buf, 25 + dx, ey, VIO_LL)
    setpx(buf, 23 + dx, 13, VIO_D)
    setpx(buf, 24 + dx, 13, VIO_D)
    hline(buf, 22 + dx, 25 + dx, 14, VIO_D)


def magic_orb(buf, cx, cy, r=3):
    disc(buf, cx, cy, r + 1, VIO_D)
    disc(buf, cx, cy, r, VIO)
    disc(buf, cx, cy, r - 1, VIO_L)
    setpx(buf, cx - 1, cy - 1, VIO_LL)
    setpx(buf, cx, cy - 1, VIO_LL)
    setpx(buf, cx + 1, cy + 1, VIO_LL)


def mage(buf, arm_l="down", arm_r="down", look="fwd", tilt=0):
    mage_robe(buf)
    hl = arm(buf, -1, arm_l, VIO_D, GOLD_D, SKIN, t=3, edge=VIO)
    hr = arm(buf, +1, arm_r, VIO_D, GOLD_D, SKIN, t=3, edge=VIO)
    mage_head(buf, look=look, tilt=tilt)
    return {"lh": hl, "rh": hr}


# ------------------------------------------------------------- tirador (arco)
def archer_legs(buf, mode="stand"):
    if mode == "step1":
        box(buf, 16, 28, 20, 35, TEAL_D)
        box(buf, 14, 36, 21, 38, NAVY)
        box(buf, 27, 28, 31, 35, TEAL_D)
        box(buf, 26, 36, 33, 37, NAVY)
    elif mode == "step2":
        box(buf, 17, 28, 21, 35, TEAL_D)
        box(buf, 15, 36, 22, 37, NAVY)
        box(buf, 26, 28, 31, 35, TEAL_D)
        box(buf, 23, 36, 32, 38, NAVY)
    else:
        box(buf, 17, 28, 21, 35, TEAL_D)
        box(buf, 15, 36, 22, 38, NAVY)
        box(buf, 26, 28, 30, 35, TEAL_D)
        box(buf, 24, 36, 32, 38, NAVY)
    for x0 in (15, 24):
        setpx(buf, x0 + 1, 36, STEEL)
        setpx(buf, x0 + 2, 38, STEEL_D)
    hline(buf, 18, 21, 32, TEAL)


def archer_torso(buf, back=False):
    box(buf, 18, 16, 29, 28, TEAL)
    if back:
        rect(buf, 19, 18, 28, 24, TEAL_D)
        vline(buf, 23, 18, 24, NAVY)
        vline(buf, 24, 18, 24, NAVY)
        hline(buf, 19, 28, 18, NAVY_L)
    else:
        rect(buf, 20, 18, 27, 24, NAVY)
        hline(buf, 20, 27, 18, NAVY_L)
        vline(buf, 20, 18, 24, NAVY_L)
        vline(buf, 27, 18, 24, NAVY_D)
        setpx(buf, 23, 20, GOLD)
        setpx(buf, 24, 20, GOLD_D)
        # correa del carcaj
        line(buf, 20, 19, 27, 24, GOLD_D)
    rect(buf, 19, 25, 28, 26, GOLD_D)
    hline(buf, 19, 28, 25, GOLD)
    hline(buf, 19, 28, 17, GOLD_D)


def archer_head(buf, look="fwd"):
    # capucha teal oscura con pico adelante y cola atras
    rows = [(3, 25, 27), (4, 23, 29), (5, 21, 30), (6, 19, 31), (7, 18, 31),
            (8, 17, 31), (9, 17, 31), (10, 17, 31), (11, 17, 31),
            (12, 17, 31), (13, 17, 31), (14, 17, 31), (15, 17, 31),
            (16, 17, 31)]
    for (y, x0, x1) in rows:
        hline(buf, x0, x1, y, INK)
    for (y, x0, x1) in rows:
        if x1 - x0 > 2:
            hline(buf, x0 + 1, x1 - 1, y, NAVY)
    for (y, x0, x1) in rows[1:]:
        setpx(buf, x0 + 1, y, TEAL_L)
        setpx(buf, x1 - 1, y, NAVY_D)
    setpx(buf, 26, 3, TEAL)
    setpx(buf, 24, 4, TEAL_L)
    # cola de la capucha
    rect(buf, 30, 9, 32, 13, INK)
    rect(buf, 30, 10, 31, 12, NAVY_D)
    # cara
    rect(buf, 19, 9, 27, 16, INK)
    rect(buf, 20, 10, 26, 15, SKIN)
    rect(buf, 20, 10, 26, 11, SKIN_D)
    hline(buf, 21, 25, 10, SKIN_L)
    for (x0, x1) in ((20, 22), (24, 26)):
        rect(buf, x0, 12, x1, 13, WHITE)
        setpx(buf, x0 + 1, 13, EYE_D)
        setpx(buf, x0 + 1, 12, EYE_D)
    if look == "up":
        for (x0, x1) in ((20, 22), (24, 26)):
            rect(buf, x0, 12, x1, 13, WHITE)
            setpx(buf, x0 + 1, 12, EYE_D)
    elif look == "left":
        for (x0, x1) in ((20, 22), (24, 26)):
            rect(buf, x0, 12, x1, 13, WHITE)
            setpx(buf, x0, 12, EYE_D)
            setpx(buf, x0, 13, EYE_D)
    elif look == "down":
        for (x0, x1) in ((20, 22), (24, 26)):
            rect(buf, x0, 12, x1, 13, WHITE)
            setpx(buf, x0 + 1, 13, EYE_D)
            hline(buf, x0, x1, 12, SKIN_D)
    setpx(buf, 23, 14, SKIN_D)
    hline(buf, 21, 25, 15, SKIN_DD)
    # cuello y broche dorado
    rect(buf, 21, 16, 24, 16, SKIN_D)
    setpx(buf, 23, 17, GOLD)
    setpx(buf, 24, 17, GOLD_D)


def quiver(buf):
    box(buf, 28, 14, 32, 25, WOOD_D)
    hline(buf, 29, 31, 16, GOLD)
    hline(buf, 29, 31, 21, GOLD_D)
    for (x, y) in ((29, 9), (31, 8)):
        vline(buf, x, y, 14, WOOD_L)
        setpx(buf, x, y - 1, TOX)
        setpx(buf, x - 1, y, TOX)
        setpx(buf, x + 1, y, TOX_D)
        setpx(buf, x, y - 2, TOX_L)


def bow(buf, cx, cy, glow=False):
    """Arco con la cuerda en x=cx y el grip en (cx-8, cy)."""
    pts = [(cx, cy - 11), (cx - 2, cy - 9), (cx - 5, cy - 6),
           (cx - 7, cy - 3), (cx - 8, cy), (cx - 7, cy + 3),
           (cx - 5, cy + 6), (cx - 2, cy + 9), (cx, cy + 11)]
    stroke(buf, pts, WOOD, 2)
    vline(buf, cx, cy - 10, cy + 10, (226, 226, 212))
    hline(buf, cx - 1, cx - 1, cy - 10, WHITE)
    rect(buf, cx - 9, cy - 2, cx - 7, cy + 1, GOLD_D)
    hline(buf, cx - 9, cx - 7, cy - 2, GOLD)
    setpx(buf, cx, cy - 11, GOLD)
    setpx(buf, cx, cy + 11, GOLD)
    if glow:
        setpx(buf, cx - 4, cy - 8, VIO_L)
        setpx(buf, cx - 6, cy + 4, VIO_L)
        setpx(buf, cx + 1, cy - 12, VIO_L)


def archer(buf, arm_l="down", arm_r="down", legs="stand", look="fwd",
           back=False):
    quiver(buf)
    archer_legs(buf, legs)
    archer_torso(buf, back=back)
    archer_head(buf, look=look)
    hl = arm(buf, -1, arm_l, NAVY, TEAL_L, SKIN, t=2, edge=TEAL)
    hr = arm(buf, +1, arm_r, NAVY, TEAL_L, SKIN, t=2, edge=TEAL)
    return {"lh": hl, "rh": hr}


# --------------------------------------------------------------- yordle
HAT = [(1, 25, 27), (2, 23, 28), (3, 21, 28), (4, 18, 27), (5, 15, 26)]


def yordle_hat(buf):
    """Sombreron: cono alto e inclinado, ala ancha y banda dorada."""
    for (y, x0, x1) in HAT:
        hline(buf, x0, x1, y, INK)
    for (y, x0, x1) in HAT:
        if x1 - x0 > 2:
            hline(buf, x0 + 1, x1 - 1, y, TEAL)
    for (y, x0, x1) in HAT[1:]:
        setpx(buf, x0 + 1, y, TEAL_L)
        setpx(buf, x1 - 1, y, TEAL_D)
    setpx(buf, 26, 1, TEAL_L)
    # ala: tres filas con banda dorada
    hline(buf, 12, 33, 6, INK)
    hline(buf, 11, 34, 7, INK)
    hline(buf, 12, 33, 8, INK)
    hline(buf, 12, 33, 6, TEAL)
    hline(buf, 12, 33, 7, GOLD)
    hline(buf, 12, 33, 8, TEAL_D)
    setpx(buf, 11, 7, TEAL_L)
    setpx(buf, 34, 7, TEAL_D)
    setpx(buf, 23, 7, GOLD_L)
    setpx(buf, 24, 7, GOLD_D)
    # pluma toxica
    setpx(buf, 27, 1, TOX_L)
    setpx(buf, 28, 2, TOX)
    setpx(buf, 29, 2, TOX_L)
    setpx(buf, 29, 3, TOX)
    setpx(buf, 30, 3, TOX_L)
    setpx(buf, 30, 4, TOX_D)


def ear(buf, side):
    """Oreja puntiaguda de yordle: triangulo con contorno, pegada a la cabeza."""
    outer = [(11, 1), (12, 1), (13, 0), (14, -1), (15, -1), (16, 0),
             (17, 1), (18, 2)]
    inner = [(12, 2), (13, 1), (14, 0), (15, 0), (16, 1), (17, 2)]

    def put(y, a, b, col):
        if side < 0:
            hline(buf, a, b, y, col)
        else:
            hline(buf, W - 1 - b, W - 1 - a, y, col)

    for (y, off) in outer:
        put(y, 10 + off, 14, INK)
    for (y, off) in inner:
        put(y, 10 + off, 14, SKIN)
    if side < 0:
        setpx(buf, 12, 14, SKIN_L)
        setpx(buf, 12, 15, SKIN_D)
    else:
        setpx(buf, 35, 14, SKIN_L)
        setpx(buf, 35, 15, SKIN_D)


def yordle_head(buf, blink=False, look="fwd", mouth="close", old=False):
    ear(buf, -1)
    ear(buf, 1)
    box(buf, 15, 9, 32, 22, SKIN)
    rect(buf, 16, 10, 31, 21, SKIN)
    hline(buf, 16, 31, 10, SKIN_L)
    if old:
        rect(buf, 16, 10, 31, 11, (216, 212, 206))
        rect(buf, 16, 12, 17, 15, (216, 212, 206))
        rect(buf, 30, 12, 31, 15, (204, 200, 194))
        hline(buf, 16, 31, 10, (240, 238, 232))
        setpx(buf, 16, 16, (216, 212, 206))
        setpx(buf, 31, 16, (204, 200, 194))
    else:
        rect(buf, 16, 10, 31, 11, (92, 60, 44))
        hline(buf, 16, 31, 10, (124, 86, 62))
        setpx(buf, 16, 12, (92, 60, 44))
        setpx(buf, 31, 12, (92, 60, 44))
    # ojos enormes
    for (x0, x1) in ((18, 21), (26, 29)):
        if blink:
            hline(buf, x0, x1, 14, SKIN_D)
            hline(buf, x0, x1, 15, SKIN_DD)
            setpx(buf, x0, 15, SKIN_D)
            setpx(buf, x1, 15, SKIN_D)
        else:
            rect(buf, x0, 12, x1, 15, WHITE)
            hline(buf, x0, x1, 12, (214, 232, 240))
            px = x0 + 1
            if look == "left":
                px = x0
            elif look == "right":
                px = x1 - 1
            rect(buf, px, 13, px + 1, 15, EYE_D)
            setpx(buf, x0, 13, WHITE)
    vline(buf, 17, 11, 20, SKIN_D)
    vline(buf, 30, 11, 20, SKIN_D)
    # nariz, mejillas y boca
    rect(buf, 23, 16, 24, 17, SKIN_D)
    setpx(buf, 23, 16, SKIN_DD)
    setpx(buf, 17, 18, (226, 142, 132))
    setpx(buf, 30, 18, (226, 142, 132))
    if mouth == "close":
        hline(buf, 22, 26, 20, MOUTH_D)
    elif mouth == "small":
        rect(buf, 23, 19, 25, 20, MOUTH_D)
        setpx(buf, 24, 20, MOUTH_I)
    elif mouth == "mid":
        rect(buf, 22, 19, 26, 20, MOUTH_D)
        hline(buf, 23, 25, 19, TEETH)
    elif mouth == "wide":
        rect(buf, 21, 19, 27, 21, MOUTH_D)
        hline(buf, 22, 26, 19, TEETH)
        setpx(buf, 24, 21, MOUTH_I)
        setpx(buf, 25, 21, MOUTH_I)
    elif mouth == "grin":
        for (x, y) in ((20, 19), (21, 20), (22, 21), (23, 21), (24, 21),
                       (25, 21), (26, 20), (27, 19)):
            setpx(buf, x, y, MOUTH_D)
        hline(buf, 22, 25, 21, TEETH)


def yordle_body(buf, arms="down"):
    box(buf, 18, 23, 29, 32, TEAL)
    rect(buf, 19, 24, 28, 30, TEAL)
    hline(buf, 19, 28, 24, TEAL_L)
    vline(buf, 19, 24, 30, TEAL_L)
    vline(buf, 28, 24, 30, TEAL_D)
    rect(buf, 23, 24, 24, 30, TEAL_D)
    rect(buf, 19, 31, 28, 31, GOLD_D)
    hline(buf, 19, 28, 31, GOLD)
    setpx(buf, 23, 31, TEAL_L)
    setpx(buf, 24, 31, NAVY_D)
    # mangas
    if arms == "up":
        pts_l = [(18, 25), (15, 22), (14, 18)]
        pts_r = [(29, 25), (32, 22), (33, 18)]
    elif arms == "front":
        pts_l = [(18, 25), (17, 28), (20, 30)]
        pts_r = [(29, 25), (30, 28), (27, 30)]
    else:
        pts_l = [(18, 25), (15, 28), (16, 30)]
        pts_r = [(29, 25), (32, 28), (31, 30)]
    stroke(buf, pts_l, TEAL, 2)
    stroke(buf, pts_r, TEAL, 2)
    for (hx, hy) in (pts_l[-1], pts_r[-1]):
        box(buf, hx - 2, hy - 2, hx + 2, hy + 2, SKIN)
        setpx(buf, hx - 1, hy - 1, SKIN_L)
    # piernas
    box(buf, 18, 33, 22, 35, NAVY)
    box(buf, 25, 33, 29, 35, NAVY)
    box(buf, 16, 36, 23, 38, GOLD_D)
    box(buf, 24, 36, 31, 38, GOLD_D)
    hline(buf, 17, 22, 37, GOLD)
    hline(buf, 25, 30, 37, GOLD)
    return (pts_l[-1], pts_r[-1])


def yordle(buf, blink=False, look="fwd", mouth="close", arms="down",
           old=False):
    yordle_hat(buf)
    yordle_head(buf, blink=blink, look=look, mouth=mouth, old=old)
    return yordle_body(buf, arms=arms)


# ------------------------------------------------------------------ objetos
def blade_v(buf, hx, top, bottom, tip="up"):
    """Hoja vertical de 5 px con punta de 3 pisos y contorno."""
    if tip == "up":
        rect(buf, hx - 3, top + 3, hx + 3, bottom, INK)
        rect(buf, hx - 2, top + 1, hx + 2, bottom, INK)
        rect(buf, hx - 1, top, hx + 1, bottom, INK)
        rect(buf, hx - 2, top + 3, hx + 2, bottom - 1, STEEL)
        rect(buf, hx - 1, top + 1, hx + 1, top + 2, STEEL)
        setpx(buf, hx, top, STEEL_L)
        vline(buf, hx - 1, top + 2, bottom - 2, STEEL_L)
        vline(buf, hx + 1, top + 3, bottom - 2, STEEL_D)
        vline(buf, hx - 2, top + 4, bottom - 2, STEEL_D)
    else:
        rect(buf, hx - 3, top, hx + 3, bottom - 3, INK)
        rect(buf, hx - 2, top, hx + 2, bottom - 1, INK)
        rect(buf, hx - 1, top, hx + 1, bottom, INK)
        rect(buf, hx - 2, top + 1, hx + 2, bottom - 3, STEEL)
        rect(buf, hx - 1, bottom - 2, hx + 1, bottom - 1, STEEL)
        setpx(buf, hx, bottom, STEEL_L)
        vline(buf, hx - 1, top + 1, bottom - 3, STEEL_L)
        vline(buf, hx + 1, top + 1, bottom - 3, STEEL_D)
        vline(buf, hx - 2, top + 1, bottom - 3, STEEL_D)


def sword_up(buf, hx, hy):
    """Espadon vertical: grip en la mano (hx, hy), hoja hacia arriba."""
    top = max(1, hy - 23)
    blade_v(buf, hx, top, hy - 4, tip="up")
    box(buf, hx - 5, hy - 3, hx + 5, hy - 2, GOLD)
    hline(buf, hx - 4, hx + 4, hy - 3, GOLD_L)
    setpx(buf, hx - 5, hy - 2, GOLD_D)
    setpx(buf, hx + 5, hy - 2, GOLD_D)
    box(buf, hx - 1, hy - 1, hx + 1, hy + 3, WOOD_D)
    setpx(buf, hx, hy, WOOD)
    setpx(buf, hx, hy + 2, WOOD_D)
    box(buf, hx - 2, hy + 4, hx + 2, hy + 5, GOLD)
    setpx(buf, hx - 1, hy + 4, GOLD_L)


def sword_diag(buf, hx, hy, tx, ty, guard=4):
    """Espada en diagonal: grip en (hx,hy), punta en (tx,ty)."""
    mx = tx - hx
    my = ty - hy
    d = max(1.0, math.sqrt(mx * mx + my * my))
    ux, uy = mx / d, my / d
    gx = int(round(hx - ux * 4))
    gy = int(round(hy - uy * 4))
    stroke(buf, [(gx, gy), (hx, hy)], WOOD_D, 2)
    ax = int(round(hx - uy * guard))
    ay = int(round(hy + ux * guard))
    bx = int(round(hx + uy * guard))
    by = int(round(hy - ux * guard))
    stroke(buf, [(ax, ay), (bx, by)], GOLD, 2)
    stroke(buf, [(hx, hy), (tx, ty)], STEEL, 3)
    setpx(buf, gx, gy, GOLD_L)
    disc(buf, gx, gy, 1, GOLD)


def sword_planted(buf, hx, hy):
    """Espada clavada en el piso: manos en el pomo (hx, hy)."""
    box(buf, hx - 2, hy, hx + 2, hy + 1, GOLD)
    setpx(buf, hx - 1, hy, GOLD_L)
    box(buf, hx - 1, hy + 2, hx + 1, hy + 5, WOOD_D)
    setpx(buf, hx, hy + 3, WOOD)
    box(buf, hx - 4, hy + 6, hx + 4, hy + 7, GOLD)
    hline(buf, hx - 3, hx + 3, hy + 6, GOLD_L)
    blade_v(buf, hx, hy + 8, 38, tip="down")


def gavel(buf, hx, hy, up=True):
    """Mazo de veredicto: (hx,hy) es la mano."""
    if up:
        stroke(buf, [(hx, hy), (hx, hy - 3)], WOOD_D, 2)
        box(buf, hx - 5, hy - 9, hx + 5, hy - 5, GOLD)
        hline(buf, hx - 4, hx + 4, hy - 8, GOLD_L)
        hline(buf, hx - 4, hx + 4, hy - 6, GOLD_D)
        setpx(buf, hx - 4, hy - 9, VIO_L)
        setpx(buf, hx + 4, hy - 9, VIO_L)
        setpx(buf, hx, hy - 9, VIO_LL)
    else:
        stroke(buf, [(hx, hy), (hx + 2, hy + 3)], WOOD_D, 2)
        box(buf, hx - 3, hy + 4, hx + 7, hy + 8, GOLD)
        hline(buf, hx - 2, hx + 6, hy + 4, GOLD_L)
        hline(buf, hx - 2, hx + 6, hy + 8, GOLD_D)
        setpx(buf, hx + 7, hy + 5, VIO_L)


def tome(buf, x, y, turn=False):
    """Tomo abierto de 16x11 con (x,y) esquina sup-izq."""
    box(buf, x, y, x + 15, y + 10, VIO_D)
    hline(buf, x + 1, x + 14, y, VIO_L)
    for (px0, px1) in ((x + 1, x + 7), (x + 8, x + 14)):
        rect(buf, px0, y + 1, px1, y + 9, PAPER)
        hline(buf, px0, px1, y + 9, PAPER_D)
    vline(buf, x + 7, y + 1, y + 10, VIO_D)
    vline(buf, x + 8, y + 1, y + 10, VIO_D)
    for yy in (y + 3, y + 5, y + 7):
        hline(buf, x + 2, x + 5, yy, PAPER_D)
        hline(buf, x + 9, x + 13, yy, PAPER_D)
    hline(buf, x + 2, x + 5, y + 1, PAPER_L)
    hline(buf, x + 10, x + 13, y + 2, MAP_LINE)
    if turn:
        rect(buf, x + 9, y - 3, x + 14, y + 2, PAPER_L)
        hline(buf, x + 9, x + 14, y - 3, PAPER_D)
        vline(buf, x + 14, y - 3, y + 2, PAPER_D)
        setpx(buf, x + 13, y - 1, VIO_L)
        vline(buf, x + 11, y - 2, y + 1, PAPER_D)
    # cinta
    rect(buf, x + 7, y + 10, x + 8, y + 12, GOLD_D)


MAP_LINE = (120, 156, 200)


def scroll(buf, x, y, lines=3, marks=False, stamped=False):
    """Pergamino vertical 10x17 con (x,y) esquina sup-izq."""
    box(buf, x, y, x + 9, y + 16, PAPER)
    rect(buf, x + 1, y + 1, x + 8, y + 15, PAPER)
    hline(buf, x + 1, x + 8, y + 1, PAPER_L)
    hline(buf, x + 1, x + 8, y + 15, PAPER_D)
    for k in range(lines):
        hline(buf, x + 2, x + 7, y + 3 + k * 2, PAPER_D)
    box(buf, x - 1, y - 2, x + 10, y, GOLD_D)
    hline(buf, x, x + 9, y - 2, GOLD)
    box(buf, x - 1, y + 16, x + 10, y + 18, GOLD_D)
    hline(buf, x, x + 9, y + 16, GOLD)
    if marks:
        for (px, py) in ((x + 2, y + 5), (x + 4, y + 7), (x + 3, y + 9)):
            setpx(buf, px, py, RED)
        hline(buf, x + 2, x + 5, y + 10, RED_D)
    if stamped:
        ring(buf, x + 5, y + 8, 3, TOX_D, 1)
        setpx(buf, x + 4, y + 8, TOX)
        setpx(buf, x + 5, y + 9, TOX)
        setpx(buf, x + 6, y + 7, TOX)
        setpx(buf, x + 7, y + 6, TOX_L)


def quill(buf, hx, hy, dx=5, dy=-7):
    stroke(buf, [(hx, hy), (hx + dx, hy + dy)], VIO_L, 1)
    setpx(buf, hx, hy, GOLD)
    setpx(buf, hx + 1, hy - 1, GOLD_D)
    for (px, py) in ((hx + 3, hy - 4), (hx + 4, hy - 3), (hx + 4, hy - 6),
                     (hx + 5, hy - 5), (hx + 2, hy - 3)):
        setpx(buf, px, py, VIO_LL)
    setpx(buf, hx + dx, hy + dy, VIO_L)


def pink_ward(buf, cx, ground=38, lit=True):
    """Ward rosa: piedra base, tallo y cristal con ojo."""
    box(buf, cx - 4, ground - 2, cx + 4, ground, STEEL_D)
    hline(buf, cx - 3, cx + 3, ground - 2, STEEL)
    vline(buf, cx - 1, ground - 7, ground - 3, STEEL)
    vline(buf, cx, ground - 7, ground - 3, STEEL_D)
    rows = [(0, 1), (1, 3), (2, 4), (3, 5), (4, 4), (5, 3), (6, 1)]
    top = ground - 13
    for (i, half) in rows:
        hline(buf, cx - half, cx + half, top + i, INK)
    for (i, half) in rows:
        if half > 1:
            hline(buf, cx - half + 1, cx + half - 1, top + i, PINK)
    hline(buf, cx - 2, cx + 2, top + 1, PINK_L)
    setpx(buf, cx - 3, top + 3, PINK_L)
    setpx(buf, cx + 3, top + 4, PINK_D)
    rect(buf, cx - 1, top + 3, cx + 1, top + 5, PINK_D)
    setpx(buf, cx, top + 3, WHITE if lit else PINK_L)
    setpx(buf, cx - 1, top + 5, PINK_D)
    if lit:
        spark(buf, cx - 6, top + 2, PINK_L)
        spark(buf, cx + 6, top + 6, PINK_L)
        setpx(buf, cx, top - 1, PINK_L)


def potion(buf, cx, ground=38, full=True):
    """Frasco de pocion: (cx, ground) es la base del cuerpo redondo."""
    box(buf, cx - 4, ground - 6, cx + 4, ground, VIO_DD)
    rect(buf, cx - 3, ground - 5, cx + 3, ground - 1,
         TOX if full else TOX_D)
    hline(buf, cx - 3, cx + 2, ground - 5, TOX_L if full else TOX)
    setpx(buf, cx - 3, ground - 3, WHITE)
    setpx(buf, cx - 2, ground - 3, WHITE)
    setpx(buf, cx + 3, ground - 2, TOX_D)
    box(buf, cx - 2, ground - 9, cx + 2, ground - 7, STEEL)
    hline(buf, cx - 1, cx + 1, ground - 9, STEEL_L)
    box(buf, cx - 1, ground - 12, cx + 1, ground - 10, WOOD_D)
    setpx(buf, cx, ground - 11, WOOD)
    if full:
        setpx(buf, cx + 4, ground - 4, TOX_L)
        setpx(buf, cx - 5, ground - 3, TOX)
        spark(buf, cx + 6, ground - 8, TOX_L)


def speed_lines(buf, x0, x1, ys):
    for y in ys:
        speed(buf, y, x0, x1)


def bubble(buf, x, y, w, h, letter, col):
    rect(buf, x + 1, y, x + w - 2, y + h - 1, INK)
    rect(buf, x, y + 1, x + w - 1, y + h - 2, INK)
    rect(buf, x + 1, y + 1, x + w - 2, y + h - 2, WHITE)
    tw = len(FONT[letter][0]) * 2
    th = 5 * 2
    text(buf, letter, x + (w - tw) // 2, y + (h - th) // 2 + 1, col,
         scale=2, outline=None)
    for (px, py) in ((x + 4, y + h - 1), (x + 3, y + h), (x + 2, y + h + 1)):
        setpx(buf, px, py, INK)
    setpx(buf, x + 5, y + h - 1, WHITE)
    setpx(buf, x + 4, y + h, WHITE)
    # remaches de color en las esquinas
    setpx(buf, x + 1, y + 1, col)
    setpx(buf, x + w - 2, y + 1, col)
    setpx(buf, x + 1, y + h - 2, col)
    setpx(buf, x + w - 2, y + h - 2, col)


def sun(buf, cx, cy, r=4, phase=0):
    disc(buf, cx, cy, r + 1, GOLD_D)
    disc(buf, cx, cy, r, GOLD)
    disc(buf, cx, cy, r - 1, (250, 220, 140))
    for k in range(0, 360, 45):
        rad = math.radians(k + phase * 22)
        setpx(buf, cx + int(round(math.cos(rad) * (r + 2))),
              cy + int(round(math.sin(rad) * (r + 2))), GOLD_L)


def hextech_turret(buf, firing=False):
    """Torreta hextech: base de piedra, cuerpo teal, canon y nucleo."""
    # base
    box(buf, 12, 34, 35, 38, NAVY_D)
    hline(buf, 13, 34, 34, NAVY_L)
    setpx(buf, 14, 37, GOLD_D)
    setpx(buf, 33, 37, GOLD_D)
    box(buf, 16, 30, 31, 34, NAVY)
    hline(buf, 17, 30, 30, TEAL)
    setpx(buf, 17, 32, GOLD)
    # cuerpo
    box(buf, 17, 20, 30, 30, TEAL)
    rect(buf, 18, 21, 29, 29, NAVY)
    vline(buf, 18, 21, 28, NAVY_L)
    vline(buf, 29, 21, 28, NAVY_D)
    hline(buf, 19, 28, 22, TEAL_D)
    # nucleo hextech
    for (y, half) in ((24, 1), (25, 2), (26, 3), (27, 2), (28, 1)):
        hline(buf, 23 - half, 24 + half, y, INK)
    for (y, half) in ((25, 1), (26, 2), (27, 1)):
        hline(buf, 23 - half, 24 + half, y, VIO if not firing else VIO_LL)
    setpx(buf, 23, 26, VIO_LL if firing else VIO_L)
    # cabeza y canon
    box(buf, 20, 15, 28, 21, TEAL)
    hline(buf, 21, 27, 15, TEAL_L)
    hline(buf, 21, 27, 20, GOLD_D)
    setpx(buf, 24, 18, TOX if firing else TOX_D)
    mx0, my0 = 26, 18
    mx1, my1 = 36, (8 if firing else 10)
    stroke(buf, [(mx0, my0), (mx1, my1)], STEEL, 3)
    disc(buf, mx1, my1, 2, GOLD_D)
    disc(buf, mx1, my1, 1, GOLD)
    if firing:
        burst(buf, mx1 + 1, my1 - 1, 4, TOX_L, WHITE)
        line_brush(buf, mx1 + 3, my1 - 3, 42, 3, TOX, 2)
        setpx(buf, 43, 2, TOX_L)
        spark(buf, 18, 12, GOLD)
        setpx(buf, 16, 22, VIO_L)
    else:
        setpx(buf, mx1, my1, GOLD_L)


def crystal_nexus(buf, lit=False):
    """Nexus de cristal violeta sobre escalones de piedra."""
    box(buf, 10, 35, 37, 38, STEEL_DD)
    hline(buf, 11, 36, 35, STEEL_D)
    box(buf, 14, 31, 33, 35, NAVY)
    hline(buf, 15, 32, 31, NAVY_L)
    setpx(buf, 16, 34, GOLD)
    setpx(buf, 31, 34, GOLD)
    rows = [(8, 1), (9, 2), (10, 3), (11, 4), (12, 5), (13, 6), (14, 6),
            (15, 7), (16, 7), (17, 7), (18, 7), (19, 6), (20, 6), (21, 5),
            (22, 5), (23, 4), (24, 4), (25, 3), (26, 3), (27, 2), (28, 2),
            (29, 1)]
    for (y, half) in rows:
        hline(buf, 24 - half - 1, 24 + half + 1, y, INK)
    for (y, half) in rows:
        hline(buf, 24 - half, 24 + half, y, VIO)
    for (y, half) in rows[3:-3]:
        hline(buf, 24 - half, 24 - half + 1, y, VIO_L)
        setpx(buf, 24 + half, y, VIO_D)
    hline(buf, 22, 26, 20, VIO_D)
    vline(buf, 25, 22, 27, VIO_D)
    if lit:
        for (y, half) in rows[4:-4]:
            hline(buf, 24 - half + 1, 24 + half - 1, y, VIO_L)
        hline(buf, 22, 26, 16, VIO_LL)
        hline(buf, 22, 26, 17, VIO_LL)
        burst(buf, 24, 18, 11, VIO_L, WHITE)
        burst(buf, 24, 30, 5, VIO, VIO_LL)
    else:
        for (x, y) in ((13, 14), (36, 12), (11, 22), (37, 24), (16, 8),
                       (33, 26)):
            spark(buf, x, y, VIO_L)
        circle(buf, 24, 31, 2, VIO_D)
    setpx(buf, 20, 12, VIO_LL)
    setpx(buf, 19, 13, VIO_LL)


def crossed_swords(buf, clash=False):
    if clash:
        shift = 1
    else:
        shift = 0
    # espada de abajo-izq a arriba-der
    stroke(buf, [(9, 34 + shift), (39, 7 - shift)], STEEL, 3)
    stroke(buf, [(13, 30 + shift), (17, 34 + shift)], GOLD, 3)
    disc(buf, 8, 35 + shift, 2, GOLD_D)
    disc(buf, 8, 35 + shift, 1, GOLD)
    # espada de abajo-der a arriba-izq
    stroke(buf, [(38, 34 + shift), (8, 7 - shift)], STEEL, 3)
    stroke(buf, [(34, 30 + shift), (30, 34 + shift)], GOLD, 3)
    disc(buf, 39, 35 + shift, 2, GOLD_D)
    disc(buf, 39, 35 + shift, 1, GOLD)
    setpx(buf, 20, 21, STEEL_L)
    setpx(buf, 27, 21, STEEL_L)
    setpx(buf, 10, 33, VIO_L)
    setpx(buf, 37, 33, VIO_L)
    if clash:
        burst(buf, 23, 21, 7, GOLD_L, WHITE)
        for (x, y) in ((14, 12), (32, 12), (12, 26), (35, 27), (23, 6),
                       (23, 36)):
            spark(buf, x, y, GOLD_L)
        star4(buf, 23, 21, VIO_LL)
    else:
        setpx(buf, 23, 21, STEEL_L)
        setpx(buf, 22, 20, STEEL_L)
        setpx(buf, 24, 22, STEEL_D)
        star4(buf, 40, 8, (170, 220, 250))


# ------------------------------------------------------------------- escenas
def scene_hi(p):
    buf = canvas()
    if p == 1:
        h = bruiser(buf, arm_l="up", arm_r="down", mouth="smile")
        sword_up(buf, h["rh"][0], h["rh"][1])
        star4(buf, 12, 8, GOLD)
        spark(buf, 9, 12, GOLD_L)
        spark(buf, 17, 6, GOLD_L)
    else:
        h = bruiser(buf, arm_l="out_up", arm_r="sword", mouth="open")
        sword_up(buf, h["rh"][0], h["rh"][1])
        spark(buf, 7, 14, GOLD_L)
        star4(buf, 42, 10, GOLD)
        spark(buf, 31, 6, GOLD_L)
    return buf


def scene_idle(p):
    buf = canvas()
    yordle(buf, blink=(p == 2))
    return buf


def scene_talk(p):
    buf = canvas()
    mouth = {1: "close", 2: "small", 3: "mid", 4: "wide"}[p]
    yordle(buf, mouth=mouth, look="fwd",
           arms="front" if p in (2, 4) else "down")
    return buf


def scene_think(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="out", arm_r="chin", look="up")
        magic_orb(buf, 11, 17, 3)
        spark(buf, 14, 13, VIO_L)
        spark(buf, 7, 20, VIO_L)
        setpx(buf, 8, 14, VIO_LL)
    else:
        h = mage(buf, arm_l="chest", arm_r="chin", look="up", tilt=-1)
        magic_orb(buf, 36, 13, 3)
        ring(buf, 36, 13, 5, VIO_D, 1)
        spark(buf, 42, 8, VIO_L)
        spark(buf, 30, 6, VIO_L)
        rune(buf, 12, 16, VIO_L)
    return buf


def scene_read(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="chest", arm_r="chest", look="down")
        tome(buf, 16, 20)
        box(buf, 15, 25, 18, 27, SKIN)
        box(buf, 30, 25, 33, 27, SKIN)
        spark(buf, 24, 17, VIO_L)
    else:
        h = mage(buf, arm_l="chest", arm_r="chest", look="down", tilt=1)
        tome(buf, 16, 20, turn=True)
        box(buf, 15, 25, 18, 27, SKIN)
        box(buf, 30, 25, 33, 27, SKIN)
        spark(buf, 33, 16, VIO_LL)
        star4(buf, 27, 17, VIO_L)
    return buf


def scene_write(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="hold", arm_r="pen", look="down")
        scroll(buf, 34, 14, lines=3)
        quill(buf, h["rh"][0] + 1, h["rh"][1] - 2, 4, -7)
        rune(buf, 39, 22, VIO_L)
        setpx(buf, 38, 19, VIO_LL)
    else:
        h = mage(buf, arm_l="hold", arm_r="up", look="fwd")
        scroll(buf, 34, 14, lines=5)
        quill(buf, h["rh"][0], h["rh"][1] - 2, 5, -6)
        rune(buf, 38, 18, VIO_L)
        rune(buf, 38, 24, VIO_LL)
        spark(buf, 41, 25, VIO_L)
    return buf


def scene_tool(p):
    buf = canvas()
    crossed_swords(buf, clash=(p == 2))
    return buf


def scene_ask(p):
    buf = canvas()
    if p == 1:
        h = archer(buf, arm_l="bow", arm_r="out", look="up")
        bow(buf, 18, 23)
        bubble(buf, 31, 1, 15, 13, "?", VIO)
        spark(buf, 43, 16, VIO_L)
    else:
        h = archer(buf, arm_l="bow_hi", arm_r="up", look="up")
        bow(buf, 18, 19, glow=True)
        bubble(buf, 2, 1, 15, 13, "?", VIO)
        setpx(buf, 16, 15, VIO_L)
        star4(buf, 22, 5, VIO_L)
    return buf


def scene_success(p):
    buf = canvas()
    if p == 1:
        h = bruiser(buf, arm_l="up_hi", arm_r="sword", mouth="shout")
        sword_up(buf, h["rh"][0], h["rh"][1])
        star4(buf, 8, 10, GOLD)
        star4(buf, 40, 13, GOLD)
        spark(buf, 14, 5, GOLD_L)
        spark(buf, 30, 4, TOX)
        for (x, y) in ((7, 20), (41, 21), (12, 30), (36, 31), (24, 28)):
            star4(buf, x, y, VIO_L)
    else:
        h = bruiser(buf, arm_l="up_hi", arm_r="up_hi", mouth="shout",
                    legs="step1")
        sword_diag(buf, h["rh"][0], h["rh"][1], 44, 4)
        star4(buf, 5, 8, GOLD)
        star4(buf, 43, 15, TOX)
        spark(buf, 16, 3, GOLD_L)
        spark(buf, 30, 6, GOLD_L)
        spark(buf, 24, 14, VIO_L)
        burst(buf, 9, 34, 2, GOLD_L, WHITE)
    return buf


def fallen_back(buf):
    """Campeon caido: cuerpo horizontal, cabeza alta y espada clavada al lado."""
    # bota al fondo (izquierda)
    box(buf, 4, 33, 12, 38, GOLD_D)
    hline(buf, 5, 11, 34, GOLD)
    setpx(buf, 5, 36, GOLD_L)
    setpx(buf, 11, 37, GOLD_DD)
    # cuerpo horizontal: piernas y torso
    box(buf, 10, 31, 31, 37, NAVY)
    hline(buf, 11, 30, 32, TEAL)
    vline(buf, 16, 33, 36, NAVY_D)
    rect(buf, 18, 31, 29, 35, TEAL)
    hline(buf, 18, 29, 31, TEAL_L)
    vline(buf, 18, 31, 35, TEAL_L)
    vline(buf, 29, 31, 35, TEAL_D)
    setpx(buf, 24, 33, TOX)
    rect(buf, 16, 35, 30, 36, GOLD_D)
    hline(buf, 16, 30, 35, GOLD)
    setpx(buf, 23, 35, TEAL)
    # hombrera y brazo bajo la cabeza
    box(buf, 24, 29, 29, 34, GOLD)
    hline(buf, 25, 28, 30, GOLD_L)
    # cabeza alta, apoyada al borde del cuerpo
    box(buf, 27, 22, 36, 31, SKIN)
    rect(buf, 28, 22, 35, 24, HAIR)
    hline(buf, 28, 35, 22, HAIR_L)
    rect(buf, 36, 25, 36, 29, HAIR)
    rect(buf, 27, 25, 27, 29, HAIR)
    for (x0, x1) in ((29, 30), (33, 34)):
        setpx(buf, x0, 27, EYE_D)
        setpx(buf, x1, 27, EYE_D)
        setpx(buf, x0 + 1, 26, EYE_D)
        setpx(buf, x1 - 1, 26, EYE_D)
    hline(buf, 31, 34, 30, MOUTH_D)
    # espada clavada al lado de la cabeza
    sword_planted(buf, 42, 13)
    # polvo y escombro
    dust(buf, 14, 37, 2)
    dust(buf, 8, 39, 1)
    setpx(buf, 22, 27, DUST_L)
    setpx(buf, 39, 31, DUST)


def kneel_champion(buf):
    """Campeon de rodillas, cabeza gacha y espada clavada al costado."""
    # piernas dobladas
    box(buf, 14, 33, 21, 38, NAVY)
    hline(buf, 15, 20, 34, TEAL)
    box(buf, 24, 33, 30, 38, NAVY)
    hline(buf, 25, 29, 34, TEAL)
    box(buf, 12, 36, 20, 38, GOLD_D)
    hline(buf, 13, 19, 37, GOLD)
    box(buf, 27, 36, 34, 38, GOLD_D)
    hline(buf, 28, 33, 37, GOLD)
    # torso encorvado
    box(buf, 16, 22, 31, 34, NAVY)
    rect(buf, 19, 24, 28, 30, TEAL)
    hline(buf, 19, 28, 24, TEAL_L)
    vline(buf, 19, 24, 30, TEAL_L)
    vline(buf, 28, 24, 30, TEAL_D)
    setpx(buf, 23, 26, TOX)
    hline(buf, 17, 30, 23, GOLD)
    rect(buf, 17, 31, 30, 32, GOLD_D)
    # hombreras
    box(buf, 13, 22, 18, 27, GOLD)
    hline(buf, 14, 17, 23, GOLD_L)
    box(buf, 29, 22, 34, 27, GOLD)
    hline(buf, 30, 33, 23, GOLD_L)
    # cabeza gacha (ojos cerrados, nariz y boca)
    box(buf, 19, 12, 28, 22, SKIN)
    rect(buf, 20, 12, 27, 15, HAIR)
    hline(buf, 20, 27, 12, HAIR_L)
    rect(buf, 20, 16, 20, 18, HAIR)
    rect(buf, 27, 16, 27, 18, HAIR)
    hline(buf, 21, 22, 17, SKIN_DD)
    hline(buf, 25, 26, 17, SKIN_DD)
    setpx(buf, 23, 18, SKIN_D)
    setpx(buf, 24, 18, SKIN_DD)
    hline(buf, 22, 25, 20, MOUTH_D)
    hline(buf, 21, 26, 21, SKIN_D)
    # brazos: uno al pomo, otro sobre la rodilla
    stroke(buf, [(30, 25), (32, 22), (33, 20)], NAVY_L, 3)
    box(buf, 31, 18, 35, 22, GOLD_D)
    hline(buf, 32, 34, 18, GOLD)
    stroke(buf, [(17, 25), (17, 28), (21, 30)], NAVY_L, 3)
    box(buf, 19, 28, 23, 32, GOLD_D)
    # espada clavada
    sword_planted(buf, 34, 15)
    dust(buf, 8, 37, 2)
    dust(buf, 40, 38, 1)
    setpx(buf, 12, 33, DUST_L)
    setpx(buf, 30, 12, DUST)


def scene_failure(p):
    buf = canvas()
    if p == 1:
        fallen_back(buf)
        setpx(buf, 44, 31, DUST_L)
        spark(buf, 25, 24, DUST_L)
        setpx(buf, 39, 30, DUST)
    else:
        kneel_champion(buf)
        dust(buf, 6, 36, 2)
        setpx(buf, 30, 9, DUST_L)
        setpx(buf, 44, 26, DUST)
        spark(buf, 8, 28, DUST_L)
    return buf


def scene_compact(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="chest", arm_r="chest", look="down")
        for (x, y) in ((6, 9), (42, 11), (5, 27), (43, 29), (14, 4),
                       (34, 4)):
            rune(buf, x, y, VIO_L)
        for (x, y) in ((11, 4), (37, 5), (9, 33), (39, 34)):
            spark(buf, x, y, VIO_L)
    else:
        tmp = canvas()
        h = mage(tmp, arm_l="chest", arm_r="chest", look="down")
        chico = scale_sprite(tmp, 3, 4, ground=38)
        blit(buf, chico)
        arrow(buf, 23, 5, "down")
        arrow(buf, 23, 9, "down")
        arrow(buf, 6, 23, "right")
        arrow(buf, 9, 30, "right")
        arrow(buf, 41, 23, "left")
        arrow(buf, 38, 30, "left")
        for (x, y) in ((6, 12), (41, 14), (7, 36), (41, 36)):
            rune(buf, x, y, VIO_L)
    return buf


def mini_yordle(buf, x, y):
    """Yordle chiquito (6x10): (x,y) esquina sup-izq."""
    box(buf, x, y, x + 5, y + 9, TEAL)
    hline(buf, x, y, x + 5, INK)
    rect(buf, x + 1, y + 1, x + 4, y + 4, INK)
    rect(buf, x + 1, y + 1, x + 4, y + 3, SKIN)
    setpx(buf, x + 1, y + 2, EYE_D)
    setpx(buf, x + 3, y + 2, EYE_D)
    rect(buf, x + 1, y + 5, x + 4, y + 6, TEAL)
    setpx(buf, x + 2, y + 5, GOLD)
    rect(buf, x, y + 7, x + 5, y + 8, GOLD_D)
    hline(buf, x + 1, x + 4, y + 7, GOLD)
    rect(buf, x + 1, y + 9, x + 4, y + 9, GOLD_DD)


def scene_delegate(p):
    buf = canvas()
    if p == 1:
        h = bruiser(buf, arm_l="out", arm_r="down", mouth="open",
                    look="left")
        mini_yordle(buf, 37, 29)
        mini_yordle(buf, 41, 28)
        for (x, y) in ((34, 14), (36, 18), (33, 22)):
            setpx(buf, x, y, GOLD_L)
    else:
        h = bruiser(buf, arm_l="down", arm_r="out", mouth="smile",
                    look="right")
        mini_yordle(buf, 2, 29)
        mini_yordle(buf, 6, 28)
        for (x, y) in ((14, 14), (12, 18), (15, 22)):
            setpx(buf, x, y, GOLD_L)
    return buf


def scene_explore(p):
    buf = canvas()
    if p == 1:
        h = archer(buf, arm_l="bow", arm_r="low", legs="step1", look="right")
        bow(buf, 18, 25)
        pink_ward(buf, 39, 38, lit=False)
        setpx(buf, 30, 38, DUST)
        setpx(buf, 27, 37, DUST_L)
        spark(buf, 12, 12, WHITE)
    else:
        h = archer(buf, arm_l="bow_hi", arm_r="out", legs="step2",
                   look="left")
        bow(buf, 18, 19, glow=True)
        pink_ward(buf, 39, 38, lit=True)
        for (x, y) in ((31, 20), (33, 25), (31, 30), (33, 34)):
            setpx(buf, x, y, PINK_L)
        setpx(buf, 20, 38, DUST)
        setpx(buf, 17, 37, DUST_L)
    return buf


def scene_build(p):
    buf = canvas()
    hextech_turret(buf, firing=(p == 2))
    if p == 1:
        for (x, y) in ((8, 30), (41, 26), (9, 20)):
            spark(buf, x, y, TOX)
        setpx(buf, 24, 12, GOLD_L)
    else:
        star4(buf, 43, 6, TOX_L)
        dust(buf, 9, 37, 2)
        setpx(buf, 6, 26, DUST_L)
        spark(buf, 16, 12, GOLD_L)
    return buf


def scene_verify(p):
    buf = canvas()
    if p == 1:
        h = archer(buf, arm_l="bow", arm_r="up", look="right")
        bow(buf, 18, 24)
        # runa con tilde verde en la mano
        box(buf, 31, 8, 40, 15, VIO_DD)
        hline(buf, 32, 39, 8, VIO)
        check(buf, 32, 10, 2, TOX_L, TOX_D)
        spark(buf, 43, 10, TOX)
        spark(buf, 27, 6, TOX_L)
    else:
        h = archer(buf, arm_l="bow_hi", arm_r="down", look="down")
        bow(buf, 18, 22)
        # sello verde estampado
        disc(buf, 36, 26, 7, TOX_D)
        disc(buf, 36, 26, 5, TOX)
        check(buf, 32, 24, 2, WHITE, TOX_L)
        for (x, y) in ((36, 16), (36, 36), (26, 26), (46, 26)):
            setpx(buf, x, y, TOX_L)
        setpx(buf, 44, 18, TOX)
        setpx(buf, 28, 34, TOX)
        hline(buf, 40, 43, 32, TOX_L)
    return buf


def scene_judge(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="chest", arm_r="up", look="fwd")
        gavel(buf, h["rh"][0], h["rh"][1] - 1, up=True)
        rune(buf, 42, 18, VIO_L)
        ring(buf, 42, 18, 4, VIO_D, 1)
        spark(buf, 30, 4, GOLD_L)
        spark(buf, 44, 8, VIO_L)
    else:
        h = mage(buf, arm_l="chest", arm_r="stamp", look="down", tilt=1)
        # bloque de sentencia a la derecha
        box(buf, 33, 33, 45, 38, STEEL_D)
        hline(buf, 34, 44, 33, STEEL)
        hline(buf, 34, 44, 37, STEEL_DD)
        hline(buf, 37, 40, 35, STEEL_DD)
        gavel(buf, h["rh"][0], h["rh"][1], up=False)
        burst(buf, 38, 31, 4, GOLD_L, WHITE)
        hline(buf, 34, 44, 32, GOLD)
        rune(buf, 8, 16, VIO_L)
        setpx(buf, 32, 32, GOLD_L)
    return buf


def scene_review(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="hold", arm_r="pen", look="down")
        scroll(buf, 33, 13, lines=4, marks=True)
        quill(buf, h["rh"][0] + 1, h["rh"][1] - 2, 4, -6)
        setpx(buf, 38, 22, RED)
        ring(buf, 10, 20, 4, GOLD_D, 1)
        line(buf, 13, 23, 17, 27, WOOD_D)
        setpx(buf, 11, 19, VIO_L)
    else:
        h = mage(buf, arm_l="chest", arm_r="up", look="down")
        scroll(buf, 33, 13, lines=4, marks=True, stamped=True)
        # sello alzado: mango en la mano, cabeza arriba
        box(buf, h["rh"][0] - 1, h["rh"][1] - 3, h["rh"][0] + 1,
            h["rh"][1] - 1, WOOD_D)
        box(buf, h["rh"][0] - 5, h["rh"][1] - 9, h["rh"][0] + 5,
            h["rh"][1] - 4, TOX_D)
        hline(buf, h["rh"][0] - 4, h["rh"][0] + 4, h["rh"][1] - 8, TOX)
        check(buf, h["rh"][0] - 3, h["rh"][1] - 8, 1, WHITE, TOX_L)
        spark(buf, 42, 8, TOX_L)
        spark(buf, 27, 4, TOX)
        rune(buf, 9, 17, VIO_L)
    return buf


def scene_jira(p):
    buf = canvas()
    crystal_nexus(buf, lit=(p == 2))
    if p == 1:
        for (x, y) in ((7, 10), (41, 9), (6, 28), (42, 29)):
            setpx(buf, x, y, VIO_L)
        spark(buf, 24, 3, VIO_LL)
        setpx(buf, 24, 31, VIO_LL)
    else:
        star4(buf, 24, 2, VIO_LL)
        star4(buf, 8, 18, VIO_L)
        star4(buf, 40, 20, VIO_L)
        setpx(buf, 6, 34, VIO)
        setpx(buf, 42, 34, VIO)
        rune(buf, 24, 33, VIO_LL)
    return buf


def scene_jobs(p):
    buf = canvas()
    if p == 1:
        h = archer(buf, arm_l="bow", arm_r="hold", look="right")
        bow(buf, 18, 25)
        potion(buf, 24, 28, full=False)
        box(buf, 22, 22, 26, 25, SKIN)
        hline(buf, 23, 25, 22, SKIN_L)
        prog = 4
    else:
        h = archer(buf, arm_l="bow_hi", arm_r="out", look="right")
        bow(buf, 18, 22)
        potion(buf, 38, 25, full=True)
        box(buf, 35, 20, 39, 23, SKIN)
        hline(buf, 36, 38, 20, SKIN_L)
        spark(buf, 44, 16, TOX_L)
        spark(buf, 31, 12, TOX)
        setpx(buf, 40, 26, TOX_L)
        prog = 10
    # barra de progreso arriba a la izquierda
    rect(buf, 3, 2, 17, 6, INK)
    rect(buf, 4, 3, 16, 5, (44, 52, 58))
    rect(buf, 4, 3, 3 + prog, 5, TOX_D)
    hline(buf, 4, 3 + prog, 3, TOX)
    setpx(buf, 4, 3, TOX_L)
    setpx(buf, 17, 4, GOLD_D)
    setpx(buf, 3, 4, GOLD_D)
    return buf


def scene_yolo(p):
    buf = canvas()
    if p == 1:
        h = bruiser(buf, arm_l="down", arm_r="fwd", legs="step1",
                    mouth="shout", look="right")
        sword_diag(buf, h["rh"][0], h["rh"][1], 43, 12)
        speed_lines(buf, 2, 9, (16, 22, 28))
        spark(buf, 12, 12, GOLD_L)
        setpx(buf, 7, 19, GOLD)
    else:
        h = bruiser(buf, arm_l="out", arm_r="swing", legs="step2",
                    mouth="shout", look="right")
        sword_diag(buf, h["rh"][0] - 1, h["rh"][1], 43, 30)
        speed_lines(buf, 2, 9, (17, 23, 29))
        spark(buf, 13, 15, GOLD_L)
        setpx(buf, 8, 26, GOLD)
        setpx(buf, 33, 8, TOX)
    return buf


def scene_super_yolo(p):
    buf = canvas()
    if p == 1:
        sun(buf, 39, 9, 4)
        h = bruiser(buf, arm_l="out_up", arm_r="sword", legs="step1",
                    mouth="shout", look="right")
        sword_up(buf, h["rh"][0], h["rh"][1])
        speed_lines(buf, 2, 10, (18, 24, 30))
        for (x, y) in ((20, 38), (28, 38), (16, 36), (32, 37)):
            setpx(buf, x, y, TOX)
        spark(buf, 14, 10, TOX_L)
    else:
        sun(buf, 8, 8, 4, phase=1)
        tmp = canvas()
        h = bruiser(tmp, arm_l="up_hi", arm_r="up_hi", legs="step2",
                    mouth="shout", look="up")
        sword_diag(tmp, h["rh"][0], h["rh"][1], 44, 5)
        blit(buf, tmp, 0, -1)
        speed_lines(buf, 2, 11, (20, 26, 32))
        for (x, y) in ((23, 37), (19, 36), (27, 35), (31, 33), (16, 33)):
            setpx(buf, x, y, TOX)
        for (x, y) in ((22, 34), (18, 31)):
            setpx(buf, x, y, TOX_L)
        star4(buf, 42, 10, TOX_L)
        spark(buf, 36, 5, GOLD_L)
    return buf


def scene_remember(p):
    buf = canvas()
    if p == 1:
        h = mage(buf, arm_l="chest", arm_r="chest", look="down")
        for (y, half) in ((0, 1), (1, 2), (2, 3), (3, 3), (4, 2), (5, 1)):
            hline(buf, 22 - half, 25 + half, 18 + y, INK)
        for (y, half) in ((1, 1), (2, 2), (3, 2), (4, 1)):
            hline(buf, 22 - half, 25 + half, 18 + y, VIO)
        hline(buf, 22, 24, 20, VIO_L)
        setpx(buf, 22, 20, VIO_LL)
        spark(buf, 18, 18, VIO_L)
        spark(buf, 30, 24, VIO_L)
        rune(buf, 24, 30, VIO_D)
    else:
        h = mage(buf, arm_l="out", arm_r="chin", look="up", tilt=1)
        disc(buf, 36, 12, 4, VIO_D)
        disc(buf, 36, 12, 3, VIO)
        disc(buf, 36, 12, 2, VIO_L)
        setpx(buf, 35, 11, VIO_LL)
        ring(buf, 36, 12, 6, VIO_D, 1)
        setpx(buf, 30, 12, VIO_L)
        setpx(buf, 42, 12, VIO_L)
        setpx(buf, 36, 5, VIO_L)
        setpx(buf, 36, 19, VIO_L)
        for (x, y) in ((44, 6), (28, 4), (43, 18)):
            spark(buf, x, y, VIO_L)
        setpx(buf, 12, 17, VIO_LL)
    return buf


def scene_grandma(p):
    buf = canvas()
    if p == 1:
        hands = yordle(buf, mouth="small", arms="front", old=True)
        # chal sobre el cuerpo
        rect(buf, 21, 23, 26, 24, GOLD_D)
        hline(buf, 21, 26, 23, GOLD)
        # agujas arriba, abiertas hacia los costados
        line(buf, 19, 28, 11, 19, STEEL_L)
        line(buf, 28, 28, 36, 19, STEEL_L)
        setpx(buf, 10, 18, WHITE)
        setpx(buf, 37, 18, WHITE)
        line(buf, 13, 22, 17, 24, (206, 206, 212))
        line(buf, 34, 22, 30, 24, (206, 206, 212))
        # tejido
        rect(buf, 20, 26, 27, 29, PINK)
        hline(buf, 20, 27, 26, PINK_L)
        hline(buf, 21, 26, 29, PINK_D)
    else:
        hands = yordle(buf, mouth="wide", arms="front", old=True)
        rect(buf, 21, 23, 26, 24, GOLD_D)
        hline(buf, 21, 26, 23, GOLD)
        line(buf, 19, 28, 13, 24, STEEL_L)
        line(buf, 28, 28, 34, 24, STEEL_L)
        setpx(buf, 12, 23, WHITE)
        setpx(buf, 35, 23, WHITE)
        rect(buf, 20, 28, 28, 31, PINK)
        hline(buf, 20, 28, 28, PINK_L)
        hline(buf, 21, 27, 31, PINK_D)
        # ovillo grande
        disc(buf, 34, 33, 4, PINK_D)
        disc(buf, 34, 33, 3, PINK)
        setpx(buf, 33, 32, PINK_L)
        line(buf, 31, 30, 27, 30, PINK)
        spark(buf, 40, 28, PINK_L)
    return buf


def scene_bye(p):
    buf = canvas()
    if p == 1:
        h = bruiser(buf, arm_l="up", arm_r="down", mouth="smile")
        sword_up(buf, h["rh"][0], h["rh"][1])
        spark(buf, 12, 8, GOLD_L)
        star4(buf, 8, 13, GOLD)
        setpx(buf, 18, 5, WHITE)
    else:
        tmp = canvas()
        bruiser(tmp, arm_l="up", arm_r="rest", legs="step1", back=True)
        sword_diag(tmp, 31, 27, 42, 11)
        blit(buf, tmp)
        dust(buf, 8, 37, 2)
        dust(buf, 14, 38, 1)
        setpx(buf, 4, 34, DUST_L)
        spark(buf, 12, 6, GOLD_L)
        star4(buf, 43, 8, GOLD)
    return buf


# ------------------------------------------------------------------- salida
FRAMES = [
    ("hi", [("hi_01.png", lambda: scene_hi(1)),
            ("hi_02.png", lambda: scene_hi(2))]),
    ("idle", [("idle.png", lambda: scene_idle(1)),
              ("idle_blink.png", lambda: scene_idle(2))]),
    ("think", [("think_01.png", lambda: scene_think(1)),
               ("think_02.png", lambda: scene_think(2))]),
    ("talk", [("talk_close.png", lambda: scene_talk(1)),
              ("talk_small.png", lambda: scene_talk(2)),
              ("talk_mid.png", lambda: scene_talk(3)),
              ("talk_wide.png", lambda: scene_talk(4))]),
    ("read", [("read_01.png", lambda: scene_read(1)),
              ("read_02.png", lambda: scene_read(2))]),
    ("write", [("write_01.png", lambda: scene_write(1)),
               ("write_02.png", lambda: scene_write(2))]),
    ("tool", [("tool_01.png", lambda: scene_tool(1)),
              ("tool_02.png", lambda: scene_tool(2))]),
    ("ask", [("ask_01.png", lambda: scene_ask(1)),
             ("ask_02.png", lambda: scene_ask(2))]),
    ("success", [("success_01.png", lambda: scene_success(1)),
                 ("success_02.png", lambda: scene_success(2))]),
    ("failure", [("down_01.png", lambda: scene_failure(1)),
                 ("down_02.png", lambda: scene_failure(2))]),
    ("compact", [("compact_01.png", lambda: scene_compact(1)),
                 ("compact_02.png", lambda: scene_compact(2))]),
    ("delegate", [("delegate_01.png", lambda: scene_delegate(1)),
                  ("delegate_02.png", lambda: scene_delegate(2))]),
    ("explore", [("explore_01.png", lambda: scene_explore(1)),
                 ("explore_02.png", lambda: scene_explore(2))]),
    ("build", [("build_01.png", lambda: scene_build(1)),
               ("build_02.png", lambda: scene_build(2))]),
    ("verify", [("verify_01.png", lambda: scene_verify(1)),
                ("verify_02.png", lambda: scene_verify(2))]),
    ("judge", [("judge_01.png", lambda: scene_judge(1)),
               ("judge_02.png", lambda: scene_judge(2))]),
    ("review", [("review_01.png", lambda: scene_review(1)),
                ("review_02.png", lambda: scene_review(2))]),
    ("jira", [("jira_01.png", lambda: scene_jira(1)),
              ("jira_02.png", lambda: scene_jira(2))]),
    ("jobs", [("jobs_01.png", lambda: scene_jobs(1)),
              ("jobs_02.png", lambda: scene_jobs(2))]),
    ("yolo", [("yolo_01.png", lambda: scene_yolo(1)),
              ("yolo_02.png", lambda: scene_yolo(2))]),
    ("super-yolo", [("super-yolo_01.png", lambda: scene_super_yolo(1)),
                    ("super-yolo_02.png", lambda: scene_super_yolo(2))]),
    ("remember", [("remember_01.png", lambda: scene_remember(1)),
                  ("remember_02.png", lambda: scene_remember(2))]),
    ("grandma", [("grandma_01.png", lambda: scene_grandma(1)),
                 ("grandma_02.png", lambda: scene_grandma(2))]),
    ("bye", [("bye_01.png", lambda: scene_bye(1)),
             ("bye_02.png", lambda: scene_bye(2))]),
]


def ihdr(path):
    with open(path, "rb") as fh:
        data = fh.read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("firma PNG invalida: " + path)
    return struct.unpack(">IIBBBBB", data[16:29])


def verify(path, buf):
    """IHDR a mano + pixeles: 48x40, 8 bits RGBA, sin interlace, sin bordes."""
    w, h, depth, ctype, comp, filt, inter = ihdr(path)
    problemas = []
    if (w, h) != (W, H):
        problemas.append("tamano %dx%d" % (w, h))
    if depth != 8:
        problemas.append("bit depth %d" % depth)
    if ctype != 6:
        problemas.append("color type %d" % ctype)
    if comp or filt or inter:
        problemas.append("compresion/filtro/interlace no estandar")
    opacos = sum(1 for i in range(3, len(buf), 4) if buf[i])
    if opacos < 150:
        problemas.append("frame casi vacio (%d px)" % opacos)
    for x in range(W):
        for y in (0, H - 1):
            if buf[(y * W + x) * 4 + 3]:
                problemas.append("borde (%d,%d) opaco" % (x, y))
                break
    for y in range(H):
        for x in (0, W - 1):
            if buf[(y * W + x) * 4 + 3]:
                problemas.append("borde (%d,%d) opaco" % (x, y))
                break
    if problemas:
        raise SystemExit("%s: %s" % (path, "; ".join(problemas)))
    return w, h, depth, ctype, inter, opacos


def main():
    total = 0
    resumen = []
    for estado, frames in FRAMES:
        carpeta = os.path.join(BASE, estado)
        os.makedirs(carpeta, exist_ok=True)
        for nombre, construir in frames:
            buf = construir()
            ruta = os.path.join(carpeta, nombre)
            datos = encode_png(W, H, buf)
            with open(ruta, "wb") as fh:
                fh.write(datos)
            w, h, depth, ctype, inter, opacos = verify(ruta, buf)
            total += 1
            print("ok %-26s %2dx%-2d depth=%d type=%d interlace=%d px=%d"
                  % (estado + "/" + nombre, w, h, depth, ctype, inter, opacos))
        resumen.append((estado, len(frames)))
    print("\nset lol: %d estados, %d frames -> %s"
          % (len(resumen), total, BASE))
    for estado, cantidad in resumen:
        print("  %-11s %d frames" % (estado, cantidad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
