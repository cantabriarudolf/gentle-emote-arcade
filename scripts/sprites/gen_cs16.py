#!/usr/bin/env python3
"""Set Counter-Strike 1.6 para gentle-emote-arcade.

24 estados x 48x40 RGBA, fondo transparente, solo stdlib (struct + zlib).
Un CT antiterrorista (casco, chaleco, uniforme azul/negro) actua cada escena,
con los objetos iconicos del juego: C4, AWP, flashbang, radio, mapa tactico,
rehen, pollo de cs_office y el mazo del admin.

Salida (relativa a este script):
  ../../emotes/cs16/<estado>/<estado>_01.png ... 02/03/04
  idle.png + idle_blink.png, talk_close/small/mid/wide.png

Uso:
  python3 scripts/sprites/gen_cs16.py
Imprime la verificacion IHDR de cada frame (48x40, 8-bit, color type 6,
no interlazado) y devuelve la lista generada.
"""
import math
import os
import struct
import sys
import zlib

W, H = 48, 40
BASE = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "..", "emotes", "cs16"))

# ── paleta CS 1.6 ──────────────────────────────────────────────────────────
INK = (16, 19, 26)          # contorno / negro de arma
DARK = (28, 33, 44)
DARK2 = (20, 24, 32)
UNI = (58, 76, 112)         # uniforme azul CT
UNI_D = (40, 54, 82)
UNI_L = (86, 108, 148)
VEST = (28, 34, 47)         # chaleco negro
VEST_D = (18, 22, 31)
VEST_L = (45, 55, 73)
HELM = (64, 82, 108)        # casco
HELM_D = (44, 58, 80)
HELM_L = (96, 118, 148)
MASK = (36, 45, 62)         # pasamontanas
MASK_D = (26, 33, 47)
SKIN = (226, 178, 142)
SKIN_D = (192, 140, 106)
SKIN_DD = (158, 106, 78)
SKIN_L = (246, 210, 178)
EYE = (240, 246, 252)
MOUTH = (150, 70, 66)
MOUTH_D = (104, 44, 46)
TONGUE = (198, 96, 90)
TEETH = (238, 240, 240)
BOOT = (24, 28, 37)
BOOT_D = (16, 19, 26)
BOOT_L = (40, 46, 58)
GLOVE = (44, 52, 68)
GLOVE_L = (76, 88, 108)
STEEL = (152, 164, 178)
STEEL_D = (104, 114, 129)
STEEL_L = (200, 210, 220)
WOOD = (140, 106, 62)
WOOD_D = (100, 74, 42)
WOOD_L = (174, 138, 84)
SAND = (198, 182, 150)
SAND_L = (222, 208, 178)
SAND_D = (164, 146, 116)
GREEN = (92, 226, 136)
GREEN_D = (40, 148, 88)
GREEN_DD = (24, 86, 56)
RED = (226, 66, 60)
RED_D = (150, 34, 38)
RED_L = (255, 132, 112)
AMBER = (255, 184, 64)
AMBER_D = (206, 124, 30)
WHITE = (246, 250, 254)
CYAN = (122, 222, 240)
CYAN_D = (52, 140, 170)
BLUE = (86, 148, 228)
BLUE_D = (46, 86, 150)
GOLD = (238, 198, 90)
GOLD_D = (176, 132, 44)
GOLD_L = (255, 230, 140)
PAPER = (238, 230, 206)
PAPER_D = (206, 196, 166)
PAPER_L = (250, 246, 228)
HAIR = (62, 44, 34)
HAIR_L = (92, 66, 50)
GREY = (140, 146, 156)
GREY_D = (86, 92, 104)
GREY_L = (186, 192, 202)

# ── PNG / canvas ───────────────────────────────────────────────────────────
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
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            setpx(buf, x, y, col, a)


def hline(buf, x0, x1, y, col):
    rect(buf, x0, y, x1, y, col)


def vline(buf, x, y0, y1, col):
    rect(buf, x, y0, x, y1, col)


def box(buf, x0, y0, x1, y1, fill, edge=INK):
    rect(buf, x0, y0, x1, y1, edge)
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
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def stroke(buf, pts, col, t=2):
    """Polilinea con contorno de 1px (pixel art de brazos, cables, armas)."""
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1], b[0], b[1], INK, t + 1)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1], b[0], b[1], col, t)


def circle(buf, cx, cy, r, col):
    for y in range(cy - r, cy + r + 1):
        d = r * r - (y - cy) * (y - cy)
        if d < 0:
            continue
        dx = int(math.sqrt(d))
        hline(buf, cx - dx, cx + dx, y, col)


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


def spark(buf, x, y, col=GOLD):
    setpx(buf, x, y, col)
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


def dust(buf, cx, cy, r=3):
    """Nube de polvo baja (failure): no es sombra, es escombro."""
    circle(buf, cx, cy, r, SAND_D)
    circle(buf, cx - r, cy + 1, 1, SAND)
    circle(buf, cx + r, cy, 1, SAND)
    setpx(buf, cx, cy - r, SAND_L)


def waves(buf, x, y, col=CYAN, steps=2):
    """Ondas de radio a la derecha del handie."""
    for k in range(steps):
        xk = x + k * 2
        yy = 2 + k
        setpx(buf, xk, y - yy, col)
        setpx(buf, xk, y - yy + 1, col)
        setpx(buf, xk, y + yy, col)
        setpx(buf, xk, y + yy - 1, col)


def paste(dst, src, dx=0, dy=0):
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3] == 0:
                continue
            j = ((y + dy) * W + (x + dx)) * 4
            if 0 <= x + dx < W and 0 <= y + dy < H:
                dst[j:j + 4] = src[i:i + 4]


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


# ── tipografia 3x5 ─────────────────────────────────────────────────────────
FONT = {
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#.."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
    "?": [".##.", "#..#", "..#.", "....", "..#."],
    "!": ["#", "#", "#", ".", "#"],
    "A": ["###", "#.#", "###", "#.#", "#.#"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "M": ["#.#", "###", "#.#", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "C": ["###", "#..", "#..", "#..", "###"],
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
}


def text(buf, word, x0, y0, col, scale=1, outline=INK):
    x = x0
    for ch in word:
        g = FONT[ch]
        gw = len(g[0])
        if outline is not None:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                gx = x
                for row in g:
                    for i, c in enumerate(row):
                        if c == "#":
                            for sy in range(scale):
                                for sx in range(scale):
                                    setpx(buf, gx + i * scale + sx + dx,
                                          y0 + g.index(row) * scale + sy + dy,
                                          outline)
        for ry, row in enumerate(g):
            for i, c in enumerate(row):
                if c == "#":
                    for sy in range(scale):
                        for sx in range(scale):
                            setpx(buf, x + i * scale + sx,
                                  y0 + ry * scale + sy, col)
        x += (gw + 1) * scale


# ── cuerpo CT ──────────────────────────────────────────────────────────────
def glove(buf, cx, cy, fist=False):
    if fist:
        rect(buf, cx - 3, cy - 3, cx + 3, cy + 3, INK)
        rect(buf, cx - 2, cy - 2, cx + 2, cy + 2, GLOVE)
        setpx(buf, cx - 2, cy - 2, GLOVE_L)
        setpx(buf, cx + 1, cy - 2, GLOVE_L)
        setpx(buf, cx - 2, cy + 1, GLOVE_L)
        vline(buf, cx, cy - 1, cy + 1, DARK)
        setpx(buf, cx + 2, cy + 2, DARK)
    else:
        rect(buf, cx - 2, cy - 2, cx + 2, cy + 2, INK)
        rect(buf, cx - 2, cy - 2, cx + 1, cy + 1, GLOVE)
        setpx(buf, cx - 2, cy - 2, GLOVE_L)
        setpx(buf, cx, cy - 1, GLOVE_L)
        setpx(buf, cx + 1, cy + 1, DARK)


def arm(buf, pts, col=UNI):
    """Brazo CT: manga gruesa con 1px de contorno y luz en el borde."""
    stroke(buf, pts, col, 3)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1] - 1, b[0], b[1] - 1, UNI_L, 1)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0] + 2, a[1] + 1, b[0] + 2, b[1] + 1, UNI_D, 1)


def skin_arm(buf, pts):
    """Brazo desnudo del rehen (manga corta)."""
    stroke(buf, pts, SKIN, 3)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0], a[1] - 1, b[0], b[1] - 1, SKIN_L, 1)
    for a, b in zip(pts, pts[1:]):
        line_brush(buf, a[0] + 2, a[1] + 1, b[0] + 2, b[1] + 1, SKIN_D, 1)


def hand(buf, cx, cy):
    rect(buf, cx - 1, cy - 1, cx + 1, cy + 1, INK)
    rect(buf, cx - 1, cy - 1, cx, cy, SKIN)
    setpx(buf, cx - 1, cy - 1, SKIN_L)
    setpx(buf, cx + 1, cy + 1, SKIN_D)


def mouth_shape(buf, kind, ox, oy):
    r = lambda a, b, c, d, col: rect(buf, a + ox, b + oy, c + ox, d + oy, col)
    p = lambda x, y, col: setpx(buf, x + ox, y + oy, col)
    if kind == "line":
        r(22, 17, 25, 17, MOUTH_D)
    elif kind == "small":
        r(23, 17, 24, 17, MOUTH_D)
        p(23, 17, MOUTH)
    elif kind == "mid":
        r(22, 17, 25, 17, MOUTH_D)
        r(23, 17, 24, 17, MOUTH)
    elif kind == "wide":
        r(22, 16, 25, 17, MOUTH_D)
        r(22, 16, 25, 16, TEETH)
        p(23, 17, TONGUE)
        p(24, 17, TONGUE)
    elif kind == "shout":
        r(22, 16, 25, 18, MOUTH_D)
        r(23, 16, 24, 16, TEETH)
        p(23, 17, TONGUE)
        p(24, 17, TONGUE)
        p(22, 18, MOUTH)
        p(25, 18, MOUTH)
    elif kind == "smile":
        r(22, 17, 25, 17, MOUTH_D)
        p(21, 16, MOUTH_D)
        p(26, 16, MOUTH_D)
        p(23, 17, TEETH)
        p(24, 17, TEETH)
    elif kind == "grin":
        r(21, 16, 26, 17, MOUTH_D)
        r(22, 16, 25, 16, TEETH)
        p(22, 17, TEETH)
        p(23, 17, TONGUE)
        p(24, 17, TONGUE)
        p(25, 17, TEETH)
    elif kind == "smirk":
        r(23, 17, 26, 17, MOUTH_D)
        p(26, 16, MOUTH_D)
    elif kind == "worried":
        r(23, 16, 24, 16, MOUTH_D)
        p(22, 17, MOUTH_D)
        p(25, 17, MOUTH_D)


def head_ct(buf, ox=0, oy=0, blink=False, mouth="line", look="fwd",
            helmet=True, hair=False, glasses=False, bandana=False,
            headset=False):
    r = lambda a, b, c, d, col: rect(buf, a + ox, b + oy, c + ox, d + oy, col)
    p = lambda x, y, col: setpx(buf, x + ox, y + oy, col)

    # casco o pelo
    if helmet:
        r(21, 3, 26, 3, INK)
        r(20, 4, 27, 4, INK)
        r(19, 5, 28, 5, INK)
        r(18, 6, 29, 8, INK)
        r(17, 9, 30, 10, INK)
        r(21, 4, 26, 4, HELM_L)
        r(20, 5, 27, 5, HELM_L)
        r(19, 6, 28, 6, HELM)
        r(19, 7, 28, 7, HELM)
        r(19, 8, 28, 8, HELM_D)
        r(18, 9, 29, 9, HELM_D)
        r(18, 10, 29, 10, HELM_D)
        hline(buf, 18 + ox, 29 + ox, 10 + oy, HELM_D)
        # montura NVG y tornillos
        r(23, 6, 24, 7, VEST_D)
        p(23, 6, STEEL)
        p(20, 8, STEEL_D)
        p(27, 8, STEEL_D)
        # orejeras laterales
        r(18, 11, 18, 13, HELM_D)
        r(29, 11, 29, 13, HELM_D)
    elif hair:
        r(20, 9, 27, 10, INK)
        r(21, 9, 26, 9, HAIR)
        r(20, 10, 27, 11, HAIR)
        r(21, 9, 22, 10, HAIR_L)
        p(20, 11, HAIR)
        p(27, 11, HAIR)
        # flequillo
        p(21, 11, HAIR)
        p(24, 11, HAIR)
        p(26, 11, HAIR)

    # cara / pasamontanas
    r(19, 11, 28, 19, INK)
    r(20, 12, 27, 18, MASK)
    r(21, 12, 26, 18, SKIN)
    r(21, 12, 26, 12, SKIN_D)
    r(21, 18, 26, 18, SKIN_D)
    p(21, 13, SKIN_L)
    p(26, 13, SKIN_D)

    if headset:
        r(18, 12, 18, 15, DARK2)
        p(18, 13, BLUE)
        stroke(buf, [(19 + ox, 16 + oy), (21 + ox, 17 + oy)], STEEL_D, 1)

    if glasses:
        r(20, 13, 27, 14, INK)
        r(21, 13, 26, 14, DARK2)
        p(21, 13, CYAN)
        p(22, 13, CYAN_D)
        p(26, 13, WHITE)
        p(19, 13, STEEL_D)
        p(28, 13, STEEL_D)
    elif blink:
        r(21, 14, 22, 14, SKIN_D)
        r(25, 14, 26, 14, SKIN_D)
        p(21, 14, MOUTH_D)
        p(26, 14, MOUTH_D)
    else:
        r(21, 14, 22, 14, EYE)
        r(25, 14, 26, 14, EYE)
        if look == "left":
            p(21, 14, INK)
            p(25, 14, INK)
        elif look == "right":
            p(22, 14, INK)
            p(26, 14, INK)
        elif look == "up":
            p(22, 14, INK)
            p(25, 14, INK)
            p(21, 13, SKIN_D)
            p(26, 13, SKIN_D)
        elif look == "down":
            p(22, 14, INK)
            p(25, 14, INK)
            p(21, 14, SKIN_D)
            p(26, 14, SKIN_D)
        else:
            p(22, 14, INK)
            p(25, 14, INK)
        # cejas
        r(21, 13, 22, 13, SKIN_D)
        r(25, 13, 26, 13, SKIN_D)

    # nariz
    r(23, 15, 24, 15, SKIN_D)
    p(24, 16, SKIN_DD)

    mouth_shape(buf, mouth, ox, oy)

    if bandana:
        r(21, 18, 26, 20, RED)
        r(22, 19, 25, 20, RED_D)
        p(21, 18, RED_L)
        p(27, 19, RED_D)

    # correa del casco
    if helmet:
        p(20, 17, MASK_D)
        p(27, 17, MASK_D)


def torso_stand(buf, ox=0, oy=0):
    r = lambda a, b, c, d, col: rect(buf, a + ox, b + oy, c + ox, d + oy, col)
    p = lambda x, y, col: setpx(buf, x + ox, y + oy, col)
    r(16, 20, 31, 31, INK)
    r(17, 21, 30, 30, UNI)
    r(17, 21, 30, 22, UNI_L)
    r(18, 29, 29, 30, UNI_D)
    r(21, 19, 26, 21, MASK_D)
    # chaleco
    r(18, 22, 29, 28, INK)
    r(19, 23, 28, 27, VEST)
    r(19, 23, 28, 23, VEST_L)
    r(19, 27, 28, 27, VEST_L)
    r(20, 24, 23, 26, VEST_D)
    r(24, 24, 27, 26, VEST_D)
    p(20, 24, VEST_L)
    p(23, 24, VEST_L)
    p(24, 24, VEST_L)
    p(27, 24, VEST_L)
    vline(buf, 21 + ox, 20 + oy, 23 + oy, VEST_D)
    vline(buf, 26 + ox, 20 + oy, 23 + oy, VEST_D)
    # cinto
    r(18, 29, 29, 31, VEST_D)
    p(23, 30, STEEL_D)
    p(24, 30, VEST)
    # hombreras
    r(16, 21, 17, 24, UNI_D)
    r(30, 21, 31, 24, UNI_D)
    p(16, 21, UNI_L)
    p(31, 21, UNI_L)


def legs_stand(buf, ox=0, oy=0):
    r = lambda a, b, c, d, col: rect(buf, a + ox, b + oy, c + ox, d + oy, col)
    p = lambda x, y, col: setpx(buf, x + ox, y + oy, col)
    r(18, 31, 29, 32, UNI_D)
    r(19, 33, 22, 35, UNI_D)
    r(25, 33, 28, 35, UNI_D)
    r(19, 33, 22, 34, VEST)
    r(25, 33, 28, 34, VEST)
    p(19, 33, VEST_L)
    p(25, 33, VEST_L)
    r(17, 36, 22, 38, INK)
    r(25, 36, 30, 38, INK)
    r(18, 36, 21, 37, (42, 50, 66))
    r(26, 36, 29, 37, (42, 50, 66))
    r(17, 38, 22, 38, BOOT_D)
    r(25, 38, 30, 38, BOOT_D)
    p(18, 36, BOOT_L)
    p(26, 36, BOOT_L)
    p(19, 37, BOOT)
    p(27, 37, BOOT)


def torso_crouch(buf, ox=0, oy=0):
    r = lambda a, b, c, d, col: rect(buf, a + ox, b + oy, c + ox, d + oy, col)
    p = lambda x, y, col: setpx(buf, x + ox, y + oy, col)
    r(15, 24, 32, 32, INK)
    r(16, 25, 31, 31, UNI)
    r(16, 25, 31, 26, UNI_L)
    r(17, 30, 30, 31, UNI_D)
    r(21, 23, 26, 25, MASK_D)
    # chaleco
    r(17, 27, 30, 30, INK)
    r(18, 28, 29, 30, VEST)
    r(18, 28, 29, 28, VEST_L)
    r(19, 29, 22, 30, VEST_D)
    r(23, 29, 26, 30, VEST_D)
    p(19, 29, VEST_L)
    p(23, 29, VEST_L)
    # cinto / union con los muslos
    r(16, 31, 31, 32, VEST_D)
    r(22, 31, 23, 32, VEST)
    p(22, 31, STEEL_D)
    r(15, 26, 16, 29, UNI_D)
    r(31, 26, 32, 29, UNI_D)
    p(15, 26, UNI_L)
    p(32, 26, UNI_L)


def legs_crouch(buf, ox=0, oy=0):
    r = lambda a, b, c, d, col: rect(buf, a + ox, b + oy, c + ox, d + oy, col)
    p = lambda x, y, col: setpx(buf, x + ox, y + oy, col)
    # muslos horizontales
    r(12, 31, 21, 35, INK)
    r(13, 32, 20, 34, UNI_D)
    r(24, 31, 33, 35, INK)
    r(25, 32, 32, 34, UNI_D)
    # rodilleras
    r(10, 32, 13, 35, VEST)
    r(32, 32, 35, 35, VEST)
    p(10, 32, VEST_L)
    p(32, 32, VEST_L)
    # canillas
    r(10, 34, 17, 36, UNI_D)
    r(29, 34, 36, 36, UNI_D)
    # botas
    r(8, 36, 19, 38, INK)
    r(9, 37, 18, 38, (42, 50, 66))
    r(27, 36, 39, 38, INK)
    r(28, 37, 38, 38, (42, 50, 66))
    p(9, 37, BOOT_L)
    p(28, 37, BOOT_L)
    p(18, 38, BOOT_D)
    p(38, 38, BOOT_D)


def ct_body_canvas(mode="stand", **opts):
    b = canvas()
    if mode == "stand":
        legs_stand(b)
        torso_stand(b)
        head_ct(b, **opts)
    elif mode == "crouch":
        legs_crouch(b)
        torso_crouch(b)
        head_ct(b, oy=5, **opts)
    elif mode == "walk":
        phase = opts.pop("phase", 1)
        legs_walk(b, phase)
        torso_stand(b)
        head_ct(b, **opts)
    elif mode == "kneel":
        ct_kneel_body(b)
        head_ct(b, ox=7, oy=3, **opts)
    return b


def legs_walk(buf, phase):
    if phase == 1:
        # pierna izquierda adelante
        rect(buf, 14, 31, 20, 36, INK)
        rect(buf, 15, 32, 19, 35, UNI_D)
        rect(buf, 13, 36, 21, 38, INK)
        rect(buf, 14, 37, 20, 38, (42, 50, 66))
        setpx(buf, 14, 37, BOOT_L)
        # pierna derecha atras, talon alto
        rect(buf, 25, 31, 29, 35, INK)
        rect(buf, 26, 32, 28, 34, UNI_D)
        rect(buf, 28, 35, 35, 37, INK)
        rect(buf, 29, 36, 34, 37, (42, 50, 66))
        setpx(buf, 29, 36, BOOT_L)
    else:
        # espejo
        rect(buf, 27, 31, 33, 36, INK)
        rect(buf, 28, 32, 32, 35, UNI_D)
        rect(buf, 26, 36, 34, 38, INK)
        rect(buf, 27, 37, 33, 38, (42, 50, 66))
        setpx(buf, 27, 37, BOOT_L)
        rect(buf, 18, 31, 22, 35, INK)
        rect(buf, 19, 32, 21, 34, UNI_D)
        rect(buf, 12, 35, 19, 37, INK)
        rect(buf, 13, 36, 18, 37, (42, 50, 66))
        setpx(buf, 13, 36, BOOT_L)


def rifle_slung(buf, dx=0, dy=0):
    """AWP colgada a la espalda (explore): culata arriba-izquierda."""
    stroke(buf, [(8 + dx, 12 + dy), (39 + dx, 33 + dy)], STEEL_D, 2)
    # culata
    rect(buf, 4 + dx, 9 + dy, 9 + dx, 14 + dy, INK)
    rect(buf, 5 + dx, 10 + dy, 8 + dx, 13 + dy, VEST_D)
    hline(buf, 5 + dx, 8 + dx, 10 + dy, VEST_L)
    rect(buf, 2 + dx, 11 + dy, 4 + dx, 13 + dy, INK)
    rect(buf, 3 + dx, 11 + dy, 3 + dx, 12 + dy, STEEL_D)
    # mira
    rect(buf, 30 + dx, 26 + dy, 35 + dx, 29 + dy, INK)
    rect(buf, 31 + dx, 27 + dy, 34 + dx, 28 + dy, STEEL_D)
    setpx(buf, 31 + dx, 27 + dy, CYAN)
    # boca del canon
    rect(buf, 38 + dx, 31 + dy, 42 + dx, 35 + dy, INK)
    rect(buf, 39 + dx, 32 + dy, 41 + dx, 34 + dy, STEEL_D)
    # cargador
    rect(buf, 24 + dx, 20 + dy, 28 + dx, 25 + dy, INK)
    rect(buf, 25 + dx, 21 + dy, 27 + dx, 24 + dy, STEEL_D)


def ct_kneel_body(b):
    # torso inclinado a la derecha, apuntando con el AWP
    rect(b, 22, 19, 38, 31, INK)
    rect(b, 23, 20, 37, 30, UNI)
    rect(b, 23, 20, 37, 21, UNI_L)
    rect(b, 24, 21, 36, 28, VEST)
    rect(b, 24, 21, 36, 21, VEST_L)
    rect(b, 25, 23, 28, 27, VEST_D)
    rect(b, 29, 23, 32, 27, VEST_D)
    rect(b, 33, 23, 35, 27, VEST_D)
    rect(b, 23, 29, 37, 31, VEST_D)
    rect(b, 28, 29, 29, 31, VEST)
    setpx(b, 28, 29, STEEL_D)
    rect(b, 22, 20, 23, 24, UNI_D)
    rect(b, 37, 20, 38, 24, UNI_D)
    # pierna izquierda adelantada (rodilla arriba)
    rect(b, 16, 26, 24, 34, INK)
    rect(b, 17, 27, 23, 33, UNI_D)
    rect(b, 15, 29, 19, 32, VEST)
    setpx(b, 15, 29, VEST_L)
    rect(b, 13, 33, 21, 38, INK)
    rect(b, 14, 34, 20, 37, UNI_D)
    rect(b, 10, 36, 22, 38, INK)
    rect(b, 11, 37, 21, 38, BOOT)
    # pierna derecha doblada bajo el cuerpo
    rect(b, 29, 30, 40, 35, INK)
    rect(b, 30, 31, 39, 34, UNI_D)
    rect(b, 34, 33, 42, 38, INK)
    rect(b, 35, 34, 41, 37, BOOT)
    setpx(b, 11, 37, BOOT_L)
    setpx(b, 35, 34, BOOT_L)
    setpx(b, 39, 31, UNI_L)


# ── objetos del juego ──────────────────────────────────────────────────────
def rifle_m4(buf):
    """M4 cruzada al pecho (idle)."""
    # culata
    rect(buf, 12, 29, 17, 34, INK)
    rect(buf, 13, 30, 16, 33, VEST_D)
    hline(buf, 13, 16, 30, VEST_L)
    # receiver
    rect(buf, 16, 24, 28, 31, INK)
    rect(buf, 17, 25, 27, 30, DARK)
    rect(buf, 18, 25, 26, 26, STEEL_D)
    # cargador
    rect(buf, 21, 31, 25, 35, INK)
    rect(buf, 22, 31, 24, 34, STEEL_D)
    hline(buf, 22, 24, 31, STEEL)
    # canon + punto de mira
    stroke(buf, [(27, 26), (37, 22)], STEEL_D, 1)
    rect(buf, 33, 19, 34, 23, INK)
    setpx(buf, 33, 19, STEEL)
    # alza
    rect(buf, 19, 22, 24, 24, INK)
    rect(buf, 20, 23, 23, 23, STEEL_D)
    setpx(buf, 20, 23, CYAN_D)
    # empunadura
    rect(buf, 25, 30, 27, 33, INK)
    rect(buf, 25, 30, 26, 32, DARK2)


def radio(buf, x, y, antenna=True):
    rect(buf, x, y, x + 4, y + 6, INK)
    rect(buf, x + 1, y + 1, x + 3, y + 5, STEEL_D)
    rect(buf, x + 1, y + 1, x + 3, y + 2, STEEL)
    for k in range(3):
        setpx(buf, x + 2, y + 3 + k, INK)
    setpx(buf, x + 3, y + 1, CYAN)
    if antenna:
        rect(buf, x + 1, y - 3, x + 1, y - 1, INK)
        setpx(buf, x + 1, y - 3, STEEL_L)
    setpx(buf, x + 4, y + 4, AMBER)


def bubble(buf, x, y, w, h, letter, col):
    rect(buf, x + 1, y, x + w - 2, y + h - 1, INK)
    rect(buf, x, y + 1, x + w - 1, y + h - 2, INK)
    rect(buf, x + 1, y + 1, x + w - 2, y + h - 2, WHITE)
    rect(buf, x + 2, y + 2, x + w - 3, y + h - 3, WHITE)
    # cola hacia el personaje
    rect(buf, x + 4, y + h, x + 8, y + h, INK)
    rect(buf, x + 4, y + h + 1, x + 6, y + h + 1, INK)
    setpx(buf, x + 4, y + h + 2, INK)
    hline(buf, x + 5, x + 7, y + h, WHITE)
    hline(buf, x + 5, x + 5, y + h + 1, WHITE)
    tw = len(FONT[letter][0])
    th = 5
    text(buf, letter, x + (w - tw * 2) // 2, y + (h - th * 2) // 2 - 1,
         col, scale=2, outline=None)
    # remache de color en el borde
    hline(buf, x + 2, x + w - 3, y + 1, col)
    hline(buf, x + 2, x + w - 3, y + h - 2, col)


def c4_bomb(buf, x, y, digits, stage):
    """C4 plantado: 01 LED apagado, 02 ambar, 03 rojo + ondas de beep."""
    w, h = 28, 14
    box(buf, x, y, x + w - 1, y + h - 1, SAND)
    hline(buf, x + 1, x + w - 2, y + 1, SAND_L)
    hline(buf, x + 1, x + w - 2, y + h - 2, SAND_D)
    # fleje
    vline(buf, x + 12, y + 2, y + h - 2, VEST_D)
    vline(buf, x + 13, y + 2, y + h - 2, SAND_D)
    # etiqueta C4 (2px de aire para que el 4 no parezca H)
    text(buf, "C", x + 2, y + 2, INK, outline=None)
    text(buf, "4", x + 7, y + 2, INK, outline=None)
    # pantalla
    box(buf, x + 14, y + 2, x + 24, y + 7, STEEL_D)
    rect(buf, x + 15, y + 3, x + 23, y + 6, DARK2)
    col = (GREEN_D, AMBER, RED)[stage]
    text(buf, digits, x + 15, y + 3, col, outline=None)
    # teclado
    box(buf, x + 2, y + 8, x + 11, y + 12, STEEL_D)
    for iy in range(2):
        for ix in range(3):
            rect(buf, x + 3 + ix * 3, y + 9 + iy * 2,
                 x + 4 + ix * 3, y + 9 + iy * 2, VEST_L)
    # LED
    led = (GREEN_DD, AMBER, RED)[stage]
    rect(buf, x + 25, y + 2, x + 26, y + 4, INK)
    rect(buf, x + 25, y + 3, x + 26, y + 4, led)
    if stage:
        setpx(buf, x + 25, y + 3, WHITE)
        waves(buf, x + 28, y + 4, led, 2 + stage)
    # cables
    stroke(buf, [(x, y + 5), (x - 4, y + 8), (x - 2, y + 12)], RED, 1)
    stroke(buf, [(x, y + 7), (x - 5, y + 10), (x - 3, y + 13)], GREEN_D, 1)
    stroke(buf, [(x, y + 9), (x - 3, y + 12), (x - 1, y + 14)], BLUE, 1)
    # detalle de carga
    for k in range(3):
        setpx(buf, x + 4 + k * 2, y + 13, VEST_D)


def defuse_kit(buf, x, y, stage):
    """Caja de defuse abierta (write)."""
    box(buf, x, y, x + 15, y + 8, STEEL_D)
    rect(buf, x + 1, y + 1, x + 14, y + 3, DARK2)
    rect(buf, x + 2, y + 4, x + 13, y + 7, (24, 30, 40))
    # cables
    stroke(buf, [(x + 3, y + 6), (x + 5, y + 3), (x + 8, y + 5)], RED, 1)
    stroke(buf, [(x + 5, y + 7), (x + 8, y + 4), (x + 11, y + 6)], GREEN_D, 1)
    stroke(buf, [(x + 8, y + 7), (x + 10, y + 3)], BLUE, 1)
    # alicate
    rect(buf, x + 10, y + 2, x + 13, y + 3, INK)
    rect(buf, x + 11, y + 2, x + 12, y + 2, STEEL)
    # LED
    led = (GREEN_D, AMBER)[stage % 2]
    rect(buf, x + 1, y + 1, x + 2, y + 2, led)
    setpx(buf, x + 2, y + 1, WHITE)
    # bisagras
    setpx(buf, x, y + 4, INK)
    setpx(buf, x + 15, y + 4, INK)


def tablet(buf, x, y, progress, alert=False):
    box(buf, x, y, x + 15, y + 10, DARK2)
    rect(buf, x + 1, y + 1, x + 14, y + 7, (12, 28, 26))
    # mini mapa tactico en pantalla
    for gx in range(x + 3, x + 14, 3):
        vline(buf, gx, y + 2, y + 6, (26, 74, 64))
    hline(buf, x + 2, x + 13, y + 4, (26, 74, 64))
    setpx(buf, x + 7, y + 3, RED if alert else GREEN)
    setpx(buf, x + 10, y + 5, CYAN)
    # barra de progreso
    rect(buf, x + 2, y + 7, x + 13, y + 8, VEST_D)
    rect(buf, x + 2, y + 7, x + 2 + progress, y + 8, RED if alert else GREEN)
    if alert:
        setpx(buf, x + 13, y + 2, RED)
    # boton home
    setpx(buf, x + 7, y + 9, STEEL_D)


def map_tac(buf, x0, y0, x1, y1):
    box(buf, x0, y0, x1, y1, PAPER)
    hline(buf, x0 + 1, x1 - 1, y0 + 1, PAPER_L)
    hline(buf, x0 + 1, x1 - 1, y1 - 1, PAPER_D)
    # grilla
    for gx in range(x0 + 4, x1 - 2, 4):
        vline(buf, gx, y0 + 2, y1 - 2, PAPER_D)
    for gy in range(y0 + 4, y1 - 2, 4):
        hline(buf, x0 + 2, x1 - 2, gy, PAPER_D)
    # zonas construidas
    rect(buf, x0 + 5, y0 + 5, x0 + 10, y0 + 8, PAPER_D)
    rect(buf, x0 + 6, y0 + 6, x0 + 9, y0 + 7, PAPER_L)
    rect(buf, x1 - 12, y1 - 9, x1 - 6, y1 - 5, PAPER_D)
    rect(buf, x1 - 11, y1 - 8, x1 - 7, y1 - 6, PAPER_L)
    # ruta azul
    stroke(buf, [(x0 + 3, y1 - 3), (x0 + 9, y1 - 7), (x0 + 14, y1 - 4),
                 (x0 + 16, y0 + 5)], BLUE, 1)
    # X roja del objetivo
    xr, yr = x1 - 6, y0 + 6
    stroke(buf, [(xr - 2, yr - 2), (xr + 2, yr + 2)], RED, 1)
    stroke(buf, [(xr - 2, yr + 2), (xr + 2, yr - 2)], RED, 1)
    # marcador de sitio A
    text(buf, "A", x0 + 2, y0 + 2, RED, outline=None)
    # compas
    setpx(buf, x0 + 3, y1 - 4, RED)
    vline(buf, x0 + 3, y1 - 6, y1 - 4, INK)
    # esquina doblada
    rect(buf, x1 - 3, y1 - 2, x1 - 1, y1 - 1, PAPER_D)
    setpx(buf, x1 - 1, y1 - 1, PAPER_L)


def map_roll(buf, x, y):
    box(buf, x, y, x + 7, y + 13, PAPER)
    vline(buf, x + 2, y + 1, y + 12, PAPER_D)
    vline(buf, x + 5, y + 1, y + 12, PAPER_D)
    # ruta y X roja visible
    stroke(buf, [(x + 1, y + 10), (x + 6, y + 7)], BLUE, 1)
    stroke(buf, [(x + 1, y + 4), (x + 6, y + 8)], RED, 1)
    stroke(buf, [(x + 1, y + 8), (x + 6, y + 4)], RED, 1)
    # remates enrollados
    rect(buf, x - 1, y - 1, x + 8, y + 1, PAPER_D)
    rect(buf, x - 1, y + 12, x + 8, y + 14, PAPER_D)
    hline(buf, x, x + 7, y, PAPER_L)
    hline(buf, x, x + 7, y + 13, PAPER_L)


def gavel(buf, x, y, down=False):
    """Mazo de admin: (x,y) es la mano; cabeza de 9x4."""
    if down:
        stroke(buf, [(x, y), (x + 4, y + 3), (x + 6, y + 5)], WOOD_D, 2)
        stroke(buf, [(x, y - 1), (x + 4, y + 2)], WOOD, 1)
        rect(buf, x + 5, y + 4, x + 14, y + 7, INK)
        rect(buf, x + 6, y + 5, x + 13, y + 6, GOLD)
        hline(buf, x + 6, x + 13, y + 5, GOLD_L)
        vline(buf, x + 7, y + 5, y + 6, GOLD_D)
        vline(buf, x + 12, y + 5, y + 6, GOLD_D)
    else:
        stroke(buf, [(x, y), (x + 4, y - 3), (x + 6, y - 5)], WOOD_D, 2)
        stroke(buf, [(x + 1, y - 1), (x + 4, y - 3)], WOOD, 1)
        rect(buf, x + 5, y - 8, x + 14, y - 5, INK)
        rect(buf, x + 6, y - 7, x + 13, y - 6, GOLD)
        hline(buf, x + 6, x + 13, y - 7, GOLD_L)
        vline(buf, x + 7, y - 7, y - 6, GOLD_D)
        vline(buf, x + 12, y - 7, y - 6, GOLD_D)


def helmet_item(buf, x, y):
    """Casco en la mano (bye_02)."""
    rect(buf, x, y, x + 11, y + 2, INK)
    rect(buf, x + 1, y, x + 10, y + 1, HELM)
    rect(buf, x + 2, y, x + 8, y, HELM_L)
    rect(buf, x - 1, y + 3, x + 12, y + 4, INK)
    rect(buf, x, y + 3, x + 11, y + 3, HELM_D)
    rect(buf, x + 1, y + 4, x + 10, y + 4, HELM_D)
    rect(buf, x + 3, y + 5, x + 8, y + 5, MASK_D)
    setpx(buf, x + 11, y + 2, STEEL)
    setpx(buf, x + 2, y + 1, HELM_L)


def flashbang(buf, x, y, blown):
    # granada cilindrica
    rect(buf, x, y, x + 3, y + 6, INK)
    rect(buf, x + 1, y + 1, x + 2, y + 5, STEEL)
    hline(buf, x + 1, x + 2, y + 2, STEEL_L)
    for k in range(3):
        setpx(buf, x + 1 + (k % 2), y + 3 + k, STEEL_D)
    rect(buf, x + 1, y - 1, x + 2, y, STEEL_D)
    if blown:
        burst(buf, x + 6, y, 5, WHITE, WHITE)
        spark(buf, x - 3, y - 4, AMBER)
        spark(buf, x + 9, y + 2, AMBER)


def seal(buf, x, y):
    """Sello verde de verificacion."""
    ring(buf, x + 5, y + 5, 5, GREEN_D, 1)
    circle(buf, x + 5, y + 5, 3, GREEN_DD)
    stroke(buf, [(x + 3, y + 5), (x + 5, y + 7), (x + 9, y + 2)], GREEN, 1)
    # cinta de sello
    rect(buf, x + 3, y + 9, x + 7, y + 11, GREEN_D)
    rect(buf, x + 4, y + 10, x + 6, y + 11, GREEN_DD)


def smoke_grenade(buf, x, y, stage):
    box(buf, x, y, x + 5, y + 7, GREY)
    hline(buf, x + 1, x + 4, y + 2, GREEN_D)
    rect(buf, x + 1, y - 1, x + 4, y, DARK2)
    puffs = [(-6, -4, 4), (0, -8, 5), (7, -6, 4), (-2, -14, 5),
             (6, -14, 4), (12, -10, 3), (2, -20, 5), (10, -19, 4),
             (-6, -18, 3), (16, -16, 3)]
    tones = [GREY_L, GREY, GREY_L, WHITE, GREY, GREY_L, GREY, GREY_L,
             GREY, GREY]
    for i, (px, py, pr) in enumerate(puffs):
        px += stage * 2 - 1
        py += (i % 2) * stage
        circle(buf, x + 3 + px, y + 2 + py, pr, tones[i])
    # reconectar el humo para que no queden huecos
    circle(buf, x + 2, y - 2, 4, GREY)
    circle(buf, x + 5, y - 1, 3, GREY_L)


def flare(buf, x, y, stage):
    # bengala roja clavada en el piso
    rect(buf, x, y, x + 2, y + 9, INK)
    rect(buf, x + 1, y + 1, x + 2, y + 8, RED_D)
    rect(buf, x, y + 8, x + 3, y + 9, STEEL_D)
    # llama
    fl = stage
    ellipse(buf, x + 2, y - 2, 2, 4, AMBER_D)
    ellipse(buf, x + 2, y - 3, 1, 3, AMBER)
    ellipse(buf, x + 2, y - 4, 1, 2, WHITE)
    if fl:
        ellipse(buf, x + 6, y - 6, 1, 2, AMBER)
        ellipse(buf, x + 2, y - 8, 1, 3, AMBER)
    # chispas
    for sx, sy in ((-3, -5), (4, -9), (0, -12), (6, -4), (-2, -10)):
        setpx(buf, x + 2 + sx, y + 2 + sy, GOLD if fl else GOLD_D)
    # humo que sube
    circle(buf, x + 4, y - 12, 2, GREY_D)
    circle(buf, x + 1, y - 16, 2, GREY)
    circle(buf, x + 6, y - 17, 2, GREY_D)


def chicken(buf, peck):
    # cuerpo
    ellipse(buf, 23, 28, 9, 8, INK)
    ellipse(buf, 23, 28, 8, 7, WHITE)
    ellipse(buf, 22, 29, 6, 5, (236, 236, 232))
    # ala
    ellipse(buf, 20, 28, 4, 3, GREY_L)
    hline(buf, 17, 22, 30, GREY)
    # cola
    rect(buf, 12, 22, 17, 27, INK)
    rect(buf, 13, 23, 16, 26, WHITE)
    setpx(buf, 13, 23, GREY_L)
    setpx(buf, 14, 22, GREY_L)
    # patas
    for lx in (20, 26):
        rect(buf, lx, 34, lx + 1, 37, AMBER_D)
    hline(buf, 19, 21, 37, AMBER_D)
    hline(buf, 25, 27, 37, AMBER_D)
    if peck:
        # cuello agachado y cabeza picoteando
        stroke(buf, [(28, 26), (32, 29), (35, 33)], WHITE, 3)
        circle(buf, 36, 33, 3, INK)
        circle(buf, 36, 33, 2, WHITE)
        rect(buf, 37, 32, 39, 34, AMBER_D)
        setpx(buf, 38, 33, GOLD)
        rect(buf, 36, 30, 37, 31, RED)
        setpx(buf, 37, 32, INK)
        # granos
        for gx, gy in ((38, 37), (41, 36), (35, 37), (30, 38)):
            setpx(buf, gx, gy, SAND_D)
    else:
        # cabeza arriba
        stroke(buf, [(28, 24), (30, 19)], WHITE, 3)
        circle(buf, 31, 18, 4, INK)
        circle(buf, 31, 18, 3, WHITE)
        rect(buf, 31, 15, 33, 17, RED)
        setpx(buf, 32, 16, RED_L)
        rect(buf, 34, 18, 36, 19, AMBER_D)
        setpx(buf, 35, 18, GOLD)
        setpx(buf, 30, 18, INK)
        # granos al aire
        for gx, gy in ((38, 24), (41, 27), (35, 28)):
            setpx(buf, gx, gy, SAND_D)


def hostage(buf, kneel):
    """Rehen de cs_office: camisa blanca, jean, manos atadas."""
    oy = 4 if kneel else 0
    r = lambda a, b, c, d, col: rect(buf, a, b + oy, c, d + oy, col)
    p = lambda x, y, col: setpx(buf, x, y + oy, col)
    # cabeza con pelo (sin casco)
    head_ct(buf, oy=oy, helmet=False, hair=True, mouth="worried",
            look="up" if kneel else "left")
    # torso camisa blanca
    r(17, 20, 31, 30, INK)
    r(18, 21, 30, 29, (226, 226, 220))
    r(18, 21, 30, 22, (244, 244, 238))
    r(24, 21, 25, 29, (206, 206, 198))
    # cuello abierto
    r(22, 19, 25, 21, SKIN)
    r(22, 20, 23, 21, INK)
    # manga corta
    r(16, 21, 18, 25, (226, 226, 220))
    r(30, 21, 32, 25, (226, 226, 220))
    if kneel:
        # manos atadas al frente
        skin_arm(buf, [(18, 26), (20, 30), (23, 31)])
        hand(buf, 23, 31)
        skin_arm(buf, [(30, 26), (28, 30), (25, 31)])
        hand(buf, 25, 31)
        rect(buf, 21, 32, 27, 33, SAND_D)
        hline(buf, 22, 26, 32, SAND)
        setpx(buf, 24, 33, SAND_L)
        # piernas dobladas, siempre dentro del cuadro
        rect(buf, 15, 33, 23, 36, INK)
        rect(buf, 16, 34, 22, 35, BLUE_D)
        rect(buf, 24, 33, 33, 36, INK)
        rect(buf, 25, 34, 32, 35, BLUE_D)
        rect(buf, 14, 36, 22, 38, INK)
        rect(buf, 15, 37, 21, 38, (90, 66, 44))
        rect(buf, 25, 36, 33, 38, INK)
        rect(buf, 26, 37, 32, 38, (90, 66, 44))
    else:
        # brazos al frente, manos atadas
        skin_arm(buf, [(18, 24), (19, 28), (23, 29)])
        hand(buf, 23, 29)
        skin_arm(buf, [(30, 24), (29, 28), (25, 29)])
        hand(buf, 25, 29)
        rect(buf, 21, 30, 27, 31, SAND_D)
        hline(buf, 22, 26, 30, SAND)
        setpx(buf, 24, 31, SAND_L)
        # jean
        rect(buf, 18, 31, 22, 37, INK)
        rect(buf, 19, 31, 22, 36, BLUE_D)
        rect(buf, 25, 31, 29, 37, INK)
        rect(buf, 25, 31, 28, 36, BLUE_D)
        rect(buf, 17, 37, 22, 38, INK)
        rect(buf, 18, 37, 21, 38, (90, 66, 44))
        rect(buf, 25, 37, 30, 38, INK)
        rect(buf, 26, 37, 29, 38, (90, 66, 44))
        # gota de sudor
        p(29, 12, CYAN)
        p(29, 13, CYAN)


def frame_hi(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="smile", headset=True))
    if n == 1:
        arm(b, [(29, 22), (32, 18), (33, 13)])
        glove(b, 33, 10)
        spark(b, 37, 9, WHITE)
        spark(b, 31, 5, GOLD)
    else:
        arm(b, [(29, 22), (33, 20), (34, 17)])
        glove(b, 34, 15)
        spark(b, 37, 13, WHITE)
    return b


def frame_idle(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", blink=(n == 2), mouth="line"))
    rifle_m4(b)
    # manos sobre el arma
    arm(b, [(18, 22), (17, 26), (19, 28)])
    glove(b, 19, 29)
    arm(b, [(29, 22), (29, 26), (27, 28)])
    glove(b, 27, 28)
    return b


def frame_think(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="line",
                            look="up" if n == 1 else "left"))
    if n == 1:
        arm(b, [(18, 22), (19, 20), (20, 19)])
        glove(b, 20, 18)
        text(b, "?", 34, 5, AMBER, outline=INK)
        radio(b, 31, 29)
        setpx(b, 37, 8, GOLD)
    else:
        arm(b, [(29, 22), (32, 18), (33, 15)])
        glove(b, 33, 14)
        radio(b, 31, 9)
        waves(b, 36, 12, CYAN, 2)
        text(b, "?", 33, 3, AMBER, outline=INK)
    return b


MOUTHS = ("line", "small", "mid", "wide")


def frame_talk(m):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth=MOUTHS[m], headset=True))
    arm(b, [(29, 22), (31, 19), (30, 17)])
    radio(b, 27, 11)
    glove(b, 30, 17)
    waves(b, 33, 14, CYAN, 2)
    return b


def frame_read(n):
    b = canvas()
    paste(b, ct_body_canvas("kneel", mouth="line", look="right"))
    # AWP delante del cuerpo, canon a la izquierda
    stroke(b, [(4, 26), (20, 26)], INK, 3)
    stroke(b, [(4, 26), (20, 26)], STEEL_D, 1)
    box(b, 19, 23, 32, 28, DARK)
    hline(b, 20, 31, 24, STEEL_D)
    rect(b, 31, 25, 39, 31, INK)
    rect(b, 32, 26, 38, 30, VEST_D)
    hline(b, 32, 38, 26, UNI_D)
    rect(b, 25, 28, 28, 31, INK)
    rect(b, 26, 28, 27, 30, STEEL_D)
    rect(b, 29, 20, 31, 22, INK)
    setpx(b, 30, 20, AMBER)
    # mira montada
    rect(b, 19, 19, 25, 22, INK)
    rect(b, 20, 20, 24, 21, STEEL_D)
    if n == 1:
        setpx(b, 20, 20, CYAN)
        setpx(b, 20, 21, CYAN)
    else:
        setpx(b, 20, 20, RED)
        setpx(b, 20, 21, RED_L)
    # brazos al arma
    arm(b, [(29, 22), (25, 25), (23, 26)])
    glove(b, 23, 26)
    arm(b, [(36, 23), (34, 26), (33, 27)])
    glove(b, 33, 27)
    # visor de la mira (mirilla)
    ring(b, 8, 9, 6, STEEL, 1)
    ring(b, 8, 9, 7, INK, 1)
    if n == 1:
        hline(b, 3, 13, 9, WHITE)
        vline(b, 8, 4, 14, WHITE)
        circle(b, 8, 9, 1, RED)
        setpx(b, 5, 6, WHITE)
    else:
        hline(b, 3, 13, 9, RED)
        vline(b, 8, 4, 14, RED)
        circle(b, 8, 9, 1, WHITE)
        burst(b, 5, 26, 3, AMBER, WHITE)
    return b


def frame_write(n):
    b = canvas()
    paste(b, ct_body_canvas("crouch", mouth="line", look="down"))
    defuse_kit(b, 19, 29, n - 1)
    if n == 1:
        arm(b, [(15, 26), (18, 30), (21, 31)])
        glove(b, 21, 32)
        arm(b, [(32, 26), (29, 30), (26, 31)])
        glove(b, 26, 32)
        # alicate y chispa del cable cortado
        rect(b, 28, 28, 31, 29, INK)
        rect(b, 28, 28, 30, 28, STEEL)
        spark(b, 35, 27, AMBER)
    else:
        arm(b, [(15, 26), (17, 30), (20, 33)])
        glove(b, 20, 34)
        arm(b, [(32, 26), (30, 31), (28, 33)])
        glove(b, 28, 34)
        spark(b, 36, 29, GREEN)
    return b


def frame_tool(n):
    b = canvas()
    digits = ("0:9", "0:8", "0:7")[n - 1]
    c4_bomb(b, 10, 19, digits, n - 1)
    if n == 3:
        # destello del ultimo tiempo
        spark(b, 8, 15, RED)
        spark(b, 41, 15, RED)
    return b


def frame_ask(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="line", look="up"))
    # radio en la mano izquierda
    arm(b, [(18, 22), (15, 25), (16, 27)])
    radio(b, 13, 25)
    glove(b, 16, 30)
    if n == 1:
        bubble(b, 25, 2, 21, 15, "Y", GREEN)
        setpx(b, 22, 8, GREEN_D)
    else:
        bubble(b, 25, 2, 21, 15, "N", RED)
        setpx(b, 22, 8, RED_D)
    return b


def frame_success(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="grin" if n == 1 else "smile",
                            look="up"))
    if n == 1:
        arm(b, [(18, 22), (15, 19), (14, 14)])
        arm(b, [(29, 22), (32, 19), (33, 14)])
        glove(b, 14, 11, fist=True)
        glove(b, 33, 11, fist=True)
        spark(b, 9, 8, GOLD)
        spark(b, 38, 8, GOLD)
        spark(b, 24, 2, WHITE)
    else:
        arm(b, [(18, 22), (15, 18), (14, 15)])
        glove(b, 13, 13, fist=True)
        arm(b, [(29, 22), (32, 19), (33, 15)])
        glove(b, 33, 12, fist=True)
        spark(b, 22, 2, GOLD)
        spark(b, 41, 15, GOLD)
    return b


def frame_failure(n):
    b = canvas()
    dust(b, 6, 35, 2)
    dust(b, 20, 35, 2)
    dust(b, 36, 35, 2)
    dust(b, 42, 35, 2)
    if n == 1:
        # de frente, cabeza a la izquierda
        rect(b, 8, 25, 17, 34, INK)
        rect(b, 9, 26, 16, 33, SKIN)
        rect(b, 9, 26, 16, 28, SKIN_D)
        rect(b, 9, 33, 16, 33, SKIN_D)
        # ojos X
        for ex in (11, 14):
            setpx(b, ex, 29, INK)
            setpx(b, ex + 1, 28, INK)
            setpx(b, ex + 1, 30, INK)
            setpx(b, ex + 2, 29, INK)
        rect(b, 13, 32, 15, 32, MOUTH_D)
        # casco caido a un lado
        rect(b, 5, 24, 15, 27, INK)
        rect(b, 6, 24, 14, 25, HELM)
        rect(b, 5, 26, 15, 27, HELM_D)
        setpx(b, 7, 24, HELM_L)
        # torso
        rect(b, 17, 27, 32, 36, INK)
        rect(b, 18, 28, 31, 35, UNI)
        rect(b, 19, 28, 30, 33, VEST)
        rect(b, 19, 28, 30, 28, VEST_L)
        rect(b, 20, 30, 23, 33, VEST_D)
        rect(b, 24, 30, 27, 33, VEST_D)
        rect(b, 31, 28, 33, 35, VEST_D)
        setpx(b, 32, 30, VEST)
        # piernas
        rect(b, 33, 28, 41, 34, INK)
        rect(b, 34, 29, 40, 33, UNI_D)
        rect(b, 35, 29, 37, 33, VEST)
        setpx(b, 35, 29, VEST_L)
        rect(b, 40, 28, 46, 33, INK)
        rect(b, 41, 29, 45, 32, (42, 50, 66))
        setpx(b, 41, 29, BOOT_L)
        # brazos tirados
        arm(b, [(21, 30), (19, 26), (18, 22)])
        glove(b, 18, 21)
        arm(b, [(29, 34), (33, 35), (36, 35)])
        glove(b, 37, 35)
    else:
        # de espaldas, cabeza a la derecha
        rect(b, 35, 26, 45, 35, INK)
        rect(b, 36, 27, 44, 34, HELM_D)
        rect(b, 37, 28, 43, 32, HELM)
        rect(b, 38, 29, 42, 31, HELM_D)
        rect(b, 39, 30, 41, 31, INK)
        rect(b, 34, 28, 36, 33, MASK_D)
        # torso de espaldas
        rect(b, 21, 27, 36, 36, INK)
        rect(b, 22, 28, 35, 35, UNI_D)
        rect(b, 23, 28, 34, 34, VEST)
        rect(b, 23, 28, 34, 28, VEST_L)
        rect(b, 26, 29, 27, 34, VEST_D)
        rect(b, 30, 29, 31, 34, VEST_D)
        rect(b, 20, 28, 22, 35, VEST_D)
        # piernas
        rect(b, 11, 28, 21, 34, INK)
        rect(b, 12, 29, 20, 33, UNI_D)
        rect(b, 14, 29, 17, 33, VEST)
        setpx(b, 14, 29, VEST_L)
        rect(b, 5, 29, 12, 35, INK)
        rect(b, 6, 30, 11, 34, (42, 50, 66))
        setpx(b, 6, 30, BOOT_L)
        # brazos
        arm(b, [(29, 33), (26, 35), (24, 35)])
        glove(b, 23, 35)
        arm(b, [(31, 31), (34, 35), (35, 36)])
        glove(b, 36, 36)
    # arma tirada
    if n == 1:
        stroke(b, [(32, 22), (44, 17)], STEEL_D, 2)
        rect(b, 29, 23, 33, 27, INK)
        rect(b, 30, 24, 32, 26, VEST_D)
        rect(b, 36, 19, 39, 23, INK)
        rect(b, 37, 20, 38, 22, VEST_D)
    else:
        stroke(b, [(5, 17), (16, 13)], STEEL_D, 2)
        rect(b, 14, 12, 18, 16, INK)
        rect(b, 15, 13, 17, 15, VEST_D)
        rect(b, 9, 17, 12, 21, INK)
        rect(b, 10, 18, 11, 20, VEST_D)
    return b


def frame_explore(n):
    b = canvas()
    rifle_slung(b)
    paste(b, ct_body_canvas("walk", phase=n, mouth="line",
                            look="right", headset=True))
    # brazos balanceandose
    if n == 1:
        arm(b, [(18, 22), (16, 26), (17, 28)])
        glove(b, 17, 29)
        arm(b, [(29, 22), (31, 25), (30, 27)])
        glove(b, 30, 28)
    else:
        arm(b, [(18, 22), (17, 25), (16, 27)])
        glove(b, 16, 28)
        arm(b, [(29, 22), (31, 26), (32, 28)])
        glove(b, 32, 29)
    # huellas del pasillo
    rect(b, 37, 37, 39, 37, SAND_D)
    rect(b, 41, 35, 43, 35, SAND_D)
    rect(b, 36, 34, 37, 34, SAND_D)
    # polvillo
    setpx(b, 35, 33, SAND)
    setpx(b, 44, 33, SAND)
    return b


def frame_compact(n):
    b = canvas()
    ct = ct_body_canvas("crouch", mouth="line")
    if n == 1:
        paste(b, ct)
    else:
        paste(b, scale_sprite(ct, 3, 4, ground=38))
    return b


def frame_delegate(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="shout" if n == 2 else "wide",
                            look="left" if n == 1 else "fwd"))
    if n == 1:
        # senalando a la izquierda
        arm(b, [(18, 22), (12, 21), (7, 21)])
        glove(b, 5, 21)
        rect(b, 3, 21, 4, 21, GLOVE)
        setpx(b, 2, 21, GLOVE)
        hline(b, 1, 4, 17, STEEL_L)
        hline(b, 1, 3, 19, STEEL_L)
        radio(b, 30, 27)
    else:
        arm(b, [(29, 22), (32, 18), (33, 15)])
        glove(b, 33, 14)
        radio(b, 31, 9)
        waves(b, 36, 12, CYAN, 2)
        # radio en el cinto
        radio(b, 14, 27)
    return b


def frame_build(n):
    b = canvas()
    paste(b, ct_body_canvas("crouch", mouth="wide" if n == 2 else "line",
                            look="down"))
    if n == 1:
        arm(b, [(15, 26), (16, 30), (18, 31)])
        arm(b, [(32, 26), (30, 29), (28, 30)])
        # C4 en las manos, por colocarla
        box(b, 17, 24, 35, 31, SAND)
        vline(b, 22, 25, 30, VEST_D)
        vline(b, 29, 25, 30, VEST_D)
        text(b, "C", 18, 25, INK, outline=None)
        text(b, "4", 23, 25, INK, outline=None)
        rect(b, 30, 25, 34, 27, INK)
        setpx(b, 31, 26, GREEN_D)
        glove(b, 18, 32)
        glove(b, 28, 31)
        spark(b, 37, 25, AMBER)
    else:
        arm(b, [(15, 26), (17, 30), (19, 32)])
        arm(b, [(32, 26), (26, 30), (23, 33)])
        # C4 plantada, teclado y LED
        box(b, 17, 29, 36, 37, SAND)
        vline(b, 22, 30, 36, VEST_D)
        vline(b, 30, 30, 36, VEST_D)
        text(b, "C", 18, 31, INK, outline=None)
        text(b, "4", 23, 31, INK, outline=None)
        box(b, 27, 31, 35, 36, DARK2)
        for ky in range(2):
            for kx in range(3):
                rect(b, 28 + kx * 2, 32 + ky * 2, 29 + kx * 2, 33 + ky * 2,
                     VEST_L)
        rect(b, 34, 30, 35, 31, INK)
        setpx(b, 34, 30, AMBER)
        glove(b, 19, 33)
        glove(b, 24, 34)
        spark(b, 38, 29, AMBER)
    return b


def frame_verify(n):
    b = canvas()
    if n == 1:
        paste(b, ct_body_canvas("stand", mouth="wide", look="up"))
        arm(b, [(29, 22), (33, 19), (35, 15)])
        glove(b, 35, 14)
        flashbang(b, 33, 7, True)
        spark(b, 25, 5, WHITE)
        spark(b, 42, 18, AMBER)
    else:
        paste(b, ct_body_canvas("stand", blink=True, mouth="line"))
        # mano cubriendo los ojos
        arm(b, [(29, 22), (31, 18), (29, 15)])
        glove(b, 28, 15)
        seal(b, 33, 4)
        # sello estampado abajo
        rect(b, 34, 30, 44, 36, INK)
        rect(b, 35, 31, 43, 35, PAPER)
        rect(b, 36, 32, 42, 34, PAPER_L)
        stroke(b, [(37, 33), (39, 35), (42, 31)], GREEN, 1)
    return b


def frame_judge(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="smirk" if n == 1 else "line",
                            look="down" if n == 2 else "fwd"))
    # corona de admin en el casco
    rect(b, 20, 3, 27, 3, GOLD_D)
    for cx in (20, 22, 24, 26):
        setpx(b, cx, 2, GOLD_L)
        setpx(b, cx, 1, GOLD)
    setpx(b, 27, 2, GOLD)
    if n == 1:
        arm(b, [(29, 22), (30, 17), (29, 14)])
        glove(b, 29, 13)
        gavel(b, 29, 12, down=False)
        spark(b, 44, 4, GOLD)
    else:
        arm(b, [(29, 22), (30, 22), (31, 21)])
        glove(b, 31, 21)
        gavel(b, 31, 21, down=True)
        # escritorio y golpe
        rect(b, 34, 30, 45, 33, INK)
        rect(b, 35, 30, 44, 32, WOOD)
        hline(b, 35, 44, 30, WOOD_L)
        spark(b, 37, 30, GOLD)
        spark(b, 43, 28, GOLD)
    return b


def frame_review(n):
    b = canvas()
    if n == 1:
        paste(b, ct_body_canvas("stand", mouth="line", look="down"))
        map_tac(b, 10, 19, 38, 34)
        # manos agarrando las esquinas inferiores del mapa
        glove(b, 11, 32)
        glove(b, 37, 32)
    else:
        paste(b, ct_body_canvas("stand", mouth="smirk", look="right"))
        map_roll(b, 34, 17)
        arm(b, [(29, 22), (32, 25), (35, 27)])
        glove(b, 35, 28)
        # lupa en la mano izquierda
        ring(b, 14, 24, 4, INK, 1)
        ring(b, 14, 24, 3, STEEL, 1)
        circle(b, 14, 24, 2, (150, 200, 214))
        setpx(b, 13, 23, WHITE)
        stroke(b, [(17, 27), (20, 29)], WOOD_D, 2)
        arm(b, [(18, 22), (18, 26), (20, 29)])
        glove(b, 21, 30)
    return b


def frame_jira(n):
    b = canvas()
    if n == 1:
        # granada de humo en el piso
        smoke_grenade(b, 8, 30, 1)
        circle(b, 30, 12, 4, GREY)
        circle(b, 34, 8, 3, GREY_L)
        setpx(b, 38, 6, GREY)
    else:
        # bengala encendida
        flare(b, 12, 29, 1)
        spark(b, 20, 14, GOLD)
        spark(b, 7, 9, AMBER)
        spark(b, 21, 5, GOLD_L)
        spark(b, 4, 18, GOLD)
    return b


def frame_jobs(n):
    b = canvas()
    paste(b, ct_body_canvas("stand", mouth="line", look="down"))
    arm(b, [(18, 22), (16, 26), (17, 29)])
    arm(b, [(29, 22), (31, 26), (30, 29)])
    tablet(b, 14, 22, 9 if n == 2 else 5, alert=(n == 2))
    glove(b, 16, 31)
    glove(b, 28, 31)
    if n == 2:
        # mano tocando la pantalla
        glove(b, 26, 26)
        spark(b, 31, 21, CYAN)
    return b


def sun(buf, stage):
    circle(buf, 24, 14, 9, GOLD_D)
    circle(buf, 24, 14, 8, GOLD)
    for k in range(0, 360, 30):
        rad = math.radians(k + stage * 15)
        for rr in (10, 12):
            setpx(buf, 24 + int(math.cos(rad) * rr),
                  14 + int(math.sin(rad) * rr), GOLD_L)
    circle(buf, 24, 14, 6, GOLD_D)


def frame_yolo(n, super_yolo=False):
    b = canvas()
    if super_yolo:
        sun(b, n)
    paste(b, ct_body_canvas("stand", glasses=True, bandana=True,
                            mouth="smirk", look="right" if n == 1 else "fwd"))
    if n == 1:
        # brazos cruzados
        arm(b, [(18, 22), (20, 26), (24, 25)])
        arm(b, [(29, 22), (27, 26), (24, 25)])
        glove(b, 24, 25)
        # cola del panuelo a la izquierda
        rect(b, 16, 19, 20, 20, RED)
        setpx(b, 15, 20, RED_D)
        setpx(b, 16, 21, RED)
    else:
        arm(b, [(29, 22), (32, 19), (33, 15)])
        glove(b, 33, 13, fist=True)
        arm(b, [(18, 22), (17, 26), (20, 28)])
        glove(b, 21, 28)
        # cola al otro lado
        rect(b, 27, 19, 31, 20, RED)
        setpx(b, 32, 20, RED_D)
        setpx(b, 31, 21, RED)
        spark(b, 38, 10, WHITE if not super_yolo else GOLD)
    return b


def frame_grandma(n):
    b = canvas()
    chicken(b, n == 1)
    return b


def frame_remember(n):
    b = canvas()
    hostage(b, n == 2)
    if n == 1:
        # marca de memoria (chip azul)
        rect(b, 34, 8, 40, 12, INK)
        rect(b, 35, 9, 39, 11, CYAN_D)
        hline(b, 36, 38, 10, CYAN)
        setpx(b, 39, 10, WHITE)
    else:
        # ondas de recuerdo
        waves(b, 36, 12, CYAN, 2)
        spark(b, 34, 6, CYAN)
    return b


def frame_bye(n):
    b = canvas()
    if n == 1:
        paste(b, ct_body_canvas("stand", mouth="smile", headset=True,
                                look="right"))
        arm(b, [(29, 22), (33, 20), (34, 16)])
        glove(b, 34, 14)
        spark(b, 38, 12, WHITE)
    else:
        paste(b, ct_body_canvas("stand", mouth="smile", helmet=False,
                                hair=True, headset=True, look="right"))
        # casco en la mano izquierda
        arm(b, [(18, 22), (15, 26), (14, 31)])
        helmet_item(b, 8, 29)
        glove(b, 15, 33)
        arm(b, [(29, 22), (33, 20), (34, 16)])
        glove(b, 34, 14)
        spark(b, 38, 12, WHITE)
    return b


# ── entrega ────────────────────────────────────────────────────────────────
FRAMES = [
    ("hi", [("hi_01.png", lambda: frame_hi(1)),
            ("hi_02.png", lambda: frame_hi(2))]),
    ("idle", [("idle.png", lambda: frame_idle(1)),
              ("idle_blink.png", lambda: frame_idle(2))]),
    ("think", [("think_01.png", lambda: frame_think(1)),
               ("think_02.png", lambda: frame_think(2))]),
    ("talk", [("talk_close.png", lambda: frame_talk(0)),
              ("talk_small.png", lambda: frame_talk(1)),
              ("talk_mid.png", lambda: frame_talk(2)),
              ("talk_wide.png", lambda: frame_talk(3))]),
    ("read", [("read_01.png", lambda: frame_read(1)),
              ("read_02.png", lambda: frame_read(2))]),
    ("write", [("write_01.png", lambda: frame_write(1)),
               ("write_02.png", lambda: frame_write(2))]),
    ("tool", [("tool_01.png", lambda: frame_tool(1)),
              ("tool_02.png", lambda: frame_tool(2)),
              ("tool_03.png", lambda: frame_tool(3))]),
    ("ask", [("ask_01.png", lambda: frame_ask(1)),
             ("ask_02.png", lambda: frame_ask(2))]),
    ("success", [("success_01.png", lambda: frame_success(1)),
                 ("success_02.png", lambda: frame_success(2))]),
    ("failure", [("failure_01.png", lambda: frame_failure(1)),
                 ("failure_02.png", lambda: frame_failure(2))]),
    ("compact", [("compact_01.png", lambda: frame_compact(1)),
                 ("compact_02.png", lambda: frame_compact(2))]),
    ("delegate", [("delegate_01.png", lambda: frame_delegate(1)),
                  ("delegate_02.png", lambda: frame_delegate(2))]),
    ("build", [("build_01.png", lambda: frame_build(1)),
               ("build_02.png", lambda: frame_build(2))]),
    ("verify", [("verify_01.png", lambda: frame_verify(1)),
                ("verify_02.png", lambda: frame_verify(2))]),
    ("judge", [("judge_01.png", lambda: frame_judge(1)),
               ("judge_02.png", lambda: frame_judge(2))]),
    ("review", [("review_01.png", lambda: frame_review(1)),
                ("review_02.png", lambda: frame_review(2))]),
    ("jira", [("jira_01.png", lambda: frame_jira(1)),
              ("jira_02.png", lambda: frame_jira(2))]),
    ("jobs", [("jobs_01.png", lambda: frame_jobs(1)),
              ("jobs_02.png", lambda: frame_jobs(2))]),
    ("explore", [("explore_01.png", lambda: frame_explore(1)),
                 ("explore_02.png", lambda: frame_explore(2))]),
    ("yolo", [("yolo_01.png", lambda: frame_yolo(1)),
              ("yolo_02.png", lambda: frame_yolo(2))]),
    ("super-yolo", [("super-yolo_01.png", lambda: frame_yolo(1, True)),
                    ("super-yolo_02.png", lambda: frame_yolo(2, True))]),
    ("remember", [("remember_01.png", lambda: frame_remember(1)),
                  ("remember_02.png", lambda: frame_remember(2))]),
    ("grandma", [("grandma_01.png", lambda: frame_grandma(1)),
                 ("grandma_02.png", lambda: frame_grandma(2))]),
    ("bye", [("bye_01.png", lambda: frame_bye(1)),
             ("bye_02.png", lambda: frame_bye(2))]),
]


def ihdr(path):
    with open(path, "rb") as fh:
        data = fh.read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("%s: no es PNG" % path)
    return struct.unpack(">IIBBBBB", data[16:29])


def verify(path, buf):
    w, h, depth, ctype, comp, filt, inter = ihdr(path)
    problems = []
    if (w, h) != (W, H):
        problems.append("tamano %dx%d" % (w, h))
    if depth != 8:
        problems.append("bit depth %d" % depth)
    if ctype != 6:
        problems.append("color type %d" % ctype)
    if comp != 0 or filt != 0 or inter != 0:
        problems.append("compresion/filtro/interlace no estandar")
    opaque = sum(1 for i in range(3, len(buf), 4) if buf[i])
    if opaque < 120:
        problems.append("frame casi vacio (%d px)" % opaque)
    for x in range(W):
        for y in (0, H - 1):
            if buf[(y * W + x) * 4 + 3]:
                problems.append("borde (%d,%d) opaco" % (x, y))
                break
    for y in range(H):
        for x in (0, W - 1):
            if buf[(y * W + x) * 4 + 3]:
                problems.append("borde (%d,%d) opaco" % (x, y))
                break
    if problems:
        raise AssertionError("%s: %s" % (path, "; ".join(problems)))
    return w, h, depth, ctype, inter, opaque


def main():
    total = 0
    for state, frames in FRAMES:
        folder = os.path.join(BASE, state)
        os.makedirs(folder, exist_ok=True)
        for name, build in frames:
            buf = build()
            path = os.path.join(folder, name)
            with open(path, "wb") as fh:
                fh.write(encode_png(W, H, buf))
            w, h, depth, ctype, inter, opaque = verify(path, buf)
            total += 1
            print("ok %-22s %2dx%-2d depth=%d type=%d interlace=%d px=%d"
                  % (state + "/" + name, w, h, depth, ctype, inter, opaque))
    print("TOTAL %d frames en %d estados" % (total, len(FRAMES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
