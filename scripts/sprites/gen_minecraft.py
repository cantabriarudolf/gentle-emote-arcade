#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set MINECRAFT del fork gentle-emote-arcade (24 estados, 48x40 RGBA).

Estilo blocky de Minecraft, fondo transparente real, movimiento por poses
sueltas: 2 frames por estado, 4 en ``talk`` (una boca cada uno) y 3 en
``tool`` (TNT apagada / encendida / explosion).

Reparto (un personaje por estado, como pide la tanda):

  Steve (camisa celeste, pantalon azul)
      hi ...... 01 saludo arriba, 02 brazo al costado
      idle .... idle.png + idle_blink.png (parpadeo)
      talk .... 4 bocas con pesos (close / small / mid / wide)
      read .... libro abierto, 01 lee, 02 pasa la pagina
      review .. libro + pluma roja, 01 escribe, 02 levanta la pluma
      write ... pico, 01 levantado, 02 picando el bloque
      ask ..... globo "?", 01 y 02
      success . brazos, 01 arriba, 02 saltito
      bye ..... 01 saluda, 02 de espaldas yendose
      jobs .... 01 mate + barra, 02 antorcha + barra llena
      explore . 01 antorcha izq, 02 antorcha der y paso
      build ... 01 bloque arriba, 02 bloque puesto
      yolo .... gafas, 01 y 02 corriendo
      super-yolo ... gafas + sol + estela de fuego
  Enderman (negro, ojos morados)
      think .... 01 mano en la barbilla, 02 cabeza ladeada
      delegate . 01 y 02 repartiendo (dos agentes chiquitos)
      remember . 01 perla al pecho, 02 perla a la cabeza
      verify ... 01 tilde chica, 02 sello verde
      compact .. 01 entero, 02 achicado (misma silueta)
  Creeper
      failure .. 01 de frente rajado, 02 en 3/4 vencido
      tool ..... TNT 01 apagada, 02 encendida, 03 explosion
  Golem de hierro .... judge 01 mazo arriba, 02 mazazo
  Aldeana narigona .... grandma 01 agujas arriba, 02 abajo
  Cohete de fuegos artificiales ... jira 01 despega, 02 en el aire

Solo stdlib: struct + zlib (PNG escrito a mano, sin PIL, sin red).
No toca ningun otro set: escribe unicamente en emotes/minecraft/.

    python3 gentle-emote-arcade/scripts/sprites/gen_minecraft.py
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
    """Bresenham de 1 px (varillas, bombillas, agujas)."""
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


def disc(buf, cx, cy, r, col):
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx * dx + dy * dy <= r * r:
                setpx(buf, cx + dx, cy + dy, col)


def box(buf, x0, y0, x1, y1, fill, dark=None, light=None):
    """Cubo con luz arriba-izquierda y sombra abajo-derecha."""
    rect(buf, x0, y0, x1, y1, fill)
    if light:
        hline(buf, x0, x1, y0, light)
        vline(buf, x0, y0, y1, light)
    if dark:
        hline(buf, x0, x1, y1, dark)
        vline(buf, x1, y0, y1, dark)


def speckle(buf, x0, y0, x1, y1, cols, cell=2, mod=7):
    """Manchas deterministicas (textura de piedra / camuflaje de creeper)."""
    for y in range(max(0, y0), min(H - 1, y1) + 1):
        for x in range(max(0, x0), min(W - 1, x1) + 1):
            k = ((x // cell) * 7 + (y // cell) * 11 + (x * y) % 5) % mod
            if k < len(cols):
                setpx(buf, x, y, cols[k])


def blit(buf, src, dx=0, dy=0):
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3]:
                setpx(buf, x + dx, y + dy, (src[i], src[i + 1], src[i + 2]))


def stamp(buf, draw, dx=0, dy=0):
    tmp = canvas()
    draw(tmp)
    blit(buf, tmp, dx, dy)


FONT = {
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "?": ["###", "..#", ".##", "...", ".#."],
}


def draw_text(buf, word, x0, y0, col, gap=1):
    x = x0
    for ch in word:
        glyph = FONT[ch]
        for dy, row in enumerate(glyph):
            for dx, cell in enumerate(row):
                if cell == "#":
                    setpx(buf, x + dx, y0 + dy, col)
        x += len(glyph[0]) + gap


# ------------------------------------------------------------------- paleta
SKIN = (200, 140, 105)
SKIND = (166, 110, 80)
SKINL = (226, 172, 136)

HAIR = (74, 48, 30)
HAIRD = (54, 34, 20)
HAIRL = (104, 72, 44)

SHIRT = (56, 170, 186)
SHIRTD = (38, 132, 148)
SHIRTL = (104, 206, 220)

PANTS = (54, 70, 164)
PANTSD = (38, 50, 124)
PANTSL = (84, 104, 196)

BOOT = (70, 70, 78)
BOOTD = (48, 48, 56)

EYEW = (244, 244, 238)
EYE = (56, 56, 150)
EYEL = (96, 96, 190)
GLASS = (26, 28, 34)
GLASSL = (98, 106, 122)
MOUTHD = (96, 52, 44)
MOUTHI = (150, 80, 74)
TEETH = (238, 232, 214)

CR = (104, 178, 86)
CRD = (74, 140, 60)
CRDD = (52, 106, 44)
CRL = (140, 206, 110)
CRBLK = (30, 36, 26)

EN = (26, 24, 34)
ENDK = (16, 15, 22)
ENL = (48, 44, 62)
PUP = (176, 84, 238)
PUPH = (222, 158, 255)
PUPD = (124, 52, 178)

IR = (188, 190, 194)
IRD = (140, 142, 150)
IRDD = (104, 106, 114)
IRL = (222, 224, 228)
VINE = (78, 124, 64)

VS = (196, 156, 124)
VSD = (160, 122, 94)
VSL = (222, 188, 158)
ROBE = (122, 90, 62)
ROBED = (94, 68, 46)
ROBEL = (150, 116, 84)
APRON = (96, 128, 74)
APROND = (72, 100, 56)
GRAY = (198, 198, 202)
GRAYD = (150, 150, 156)
YARN = (216, 98, 112)
YARND = (170, 70, 84)

TRED = (180, 54, 46)
TREDD = (138, 36, 32)
TREDL = (214, 88, 78)
TBAND = (200, 194, 184)
TBANDD = (160, 154, 144)

ROCK = (196, 74, 74)
ROCKD = (150, 50, 50)
ROCKL = (226, 110, 104)
GOLD = (230, 190, 86)
GOLDD = (176, 138, 52)
STAR1 = (120, 214, 238)
STAR2 = (232, 120, 230)
STAR3 = (150, 230, 130)
WHITE = (250, 248, 240)

FO = (216, 98, 32)
FY = (250, 168, 50)
FC = (255, 234, 148)
FW = (255, 252, 220)

COVER = (150, 86, 54)
COVERD = (112, 62, 38)
PAGE = (238, 226, 190)
PAGED = (206, 190, 150)
INKD = (60, 48, 40)
RIBBON = (196, 64, 64)
REDINK = (198, 54, 54)

WOOD = (150, 110, 64)
WOODD = (112, 80, 44)
STONE = (154, 150, 142)
STONED = (118, 114, 108)
STONEL = (186, 182, 172)
SMOKE = (168, 166, 162)
SMOKEL = (208, 206, 200)


# ------------------------------------------------------------------- Steve
# (rects de la mano derecha de la pantalla + ancla de la mano)
ARM = {
    "down": ([(29, 16, 33, 20, "shirt"), (29, 21, 33, 26, "skin"),
              (29, 27, 33, 27, "skind")], (31, 26)),
    "up": ([(29, 16, 33, 19, "shirt"), (31, 11, 35, 15, "skin"),
            (33, 5, 37, 10, "skin")], (35, 8)),
    "up_hi": ([(29, 16, 33, 19, "shirt"), (31, 9, 35, 15, "skin"),
               (34, 2, 38, 8, "skin")], (36, 4)),
    "out": ([(29, 16, 32, 20, "shirt"), (33, 17, 36, 20, "skin"),
             (37, 16, 39, 20, "skin")], (38, 18)),
    "out_up": ([(29, 16, 33, 19, "shirt"), (32, 12, 35, 16, "skin"),
                (34, 8, 38, 12, "skin")], (36, 10)),
    "bend": ([(29, 16, 33, 21, "shirt"), (26, 20, 30, 24, "skin"),
              (23, 19, 27, 23, "skin")], (25, 21)),
    "bend_hi": ([(29, 16, 33, 19, "shirt"), (27, 17, 31, 21, "skin"),
                 (24, 18, 28, 21, "skin")], (26, 19)),
}


def steve_arm(buf, side, mode):
    rects, hand = ARM[mode]
    for (x0, y0, x1, y1, kind) in rects:
        if side < 0:
            x0, x1 = W - 1 - x1, W - 1 - x0
        col = {"shirt": SHIRT, "skin": SKIN, "skind": SKIND}[kind]
        rect(buf, x0, y0, x1, y1, col)
        shade = {"shirt": SHIRTD, "skin": SKIND, "skind": BOOTD}[kind]
        hline(buf, x0, x1, y1, shade)
        if kind == "shirt":
            vline(buf, x1 if side > 0 else x0, y0, y1, SHIRTL)
    hx, hy = hand
    if side < 0:
        hx = W - 1 - hx
    return (hx, hy)


def steve_legs(buf, mode="stand"):
    if mode == "step1":
        spans = [(19, 30, 37), (26, 30, 36)]
    elif mode == "step2":
        spans = [(20, 30, 36), (26, 30, 37)]
    else:
        spans = [(20, 30, 37), (25, 30, 37)]
    for (x0, y0, y1) in spans:
        x1 = x0 + 3
        rect(buf, x0, y0, x1, y1, PANTS)
        vline(buf, x0, y0, y1, PANTSL)
        vline(buf, x1, y0, y1, PANTSD)
        hline(buf, x0, x1, y1 - 3, PANTSD)
        rect(buf, x0, y1 - 2, x1, y1, BOOT)
        hline(buf, x0, x1, y1 - 2, (92, 92, 100))
        hline(buf, x0, x1, y1, BOOTD)


def steve_torso(buf):
    rect(buf, 19, 16, 28, 28, SHIRT)
    vline(buf, 19, 16, 28, SHIRTL)
    vline(buf, 28, 16, 28, SHIRTD)
    hline(buf, 19, 28, 27, SHIRTD)
    hline(buf, 19, 28, 28, SHIRTD)
    rect(buf, 22, 15, 25, 15, SKIND)          # cuello


def steve_head(buf, hair=True):
    rect(buf, 18, 3, 29, 14, SKIN)
    vline(buf, 29, 3, 14, SKIND)
    hline(buf, 18, 29, 14, SKIND)
    if hair:
        rect(buf, 18, 3, 29, 5, HAIR)
        hline(buf, 18, 29, 3, HAIRL)
        rect(buf, 18, 6, 19, 9, HAIR)
        rect(buf, 28, 6, 29, 9, HAIR)
        rect(buf, 22, 6, 25, 6, HAIRD)


def steve_face(buf, mouth="close", blink=False, glasses=False, look="front"):
    if glasses:
        rect(buf, 19, 7, 28, 9, GLASS)
        setpx(buf, 20, 8, GLASSL)
        setpx(buf, 21, 8, GLASSL)
        setpx(buf, 26, 8, GLASSL)
        setpx(buf, 25, 8, GLASSL)
        return
    if blink:
        rect(buf, 20, 7, 22, 8, SKIN)
        rect(buf, 25, 7, 27, 8, SKIN)
        hline(buf, 20, 22, 8, SKIND)
        hline(buf, 25, 27, 8, SKIND)
        hline(buf, 20, 22, 7, SKINL)
        hline(buf, 25, 27, 7, SKINL)
    else:
        for (x0, x1) in ((20, 22), (25, 27)):
            rect(buf, x0, 7, x1, 8, EYEW)
            if look == "down":
                rect(buf, x0 + 1, 8, x0 + 1, 8, EYE)
            elif look == "left":
                rect(buf, x0, 7, x0, 8, EYE)
            elif look == "right":
                rect(buf, x1, 7, x1, 8, EYE)
            else:
                rect(buf, x0 + 1, 7, x0 + 1, 8, EYE)
    hline(buf, 20, 22, 6, SKIND)
    hline(buf, 25, 27, 6, SKIND)
    rect(buf, 23, 9, 24, 10, SKIND)
    setpx(buf, 23, 9, SKINL)
    if mouth == "close":
        hline(buf, 22, 25, 12, MOUTHD)
    elif mouth == "closed":
        hline(buf, 21, 26, 12, MOUTHD)
        hline(buf, 22, 25, 11, SKIND)
    elif mouth == "small":
        rect(buf, 23, 11, 24, 12, MOUTHD)
    elif mouth == "mid":
        rect(buf, 22, 11, 25, 12, MOUTHD)
        hline(buf, 22, 25, 11, TEETH)
    elif mouth == "wide":
        rect(buf, 21, 11, 26, 13, MOUTHD)
        hline(buf, 21, 26, 11, TEETH)
        hline(buf, 22, 26, 12, TEETH)
        rect(buf, 23, 13, 24, 13, MOUTHI)
    elif mouth == "smile":
        for (x, y) in ((21, 12), (22, 13), (23, 13), (24, 13), (25, 13),
                       (26, 12)):
            setpx(buf, x, y, MOUTHD)
    elif mouth == "open":
        rect(buf, 23, 12, 25, 13, MOUTHD)
    # barba de Steve
    rect(buf, 19, 13, 20, 14, SKIND)
    rect(buf, 27, 13, 28, 14, SKIND)


def draw_steve(buf, arm_l="down", arm_r="down", mouth="close", blink=False,
               legs="stand", glasses=False, look="front"):
    steve_legs(buf, legs)
    steve_torso(buf)
    steve_head(buf)
    steve_face(buf, mouth=mouth, blink=blink, glasses=glasses, look=look)
    hl = steve_arm(buf, -1, arm_l)
    hr = steve_arm(buf, +1, arm_r)
    return {"hand_l": hl, "hand_r": hr, "head": (18, 3, 29, 14)}


def draw_steve_back(buf, arm_r="up", legs="step1"):
    steve_legs(buf, legs)
    steve_torso(buf)
    rect(buf, 18, 3, 29, 14, HAIR)
    hline(buf, 18, 29, 3, HAIRL)
    rect(buf, 18, 11, 29, 14, SKIN)
    vline(buf, 29, 3, 14, HAIRD)
    hline(buf, 18, 29, 14, SKIND)
    vline(buf, 20, 5, 12, HAIRD)
    vline(buf, 25, 5, 12, HAIRD)
    vline(buf, 23, 15, 28, SHIRTD)      # costura de la espalda
    vline(buf, 24, 15, 28, SHIRTD)
    steve_arm(buf, +1, arm_r)
    steve_arm(buf, -1, "down")


# ------------------------------------------------------------------- props
def draw_book(buf, x, y, turn=False, marks=False):
    rect(buf, x, y, x + 13, y + 9, COVER)
    hline(buf, x, x + 13, y, COVERD)
    vline(buf, x, y, y + 9, COVERD)
    vline(buf, x + 13, y, y + 9, COVERD)
    rect(buf, x + 1, y + 2, x + 12, y + 8, PAGE)
    hline(buf, x + 1, x + 12, y + 8, PAGED)
    vline(buf, x + 6, y + 2, y + 8, COVERD)
    vline(buf, x + 7, y + 2, y + 8, COVERD)
    for yy in (y + 3, y + 5, y + 7):
        hline(buf, x + 2, x + 4, yy, PAGED)
        hline(buf, x + 9, x + 11, yy, PAGED)
    if turn:
        rect(buf, x + 9, y + 1, x + 12, y + 3, (250, 240, 208))
        hline(buf, x + 9, x + 12, y + 1, PAGED)
        setpx(buf, x + 12, y + 2, COVERD)
    if marks:
        hline(buf, x + 9, x + 12, y + 4, REDINK)
        hline(buf, x + 9, x + 11, y + 6, REDINK)
    rect(buf, x + 6, y + 10, x + 7, y + 11, RIBBON)


def draw_torch(buf, cx, top, h=4):
    """Antorcha: `top` es la punta de la llama."""
    rect(buf, cx, top + 3, cx + 1, top + 8, WOOD)
    vline(buf, cx + 1, top + 3, top + 8, WOODD)
    hline(buf, cx, cx + 1, top + 3, (96, 70, 40))
    rect(buf, cx - 1, top, cx + 2, top + 2, FO)
    rect(buf, cx, top - 1, cx + 1, top + 1, FY)
    setpx(buf, cx, top - 2, FC)
    setpx(buf, cx + 1, top - 1, FC)
    setpx(buf, cx - 1, top + 1, FC)
    setpx(buf, cx - 2, top - 3, (255, 210, 120))
    setpx(buf, cx + 3, top - 2, (255, 210, 120))


def draw_mate(buf, x, y):
    rect(buf, x, y, x + 4, y + 5, (122, 84, 52))
    vline(buf, x, y, y + 5, (96, 64, 38))
    rect(buf, x, y, x + 4, y + 1, (150, 116, 74))
    hline(buf, x, x + 4, y, (190, 190, 196))
    line(buf, x + 3, y, x + 5, y - 4, (206, 206, 212))
    setpx(buf, x + 5, y - 5, (216, 216, 222))
    setpx(buf, x + 6, y - 7, (222, 222, 226))
    setpx(buf, x + 7, y - 9, (238, 238, 242))


def draw_block(buf, x, y, kind="stone"):
    if kind == "grass":
        rect(buf, x, y, x + 7, y + 7, (134, 96, 64))
        rect(buf, x, y, x + 7, y + 2, (104, 168, 80))
        hline(buf, x, x + 7, y, (140, 196, 110))
        hline(buf, x, x + 7, y + 3, (84, 140, 64))
        speckle(buf, x, y + 4, x + 7, y + 7, [(118, 84, 56), (152, 112, 76)])
    else:
        rect(buf, x, y, x + 7, y + 7, STONE)
        hline(buf, x, x + 7, y, STONEL)
        hline(buf, x, x + 7, y + 7, STONED)
        vline(buf, x, y, y + 7, STONEL)
        vline(buf, x + 7, y, y + 7, STONED)
    setpx(buf, x, y + 7, (90, 88, 82))
    setpx(buf, x + 7, y + 7, (90, 88, 82))


def spark(buf, x, y):
    setpx(buf, x, y, FW)
    setpx(buf, x - 1, y, FY)
    setpx(buf, x + 1, y, FY)
    setpx(buf, x, y - 1, FY)
    setpx(buf, x, y + 1, FO)


def xp_orb(buf, x, y):
    rect(buf, x, y, x + 1, y + 1, (150, 220, 90))
    setpx(buf, x, y, (226, 250, 180))
    setpx(buf, x + 1, y + 1, (96, 168, 60))


def speed_line(buf, y, x0, x1):
    hline(buf, x0, x1, y, (128, 128, 136))
    hline(buf, x0, x1, y + 1, (198, 198, 204))


def draw_bubble(buf, x, y, glyph="?"):
    w, h = 12, 10
    rect(buf, x + 1, y, x + w - 2, y + h - 1, (46, 46, 56))
    rect(buf, x, y + 1, x + w - 1, y + h - 2, (46, 46, 56))
    rect(buf, x + 2, y + 1, x + w - 3, y + h - 2, (248, 248, 242))
    rect(buf, x + 1, y + 2, x + w - 2, y + h - 3, (248, 248, 242))
    draw_text(buf, glyph, x + 4, y + 3, (56, 90, 170))
    for (px, py) in ((x + 3, y + h), (x + 2, y + h + 1), (x + 2, y + h + 2)):
        setpx(buf, px, py, (46, 46, 56))


def star4(buf, x, y, col):
    setpx(buf, x, y, WHITE)
    setpx(buf, x - 1, y, col)
    setpx(buf, x + 1, y, col)
    setpx(buf, x, y - 1, col)
    setpx(buf, x, y + 1, col)


def draw_sun(buf, cx, cy, r=4):
    disc(buf, cx, cy, r, GOLD)
    disc(buf, cx, cy, r - 1, (248, 214, 120))
    for (dx, dy) in ((r + 2, 0), (-r - 2, 0), (0, r + 2), (0, -r - 2),
                     (r + 1, r + 1), (-r - 1, r + 1), (r + 1, -r - 1),
                     (-r - 1, -r - 1)):
        setpx(buf, cx + dx, cy + dy, GOLD)


def draw_pickaxe(buf, mode):
    """modo 'up' (pico alzado) o 'down' (golpe a la derecha)."""
    if mode == "up":
        vline(buf, 34, 6, 24, WOOD)
        vline(buf, 35, 6, 24, WOODD)
        rect(buf, 29, 2, 37, 4, IR)
        rect(buf, 27, 4, 29, 6, IR)
        rect(buf, 37, 4, 39, 6, IR)
        hline(buf, 29, 37, 2, IRL)
        setpx(buf, 31, 4, IRL)
        setpx(buf, 36, 4, IRL)
        setpx(buf, 29, 6, IRD)
        setpx(buf, 38, 6, IRD)
    else:
        line(buf, 31, 24, 35, 31, WOOD)
        line(buf, 32, 24, 36, 31, WOODD)
        rect(buf, 28, 29, 36, 31, IR)
        rect(buf, 26, 31, 28, 33, IR)
        rect(buf, 36, 31, 38, 33, IR)
        hline(buf, 28, 36, 29, IRL)
        hline(buf, 26, 38, 33, IRD)


# --------------------------------------------------------------- Enderman
def draw_enderman(buf, h=37, arm_l="down", arm_r="down", tilt=0):
    s = h / 37.0
    head_h = max(6, int(round(10 * s)))
    head_w = max(6, int(round(10 * s)))
    tw = max(5, int(round(8 * s)))
    th = max(6, int(round(11 * s)))
    top = 38 - h
    hx0 = 24 - head_w // 2 + tilt
    hx1 = hx0 + head_w - 1
    tx0 = 24 - tw // 2
    tx1 = tx0 + tw - 1
    hy0 = top
    hy1 = hy0 + head_h - 1
    ty0 = hy1 + 1
    ty1 = ty0 + th - 1
    ly0 = ty1 + 1
    ly1 = 38
    aw = max(2, int(round(3 * s)))
    al = max(4, int(round(18 * s)))

    lw = max(2, (tw - 1) // 2)
    for (x0, x1) in ((tx0, tx0 + lw - 1), (tx1 - lw + 1, tx1)):
        rect(buf, x0, ly0, x1, ly1, EN)
        vline(buf, x0, ly0, ly1, ENL)
        vline(buf, x1, ly0, ly1, ENDK)

    rect(buf, tx0, ty0, tx1, ty1, EN)
    vline(buf, tx0, ty0, ty1, ENL)
    vline(buf, tx1, ty0, ty1, ENDK)
    hline(buf, tx0, tx1, ty1, ENDK)

    rect(buf, hx0, hy0, hx1, hy1, EN)
    hline(buf, hx0, hx1, hy0, ENL)
    vline(buf, hx0, hy0, hy1, ENL)
    vline(buf, hx1, hy0, hy1, ENDK)
    hline(buf, hx0, hx1, hy1, ENDK)

    ew = max(2, head_w // 3)
    eh = max(1, head_h // 5)
    ey = hy0 + max(2, head_h // 4)
    lx = hx0 + max(1, head_w // 6)
    rx = hx1 - max(1, head_w // 6) - ew + 1
    for x0 in (lx, rx):
        rect(buf, x0, ey, x0 + ew - 1, ey + eh - 1, PUP)
        if eh > 1:
            rect(buf, x0, ey, x0 + ew - 1, ey, PUPD)
        if ew > 2:
            setpx(buf, x0 + 1, ey, PUPH)
    if head_h >= 9:
        rect(buf, hx0 + head_w // 2 - 1, hy1 - 1, hx0 + head_w // 2,
             hy1 - 1, PUPD)

    def arm(side, mode):
        if mode == "down":
            rects = [(tx1 + 1, ty0 + 1, tx1 + aw, ty0 + al)]
        elif mode == "up":
            rects = [(tx1 + 1, hy0 - 3, tx1 + aw, ty0 + 2)]
        elif mode == "out":
            rects = [(tx1 + 1, ty0 + 2, tx1 + aw + al // 2, ty0 + 2 + aw)]
        elif mode == "chin":
            rects = [(tx1 + 1, hy1 - 3, tx1 + aw, ty0 + al),
                     (hx0 + 2, hy1 - 2, tx1 + aw, hy1 - 1)]
        elif mode == "hold":
            rects = [(tx1 + 1, ty0 + 1, tx1 + aw, ty0 + al // 2 + 3),
                     (tx1 - 3, ty0 + al // 2, tx1 + aw - 1,
                      ty0 + al // 2 + 2)]
        else:
            rects = []
        for (x0, y0, x1, y1) in rects:
            if side < 0:
                x0, x1 = W - 1 - x1, W - 1 - x0
            rect(buf, x0, y0, x1, y1, EN)
            if (x1 - x0) >= (y1 - y0):
                hline(buf, x0, x1, y0, ENL)
                hline(buf, x0, x1, y1, ENDK)
            elif side > 0:
                vline(buf, x1, y0, y1, ENDK)
                vline(buf, x0, y0, y1, ENL)
            else:
                vline(buf, x0, y0, y1, ENL)
                vline(buf, x1, y0, y1, ENDK)

    arm(+1, arm_r)
    arm(-1, arm_l)
    return {"head": (hx0, hy0, hx1, hy1),
            "chest": ((tx0 + tx1) // 2, (ty0 + ty1) // 2)}


def ender_spark(buf, x, y):
    setpx(buf, x, y, PUPH)
    setpx(buf, x - 1, y, PUPD)
    setpx(buf, x + 1, y, PUPD)
    setpx(buf, x, y - 1, PUPD)


def mini_ender(buf, x, y):
    """Enderman chiquito (4 x 8) para delegate."""
    rect(buf, x, y, x + 3, y + 2, EN)
    vline(buf, x, y, y + 2, ENL)
    setpx(buf, x, y + 1, PUP)
    setpx(buf, x + 2, y + 1, PUP)
    rect(buf, x + 1, y + 3, x + 2, y + 5, EN)
    rect(buf, x, y + 6, x + 1, y + 7, ENDK)
    rect(buf, x + 2, y + 6, x + 3, y + 7, ENDK)


# ------------------------------------------------------------------ Creeper
CREEPER_MOUTH = [
    "..##.##.",
    ".######.",
    ".######.",
    "##.##.##",
    "#..##..#",
]


def draw_creeper(buf, angle="front", cracked=False):
    """Creeper de frente o en 3/4. Cabeza 14x14, cuerpo 14x14, patas."""
    if angle == "front":
        hx, bx = 17, 17
    else:
        hx, bx = 18, 17

    # patas (las de atras primero, mas oscuras)
    for (x0, col, y1) in ((21, CRDD, 36), (24, CRDD, 36),
                          (17, CRD, 37), (27, CRD, 37)):
        rect(buf, x0, 30, x0 + 3, y1, col)
        vline(buf, x0, 30, y1, CR)
        hline(buf, x0, x0 + 3, y1, CRDD)

    # cuerpo
    rect(buf, bx, 16, bx + 13, 29, CRD)
    vline(buf, bx, 16, 29, CR)
    vline(buf, bx + 13, 16, 29, CRDD)
    hline(buf, bx, bx + 13, 16, CRDD)      # costura cabeza / cuerpo
    hline(buf, bx, bx + 13, 29, CRDD)
    if angle != "front":
        rect(buf, bx, 16, bx + 1, 29, CRDD)
    speckle(buf, bx + 2 if angle != "front" else bx, 18, bx + 12, 28,
            [CRD, CRL], cell=3, mod=11)

    # cabeza
    rect(buf, hx, 2, hx + 13, 15, CR)
    hline(buf, hx, hx + 13, 2, CRL)
    vline(buf, hx, 2, 15, CRL)
    vline(buf, hx + 13, 2, 15, CRD)
    hline(buf, hx, hx + 13, 15, CRDD)
    speckle(buf, hx + 1, 3, hx + 12, 14, [CRD, CRL], cell=3, mod=11)

    # cara
    if angle == "front":
        ey0, ey1 = 5, 7
        for x0 in (19, 26):
            rect(buf, x0, ey0, x0 + 2, ey1, CRBLK)
        my = 9
        for row, mask in enumerate(CREEPER_MOUTH):
            for i, ch in enumerate(mask):
                if ch == "#":
                    setpx(buf, 20 + i, my + row, CRBLK)
    else:
        rect(buf, 17, 2, 18, 15, CRD)
        ey0, ey1 = 5, 7
        for x0 in (21, 27):
            rect(buf, x0, ey0, x0 + 1, ey1, CRBLK)
        my = 9
        for row, mask in enumerate(CREEPER_MOUTH):
            for i, ch in enumerate(mask):
                if ch == "#" and 0 <= i < 7:
                    setpx(buf, 21 + i, my + row, CRBLK)

    if cracked:
        # grieta de la cabeza (baja desde la sien izquierda)
        for (x, y) in ((18, 8), (18, 9), (19, 10), (18, 11), (18, 12),
                       (19, 13)):
            setpx(buf, x, y, CRDD)
        # grieta del cuerpo, en zigzag
        for (x, y) in ((20, 17), (20, 18), (21, 19), (21, 20), (20, 21),
                       (20, 22), (21, 23), (21, 24), (20, 25), (20, 26)):
            setpx(buf, x, y, CRDD)
        for (x, y) in ((22, 18), (19, 20), (22, 22), (19, 24), (22, 26)):
            setpx(buf, x, y, (36, 68, 32))


def draw_creeper_mini(buf, x, y, knocked=False):
    """Creeper chiquito para la escena de la TNT (10 x 12)."""
    if knocked:
        # tumbado de costado, ojos en X
        rect(buf, x, y + 2, x + 9, y + 6, CR)
        hline(buf, x, x + 9, y + 2, CRL)
        hline(buf, x, x + 9, y + 6, CRDD)
        rect(buf, x, y + 2, x + 4, y + 6, CR)
        vline(buf, x, y + 2, y + 6, CRL)
        for (px, py) in ((x + 1, y + 3), (x + 2, y + 3), (x + 1, y + 4),
                         (x + 2, y + 4)):
            setpx(buf, px, py, CRBLK)
        setpx(buf, x + 4, y + 5, CRBLK)
        # patitas para arriba
        rect(buf, x + 6, y + 1, x + 7, y + 2, CRD)
        rect(buf, x + 9, y, x + 9, y + 2, CRD)
        return
    rect(buf, x, y, x + 7, y + 6, CR)
    hline(buf, x, x + 7, y, CRL)
    vline(buf, x, y, y + 6, CRL)
    vline(buf, x + 7, y, y + 6, CRD)
    hline(buf, x, x + 7, y + 6, CRDD)
    speckle(buf, x + 1, y + 1, x + 6, y + 5, [CRD, CRL], cell=2, mod=7)
    rect(buf, x + 1, y + 2, x + 2, y + 3, CRBLK)
    rect(buf, x + 5, y + 2, x + 6, y + 3, CRBLK)
    setpx(buf, x + 3, y + 4, CRBLK)
    setpx(buf, x + 4, y + 4, CRBLK)
    setpx(buf, x + 2, y + 5, CRBLK)
    setpx(buf, x + 5, y + 5, CRBLK)
    rect(buf, x, y + 7, x + 7, y + 9, CR)
    hline(buf, x, x + 7, y + 9, CRDD)
    for lx in (x, x + 3, x + 5):
        rect(buf, lx, y + 10, lx + 1, y + 11, CRD)
        hline(buf, lx, lx + 1, y + 11, CRDD)


# --------------------------------------------------------------------- TNT
def draw_tnt(buf, x, y, lit=False, flash=False):
    """Bloque TNT de 20 x 17. `x, y` = esquina de arriba a la izquierda."""
    body = (250, 240, 230) if flash else TRED
    edge = TREDD if not flash else (206, 150, 140)
    rect(buf, x, y, x + 19, y + 16, body)
    hline(buf, x, x + 19, y, TREDL)
    vline(buf, x, y, y + 16, TREDL)
    vline(buf, x + 19, y, y + 16, edge)
    hline(buf, x, x + 19, y + 16, edge)
    # banda
    rect(buf, x + 1, y + 6, x + 18, y + 11, TBAND)
    hline(buf, x + 1, x + 18, y + 6, TBANDD)
    hline(buf, x + 1, x + 18, y + 11, TBANDD)
    draw_text(buf, "TNT", x + 4, y + 7, TREDD)
    # mecha
    vline(buf, x + 10, y - 4, y - 1, (110, 92, 62))
    setpx(buf, x + 9, y - 1, (94, 78, 52))
    if lit:
        spark(buf, x + 10, y - 5)
        setpx(buf, x + 10, y - 6, FC)
        setpx(buf, x + 12, y - 4, FY)
        setpx(buf, x + 8, y - 5, FY)


def draw_explosion(buf, cx=24, cy=20):
    disc(buf, cx, cy, 10, (186, 66, 40))
    for (dx, dy) in ((0, -11), (0, 11), (-11, 0), (11, 0), (8, -8),
                     (-8, -8), (8, 8), (-8, 8)):
        setpx(buf, cx + dx, cy + dy, FO)
        setpx(buf, cx + dx + (1 if dx > 0 else -1 if dx < 0 else 0),
              cy + dy + (1 if dy > 0 else -1 if dy < 0 else 0), FO)
    disc(buf, cx, cy, 8, FO)
    disc(buf, cx, cy, 6, FY)
    disc(buf, cx, cy, 3, FC)
    setpx(buf, cx, cy, FW)
    setpx(buf, cx + 1, cy - 1, FW)
    # escombros
    for (x, y) in ((cx - 15, cy - 9), (cx + 12, cy - 10), (cx - 14, cy + 8),
                   (cx + 14, cy + 6), (cx - 9, cy - 14), (cx + 8, cy + 13)):
        rect(buf, x, y, x + 2, y + 2, STONE)
        hline(buf, x, x + 2, y, STONEL)
        hline(buf, x, x + 2, y + 2, STONED)
    for (x, y) in ((cx - 18, cy + 1), (cx + 18, cy - 3), (cx - 4, cy - 16),
                   (cx + 5, cy + 16)):
        setpx(buf, x, y, SMOKEL)
        setpx(buf, x + 1, y, SMOKE)


# ----------------------------------------------------------- Golem de hierro
def draw_golem(buf, pose="up"):
    # piernas
    for x0 in (16, 26):
        rect(buf, x0, 30, x0 + 5, 37, IRD)
        vline(buf, x0, 30, 37, IR)
        rect(buf, x0, 36, x0 + 5, 37, IRDD)
    # torso
    rect(buf, 15, 13, 32, 29, IR)
    vline(buf, 15, 13, 29, IRL)
    vline(buf, 32, 13, 29, IRD)
    hline(buf, 15, 32, 29, IRDD)
    rect(buf, 18, 16, 29, 24, (200, 202, 206))
    hline(buf, 18, 29, 26, IRD)
    # cabeza
    rect(buf, 18, 3, 29, 12, IR)
    hline(buf, 18, 29, 3, IRL)
    vline(buf, 18, 3, 12, IRL)
    vline(buf, 29, 3, 12, IRD)
    # ojos y ceño
    rect(buf, 20, 6, 21, 7, (44, 46, 52))
    rect(buf, 26, 6, 27, 7, (44, 46, 52))
    hline(buf, 19, 28, 5, IRDD)
    # nariz larga
    rect(buf, 23, 6, 24, 16, IRL)
    vline(buf, 23, 6, 16, IR)
    # boca
    hline(buf, 21, 26, 10, IRDD)
    # brazo izquierdo (abajo)
    rect(buf, 9, 12, 14, 30, IR)
    vline(buf, 9, 12, 30, IRL)
    vline(buf, 14, 12, 30, IRD)
    rect(buf, 8, 26, 15, 32, IRD)
    hline(buf, 8, 15, 26, IR)
    hline(buf, 8, 15, 32, IRDD)
    for (x, y) in ((10, 14), (11, 15), (10, 16)):
        setpx(buf, x, y, VINE)
    setpx(buf, 12, 17, VINE)
    if pose == "up":
        rect(buf, 34, 8, 39, 16, IR)
        vline(buf, 39, 8, 16, IRD)
        rect(buf, 32, 4, 41, 10, IRD)
        hline(buf, 32, 41, 4, IRL)
        hline(buf, 32, 41, 10, IRDD)
        # mazo
        rect(buf, 34, 1, 42, 4, WOOD)
        hline(buf, 34, 42, 1, (170, 130, 78))
        hline(buf, 34, 42, 4, WOODD)
        vline(buf, 38, 5, 9, WOODD)
    else:
        rect(buf, 34, 13, 39, 24, IR)
        vline(buf, 39, 13, 24, IRD)
        rect(buf, 32, 24, 41, 30, IRD)
        hline(buf, 32, 41, 24, IR)
        hline(buf, 32, 41, 30, IRDD)
        # mazo apuntando abajo
        vline(buf, 36, 31, 34, WOODD)
        rect(buf, 31, 34, 40, 37, WOOD)
        hline(buf, 31, 40, 34, (170, 130, 78))
        hline(buf, 31, 40, 37, WOODD)
        for (x, y) in ((28, 34), (43, 33), (30, 30), (44, 36)):
            setpx(buf, x, y, GOLD)
            setpx(buf, x + 1, y, FC)


# --------------------------------------------------- aldeana (villager) abuela
def draw_grandma(buf, pose="up"):
    # pelo cano + rodete
    rect(buf, 22, 0, 25, 2, GRAY)
    hline(buf, 22, 25, 0, (226, 226, 230))
    vline(buf, 22, 0, 2, GRAYD)
    # cabeza
    rect(buf, 16, 2, 31, 14, VS)
    hline(buf, 16, 31, 2, VSL)
    vline(buf, 16, 2, 14, VSL)
    vline(buf, 31, 2, 14, VSD)
    hline(buf, 16, 31, 14, VSD)
    # canas a los costados
    rect(buf, 16, 3, 17, 7, GRAY)
    rect(buf, 30, 3, 31, 7, GRAY)
    # cejas
    rect(buf, 18, 5, 22, 5, GRAYD)
    rect(buf, 25, 5, 29, 5, GRAYD)
    hline(buf, 18, 29, 6, VSD)
    # ojos
    for (x0, x1) in ((18, 19), (28, 29)):
        rect(buf, x0, 7, x1, 8, EYEW)
        setpx(buf, x0, 8, (64, 54, 44))
        setpx(buf, x1, 8, (64, 54, 44))
    # nariz grande
    rect(buf, 21, 6, 25, 13, VSD)
    vline(buf, 21, 6, 13, VSL)
    hline(buf, 21, 25, 6, VSL)
    hline(buf, 21, 25, 13, (128, 94, 70))
    setpx(buf, 22, 8, VSL)
    setpx(buf, 22, 9, VSL)
    # boca
    hline(buf, 22, 24, 12, (120, 78, 62))
    # tunica
    rect(buf, 16, 15, 31, 33, ROBE)
    vline(buf, 16, 15, 33, ROBEL)
    vline(buf, 31, 15, 33, ROBED)
    hline(buf, 16, 31, 15, (168, 132, 96))
    # delantal
    rect(buf, 19, 18, 28, 31, APRON)
    vline(buf, 19, 18, 31, (118, 152, 92))
    vline(buf, 28, 18, 31, APROND)
    hline(buf, 19, 28, 18, (118, 152, 92))
    hline(buf, 20, 23, 22, APROND)
    # pies
    rect(buf, 17, 34, 22, 37, ROBED)
    rect(buf, 25, 34, 30, 37, ROBED)
    hline(buf, 17, 22, 37, (68, 48, 32))
    hline(buf, 25, 30, 37, (68, 48, 32))
    # mangas
    rect(buf, 12, 16, 17, 26, ROBE)
    vline(buf, 12, 16, 26, ROBEL)
    rect(buf, 30, 16, 35, 26, ROBE)
    vline(buf, 35, 16, 26, ROBED)
    # manos
    if pose == "up":
        rect(buf, 18, 23, 21, 27, VS)
        rect(buf, 26, 23, 29, 27, VS)
        hline(buf, 18, 21, 27, VSD)
        hline(buf, 26, 29, 27, VSD)
        # agujas
        line(buf, 20, 23, 24, 14, (214, 214, 220))
        line(buf, 27, 23, 23, 14, (214, 214, 220))
        setpx(buf, 24, 13, (232, 232, 238))
        setpx(buf, 23, 13, (232, 232, 238))
        # tejido
        for yy in (18, 19, 20):
            hline(buf, 22, 26, yy, YARN)
            hline(buf, 23, 25, yy, YARND)
        hline(buf, 22, 26, 17, (236, 140, 152))
    else:
        rect(buf, 18, 26, 21, 30, VS)
        rect(buf, 26, 26, 29, 30, VS)
        hline(buf, 18, 21, 30, VSD)
        hline(buf, 26, 29, 30, VSD)
        line(buf, 20, 27, 25, 21, (214, 214, 220))
        line(buf, 27, 27, 24, 21, (214, 214, 220))
        for yy in (23, 24, 25, 26):
            hline(buf, 21, 27, yy, YARN)
            hline(buf, 22, 26, yy, YARND)
    # ovillo
    disc(buf, 33, 33, 3, YARN)
    disc(buf, 33, 33, 2, (232, 128, 140))
    setpx(buf, 32, 32, (246, 168, 176))
    line(buf, 33, 30, 30, 27, YARND)


# --------------------------------------------------------------- cohete jira
def draw_rocket(buf, x, y, flame=1):
    """Cohete de fuegos artificiales (10 x 20) con la punta en (x, y)."""
    rect(buf, x + 3, y, x + 6, y + 1, GOLD)
    hline(buf, x + 3, x + 6, y, (248, 220, 130))
    rect(buf, x + 1, y + 2, x + 8, y + 2, GOLD)
    hline(buf, x + 1, x + 8, y + 2, (248, 220, 130))
    # cuerpo
    rect(buf, x, y + 3, x + 9, y + 18, ROCK)
    vline(buf, x, y + 3, y + 18, ROCKL)
    vline(buf, x + 9, y + 3, y + 18, ROCKD)
    hline(buf, x, x + 9, y + 18, ROCKD)
    hline(buf, x + 1, x + 8, y + 7, WHITE)
    hline(buf, x + 1, x + 8, y + 8, WHITE)
    hline(buf, x + 1, x + 8, y + 13, WHITE)
    # aletas
    rect(buf, x - 1, y + 13, x - 1, y + 18, ROCKD)
    rect(buf, x + 10, y + 13, x + 10, y + 18, ROCKD)
    hline(buf, x - 1, x, y + 18, ROCKD)
    hline(buf, x + 9, x + 10, y + 18, ROCKD)
    # palito
    rect(buf, x + 7, y + 19, x + 8, y + 24, WOOD)
    vline(buf, x + 8, y + 19, y + 24, WOODD)
    setpx(buf, x + 7, y + 24, (92, 66, 36))
    # llama
    if flame:
        base = y + 19
        for i in range(7):
            half = max(0, 4 - i // 2)
            rect(buf, x + 4 - half, base + i, x + 5 + half, base + i,
                 FO if i > 2 else FY)
        rect(buf, x + 3, base, x + 6, base + 1, FC)
        rect(buf, x + 4, base + 1, x + 5, base + 3, FW)
    # el palito se ve por fuera de la llama
    line(buf, x + 8, y + 20, x + 11, y + 27, WOOD)
    line(buf, x + 9, y + 20, x + 12, y + 27, WOODD)


# ------------------------------------------------------------------- escenas
def scene_hi(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_r="up", mouth="smile")
        for (x, y) in ((38, 4), (39, 6), (38, 8)):
            setpx(buf, x, y, (250, 220, 110))
        setpx(buf, 37, 5, (255, 250, 200))
    else:
        draw_steve(buf, arm_r="out_up", mouth="smile")
        for (x, y) in ((41, 11), (42, 13), (41, 15)):
            setpx(buf, x, y, (250, 220, 110))
        setpx(buf, 40, 12, (255, 250, 200))
    return buf


def scene_idle(p):
    buf = canvas()
    draw_steve(buf, blink=(p == 2))
    return buf


def scene_talk(p):
    buf = canvas()
    mouth = {1: "closed", 2: "small", 3: "mid", 4: "wide"}[p]
    draw_steve(buf, mouth=mouth)
    return buf


def scene_read(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_l="bend_hi", arm_r="bend_hi", look="down",
                   mouth="close")
        draw_book(buf, 17, 18)
    else:
        draw_steve(buf, arm_l="bend_hi", arm_r="bend_hi", look="down",
                   mouth="small")
        draw_book(buf, 17, 18, turn=True)
        setpx(buf, 33, 17, (250, 240, 208))
    return buf


def scene_review(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_l="bend_hi", arm_r="bend_hi", look="down",
                   mouth="close")
        draw_book(buf, 17, 18, marks=True)
        line(buf, 28, 17, 33, 9, (222, 222, 228))
        line(buf, 29, 17, 34, 9, (176, 42, 42))
        setpx(buf, 27, 18, REDINK)
        setpx(buf, 26, 19, (156, 36, 36))
    else:
        draw_steve(buf, arm_l="bend_hi", arm_r="out_up", look="down",
                   mouth="smile")
        draw_book(buf, 17, 18, marks=True)
        line(buf, 36, 11, 40, 4, (222, 222, 228))
        line(buf, 37, 11, 41, 4, (176, 42, 42))
        setpx(buf, 35, 12, REDINK)
        # tilde verde grande
        for (x, y) in ((34, 17), (35, 18), (36, 19), (37, 18), (38, 16),
                       (39, 14), (40, 12), (34, 18), (35, 19), (36, 20),
                       (37, 19), (38, 17), (39, 15), (40, 13)):
            setpx(buf, x, y, (110, 200, 90))
    return buf


def scene_write(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_l="bend", arm_r="up", mouth="close")
        draw_pickaxe(buf, "up")
    else:
        draw_steve(buf, arm_l="down", arm_r="down", mouth="smile")
        draw_pickaxe(buf, "down")
        draw_block(buf, 34, 30, "stone")
        spark(buf, 31, 28)
        spark(buf, 40, 32)
        setpx(buf, 33, 27, FC)
    return buf


def scene_ask(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_r="out", mouth="small")
        draw_bubble(buf, 33, 1)
        setpx(buf, 45, 5, (56, 90, 170))
    else:
        draw_steve(buf, arm_r="out_up", mouth="close", look="left")
        draw_bubble(buf, 32, 4)
        setpx(buf, 44, 8, (56, 90, 170))
    return buf


def scene_success(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_l="up", arm_r="up", mouth="smile")
    else:
        tmp = canvas()
        draw_steve(tmp, arm_l="up_hi", arm_r="up_hi", mouth="smile",
                   legs="step1")
        blit(buf, tmp, 0, -1)
    for (x, y) in ((8, 12), (41, 10), (11, 25), (39, 22), (6, 20)):
        xp_orb(buf, x, y)
    return buf


def scene_bye(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_r="up", mouth="smile")
        setpx(buf, 38, 5, (250, 220, 110))
        setpx(buf, 39, 7, (255, 250, 200))
    else:
        draw_steve_back(buf, arm_r="up", legs="step1")
        for (x, y) in ((13, 37), (10, 36), (7, 35)):
            setpx(buf, x, y, (170, 170, 176))
        setpx(buf, 37, 8, (250, 220, 110))
    return buf


def scene_jobs(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_r="bend", mouth="small", look="down")
        draw_mate(buf, 24, 19)
        progress = 0.35
    else:
        draw_steve(buf, arm_r="out_up", mouth="smile")
        draw_torch(buf, 35, 4)
        progress = 1.0
    # barra de progreso tipo XP
    rect(buf, 4, 34, 16, 37, (44, 44, 52))
    rect(buf, 5, 35, 15, 36, (78, 78, 88))
    fill = int(round(10 * progress))
    if fill:
        rect(buf, 5, 35, 4 + fill, 36, (126, 210, 92))
        hline(buf, 5, 4 + fill, 35, (176, 240, 140))
    return buf


def scene_explore(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_l="out_up", mouth="close")
        draw_torch(buf, 12, 4)
        setpx(buf, 15, 2, (255, 214, 130))
        for (x, y) in ((30, 38), (33, 38), (36, 38)):
            setpx(buf, x, y, (150, 146, 138))
    else:
        draw_steve(buf, arm_r="down", legs="step1", mouth="smile")
        draw_torch(buf, 33, 17)
        for (x, y) in ((10, 38), (13, 38), (16, 38)):
            setpx(buf, x, y, (150, 146, 138))
    return buf


def scene_build(p):
    buf = canvas()
    if p == 1:
        stamp(buf, lambda b: draw_steve(b, arm_r="up_hi", arm_l="down",
                                        mouth="close"), -3)
        draw_block(buf, 30, 2, "stone")
        setpx(buf, 31, 1, STONEL)
        setpx(buf, 29, 9, SMOKEL)
    else:
        stamp(buf, lambda b: draw_steve(b, arm_r="down", arm_l="down",
                                        mouth="smile"), -3)
        draw_block(buf, 30, 30, "stone")
        for (x, y) in ((28, 29), (39, 28), (27, 33), (40, 33), (29, 38),
                       (38, 38)):
            setpx(buf, x, y, SMOKEL)
            setpx(buf, x + 1, y, SMOKE)
    return buf


def scene_yolo(p):
    buf = canvas()
    if p == 1:
        draw_steve(buf, arm_r="out", arm_l="down", glasses=True,
                   mouth="smile", legs="step1")
        for y in (17, 23, 29):
            speed_line(buf, y, 2, 7)
    else:
        draw_steve(buf, arm_r="down", arm_l="out", glasses=True,
                   mouth="smile", legs="step2")
        for y in (18, 24, 30):
            speed_line(buf, y, 1, 6)
    return buf


def scene_super_yolo(p):
    buf = canvas()
    if p == 1:
        draw_sun(buf, 38, 8, 4)
        draw_steve(buf, arm_l="out_up", arm_r="out_up", glasses=True,
                   mouth="wide", legs="step1")
        for (x, y) in ((20, 37), (28, 37), (24, 38)):
            setpx(buf, x, y, FY)
        for (x, y) in ((16, 36), (32, 36)):
            setpx(buf, x, y, GOLD)
    else:
        draw_sun(buf, 9, 7, 4)
        tmp = canvas()
        draw_steve(tmp, arm_l="up", arm_r="up", glasses=True, mouth="wide",
                   legs="step2")
        blit(buf, tmp, 0, -1)
        for (x, y) in ((19, 36), (26, 36), (22, 37)):
            setpx(buf, x, y, FY)
        for (x, y) in ((14, 34), (33, 35)):
            setpx(buf, x, y, FC)
    return buf


def scene_think(p):
    buf = canvas()
    if p == 1:
        draw_enderman(buf, arm_r="chin", arm_l="down")
    else:
        draw_enderman(buf, arm_l="chin", arm_r="down", tilt=-1)
    for (x, y) in (((32, 12), (36, 16), (34, 20)) if p == 1
                   else ((12, 14), (14, 18), (11, 22))):
        ender_spark(buf, x, y)
    setpx(buf, 35 if p == 1 else 13, 8, PUPD)
    return buf


def scene_delegate(p):
    buf = canvas()
    if p == 1:
        draw_enderman(buf, arm_r="out", arm_l="down")
        mini_ender(buf, 38, 30)
        mini_ender(buf, 43, 31)
    else:
        draw_enderman(buf, arm_l="out", arm_r="down")
        mini_ender(buf, 2, 30)
        mini_ender(buf, 6, 31)
    for (x, y) in ((34, 8), (14, 6)):
        setpx(buf, x, y, PUPD)
    return buf


def scene_remember(p):
    buf = canvas()
    if p == 1:
        draw_enderman(buf, arm_l="hold", arm_r="down")
        rect(buf, 20, 20, 24, 24, PUPD)
        hline(buf, 20, 24, 20, PUP)
        setpx(buf, 21, 21, PUPH)
        ender_spark(buf, 18, 18)
        ender_spark(buf, 27, 24)
    else:
        draw_enderman(buf, arm_r="chin", arm_l="down", tilt=1)
        rect(buf, 26, 10, 30, 14, PUPD)
        hline(buf, 26, 30, 10, PUP)
        setpx(buf, 27, 11, PUPH)
        for (x, y) in ((33, 8), (35, 12), (29, 5)):
            ender_spark(buf, x, y)
    return buf


def scene_verify(p):
    buf = canvas()
    if p == 1:
        draw_enderman(buf, arm_r="out", arm_l="down")
        # tilde chica
        for (x, y) in ((39, 20), (39, 21), (40, 22), (41, 21), (42, 20),
                       (43, 19)):
            setpx(buf, x, y, (110, 200, 90))
    else:
        draw_enderman(buf, arm_l="out", arm_r="down")
        disc(buf, 9, 20, 5, (74, 150, 70))
        disc(buf, 9, 20, 4, (110, 200, 90))
        for (x, y) in ((7, 20), (7, 21), (8, 22), (9, 21), (10, 20),
                       (11, 19), (12, 18)):
            setpx(buf, x, y, (240, 250, 232))
        setpx(buf, 13, 16, (200, 240, 180))
    return buf


def scene_compact(p):
    buf = canvas()
    if p == 1:
        draw_enderman(buf, h=37)
        # pinzas que aprietan de los costados
        for (x, y) in ((12, 7), (13, 8), (12, 9), (34, 7), (33, 8),
                       (34, 9)):
            setpx(buf, x, y, PUP)
    else:
        draw_enderman(buf, h=18)
        for (x, y) in ((20, 2), (24, 2), (28, 3), (17, 8), (31, 9),
                       (22, 12), (26, 13)):
            ender_spark(buf, x, y)
        # flechas de compresion arriba
        for (x, y) in ((20, 15), (24, 14), (28, 15)):
            setpx(buf, x, y, PUPD)
            setpx(buf, x, y + 1, PUP)
            setpx(buf, x, y + 2, PUPD)
            setpx(buf, x - 1, y + 1, PUP)
            setpx(buf, x + 1, y + 1, PUP)
    return buf


def scene_failure(p):
    buf = canvas()
    if p == 1:
        draw_creeper(buf, angle="front", cracked=True)
        for (x, y) in ((14, 8), (13, 12), (34, 6), (35, 10)):
            setpx(buf, x, y, SMOKEL)
            setpx(buf, x, y + 1, SMOKE)
        setpx(buf, 17, 6, WHITE)
        setpx(buf, 30, 9, WHITE)
        setpx(buf, 24, 1, (220, 220, 216))
    else:
        stamp(buf, lambda b: draw_creeper(b, angle="quarter", cracked=True),
               -4, 1)
        for (x, y) in ((9, 34), (13, 33), (6, 31), (38, 32), (41, 34)):
            setpx(buf, x, y, SMOKE)
            setpx(buf, x + 1, y, SMOKEL)
        setpx(buf, 12, 28, SMOKEL)
        setpx(buf, 11, 30, SMOKE)
    return buf


def scene_tool(p):
    buf = canvas()
    if p == 1:
        draw_tnt(buf, 6, 14)
        draw_creeper_mini(buf, 32, 26)
        setpx(buf, 29, 13, SMOKEL)
        setpx(buf, 30, 12, SMOKE)
    elif p == 2:
        draw_tnt(buf, 6, 14, lit=True, flash=True)
        draw_creeper_mini(buf, 34, 26)
        for (x, y) in ((29, 10), (31, 8), (27, 7)):
            setpx(buf, x, y, FY)
            setpx(buf, x + 1, y - 1, FC)
        setpx(buf, 36, 24, SMOKEL)
        setpx(buf, 39, 23, SMOKE)
    else:
        draw_explosion(buf, 22, 18)
        draw_creeper_mini(buf, 33, 28, knocked=True)
        for (x, y) in ((8, 8), (4, 20), (10, 30), (36, 6), (42, 14)):
            setpx(buf, x, y, SMOKE)
            setpx(buf, x + 1, y + 1, SMOKEL)
        for (x, y) in ((18, 38), (26, 38), (30, 38)):
            setpx(buf, x, y, (96, 90, 84))
    return buf


def scene_judge(p):
    buf = canvas()
    if p == 1:
        draw_golem(buf, pose="up")
        for (x, y) in ((30, 1), (45, 5), (44, 1)):
            setpx(buf, x, y, GOLD)
    else:
        draw_golem(buf, pose="down")
        for (x, y) in ((26, 32), (45, 30), (42, 28), (29, 36)):
            setpx(buf, x, y, GOLD)
            setpx(buf, x + 1, y - 1, FC)
        for (x, y) in ((28, 38), (43, 38)):
            setpx(buf, x, y, SMOKEL)
    return buf


def scene_jira(p):
    buf = canvas()
    if p == 1:
        draw_rocket(buf, 18, 4)
        for (x, y) in ((12, 32), (22, 33), (15, 35), (27, 31), (9, 29),
                       (30, 35), (18, 30), (24, 36), (5, 33), (33, 31)):
            setpx(buf, x, y, SMOKE)
            setpx(buf, x + 1, y, SMOKEL)
            setpx(buf, x, y + 1, (150, 148, 144))
        for (x, y) in ((14, 38), (20, 38), (27, 38), (34, 38), (8, 38)):
            setpx(buf, x, y, (198, 196, 192))
        star4(buf, 40, 13, STAR1)
        star4(buf, 6, 17, STAR2)
    else:
        draw_rocket(buf, 19, 1, flame=0)
        for (x, y) in ((24, 22), (22, 26), (27, 30), (25, 34), (24, 38)):
            setpx(buf, x, y, GOLD)
        for (x, y, col) in ((13, 9, STAR1), (35, 6, STAR2),
                            (11, 17, STAR3), (37, 15, STAR1),
                            (16, 2, STAR2), (31, 3, STAR3),
                            (8, 12, STAR1), (40, 11, STAR2)):
            star4(buf, x, y, col)
        for (x, y) in ((17, 21), (33, 22), (14, 29), (36, 31), (24, 35)):
            setpx(buf, x, y, (238, 220, 150))
            setpx(buf, x, y + 1, GOLDD)
    return buf


def scene_grandma(p):
    buf = canvas()
    stamp(buf, lambda b: draw_grandma(b, pose="up" if p == 1 else "down"),
          0, 1)
    return buf


# ------------------------------------------------------------------- salida
BASE = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "emotes",
    "minecraft"))

STATES = [
    ("hi", [("hi_01.png", scene_hi, 1), ("hi_02.png", scene_hi, 2)]),
    ("idle", [("idle.png", scene_idle, 1), ("idle_blink.png", scene_idle, 2)]),
    ("talk", [("talk_close.png", scene_talk, 1),
              ("talk_small.png", scene_talk, 2),
              ("talk_mid.png", scene_talk, 3),
              ("talk_wide.png", scene_talk, 4)]),
    ("think", [("think_01.png", scene_think, 1),
               ("think_02.png", scene_think, 2)]),
    ("read", [("read_01.png", scene_read, 1),
              ("read_02.png", scene_read, 2)]),
    ("write", [("write_01.png", scene_write, 1),
               ("write_02.png", scene_write, 2)]),
    ("tool", [("tool_01.png", scene_tool, 1),
              ("tool_02.png", scene_tool, 2),
              ("tool_03.png", scene_tool, 3)]),
    ("ask", [("ask_01.png", scene_ask, 1), ("ask_02.png", scene_ask, 2)]),
    ("success", [("success_01.png", scene_success, 1),
                 ("success_02.png", scene_success, 2)]),
    ("failure", [("failure_01.png", scene_failure, 1),
                 ("failure_02.png", scene_failure, 2)]),
    ("compact", [("compact_01.png", scene_compact, 1),
                 ("compact_02.png", scene_compact, 2)]),
    ("delegate", [("delegate_01.png", scene_delegate, 1),
                  ("delegate_02.png", scene_delegate, 2)]),
    ("explore", [("explore_01.png", scene_explore, 1),
                 ("explore_02.png", scene_explore, 2)]),
    ("build", [("build_01.png", scene_build, 1),
               ("build_02.png", scene_build, 2)]),
    ("verify", [("verify_01.png", scene_verify, 1),
                ("verify_02.png", scene_verify, 2)]),
    ("judge", [("judge_01.png", scene_judge, 1),
               ("judge_02.png", scene_judge, 2)]),
    ("review", [("review_01.png", scene_review, 1),
                ("review_02.png", scene_review, 2)]),
    ("jira", [("jira_01.png", scene_jira, 1),
              ("jira_02.png", scene_jira, 2)]),
    ("jobs", [("jobs_01.png", scene_jobs, 1),
              ("jobs_02.png", scene_jobs, 2)]),
    ("yolo", [("yolo_01.png", scene_yolo, 1),
              ("yolo_02.png", scene_yolo, 2)]),
    ("super-yolo", [("super-yolo_01.png", scene_super_yolo, 1),
                    ("super-yolo_02.png", scene_super_yolo, 2)]),
    ("remember", [("remember_01.png", scene_remember, 1),
                  ("remember_02.png", scene_remember, 2)]),
    ("grandma", [("grandma_01.png", scene_grandma, 1),
                 ("grandma_02.png", scene_grandma, 2)]),
    ("bye", [("bye_01.png", scene_bye, 1), ("bye_02.png", scene_bye, 2)]),
]


def check_png(data, path):
    """IHDR a mano: 48x40, 8 bits, color type 6 (RGBA), sin interlace."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("firma PNG invalida: " + path)
    if data[12:16] != b"IHDR":
        raise SystemExit("sin IHDR: " + path)
    w, h, depth, color, comp, filt, inter = struct.unpack(">IIBBBBB",
                                                          data[16:29])
    if (w, h, depth, color, comp, filt, inter) != (W, H, 8, 6, 0, 0, 0):
        raise SystemExit("IHDR fuera de norma %s: %dx%d d%d ct%d i%d"
                         % (path, w, h, depth, color, inter))
    if not data.startswith(b"\x89PNG") or b"IDAT" not in data:
        raise SystemExit("PNG incompleto: " + path)


def main():
    resumen = []
    for state, frames in STATES:
        directory = os.path.join(BASE, state)
        os.makedirs(directory, exist_ok=True)
        total = 0
        names = []
        for (name, draw, pose) in frames:
            path = os.path.join(directory, name)
            data = encode_png(W, H, draw(pose))
            check_png(data, path)
            with open(path, "wb") as fh:
                fh.write(data)
            total += len(data)
            names.append("%s (%d B)" % (name, len(data)))
            print("ok  %-22s %6d B" % (state + "/" + name, len(data)))
        resumen.append((state, names, total))
    print("\nset minecraft: %d estados, %d frames"
          % (len(resumen), sum(len(n) for _, n, _ in resumen)))
    for state, names, total in resumen:
        print("%-11s %2d frames %6d B  %s"
              % (state, len(names), total, ", ".join(names)))


if __name__ == "__main__":
    main()
