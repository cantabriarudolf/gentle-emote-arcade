#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set STARCRAFT del fork gentle-emote-arcade (24 estados, 48x40 RGBA).

Pixel art de StarCraft dibujado a mano con rectangulos, sin assets externos y
sin red: solo stdlib (struct + zlib) para escribir el PNG. Dos corridas
seguidas dejan los mismos bytes.

Reparto por escena (un actor por escena, como en minecraft / cs16):

  Marine terran (armadura azul acero, hombreras enormes, visor cian, rifle
  gauss). Es el caballo de batalla del set:
      hi ....... 01 saluda con la mano libre, 02 saludo corto y chispa
      success .. 01 los dos punos arriba, 02 saltito con destello
      bye ...... 01 saluda de frente, 02 de espaldas con la mochila
      yolo ..... 01 y 02 corriendo, piernas cambiadas y lineas de velocidad
      super-yolo 01 y 02 igual pero con sol y estela de fuego
      tool ..... 01 apunta el rifle, 02 dispara (fogonazo + retroceso)
      write .... 01 teclea la consola, 02 las dos manos y texto en el holograma

  Templario protoss (oro, cresta, sin cara, hojas psi cian):
      think .... 01 mano en el menton, 02 cabeza girada
      verify ... 01 alza el check holografico, 02 lo estampa (onda psi)
      judge .... 01 las dos hojas arriba, 02 golpe al piso con onda
      review ... 01 lee el pergamino holografico, 02 marca el renglon
      delegate . 01 reparte a la derecha, 02 a la izquierda (dos sondas)
      remember . 01 cristal khaydarin al pecho, 02 cristal sobre la cabeza
      compact .. 01 entero con pinzas psi, 02 achicado (misma silueta)

  Zergling (caparazon carmesi, espinas, ojos que brillan):
      idle ..... idle.png + idle_blink.png (los ojos se apagan)
      talk ..... 4 bocas con pesos (close / small / mid / wide), misma cara
      ask ...... 01 globo "?" a la derecha, 02 cabeza al otro lado

  SCV terran (cabina amarilla, tren de rodaje, brazo taladro):
      read ..... 01 lee el datapad, 02 pasa la pantalla
      explore .. 01 faro a la izquierda con polvo, 02 faro a la derecha

  Props: la escena entera es el objeto.
      jobs ..... pylon protoss, 01 cargando, 02 encendido con anillo
      build .... centro de mando, 01 en obra con grua, 02 terminado
      jira ..... nave de desembarco, 01 en la plataforma, 02 despegando
      failure .. creep + marine caido, 01 se hunde, 02 el creep lo tapa

  Abuela terran (mono de trabajo, rodete cano, agujas y ovillo):
      grandma .. 01 agujas arriba, 02 agujas abajo con el ovillo

Todo frame: 48x40, RGBA de 8 bits, sin interlace, fondo transparente real,
pies en y=38 y personaje centrado en x=24. Nada queda cortado por el borde.

Salida (relativa a este script):
  ../../emotes/starcraft/<estado>/<estado>_01.png ... 02 (04 en talk)
  idle.png + idle_blink.png, talk_close/small/mid/wide.png,
  failure usa down_01.png / down_02.png

Uso:
  python3 gentle-emote-arcade/scripts/sprites/gen_starcraft.py
Imprime la verificacion IHDR de cada frame (48x40, 8-bit, color type 6,
no interlazado) y devuelve la lista generada.
"""
import math
import os
import struct
import sys
import zlib

W, H = 48, 40
GROUND = 37                  # ultimo pixel del dibujo; el contorno cae en 38
BASE = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "emotes",
    "starcraft"))

# ── paleta StarCraft ───────────────────────────────────────────────────────
INK = (12, 16, 19)           # contorno #0C1013
MAR = (43, 76, 126)          # marina #2B4C7E
MAR_L = (110, 143, 184)      # #6E8FB8
MAR_L2 = (150, 178, 212)
MAR_D = (22, 40, 63)         # #16283F
VIS = (111, 227, 225)        # visor / psi #6FE3E1
VIS_D = (46, 154, 168)       # #2E9AA8
VIS_W = (198, 252, 246)
GOLD = (200, 162, 74)        # oro protoss #C8A24A
GOLD_L = (238, 210, 132)
GOLD_D = (122, 95, 34)       # #7A5F22
GOLD_DD = (74, 56, 22)
ZR = (140, 58, 46)           # caparazon #8C3A2E
ZR_D = (90, 30, 30)          # #5A1E1E
ZR_L = (194, 90, 60)         # #C25A3C
ZR_X = (222, 128, 92)
ZR_DD = (58, 20, 22)
EYE_Z = (255, 214, 106)      # ojos zerg que brillan
EYE_ZD = (186, 128, 42)
SKIN = (217, 160, 121)       # piel #D9A079
SKIN_D = (178, 122, 88)
SKIN_L = (240, 194, 160)
STEEL = (150, 162, 176)
STEEL_D = (100, 110, 124)
STEEL_DD = (54, 62, 74)
STEEL_L = (200, 210, 220)
SCV_Y = (226, 176, 62)
SCV_YL = (250, 214, 118)
SCV_YD = (166, 120, 34)
CREEP = (98, 48, 100)
CREEP_D = (62, 28, 66)
CREEP_L = (146, 78, 142)
RUST = (176, 96, 52)
RUST_D = (128, 64, 34)
RUST_L = (212, 132, 78)
GREEN = (118, 214, 132)
GREEN_D = (52, 138, 84)
RED = (214, 66, 58)
RED_D = (140, 34, 40)
RED_L = (248, 132, 112)
AMBER = (255, 190, 74)
AMBER_D = (198, 128, 32)
WHITE = (246, 250, 254)
PAPER = (232, 240, 236)
PAPER_D = (188, 202, 198)
GREY = (140, 146, 156)
GREY_D = (92, 98, 110)
GREY_L = (188, 194, 204)


# ── PNG / canvas (mismo motor que minecraft y cs16) ────────────────────────
def encode_png(w, h, pixels):
    def chunk(t, body):
        c = t + body
        return (struct.pack(">I", len(body)) + c +
                struct.pack(">I", zlib.crc32(c) & 0xffffffff))
    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def canvas():
    return bytearray(b"\x00\x00\x00\x00" * W * H)


def setpx(buf, x, y, col, a=255):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i:i + 4] = bytes([col[0], col[1], col[2], a])


def rect(buf, x0, y0, x1, y1, col, a=255):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            setpx(buf, x, y, col, a)


def hline(buf, x0, x1, y, col):
    rect(buf, x0, y, x1, y, col)


def vline(buf, x, y0, y1, col):
    rect(buf, x, y0, x, y1, col)


def line(buf, x0, y0, x1, y1, col):
    """Bresenham de 1 px."""
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


def box(buf, x0, y0, x1, y1, fill, edge=INK):
    """Rectangulo con borde de 1 px (alias corto de panel sin esquinas)."""
    panel(buf, x0, y0, x1, y1, fill, None, None, edge, 0)


def panel(buf, x0, y0, x1, y1, fill, light=None, dark=None, edge=INK, cut=0):
    """Placa: relleno + borde de 1 px + bisel luz/sombra y esquinas cortadas."""
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    h = y1 - y0 + 1
    cut = max(0, min(cut, (h - 1) // 2))
    mask = set()
    for j in range(h):
        inset = cut if (j < cut or j >= h - cut) else 0
        for x in range(x0 + inset, x1 - inset + 1):
            mask.add((x, y0 + j))
    if not mask:
        return
    for (x, y) in mask:
        setpx(buf, x, y, fill)
    border = set()
    if edge is not None:
        for (x, y) in mask:
            if ((x - 1, y) not in mask or (x + 1, y) not in mask or
                    (x, y - 1) not in mask or (x, y + 1) not in mask):
                border.add((x, y))
        for (x, y) in border:
            setpx(buf, x, y, edge)
    inner = mask - border
    if light:
        for (x, y) in inner:
            if (x - 1, y) in border or (x, y - 1) in border:
                setpx(buf, x, y, light)
    if dark:
        for (x, y) in inner:
            if (x + 1, y) in border or (x, y + 1) in border:
                setpx(buf, x, y, dark)


def clearpx(buf, x, y):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i:i + 4] = b"\x00\x00\x00\x00"


def contour(buf, col=INK):
    """Contorno de 1 px alrededor de todo lo opaco (silueta de la casa)."""
    add = []
    for y in range(H):
        for x in range(W):
            if buf[(y * W + x) * 4 + 3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and buf[(ny * W + nx) * 4 + 3]:
                    add.append((x, y))
                    break
    for (x, y) in add:
        setpx(buf, x, y, col)


def paste(dst, src, dx=0, dy=0):
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3] == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < W and 0 <= ny < H:
                j = (ny * W + nx) * 4
                dst[j:j + 4] = src[i:i + 4]


blit = paste


def figure(parts, dx=0, dy=0):
    """Une varias piezas, les pone contorno de 1 px y devuelve el lienzo."""
    tmp = canvas()
    for part in parts:
        part(tmp)
    contour(tmp)
    if dx or dy:
        out = canvas()
        paste(out, tmp, dx, dy)
        return out
    return tmp


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
    """Polilinea con contorno de 1 px (brazos, cables, hojas psi)."""
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1], b[0], b[1], INK, t + 1)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1], b[0], b[1], col, t)


def limb(buf, pts, col, light=None, t=4):
    stroke(buf, pts, col, t)
    if light:
        for a, b in zip(pts, pts[1:]):
            line_brush(buf, a[0] - 1, a[1] - 1, b[0] - 1, b[1] - 1, light, 1)


def spark(buf, x, y, col=AMBER):
    setpx(buf, x, y, col)
    setpx(buf, x - 1, y, col)
    setpx(buf, x + 1, y, col)
    setpx(buf, x, y - 1, col)
    setpx(buf, x, y + 1, col)


def sparkle(buf, x, y, col=AMBER, core=WHITE):
    spark(buf, x, y, col)
    setpx(buf, x, y, core)


def burst(buf, cx, cy, r, col, core=WHITE):
    for k in range(0, 360, 45):
        rad = math.radians(k)
        line(buf, cx, cy, cx + int(round(math.cos(rad) * r)),
             cy + int(round(math.sin(rad) * r)), col)
    circle(buf, cx, cy, max(1, r // 3), core)


def dust(buf, cx, cy, r=3, col=GREY):
    circle(buf, cx, cy, r, col)
    circle(buf, cx - r, cy + 1, 1, GREY_L)
    circle(buf, cx + r, cy, 1, GREY_L)
    setpx(buf, cx, cy - r, WHITE)


def smoke(buf, x, y, t=0):
    circle(buf, x, y, 2, GREY_D)
    circle(buf, x, y, 1, GREY)
    setpx(buf, x, y - 1, GREY_L)
    if t:
        circle(buf, x + 3, y - 3, 2, GREY_D)
        circle(buf, x + 3, y - 3, 1, GREY)


def waves(buf, x, y, col=VIS, steps=2):
    for k in range(steps):
        xk = x + k * 2
        yy = 2 + k
        setpx(buf, xk, y - yy, col)
        setpx(buf, xk, y - yy + 1, col)
        setpx(buf, xk, y + yy, col)
        setpx(buf, xk, y + yy - 1, col)


def glow(buf, cx, cy, r, col, a=90):
    """Halo suave (alfa real, se dibuja despues del contorno)."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if d <= r * r and d > (r - 2) * (r - 2):
                setpx(buf, x, y, col, a)


# ── tipografia 3x5 ─────────────────────────────────────────────────────────
FONT = {
    "A": ["###", "#.#", "###", "#.#", "#.#"],
    "C": ["###", "#..", "#..", "#..", "###"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "##.", "#..", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "M": ["#.#", "###", "#.#", "#.#", "#.#"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#.."],
    "?": [".##.", "#..#", "..#.", "....", "..#."],
    "!": ["#", "#", "#", ".", "#"],
    ".": [".", ".", ".", ".", "#"],
    ":": [".", "#", ".", "#", "."],
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
}


def text(buf, word, x0, y0, col, scale=1, outline=None):
    x = x0
    for ch in word:
        if ch == " ":
            x += 2 * scale
            continue
        g = FONT[ch]
        gw = len(g[0])
        for ry, row in enumerate(g):
            for i, c in enumerate(row):
                if c != "#":
                    continue
                for sy in range(scale):
                    for sx in range(scale):
                        px = x + i * scale + sx
                        py = y0 + ry * scale + sy
                        if outline is not None:
                            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                                setpx(buf, px + dx, py + dy, outline)
                        setpx(buf, px, py, col)
        x += (gw + 1) * scale


def bubble(buf, x, y, w, h, glyph="?", col=VIS_D, edge=INK, fill=WHITE,
           tail="left"):
    rect(buf, x + 1, y, x + w - 2, y + h - 1, edge)
    rect(buf, x, y + 1, x + w - 1, y + h - 2, edge)
    rect(buf, x + 1, y + 1, x + w - 2, y + h - 2, fill)
    # cola hacia el personaje
    if tail == "left":
        for (px, py) in ((x + 3, y + h), (x + 2, y + h + 1),
                         (x + 1, y + h + 2)):
            setpx(buf, px, py, edge)
        setpx(buf, x + 3, y + h - 1, fill)
    else:
        for (px, py) in ((x + w - 4, y + h), (x + w - 3, y + h + 1),
                         (x + w - 2, y + h + 2)):
            setpx(buf, px, py, edge)
        setpx(buf, x + w - 4, y + h - 1, fill)
    tw = len(FONT[glyph][0])
    text(buf, glyph, x + (w - tw * 2) // 2, y + (h - 5 * 2) // 2 - 1,
         col, scale=2, outline=None)


# ── marine terran ──────────────────────────────────────────────────────────
MARINE_LEGS = {
    # ((muslo x0,y0,x1,y1), (bota x0,y0,x1,y1)) por pierna
    "stand": (((17, 24, 22, 33), (15, 33, 23, GROUND)),
              ((25, 24, 30, 33), (25, 33, 33, GROUND))),
    "walk1": (((15, 24, 20, 32), (13, 32, 21, GROUND)),
              ((27, 24, 32, 32), (26, 33, 34, GROUND))),
    "walk2": (((20, 24, 25, 32), (18, 33, 26, GROUND)),
              ((25, 24, 30, 31), (26, 32, 34, GROUND))),
    "run1": (((13, 24, 18, 30), (10, 31, 20, GROUND)),
             ((28, 24, 33, 31), (27, 33, 37, GROUND))),
    "run2": (((19, 24, 24, 31), (16, 33, 26, GROUND)),
             ((26, 24, 31, 30), (26, 31, 36, GROUND))),
    "air": (((15, 25, 20, 30), (12, 30, 21, 34)),
            ((27, 25, 32, 30), (26, 31, 35, 34))),
}


def marine_legs(b, oy=0, pose="stand"):
    for (thigh, boot) in MARINE_LEGS[pose]:
        tx0, ty0, tx1, ty1 = thigh
        bx0, by0, bx1, by1 = boot
        panel(b, tx0, ty0 + oy, tx1, ty1 + oy, MAR, MAR_L, MAR_D, cut=1)
        # rodillera
        panel(b, tx0 - 1, ty1 - 2 + oy, tx1 + 1, ty1 + oy, MAR_D, MAR, INK)
        # bota blindada
        panel(b, bx0, by0 + oy, bx1, by1 + oy, (38, 46, 58), (66, 78, 94), INK,
              cut=1)
        hline(b, bx0 + 1, bx1 - 1, by1 - 1 + oy, INK)


def marine_torso(b, oy=0, back=False, pack=False):
    # peto
    panel(b, 18, 12 + oy, 29, 26 + oy, MAR, MAR_L, MAR_D, cut=1)
    if pack or back:
        # mochila de energia (TB-2): dos tanques y toberas
        panel(b, 17, 11 + oy, 30, 25 + oy, STEEL_DD, STEEL_D, INK, cut=1)
        panel(b, 19, 12 + oy, 22, 22 + oy, STEEL_D, STEEL, INK, cut=1)
        panel(b, 25, 12 + oy, 28, 22 + oy, STEEL_D, STEEL, INK, cut=1)
        hline(b, 19, 22, 13 + oy, STEEL_L)
        hline(b, 25, 28, 13 + oy, STEEL_L)
        rect(b, 23, 15 + oy, 24, 20 + oy, INK)
        # toberas
        panel(b, 19, 23 + oy, 22, 26 + oy, INK, None, None, INK)
        panel(b, 25, 23 + oy, 28, 26 + oy, INK, None, None, INK)
        setpx(b, 20, 25 + oy, AMBER_D)
        setpx(b, 26, 25 + oy, AMBER_D)
    else:
        # placa pectoral y luces
        panel(b, 20, 13 + oy, 27, 18 + oy, MAR_L, MAR_L2, MAR, cut=1)
        hline(b, 21, 26, 16 + oy, MAR_D)
        setpx(b, 24, 15 + oy, VIS)
        setpx(b, 23, 15 + oy, VIS_D)
        # rejillas del vientre
        for y in (20, 22):
            hline(b, 20, 27, y + oy, MAR_D)
        # cinturon
        rect(b, 18, 24 + oy, 29, 26 + oy, MAR_D)
        hline(b, 18, 29, 24 + oy, INK)
        panel(b, 22, 24 + oy, 25, 26 + oy, STEEL_D, STEEL, INK)
    # hombreras enormes
    panel(b, 11, 12 + oy, 19, 21 + oy, MAR, MAR_L, MAR_D, cut=2)
    panel(b, 28, 12 + oy, 36, 21 + oy, MAR, MAR_L, MAR_D, cut=2)
    hline(b, 13, 17, 18 + oy, MAR_D)
    hline(b, 30, 34, 18 + oy, MAR_D)
    setpx(b, 14, 15 + oy, MAR_L2)
    setpx(b, 31, 15 + oy, MAR_L2)
    # baliza de la hombrera izquierda
    setpx(b, 13, 14 + oy, AMBER)
    setpx(b, 13, 15 + oy, AMBER_D)


def marine_head(b, oy=0, visor="on", back=False, lamp=True):
    panel(b, 19, 4 + oy, 28, 12 + oy, MAR, MAR_L, MAR_D, cut=2)
    if back:
        rect(b, 20, 6 + oy, 27, 10 + oy, MAR_D)
        hline(b, 21, 26, 6 + oy, MAR)
        setpx(b, 21, 8 + oy, MAR_L)
        setpx(b, 26, 8 + oy, MAR_L)
        vline(b, 23, 7 + oy, 10 + oy, MAR)
    else:
        rect(b, 20, 6 + oy, 27, 6 + oy, INK)
        if visor == "on":
            rect(b, 20, 7 + oy, 27, 8 + oy, VIS)
            hline(b, 20, 27, 8 + oy, VIS_D)
            hline(b, 20, 23, 7 + oy, VIS_W)
        elif visor == "dim":
            rect(b, 20, 7 + oy, 27, 8 + oy, VIS_D)
            hline(b, 22, 25, 7 + oy, VIS)
        elif visor == "off":
            rect(b, 20, 7 + oy, 27, 8 + oy, (20, 34, 40))
            hline(b, 22, 25, 9 + oy, VIS_D)
        elif visor == "angry":
            rect(b, 20, 7 + oy, 27, 8 + oy, VIS)
            hline(b, 20, 24, 7 + oy, VIS_W)
            hline(b, 20, 21, 6 + oy, MAR_D)
            hline(b, 26, 27, 6 + oy, MAR_D)
        # rejilla de la barbilla y tornillos
        rect(b, 21, 10 + oy, 26, 10 + oy, MAR_D)
        for x in (22, 24, 26):
            setpx(b, x, 10 + oy, MAR)
        setpx(b, 20, 6 + oy, AMBER)
    if lamp:
        vline(b, 29, 2 + oy, 4 + oy, STEEL_D)
        setpx(b, 29, 1 + oy, AMBER)


def marine(b, oy=0, legs="stand", visor="on", back=False, pack=False,
           lamp=True):
    marine_legs(b, oy, legs)
    marine_torso(b, oy, back=back, pack=pack)
    marine_head(b, oy, visor=visor, back=back, lamp=lamp)


def glove(b, x, y, fist=False, col=MAR_D, light=MAR_L):
    panel(b, x - 2, y - 2, x + 2, y + 2, col, light, INK, cut=1)
    if fist:
        hline(b, x - 1, x, y - 1, INK)
    else:
        vline(b, x, y - 1, y, INK)


def marine_arm(b, pts, oy=0, col=MAR, light=MAR_L2):
    limb(b, [(x, y + oy) for (x, y) in pts], col, light, 4)


def gauss(b, x0, y0, x1, y1, coil=True):
    """Rifle gauss sobre una recta: culata en (x0,y0), boca en (x1,y1)."""
    line_brush(b, x0, y0, x1, y1, INK, 5)
    line_brush(b, x0, y0, x1, y1, STEEL_DD, 3)
    # filo claro arriba
    line_brush(b, x0, y0 - 1, x1, y1 - 1, STEEL_D, 1)
    # culata y empunadura
    panel(b, x0 - 3, y0 - 2, x0 + 2, y0 + 3, STEEL_DD, STEEL_D, INK, cut=1)
    # cargador
    panel(b, x0 + 4, y0 + 2, x0 + 7, y0 + 5, STEEL_DD, None, INK)
    # bobina de energia
    if coil:
        vline(b, x1 - 5, y1 - 2, y1 + 2, VIS_D)
        setpx(b, x1 - 4, y1 - 1, VIS)
        setpx(b, x1 - 3, y1, VIS_W)
        setpx(b, x1 - 5, y1 + 1, VIS)
    # bocacha
    panel(b, x1 - 2, y1 - 2, x1, y1 + 2, STEEL_DD, None, INK)


def muzzle(buf, x, y, big=False):
    """Fogonazo de la boca del rifle."""
    r = 4 if big else 3
    for k in range(0, 360, 45):
        rad = math.radians(k)
        line(buf, x, y, x + int(round(math.cos(rad) * r)),
             y + int(round(math.sin(rad) * r)), AMBER)
    circle(buf, x, y, r - 2, AMBER)
    circle(buf, x, y, 1, WHITE)
    setpx(buf, x + r - 1, y - 1, AMBER_D)


# ── templario protoss ─────────────────────────────────────────────────────
ZEALOT_LEGS = {
    "stand": (((18, 24, 22, 32), (16, 32, 23, GROUND)),
              ((26, 24, 30, 32), (25, 32, 32, GROUND))),
    "walk1": (((16, 24, 20, 31), (14, 31, 21, GROUND)),
              ((27, 24, 31, 32), (26, 32, 33, GROUND))),
    "walk2": (((20, 24, 24, 32), (18, 32, 25, GROUND)),
              ((26, 24, 30, 31), (25, 31, 33, GROUND))),
    "wide": (((16, 24, 20, 31), (14, 31, 21, GROUND)),
             ((28, 24, 32, 31), (26, 31, 33, GROUND))),
    "air": (((17, 25, 21, 30), (15, 30, 22, 33)),
            ((27, 25, 31, 30), (26, 30, 33, 33))),
}


def zealot_legs(b, oy=0, pose="stand"):
    for (thigh, boot) in ZEALOT_LEGS[pose]:
        tx0, ty0, tx1, ty1 = thigh
        bx0, by0, bx1, by1 = boot
        panel(b, tx0, ty0 + oy, tx1, ty1 + oy, GOLD, GOLD_L, GOLD_D, cut=1)
        panel(b, tx0 - 1, ty1 - 2 + oy, tx1 + 1, ty1 + oy, GOLD_DD, GOLD_D)
        panel(b, bx0, by0 + oy, bx1, by1 + oy, GOLD_D, GOLD, GOLD_DD, cut=1)
        hline(b, bx0 + 1, bx1 - 1, by1 - 1 + oy, GOLD_DD)


def zealot_torso(b, oy=0, back=False):
    panel(b, 18, 12 + oy, 29, 26 + oy, GOLD, GOLD_L, GOLD_D, cut=1)
    if back:
        panel(b, 19, 13 + oy, 28, 24 + oy, GOLD_D, None, GOLD_DD, cut=1)
        vline(b, 24, 15 + oy, 23 + oy, GOLD_DD)
        hline(b, 20, 27, 19 + oy, GOLD_DD)
    else:
        # peto con gema psi y falda de placas
        panel(b, 20, 13 + oy, 27, 19 + oy, GOLD_L, (250, 232, 168), GOLD, cut=1)
        rect(b, 23, 15 + oy, 24, 17 + oy, VIS_D)
        setpx(b, 23, 15 + oy, VIS)
        setpx(b, 24, 16 + oy, VIS_W)
        hline(b, 19, 28, 20 + oy, GOLD_D)
        for x in (19, 22, 25, 28):
            vline(b, x, 21 + oy, 25 + oy, GOLD_D)
        rect(b, 18, 24 + oy, 29, 25 + oy, GOLD_D)
    # hombreras
    panel(b, 11, 12 + oy, 19, 21 + oy, GOLD, GOLD_L, GOLD_D, cut=2)
    panel(b, 28, 12 + oy, 36, 21 + oy, GOLD, GOLD_L, GOLD_D, cut=2)
    hline(b, 13, 17, 18 + oy, GOLD_D)
    hline(b, 30, 34, 18 + oy, GOLD_D)
    setpx(b, 14, 15 + oy, (250, 232, 168))
    setpx(b, 31, 15 + oy, (250, 232, 168))


def zealot_head(b, oy=0, ox=0, crest=True, glow="on", tilt=0):
    ox += tilt
    if crest:
        # cresta de templario
        for j in range(0, 6):
            w = j
            hline(b, 24 + ox - w, 24 + ox + w, 0 + oy + j, GOLD_D)
        vline(b, 24 + ox, 1 + oy, 4 + oy, GOLD)
        setpx(b, 24 + ox, 0 + oy, GOLD_L)
        setpx(b, 23 + ox, 0 + oy, INK)
    panel(b, 19 + ox, 5 + oy, 28 + ox, 14 + oy, GOLD, GOLD_L, GOLD_D, cut=2)
    # la cara es una ranura: nada de ojos humanos
    rect(b, 20 + ox, 8 + oy, 27 + ox, 11 + oy, GOLD_DD)
    if glow == "on":
        hline(b, 21 + ox, 26 + ox, 10 + oy, VIS)
        hline(b, 21 + ox, 23 + ox, 9 + oy, VIS_W)
    elif glow == "dim":
        hline(b, 21 + ox, 26 + ox, 10 + oy, VIS_D)
    elif glow == "off":
        hline(b, 21 + ox, 26 + ox, 10 + oy, (30, 46, 46))
    # mandibula y remaches
    hline(b, 21 + ox, 26 + ox, 13 + oy, GOLD_D)
    setpx(b, 20 + ox, 6 + oy, GOLD_L)
    setpx(b, 27 + ox, 6 + oy, GOLD_L)


def zealot(b, oy=0, legs="stand", back=False, glow="on", crest=True, tilt=0):
    zealot_legs(b, oy, legs)
    zealot_torso(b, oy, back=back)
    zealot_head(b, oy, crest=crest, glow=glow, tilt=tilt)


def zealot_arm(b, pts, oy=0, col=GOLD, light=GOLD_L):
    limb(b, [(x, y + oy) for (x, y) in pts], col, light, 4)


def psi_blade(b, x, y, x1, y1, dim=False):
    """Hoja psi que sale del guante (x,y) hacia (x1,y1)."""
    mx, my = (x + x1) // 2, (y + y1) // 2
    base = VIS_D if dim else VIS
    core = VIS_W if not dim else VIS
    line_brush(b, x, y, mx, my, VIS_D, 4)
    line_brush(b, x, y, mx, my, base, 2)
    line_brush(b, mx, my, x1, y1, base, 2)
    line_brush(b, mx, my, x1, y1, core, 1)
    setpx(b, x1, y1, WHITE if not dim else VIS_W)
    setpx(b, x1 - 1, y1, WHITE if not dim else VIS_W)


def gauntlet(b, x, y, col=GOLD_D, light=GOLD):
    panel(b, x - 2, y - 2, x + 2, y + 2, col, light, GOLD_DD, cut=1)


# ══════════════════════════════════════════════════════════════════════════
# actores que faltaban: zergling, SCV, abuela terran
# ══════════════════════════════════════════════════════════════════════════

ZERG_PAWS = {
    "stand": (16, 21, 27, 32),
    "step1": (14, 22, 28, 33),
    "step2": (18, 20, 26, 31),
}


def zergling_body(b, oy=0, lift=0, pose="stand"):
    """Cuerpo bajo y alargado, caparazon carmesi, lomo de espinas y cola."""
    cy = 28 + oy - lift
    ellipse(b, 21, cy + 5, 10, 5, ZR_D)
    ellipse(b, 20, cy + 4, 8, 3, ZR)
    ellipse(b, 17, cy + 2, 4, 2, ZR_L)
    for x, alto in ((14, 3), (18, 5), (23, 5), (28, 3)):
        vline(b, x, cy + 2 - alto, cy + 2, ZR_D)
        setpx(b, x, cy + 1 - alto, ZR_X)
    # cola
    line_brush(b, 13, cy + 6, 8, cy + 4, ZR_D, 2)
    setpx(b, 7, cy + 3, ZR_X)
    for x in ZERG_PAWS[pose]:
        vline(b, x, cy + 8, GROUND - 2, ZR_D)
        hline(b, x - 1, x + 2, GROUND - 1, ZR_DD)
        setpx(b, x + 2, GROUND - 1, ZR)


def zergling_head(b, oy=0, blink=False, mouth="line", dx=0, dy=0, lift=0):
    hx = 34 + dx
    hy = 21 + oy + dy - lift
    panel(b, hx - 4, hy - 4, hx + 3, hy + 3, ZR, ZR_L, ZR_D, cut=1)
    # hocico que sobresale
    panel(b, hx + 3, hy - 1, hx + 6, hy + 2, ZR_D, ZR, ZR_DD, cut=1)
    # mandibulas
    line(b, hx + 5, hy + 2, hx + 7, hy + 4, ZR_DD)
    line(b, hx + 5, hy - 1, hx + 7, hy - 3, ZR_DD)
    if mouth in ("open", "wide"):
        box(b, hx + 3, hy + 1, hx + 6, hy + 2, ZR_DD)
        if mouth == "wide":
            box(b, hx + 2, hy + 1, hx + 6, hy + 3, ZR_DD)
    elif mouth == "small":
        hline(b, hx + 4, hx + 6, hy + 1, ZR_DD)
    else:
        hline(b, hx + 3, hx + 6, hy + 1, ZR_D)
    for ex in (hx - 1, hx + 2):
        if blink:
            hline(b, ex, ex + 1, hy - 2, ZR_DD)
        else:
            setpx(b, ex, hy - 2, EYE_Z)
            setpx(b, ex + 1, hy - 2, EYE_ZD)
            setpx(b, ex, hy - 1, EYE_ZD)


def zergling(b, oy=0, blink=False, mouth="line", dx=0, pose="stand", lift=0):
    zergling_body(b, oy, lift, pose)
    zergling_head(b, oy, blink, mouth, dx, 0, lift)
    # garra delantera
    limb(b, [(30, 28 + oy - lift), (33, 33 + oy - lift), (31, 36 + oy - lift)],
         ZR, ZR_L, 3)


def scv_tracks(b, oy=0):
    """Tren de rodaje: dos orugas oscuras."""
    for x0, x1 in ((12, 22), (26, 36)):
        box(b, x0, 32 + oy, x1, GROUND - 1, STEEL_DD, INK)
        hline(b, x0 + 1, x1 - 1, 33 + oy, STEEL)
        for x in range(x0 + 2, x1, 3):
            setpx(b, x, 35 + oy, STEEL_D)


def scv_body(b, oy=0, drill="up"):
    scv_tracks(b, oy)
    panel(b, 17, 18 + oy, 31, 32 + oy, SCV_Y, SCV_YL, SCV_YD, cut=1)
    panel(b, 19, 13 + oy, 29, 19 + oy, SCV_Y, SCV_YL, SCV_YD, cut=1)
    hline(b, 20, 28, 15 + oy, INK)          # visera
    hline(b, 21, 27, 16 + oy, VIS_D)
    setpx(b, 22, 16 + oy, VIS)
    # brazo taladro
    if drill == "up":
        limb(b, [(31, 22 + oy), (35, 20 + oy), (37, 15 + oy)], STEEL_D, STEEL_L, 3)
        line_brush(b, 36, 15 + oy, 39, 10 + oy, STEEL, 2)
        setpx(b, 40, 9 + oy, STEEL_L)
    else:
        limb(b, [(31, 24 + oy), (35, 27 + oy), (38, 29 + oy)], STEEL_D, STEEL_L, 3)
        line_brush(b, 37, 29 + oy, 40, 31 + oy, STEEL, 2)
        setpx(b, 41, 32 + oy, STEEL_L)


def datapad(b, x, y, page=0):
    """Datapad terran con una pantalla holografica."""
    box(b, x, y, x + 8, y + 6, STEEL_DD, INK)
    box(b, x + 1, y + 1, x + 7, y + 5, PAPER, INK)
    if page == 0:
        for k in range(3):
            hline(b, x + 2, x + 6, y + 2 + k, PAPER_D)
    else:
        for k in range(2):
            hline(b, x + 2, x + 6, y + 2 + k, PAPER_D)
        hline(b, x + 2, x + 5, y + 4, VIS_D)


def abuela(b, oy=0, needles="up"):
    """Abuela terran: mono de trabajo, rodete cano, agujas de tejer."""
    # falda / mono
    panel(b, 16, 24 + oy, 32, GROUND - 1, CREEP_D, CREEP, INK, cut=1)
    hline(b, 17, 31, 27 + oy, CREEP_L)
    # torso
    panel(b, 17, 17 + oy, 31, 25 + oy, RUST, RUST_L, RUST_D, cut=1)
    # delantal
    box(b, 20, 20 + oy, 28, 27 + oy, PAPER, PAPER_D)
    # brazos
    limb(b, [(17, 19 + oy), (13, 23 + oy)], RUST, RUST_L, 3)
    if needles == "up":
        limb(b, [(31, 19 + oy), (35, 15 + oy), (36, 10 + oy)], RUST, RUST_L, 3)
    else:
        limb(b, [(31, 20 + oy), (34, 24 + oy), (34, 29 + oy)], RUST, RUST_L, 3)
    # cabeza
    disc(b, 24, 13 + oy, 6, SKIN)
    hline(b, 18, 30, 11 + oy, SKIN_L)
    # pelo y rodete
    for x in range(18, 31):
        hline(b, x, x, 8 + oy, GREY_L)
    rect(b, 17, 9 + oy, 21, 14 + oy, GREY_L)
    rect(b, 27, 9 + oy, 31, 14 + oy, GREY)
    disc(b, 24, 6 + oy, 3, GREY_L)
    # ojos y boca
    setpx(b, 21, 13 + oy, INK)
    setpx(b, 27, 13 + oy, INK)
    hline(b, 23, 25, 16 + oy, SKIN_D)
    # agujas y ovillo
    if needles == "up":
        line_brush(b, 35, 10 + oy, 40, 3 + oy, STEEL_L, 1)
        line_brush(b, 37, 11 + oy, 42, 5 + oy, STEEL, 1)
        setpx(b, 41, 2 + oy, WHITE)
        setpx(b, 43, 4 + oy, WHITE)
    else:
        line_brush(b, 34, 29 + oy, 39, 33 + oy, STEEL_L, 1)
        line_brush(b, 36, 30 + oy, 41, 35 + oy, STEEL, 1)
        disc(b, 38, 35 + oy, 3, RED_D)
        disc(b, 38, 34 + oy, 2, RED)
        setpx(b, 37, 33 + oy, RED_L)


# ══════════════════════════════════════════════════════════════════════════
# props: la escena entera es el objeto
# ══════════════════════════════════════════════════════════════════════════

def pylon(b, stage=0):
    """Pylon protoss: cristal ancho sobre tripode, apagado o encendido."""
    col = VIS if stage else VIS_D
    core = VIS_W if stage else VIS
    # cristal: diamante de 15 filas
    for k in range(15):
        w = min(k, 14 - k) // 2 + 1
        y = 7 + k
        hline(b, 24 - w, 24 + w, y, GOLD_D)
        if w > 1:
            hline(b, 25 - w, 23 + w, y, col)
        else:
            setpx(b, 24, y, col)
    vline(b, 24, 10, 20, core)
    setpx(b, 23, 12, WHITE)
    setpx(b, 25, 17, core)
    hline(b, 20, 28, 22, GOLD_D)
    hline(b, 21, 27, 23, GOLD)
    # tripode
    for x0, y0 in ((14, GROUND - 1), (24, GROUND), (34, GROUND - 1)):
        line_brush(b, 24, 24, x0, y0, GOLD_D, 2)
        setpx(b, x0, y0, GOLD)
    hline(b, 22, 26, 24, GOLD_DD)
    if stage:
        ring(b, 24, 24, 10, VIS_D)
        glow(b, 24, 17, 11, VIS, 40)
        sparkle(b, 13, 20)
        sparkle(b, 35, 15, VIS_D)


def command_center(b, stage=0):
    """Centro de mando terran: plataforma ancha, cupula y antena."""
    panel(b, 6, 26, 42, GROUND - 1, STEEL_DD, STEEL_D, INK, cut=1)
    hline(b, 7, 41, 29, STEEL)
    panel(b, 10, 18, 38, 26, STEEL_D, STEEL, STEEL_DD, cut=2)
    if stage == 0:
        # en obra: andamio y grua
        for x in (12, 22, 32):
            for y in range(18, 28, 3):
                hline(b, x, x + 2, y, RUST)
            vline(b, x, 18, 27, RUST_D)
        line_brush(b, 38, 6, 38, 20, RUST, 2)
        line_brush(b, 30, 6, 38, 6, RUST, 2)
        line_brush(b, 30, 6, 30, 12, RUST_D, 1)
        box(b, 28, 12, 32, 16, STEEL_D, INK)
    else:
        # terminado: cupula, luces y antena
        for k in range(6):
            hline(b, 16 + k, 32 - k, 17 - k, STEEL_L)
        hline(b, 17, 31, 18, STEEL)
        for x in range(12, 38, 4):
            setpx(b, x, 23, AMBER)
        vline(b, 33, 2, 10, STEEL)
        setpx(b, 33, 1, RED)
        setpx(b, 32, 4, AMBER)
    dust(b, 8, GROUND - 2, 3)
    dust(b, 40, GROUND - 2, 3)


def dropship(b, stage=0):
    """Nave de desembarco: en la plataforma o despegando."""
    oy = 0 if stage == 0 else -6
    # plataforma
    if stage == 0:
        panel(b, 4, 32, 44, GROUND - 1, STEEL_DD, STEEL_D, INK, cut=1)
        for x in range(8, 42, 6):
            setpx(b, x, 35, AMBER_D)
    # casco
    for k, (x0, x1) in enumerate(((14, 34), (10, 38), (8, 40), (10, 38),
                                  (14, 34), (18, 30))):
        hline(b, x0, x1, 8 + oy + k, MAR_D)
    hline(b, 10, 38, 10 + oy, MAR)
    hline(b, 12, 36, 9 + oy, MAR_L)
    # cabina
    box(b, 28, 8 + oy, 34, 11 + oy, VIS_D, INK)
    setpx(b, 30, 9 + oy, VIS_W)
    # motores
    for x in (13, 33):
        panel(b, x, 13 + oy, x + 3, 16 + oy, STEEL_DD, STEEL_D, INK)
    if stage == 0:
        hline(b, 12, 36, 18 + oy, STEEL_D)
        for x in (16, 24, 32):
            vline(b, x, 18 + oy, 20 + oy, STEEL_DD)
    else:
        for x in (13, 33):
            for k in range(4):
                setpx(b, x + 1, 17 + oy + k, AMBER if k % 2 else RED)
            smoke(b, x + 1, 22 + oy, 1)
        speed_line = 1


def creep_pool(b, stage=0):
    """Charco de creep con burbujas; en stage 1 tapa mas."""
    alto = 5 if stage == 0 else 8
    for k in range(alto):
        wx = 14 - k // 2
        hline(b, 24 - wx, 24 + wx, GROUND - 1 - k, CREEP_D)
    hline(b, 12, 36, GROUND - 1, CREEP)
    for x in (16, 22, 29, 34):
        setpx(b, x, GROUND - 2 - (x % 3), CREEP_L)
    if stage == 1:
        for x in (18, 26, 31):
            setpx(b, x, GROUND - 4, CREEP_L)


def fallen_marine(b, sink=0):
    """Marine caido de costado, el rifle suelto al lado."""
    y = 32 + sink
    # piernas
    panel(b, 8, y + 2, 17, y + 5, MAR_D, MAR_L, INK, cut=1)
    # torso
    panel(b, 17, y, 29, y + 6, MAR, MAR_L, MAR_D, cut=1)
    hline(b, 19, 27, y + 2, MAR_L)
    # hombrera
    panel(b, 27, y - 1, 33, y + 4, MAR, MAR_L, MAR_D, cut=1)
    # casco
    disc(b, 34, y + 2, 4, MAR)
    hline(b, 32, 36, y + 1, VIS_D)
    setpx(b, 34, y + 1, VIS)
    # rifle suelto
    line_brush(b, 12, GROUND - 1, 24, GROUND - 2, STEEL_DD, 2)
    setpx(b, 25, GROUND - 2, STEEL_L)


# ══════════════════════════════════════════════════════════════════════════
# utilidades de escena
# ══════════════════════════════════════════════════════════════════════════

def sun(b, cx, cy, r=4):
    for k in range(0, 360, 45):
        rad = math.radians(k)
        line(b, cx + int(round(math.cos(rad) * (r + 1))),
             cy + int(round(math.sin(rad) * (r + 1))),
             cx + int(round(math.cos(rad) * (r + 3))),
             cy + int(round(math.sin(rad) * (r + 3))), AMBER)
    disc(b, cx, cy, r, AMBER)
    disc(b, cx - 1, cy - 1, r - 2, AMBER_D)
    setpx(b, cx, cy, WHITE)


def speed_lines(b, y):
    for k in range(3):
        yy = y + k * 4
        hline(b, 2, 8 + k * 2, yy, STEEL_D)
        hline(b, 38 - k * 2, 45, yy, STEEL_D)


def holo_check(b, x, y, stamped=False):
    """Tilde holografico protoss."""
    col = VIS if stamped else VIS_D
    ring(b, x, y, 5, col)
    if stamped:
        ring(b, x, y, 7, VIS_D)
    line_brush(b, x - 2, y, x, y + 2, col, 1)
    line_brush(b, x, y + 2, x + 3, y - 2, col, 1)
    if stamped:
        sparkle(b, x - 6, y - 5, VIS_D)
        sparkle(b, x + 6, y + 5, VIS_D)


def scroll(b, x, y, mark=False):
    box(b, x, y, x + 11, y + 9, PAPER, INK)
    hline(b, x, x + 11, y, PAPER_D)
    hline(b, x, x + 11, y + 9, PAPER_D)
    for k in range(3):
        hline(b, x + 2, x + 9 - k, y + 2 + k * 2, PAPER_D)
    if mark:
        vline(b, x + 3, y + 2, y + 8, RED_D)
        setpx(b, x + 2, y + 8, RED)


def crystal(b, x, y, lit=True):
    """Cristal khaydarin."""
    col = VIS_W if lit else VIS_D
    base = VIS if lit else VIS_D
    for k in range(6):
        w = 2 if k in (2, 3) else 1
        hline(b, x - w, x + w, y + k, base)
    vline(b, x, y + 1, y + 4, col)
    setpx(b, x - 1, y + 2, WHITE)
    if lit:
        glow(b, x, y + 3, 6, VIS, 46)


def console(b, x, y, lit=False):
    """Consola terran con pantalla holografica."""
    panel(b, x, y, x + 10, y + 8, STEEL_DD, STEEL_D, INK, cut=1)
    box(b, x + 1, y + 1, x + 9, y + 6, STEEL_DD, STEEL)
    if lit:
        for k in range(3):
            hline(b, x + 3, x + 7, y + 2 + k * 2, VIS_D)
        setpx(b, x + 3, y + 2, VIS_W)
    else:
        hline(b, x + 3, x + 7, y + 3, STEEL)


# ══════════════════════════════════════════════════════════════════════════
# las 24 escenas
# ══════════════════════════════════════════════════════════════════════════

def escena_hi(b, n):
    marine(b, legs="stand")
    if n == 0:
        marine_arm(b, [(30, 18), (33, 14), (35, 9)])
        glove(b, 36, 7, fist=True)
        setpx(b, 38, 4, AMBER)
    else:
        marine_arm(b, [(30, 18), (34, 16), (36, 13)])
        glove(b, 37, 12)
        spark(b, 39, 9)
        spark(b, 41, 12)


def escena_success(b, n):
    if n == 0:
        marine(b, legs="stand")
        gy = 6
    else:
        marine(b, oy=-2, legs="air")
        gy = 4
    marine_arm(b, [(30, 18), (33, 13), (34, 8 + (0 if n == 0 else -2))])
    glove(b, 35, gy, fist=True)
    marine_arm(b, [(17, 18), (14, 13), (13, 8 + (0 if n == 0 else -2))])
    glove(b, 12, gy, fist=True)
    if n == 0:
        sparkle(b, 41, 6)
        sparkle(b, 6, 8)
    else:
        burst(b, 24, 6, 5, AMBER)
        dust(b, 14, GROUND - 1, 3)
        dust(b, 34, GROUND - 1, 3)


def escena_bye(b, n):
    if n == 0:
        marine(b, legs="stand")
        marine_arm(b, [(30, 18), (34, 17), (36, 14)])
        glove(b, 37, 13)
        setpx(b, 39, 10, AMBER)
    else:
        marine(b, legs="walk1", back=True, pack=True)
        marine_arm(b, [(17, 18), (13, 16), (11, 12)])
        glove(b, 10, 10, fist=True)
        hline(b, 2, 7, 30, STEEL_D)


def escena_yolo(b, n, super_yolo=False):
    pos = "run1" if n == 0 else "run2"
    marine(b, legs=pos, visor="on")
    marine_arm(b, [(30, 18), (34, 17), (37, 19)]) if n == 0 else \
        marine_arm(b, [(17, 18), (13, 17), (10, 19)])
    gauss(b, 20, 22 if n == 0 else 21, 40 if n == 0 else 4,
          19 if n == 0 else 20)
    speed_lines(b, 26)
    if super_yolo:
        sun(b, 8, 7, 4)
        for k in range(3):
            setpx(b, 18 + k * 2, GROUND - 1 - (k % 2), AMBER)
            setpx(b, 30 + k * 2, GROUND - 2 + (k % 2), RED)
        glow(b, 24, 16, 12, AMBER, 28)


def escena_tool(b, n):
    if n == 0:
        marine(b, legs="stand")
        marine_arm(b, [(30, 18), (34, 19)])
        gauss(b, 18, 21, 40, 18)
        glove(b, 32, 21)
    else:
        marine(b, oy=0, legs="walk2")
        marine_arm(b, [(30, 18), (33, 19)])
        gauss(b, 16, 21, 38, 19)
        glove(b, 30, 21)
        muzzle(b, 41, 18, big=True)
        setpx(b, 36, 24, AMBER)


def escena_write(b, n):
    marine(b, legs="stand")
    console(b, 34, 26, lit=(n == 1))
    if n == 0:
        marine_arm(b, [(30, 18), (34, 21), (36, 24)])
        glove(b, 37, 25)
    else:
        marine_arm(b, [(30, 18), (33, 21), (36, 22)])
        glove(b, 37, 22)
        marine_arm(b, [(17, 18), (20, 22), (23, 25)])
        glove(b, 24, 26)
        setpx(b, 39, 27, VIS_W)


def escena_think(b, n):
    zealot(b, legs="stand")
    if n == 0:
        zealot_arm(b, [(29, 18), (31, 13), (28, 10)])
        gauntlet(b, 27, 9)
        psi_blade(b, 27, 9, 25, 3, dim=True)
    else:
        zealot(b, legs="stand", tilt=1)
        zealot_arm(b, [(29, 18), (33, 14), (31, 10)])
        gauntlet(b, 30, 9)
        psi_blade(b, 30, 9, 33, 3, dim=True)
    setpx(b, 20, 6, VIS_W)
    setpx(b, 21, 5, VIS_D)


def escena_verify(b, n):
    zealot(b, legs="stand")
    zealot_arm(b, [(29, 18), (33, 15), (34, 11)])
    gauntlet(b, 34, 10)
    holo_check(b, 37, 7, stamped=(n == 1))
    if n == 1:
        waves(b, 24, 20, VIS, 2)
        setpx(b, 24, 12, VIS_W)


def escena_judge(b, n):
    if n == 0:
        zealot(b, legs="stand")
        zealot_arm(b, [(29, 18), (33, 14), (34, 9)])
        gauntlet(b, 34, 8)
        psi_blade(b, 34, 8, 40, 3)
        zealot_arm(b, [(18, 18), (14, 14), (13, 9)])
        gauntlet(b, 13, 8)
        psi_blade(b, 13, 8, 7, 3)
    else:
        zealot(b, legs="wide")
        zealot_arm(b, [(29, 18), (33, 23), (35, 30)])
        gauntlet(b, 35, 31)
        psi_blade(b, 35, 31, 40, 37)
        waves(b, 24, GROUND - 3, VIS, 3)
        dust(b, 14, GROUND - 1, 3)
        dust(b, 34, GROUND - 1, 3)


def escena_review(b, n):
    zealot(b, legs="stand")
    scroll(b, 26, 14, mark=(n == 1))
    zealot_arm(b, [(29, 18), (32, 16)])
    gauntlet(b, 33, 15)
    if n == 0:
        zealot_arm(b, [(18, 18), (22, 15)])
        gauntlet(b, 23, 14)
        setpx(b, 24, 12, VIS)
    else:
        zealot_arm(b, [(18, 18), (23, 21)])
        gauntlet(b, 24, 22)
        setpx(b, 28, 17, RED)
        setpx(b, 29, 17, RED_L)


def escena_delegate(b, n):
    zealot(b, legs="stand")
    if n == 0:
        zealot_arm(b, [(29, 18), (34, 16), (38, 14)])
        gauntlet(b, 39, 13)
        sonda(b, 41, 22, 0)
        sonda(b, 33, 24, 1)
    else:
        zealot_arm(b, [(18, 18), (13, 16), (9, 14)])
        gauntlet(b, 8, 13)
        sonda(b, 5, 22, 0)
        sonda(b, 14, 24, 1)


def sonda(b, x, y, fase):
    """Sonda protoss chiquita: rombo dorado con nucleo psi."""
    oy = -1 if fase else 0
    setpx(b, x, y - 2 + oy, GOLD_L)
    hline(b, x - 1, x + 1, y - 1 + oy, GOLD)
    hline(b, x - 2, x + 2, y + oy, GOLD_D)
    hline(b, x - 1, x + 1, y + 1 + oy, GOLD_D)
    setpx(b, x, y + 2 + oy, GOLD_DD)
    setpx(b, x, y + oy, VIS_W)
    setpx(b, x, y + 1 + oy, VIS_D)


def escena_remember(b, n):
    zealot(b, legs="stand")
    if n == 0:
        crystal(b, 24, 15, lit=True)
        zealot_arm(b, [(18, 18), (21, 16)])
        gauntlet(b, 22, 15)
        zealot_arm(b, [(29, 18), (27, 16)])
        gauntlet(b, 26, 15)
    else:
        crystal(b, 24, 5, lit=True)
        zealot_arm(b, [(29, 18), (33, 12), (30, 8)])
        gauntlet(b, 29, 7)
        zealot_arm(b, [(18, 18), (16, 13), (20, 8)])
        gauntlet(b, 21, 7)
        waves(b, 24, 12, VIS, 2)


def escena_compact(b, n):
    if n == 0:
        zealot(b, legs="stand")
        zealot_arm(b, [(29, 18), (34, 16)])
        gauntlet(b, 35, 15)
        setpx(b, 37, 12, VIS_D)
        setpx(b, 39, 9, VIS_D)
    else:
        chico = figure([lambda t: zealot(t, legs="stand")])
        otro = scale_sprite(chico, 6, 10)
        paste(b, otro, 0, 0)
        sparkle(b, 34, 12, VIS_D)
        sparkle(b, 38, 18, VIS_D)
        setpx(b, 30, 8, VIS_W)


def escena_idle(b, n):
    zergling(b, blink=(n == 1), mouth="line")
    if n == 0:
        setpx(b, 40, 30, ZR_D)
    else:
        setpx(b, 39, 31, ZR_D)


def escena_talk(b, n):
    bocas = ("close", "small", "mid", "wide")
    zergling(b, mouth=bocas[n])
    if n >= 2:
        setpx(b, 40, 24, ZR_L)


def escena_ask(b, n):
    zergling(b, mouth="small", dx=0 if n == 0 else 2)
    if n == 0:
        bubble(b, 4, 6, 13, 11, "?", tail="right")
    else:
        bubble(b, 4, 8, 13, 11, "?", tail="right")
        setpx(b, 40, 26, ZR_D)


def escena_read(b, n):
    scv_body(b, drill="down")
    datapad(b, 34, 20, page=n)
    limb(b, [(31, 22), (34, 24)], STEEL_D, STEEL_L, 3)
    if n == 1:
        setpx(b, 43, 18, VIS_D)


def escena_explore(b, n):
    if n == 0:
        scv_body(b, drill="up")
        line_brush(b, 40, 12, 44, 8, AMBER, 2)
        disc(b, 44, 7, 2, AMBER)
        dust(b, 44, GROUND - 1, 3)
        spark(b, 12, 24)
    else:
        scv_body(b, drill="down")
        line_brush(b, 8, 12, 4, 8, AMBER, 2)
        disc(b, 4, 7, 2, AMBER)
        dust(b, 4, GROUND - 1, 3)
        spark(b, 36, 24)


def escena_jobs(b, n):
    pylon(b, stage=n)


def escena_build(b, n):
    command_center(b, stage=n)


def escena_jira(b, n):
    dropship(b, stage=n)


def escena_failure(b, n):
    fallen_marine(b, sink=-6 if n == 0 else -4)
    creep_pool(b, stage=(0 if n == 0 else 1))
    if n == 0:
        dust(b, 43, GROUND - 5, 3)
        spark(b, 33, 22, RED)
        glow(b, 24, 32, 9, CREEP, 28)
    else:
        smoke(b, 42, 24, 1)
        setpx(b, 12, GROUND - 4, CREEP_L)
        setpx(b, 20, GROUND - 3, CREEP_L)
        spark(b, 36, 20, AMBER_D)


def escena_grandma(b, n):
    abuela(b, needles=("up" if n == 0 else "down"))
    if n == 0:
        sparkle(b, 44, 2, AMBER)
    else:
        setpx(b, 12, 34, RUST_D)
        setpx(b, 10, 33, RUST)


# ══════════════════════════════════════════════════════════════════════════
# plan, escritura y verificacion
# ══════════════════════════════════════════════════════════════════════════

PLAN = (
    ("hi", ("hi_01.png", "hi_02.png"), (escena_hi,)),
    ("idle", ("idle.png", "idle_blink.png"), (escena_idle,)),
    ("think", ("think_01.png", "think_02.png"), (escena_think,)),
    ("talk", ("talk_close.png", "talk_small.png", "talk_mid.png",
              "talk_wide.png"), (escena_talk,)),
    ("read", ("read_01.png", "read_02.png"), (escena_read,)),
    ("write", ("write_01.png", "write_02.png"), (escena_write,)),
    ("tool", ("tool_01.png", "tool_02.png"), (escena_tool,)),
    ("ask", ("ask_01.png", "ask_02.png"), (escena_ask,)),
    ("success", ("success_01.png", "success_02.png"), (escena_success,)),
    ("failure", ("down_01.png", "down_02.png"), (escena_failure,)),
    ("compact", ("compact_01.png", "compact_02.png"), (escena_compact,)),
    ("delegate", ("delegate_01.png", "delegate_02.png"), (escena_delegate,)),
    ("explore", ("explore_01.png", "explore_02.png"), (escena_explore,)),
    ("build", ("build_01.png", "build_02.png"), (escena_build,)),
    ("verify", ("verify_01.png", "verify_02.png"), (escena_verify,)),
    ("judge", ("judge_01.png", "judge_02.png"), (escena_judge,)),
    ("review", ("review_01.png", "review_02.png"), (escena_review,)),
    ("jira", ("jira_01.png", "jira_02.png"), (escena_jira,)),
    ("jobs", ("jobs_01.png", "jobs_02.png"), (escena_jobs,)),
    ("yolo", ("yolo_01.png", "yolo_02.png"), (escena_yolo,)),
    ("super-yolo", ("super-yolo_01.png", "super-yolo_02.png"),
     (lambda b, n: escena_yolo(b, n, super_yolo=True),)),
    ("remember", ("remember_01.png", "remember_02.png"), (escena_remember,)),
    ("grandma", ("grandma_01.png", "grandma_02.png"), (escena_grandma,)),
    ("bye", ("bye_01.png", "bye_02.png"), (escena_bye,)),
)


def verificar(datos, ruta):
    """IHDR: 48x40, 8 bits, color type 6, sin interlace."""
    if datos[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("%s: firma PNG invalida" % ruta)
    ancho, alto = struct.unpack(">II", datos[16:24])
    profundidad, color, _c, _f, interlace = datos[24:29]
    if (ancho, alto) != (W, H):
        raise SystemExit("%s: %dx%d, se esperaba %dx%d" % (ruta, ancho, alto, W, H))
    if profundidad != 8 or color != 6 or interlace != 0:
        raise SystemExit("%s: depth=%d color=%d interlace=%d" %
                         (ruta, profundidad, color, interlace))


def main():
    total = 0
    print("== starcraft: %d escenas -> %s" % (len(PLAN), BASE))
    for carpeta, nombres, dibujos in PLAN:
        destino = os.path.join(BASE, carpeta)
        os.makedirs(destino, exist_ok=True)
        dibujar = dibujos[0]
        for indice, nombre in enumerate(nombres):
            buf = canvas()
            dibujar(buf, indice)
            contour(buf)
            datos = encode_png(W, H, buf)
            ruta = os.path.join(destino, nombre)
            with open(ruta, "wb") as fh:
                fh.write(datos)
            verificar(datos, ruta)
            total += 1
        print("  %-12s %d frames" % (carpeta, len(nombres)))
    print("  %d frames escritos" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


