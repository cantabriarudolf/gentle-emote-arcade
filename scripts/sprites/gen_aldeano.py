#!/usr/bin/env python3
"""Dibuja por codigo los estados del ALDEANO de AoE II (48x40, 8-bit RGBA).

Base visual: `antigravity-pack/refs/raw_idle.jpg` y
`antigravity-pack/refs/ref-villager-moddb.png` (aldeano con sombrero de paja,
tunica marron con cinturon y botas). Un solo personaje y una sola paleta: cada
pose solo mueve brazos, boca, sombrero y accesorios de la escena.

El cuerpo entero se dibuja en una capa y se pega con un unico contorno de 1 px
(dilatacion del alfa): silueta limpia de sprite clasico, sin brochazos, con
sombreado interno para separar brazos, cinturon y pliegues.

Estados que genera (carpeta dentro de `emotes/aoe/`):

    hi/         hi_01, hi_02                     saludo (mano arriba / abajo)
    idle/       idle, idle_blink                 parpadeo del mismo aldeano
    talk/       talk_close, talk_small,
                talk_mid, talk_wide, talk        cuatro bocas + neutral
    ask/        ask_01, ask_02                   globo Y / globo N
    success/    success_01, success_02           brazos arriba / brazos afuera
    failure/    failure_01, failure_02           caido de frente / de espaldas
    bye/        bye_01, bye_02                   sombrero puesto / en la mano
    jobs/       jobs_01, jobs_02                 tomando mate / mirando la barra
    yolo/       yolo_01, yolo_02                 vincha magenta + cohete (izq/der)
    super-yolo/ super-yolo_01, super-yolo_02     igual + sol
    grandma/    grandma_01, grandma_02           aldeana tejiendo (manos arriba/abajo)
    write/      write_01, write_02               martillo arriba / abajo

Solo stdlib (struct + zlib): no usa PIL ni red. Uso, desde la raiz del repo:

    python3 gentle-emote-arcade/scripts/sprites/gen_aldeano.py

Al final verifica el IHDR de cada PNG (48x40, bit depth 8, color type 6,
interlace 0), que haya alfa real (0 y 255) y que las dos poses del ciclo no
sean el mismo bitmap; imprime la lista `estado: frames y bytes`.
"""

import os
import struct
import zlib

W, H = 48, 40

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..")
)
SET_DIR = os.path.join(ROOT, "emotes", "aoe")

# Guarda: si la ruta no es el set `emotes/aoe` del repo, no escribe nada.
if not os.path.isfile(os.path.join(SET_DIR, "emotes.json")):
    raise SystemExit(
        "no encuentro emotes/aoe/emotes.json en %s: correr el script desde "
        "gentle-emote-arcade/" % SET_DIR
    )

# ── Paleta (una sola para todo el set) ──────────────────────────────────────
OUT = (26, 18, 12)          # contorno
HAT = (200, 166, 96)        # paja
HAT_L = (226, 194, 122)
HAT_D = (160, 126, 66)
HAT_BAND = (74, 50, 30)
SKIN = (232, 178, 138)
SKIN_L = (246, 208, 172)
SKIN_D = (198, 138, 100)
HAIR = (74, 48, 28)
HAIR_L = (108, 74, 44)
HAIR_G = (198, 196, 188)    # canas de la abuela
HAIR_G_D = (148, 146, 140)
TUNIC = (126, 92, 52)
TUNIC_L = (152, 114, 66)
TUNIC_D = (96, 68, 36)
BELT = (58, 40, 26)
BUCKLE = (216, 182, 88)
PANTS = (92, 68, 42)
PANTS_D = (68, 50, 30)
PANTS_L = (110, 82, 52)
BOOT = (56, 38, 24)
BOOT_L = (84, 58, 34)
BOOT_D = (40, 26, 16)
LIP = (152, 94, 74)
MOUTH = (104, 50, 42)
TEETH = (240, 228, 202)
CREAM = (238, 226, 198)
PARCH = (236, 224, 190)
PARCH_D = (200, 182, 142)
GREEN = (92, 166, 74)
GREEN_L = (128, 196, 106)
RED = (186, 66, 54)
YELLOW = (240, 202, 92)
YELLOW_D = (198, 156, 52)
MAGENTA = (232, 62, 152)
MAGENTA_D = (168, 34, 106)
GREY = (186, 190, 200)
GREY_D = (124, 128, 140)
STEEL = (208, 212, 222)
STEEL_L = (234, 238, 246)
STEEL_D = (146, 152, 166)
FLAME = (244, 148, 56)
FLAME_L = (252, 214, 92)
DUST = (206, 186, 152)
DUST_D = (170, 148, 118)
WOOD = (124, 88, 50)
WOOD_D = (92, 64, 36)
YARN = (198, 92, 90)
YARN_D = (152, 62, 62)
YARN_L = (228, 140, 136)
NEEDLE = (182, 152, 100)


# ── PNG (stdlib) ───────────────────────────────────────────────────────────
def encode_png(w, h, pixels):
    """RGBA row-major -> PNG 8-bit/color type 6, filtro 0, sin interlace."""

    def chunk(tag, body):
        crudo = tag + body
        return (
            struct.pack(">I", len(body))
            + crudo
            + struct.pack(">I", zlib.crc32(crudo) & 0xFFFFFFFF)
        )

    raw = bytearray()
    stride = w * 4
    for y in range(h):
        raw.append(0)
        raw.extend(pixels[y * stride:(y + 1) * stride])
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def canvas():
    return bytearray(W * H * 4)


# ── Primitivas (dibujan sobre cualquier capa) ──────────────────────────────
def px(buf, x, y, col):
    x, y = int(x), int(y)
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i:i + 4] = bytes((col[0], col[1], col[2], 255))


def box(buf, x0, y0, x1, y1, col):
    for y in range(int(y0), int(y1) + 1):
        for x in range(int(x0), int(x1) + 1):
            px(buf, x, y, col)


def borrar(buf, x, y):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        buf[i:i + 4] = b"\x00\x00\x00\x00"


def line(buf, x0, y0, x1, y1, col, w=1):
    """Bresenham con pincel cuadrado de `w` px."""
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    r0, r1 = (w - 1) // 2, w // 2
    while True:
        box(buf, x0 - r0, y0 - r0, x0 + r1, y0 + r1, col)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ell(buf, cx, cy, rx, ry, col):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            dx = (x - cx) / max(rx, 0.5)
            dy = (y - cy) / max(ry, 0.5)
            if dx * dx + dy * dy <= 1.05:
                px(buf, x, y, col)


def pegar(dst, src, contorno=OUT):
    """Pega una capa con contorno de 1 px (dilatacion del alfa) y sus pixeles."""
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3]:
                continue
            if ((x > 0 and src[i - 1]) or (x < W - 1 and src[i + 7])
                    or (y > 0 and src[i - W * 4 + 3])
                    or (y < H - 1 and src[i + W * 4 + 3])):
                px(dst, x, y, contorno)
    for y in range(H):
        for x in range(W):
            i = (y * W + x) * 4
            if src[i + 3]:
                dst[i:i + 4] = src[i:i + 4]


# ── Partes del aldeano (se dibujan todas en la misma capa) ─────────────────
def dib_piernas(c, dx=0):
    box(c, 20 + dx, 28, 22 + dx, 33, PANTS)
    box(c, 25 + dx, 28, 27 + dx, 33, PANTS)
    box(c, 20 + dx, 29, 20 + dx, 33, PANTS_D)
    box(c, 27 + dx, 29, 27 + dx, 33, PANTS_D)
    for y in (30, 32):
        px(c, 21 + dx, y, PANTS_L)
        px(c, 26 + dx, y, PANTS_L)
    # botas
    box(c, 19 + dx, 34, 22 + dx, 37, BOOT)
    box(c, 25 + dx, 34, 28 + dx, 37, BOOT)
    box(c, 19 + dx, 34, 22 + dx, 34, BOOT_L)
    box(c, 25 + dx, 34, 28 + dx, 34, BOOT_L)
    px(c, 20 + dx, 35, BOOT_L)
    px(c, 26 + dx, 35, BOOT_L)
    box(c, 19 + dx, 37, 22 + dx, 37, BOOT_D)
    box(c, 25 + dx, 37, 28 + dx, 37, BOOT_D)


def dib_torso(c, dx=0, largo=0):
    """Tunica marron con cinturon; `largo` alarga el ruedo (abuela)."""
    L, R = 19 + dx, 28 + dx
    ruedo = 27 + largo
    box(c, L, 18, R, ruedo, TUNIC)
    # sombra de hombros y luz lateral
    box(c, L, 18, L, 23, TUNIC_D)
    box(c, R, 18, R, 23, TUNIC_D)
    box(c, L + 1, 19, L + 1, 24, TUNIC_L)
    # cuello en V
    box(c, 23 + dx, 18, 24 + dx, 18, TUNIC_D)
    px(c, 22 + dx, 18, TUNIC_D)
    px(c, 25 + dx, 18, TUNIC_D)
    px(c, 23 + dx, 19, SKIN_D)
    px(c, 24 + dx, 19, SKIN_D)
    # pliegues de la tela
    px(c, 22 + dx, 21, TUNIC_D)
    px(c, 25 + dx, 21, TUNIC_L)
    px(c, 22 + dx, 23, TUNIC_D)
    px(c, 25 + dx, 23, TUNIC_D)
    # cinturon
    box(c, L, 24, R, 25, BELT)
    box(c, 23 + dx, 24, 24 + dx, 25, BUCKLE)
    px(c, 24 + dx, 24, BELT)
    px(c, 23 + dx, 25, (176, 144, 66))
    # ruedo
    box(c, L, ruedo, R, ruedo, TUNIC_D)
    px(c, 21 + dx, ruedo - 1, TUNIC_D)
    px(c, 26 + dx, ruedo - 1, TUNIC_D)
    if largo:
        box(c, L - 1, 28, R + 1, 29, TUNIC)
        box(c, L - 1, 30, R + 1, 30, TUNIC_D)
        px(c, 23 + dx, 28, TUNIC_D)
        px(c, 23 + dx, 29, TUNIC_D)
        px(c, 26 + dx, 28, TUNIC_D)
        px(c, 21 + dx, 29, TUNIC_D)


def dib_cabeza(c, dx=0, blink=False, mouth=1, cara=True, canas=False):
    """Cara de frente; con `cara=False` dibuja la nuca (vista de espaldas)."""
    pelo = HAIR_G if canas else HAIR
    pelo_l = HAIR_G_D if canas else HAIR_L
    # cara redondeada (esquinas comidas)
    box(c, 20 + dx, 10, 27 + dx, 16, SKIN)
    borrar(c, 20 + dx, 10)
    borrar(c, 27 + dx, 10)
    borrar(c, 20 + dx, 16)
    borrar(c, 27 + dx, 16)
    # pelo bajo el ala del sombrero
    box(c, 21 + dx, 10, 26 + dx, 10, pelo)
    box(c, 20 + dx, 11, 20 + dx, 13, pelo)
    box(c, 27 + dx, 11, 27 + dx, 13, pelo)
    px(c, 22 + dx, 10, pelo_l)
    px(c, 24 + dx, 10, pelo_l)
    if not cara:
        # nuca: todo pelo, sin facciones
        box(c, 21 + dx, 11, 26 + dx, 15, pelo)
        box(c, 22 + dx, 12, 25 + dx, 14, pelo)
        px(c, 22 + dx, 11, pelo_l)
        px(c, 23 + dx, 11, pelo_l)
        px(c, 25 + dx, 13, pelo_l)
        px(c, 21 + dx, 14, pelo_l)
        box(c, 22 + dx, 17, 25 + dx, 17, SKIN)
        px(c, 25 + dx, 17, SKIN_D)
        return
    # sombra lateral
    px(c, 20 + dx, 14, SKIN_D)
    px(c, 27 + dx, 14, SKIN_D)
    # cejas y ojos
    box(c, 21 + dx, 11, 22 + dx, 11, pelo)
    box(c, 25 + dx, 11, 26 + dx, 11, pelo)
    if blink:
        box(c, 21 + dx, 12, 22 + dx, 12, SKIN_D)
        box(c, 25 + dx, 12, 26 + dx, 12, SKIN_D)
        px(c, 21 + dx, 12, OUT)
        px(c, 26 + dx, 12, OUT)
    else:
        box(c, 21 + dx, 12, 22 + dx, 12, OUT)
        box(c, 25 + dx, 12, 26 + dx, 12, OUT)
    # nariz y mejillas
    px(c, 24 + dx, 13, SKIN_D)
    px(c, 23 + dx, 13, SKIN_L)
    px(c, 21 + dx, 14, SKIN_L)
    px(c, 26 + dx, 14, SKIN_L)
    # boca: 0 cerrada, 1 chica, 2 media, 3 ancha (abierta)
    if mouth == 0:
        px(c, 23 + dx, 14, LIP)
    elif mouth == 1:
        box(c, 22 + dx, 14, 24 + dx, 14, LIP)
        px(c, 23 + dx, 14, MOUTH)
    elif mouth == 2:
        box(c, 21 + dx, 14, 25 + dx, 14, LIP)
        box(c, 22 + dx, 14, 24 + dx, 14, MOUTH)
    else:
        box(c, 21 + dx, 14, 25 + dx, 15, LIP)
        box(c, 22 + dx, 14, 24 + dx, 15, MOUTH)
        box(c, 22 + dx, 14, 24 + dx, 14, TEETH)
    # menton
    px(c, 22 + dx, 15, SKIN_D)
    px(c, 25 + dx, 15, SKIN_D)
    # cuello
    box(c, 22 + dx, 17, 25 + dx, 17, SKIN)
    px(c, 25 + dx, 17, SKIN_D)


def dib_sombrero(c, dx=0):
    """Sombrero de paja: ala ancha + copa con cinta oscura."""
    # ala
    box(c, 16 + dx, 7, 30 + dx, 9, HAT)
    box(c, 16 + dx, 7, 30 + dx, 7, HAT_L)
    box(c, 16 + dx, 9, 30 + dx, 9, HAT_D)
    for x in range(17 + dx, 30 + dx, 2):
        px(c, x, 8, HAT_D)
    for x, y in ((15, 8), (15, 9), (31, 8), (31, 9)):
        px(c, x + dx, y, HAT_D)
    # copa
    box(c, 20 + dx, 3, 27 + dx, 6, HAT)
    box(c, 20 + dx, 3, 27 + dx, 3, HAT_L)
    box(c, 20 + dx, 4, 20 + dx, 6, HAT_L)
    box(c, 27 + dx, 4, 27 + dx, 5, HAT_D)
    box(c, 20 + dx, 5, 27 + dx, 6, HAT_BAND)
    px(c, 21 + dx, 5, (104, 72, 42))


def dib_panuelo(c, dx=0):
    """Panuelo de la abuela: cubre la cabeza y cae a los costados."""
    for y, (x0, x1) in ((7, (22, 25)), (8, (21, 26)), (9, (20, 27))):
        box(c, x0 + dx, y, x1 + dx, y, CREAM)
    box(c, 20 + dx, 10, 27 + dx, 10, CREAM)
    box(c, 20 + dx, 11, 27 + dx, 11, PARCH_D)
    box(c, 19 + dx, 11, 19 + dx, 14, CREAM)
    box(c, 28 + dx, 11, 28 + dx, 14, CREAM)
    px(c, 19 + dx, 14, PARCH_D)
    px(c, 28 + dx, 14, PARCH_D)
    # nudo a la derecha
    box(c, 29 + dx, 11, 30 + dx, 12, PARCH_D)
    px(c, 28 + dx, 12, CREAM)
    px(c, 30 + dx, 13, CREAM)
    px(c, 31 + dx, 14, PARCH_D)


def dib_mano(c, x, y, abierta=False):
    box(c, x, y, x + 1, y + 1, SKIN)
    px(c, x, y, SKIN_L)
    if abierta:
        px(c, x, y + 2, SKIN)
        px(c, x + 1, y + 2, SKIN_D)
    else:
        px(c, x + 1, y + 1, SKIN_D)


def dib_brazo(c, pts, mano_en=None, abierta=False, lado=-1):
    """Brazo de 3 px sobre la capa del cuerpo.

    `lado=-1` para el brazo izquierdo (sombra a la derecha) y `+1` para el
    derecho (sombra a la izquierda): la sombra marca el pliegue contra la
    tunica.
    """
    for a, b in zip(pts, pts[1:]):
        line(c, a[0], a[1], b[0], b[1], TUNIC, 3)
    for a, b in zip(pts, pts[1:]):
        if abs(a[1] - b[1]) >= abs(a[0] - b[0]):
            line(c, a[0] - lado, a[1], b[0] - lado, b[1], TUNIC_D, 1)
    if mano_en:
        dib_mano(c, mano_en[0], mano_en[1], abierta)


def cuerpo(c, dx=0, blink=False, mouth=1, largo=0, cara=True, canas=False,
           sombrero=True, panuelo=False):
    """Pega piernas, torso, cabeza y sombrero/panuelo en la capa `c`."""
    dib_piernas(c, dx)
    dib_torso(c, dx, largo)
    dib_cabeza(c, dx, blink=blink, mouth=mouth, cara=cara, canas=canas)
    if sombrero:
        dib_sombrero(c, dx)
    if panuelo:
        dib_panuelo(c, dx)


# ── Accesorios de escena ───────────────────────────────────────────────────
FONT = {
    "Y": ["#...#", "#...#", ".###.", "..#..", "..#.."],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#"],
}


def letra(buf, ch, x0, y0, col):
    for dy, fila in enumerate(FONT[ch]):
        for dx, c in enumerate(fila):
            if c == "#":
                px(buf, x0 + dx, y0 + dy, col)


def globo(dst, ch, col):
    """Globo de dialogo tipo pergamino, arriba a la derecha, con cola."""
    box(dst, 33, 2, 45, 12, OUT)
    box(dst, 34, 3, 44, 11, PARCH)
    box(dst, 34, 3, 44, 3, CREAM)
    box(dst, 34, 11, 44, 11, PARCH_D)
    box(dst, 34, 12, 35, 12, PARCH)
    # cola hacia la cabeza
    px(dst, 33, 13, OUT)
    px(dst, 32, 14, OUT)
    px(dst, 31, 15, OUT)
    px(dst, 33, 12, PARCH)
    letra(dst, ch, 36, 6, col)


def barra(dst, lleno):
    """Barra de progreso (jobs): verde sobre fondo oscuro."""
    box(dst, 33, 3, 45, 9, OUT)
    box(dst, 34, 4, 44, 8, (56, 44, 30))
    box(dst, 34, 4, 44, 4, (74, 58, 40))
    for x in range(34, 34 + lleno):
        box(dst, x, 5, x, 7, GREEN)
        px(dst, x, 5, GREEN_L)
    for x in range(34 + lleno, 45):
        px(dst, x, 6, (44, 34, 24))


def dib_mate(c, x, y):
    """Mate: calabaza de madera con bombilla (sobre la capa del cuerpo)."""
    box(c, x, y, x + 2, y + 3, WOOD)
    box(c, x, y, x + 2, y, WOOD_D)
    px(c, x, y + 2, (168, 126, 78))
    px(c, x + 2, y + 3, WOOD_D)
    line(c, x + 1, y - 1, x + 1, y - 3, STEEL_D, 1)
    px(c, x + 1, y - 4, STEEL)


def dib_martillo(c, x, y, arriba=True):
    """Martillo de construccion: mango de madera y cabeza de hierro."""
    if arriba:
        line(c, x, y, x + 3, y - 4, WOOD, 1)
        box(c, x + 2, y - 8, x + 6, y - 6, STEEL)
        box(c, x + 2, y - 8, x + 6, y - 8, STEEL_L)
        box(c, x + 4, y - 7, x + 4, y - 6, STEEL_D)
    else:
        line(c, x, y, x + 3, y + 3, WOOD, 1)
        box(c, x + 2, y + 3, x + 6, y + 5, STEEL)
        box(c, x + 2, y + 3, x + 6, y + 3, STEEL_L)
        box(c, x + 4, y + 4, x + 4, y + 5, STEEL_D)


def dib_cohete(c, x, y):
    """Cohete de madera atado a la espalda (yolo/super-yolo)."""
    box(c, x, y, x + 3, y + 8, WOOD)
    box(c, x, y, x, y + 8, WOOD_D)
    px(c, x + 1, y + 2, WOOD_D)
    px(c, x + 3, y + 5, WOOD_D)
    # punta
    box(c, x + 1, y - 1, x + 2, y - 1, STEEL)
    # aletas
    for yy in (y + 6, y + 7):
        px(c, x - 1, yy, GREY_D)
        px(c, x + 4, yy, GREY_D)


def dib_llama(c, x, y):
    """Llama del cohete (fuera del contorno del cuerpo)."""
    box(c, x + 1, y + 9, x + 2, y + 9, FLAME)
    box(c, x + 1, y + 10, x + 2, y + 10, FLAME_L)
    px(c, x + 1, y + 11, FLAME)
    px(c, x + 2, y + 11, FLAME)


def vincha(dst, dx=0):
    """Vincha magenta YOLO sobre la frente."""
    box(dst, 20 + dx, 11, 26 + dx, 11, MAGENTA)
    px(dst, 20 + dx, 11, MAGENTA_D)
    px(dst, 26 + dx, 11, MAGENTA_D)
    px(dst, 19 + dx, 12, MAGENTA)
    px(dst, 18 + dx, 13, MAGENTA)
    px(dst, 17 + dx, 14, MAGENTA_D)


def sol(dst, cx, cy):
    ell(dst, cx, cy, 2, 2, YELLOW)
    px(dst, cx - 1, cy - 1, FLAME_L)
    for dx, dy in ((0, -3), (0, 3), (-3, 0), (3, 0),
                   (-2, -2), (2, -2), (-2, 2), (2, 2)):
        px(dst, cx + dx, cy + dy, YELLOW_D)


def polvo(dst, cx, cy, r=2):
    """Nube de polvo del aldeano caido (borde suave, sin contorno duro)."""
    ell(dst, cx, cy, r + 1, r, DUST_D)
    ell(dst, cx, cy, r, r - 1, DUST)
    px(dst, cx - 1, cy, DUST)
    px(dst, cx + 1, cy - 1, DUST)


def espada(dst, x, y):
    """Espada clavada en el suelo, junto al caido."""
    line(dst, x, y, x, y + 8, STEEL, 1)
    px(dst, x + 1, y + 1, STEEL_D)
    box(dst, x - 2, y - 1, x + 2, y - 1, GREY_D)
    line(dst, x, y - 5, x, y - 2, WOOD, 1)
    px(dst, x, y - 6, BUCKLE)
    px(dst, x - 2, y - 1, OUT)
    px(dst, x + 2, y - 1, OUT)


# ── Poses ──────────────────────────────────────────────────────────────────
def frame_hi(n):
    b = canvas()
    c = canvas()
    cuerpo(c, mouth=2 if n == 1 else 1)
    dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
    if n == 1:  # mano arriba, saludando
        dib_brazo(c, [(28, 19), (32, 16), (34, 13)], (35, 12), abierta=True, lado=+1)
    else:  # mano abajo, abierta
        dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), abierta=True, lado=+1)
    pegar(b, c)
    if n == 1:
        px(b, 38, 7, YELLOW)
        px(b, 39, 11, YELLOW_D)
        px(b, 36, 4, YELLOW_D)
    return b


def frame_idle(n):
    b = canvas()
    c = canvas()
    cuerpo(c, blink=(n == 2), mouth=0)
    dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
    dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), lado=+1)
    pegar(b, c)
    return b


def frame_talk(n):
    b = canvas()
    c = canvas()
    cuerpo(c, mouth=n)
    dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
    if n >= 2:
        dib_brazo(c, [(28, 19), (30, 21), (30, 24)], (30, 25), abierta=True, lado=+1)
    else:
        dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), lado=+1)
    pegar(b, c)
    return b


def frame_ask(n):
    b = canvas()
    c = canvas()
    cuerpo(c, mouth=1)
    dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
    dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), lado=+1)
    # mano que presenta el globo
    dib_brazo(c, [(28, 19), (30, 18), (31, 17)], (31, 16), abierta=True, lado=+1)
    pegar(b, c)
    globo(b, "Y" if n == 1 else "N", GREEN if n == 1 else RED)
    return b


def frame_success(n):
    b = canvas()
    c = canvas()
    if n == 1:  # brazos arriba, en V
        cuerpo(c, mouth=3)
        dib_brazo(c, [(19, 19), (15, 16), (13, 13)], (12, 12), abierta=True, lado=-1)
        dib_brazo(c, [(28, 19), (33, 16), (35, 13)], (36, 12), abierta=True, lado=+1)
        pegar(b, c)
        for x, y in ((8, 8), (39, 8), (33, 5), (14, 6)):
            px(b, x, y, YELLOW)
        px(b, 40, 14, YELLOW_D)
        px(b, 7, 14, YELLOW_D)
    else:  # brazos abajo y afuera
        cuerpo(c, mouth=2)
        dib_brazo(c, [(19, 19), (14, 21), (11, 24)], (10, 25), abierta=True, lado=-1)
        dib_brazo(c, [(28, 19), (33, 21), (36, 24)], (37, 25), abierta=True, lado=+1)
        pegar(b, c)
        px(b, 41, 19, YELLOW_D)
        px(b, 6, 19, YELLOW_D)
    return b


def frame_failure_front():
    b = canvas()
    c = canvas()
    # piernas hacia la derecha
    box(c, 29, 28, 37, 30, PANTS)
    box(c, 29, 30, 37, 30, PANTS_D)
    box(c, 30, 31, 37, 33, PANTS)
    box(c, 30, 33, 37, 33, PANTS_D)
    box(c, 37, 27, 40, 30, BOOT)
    box(c, 37, 27, 40, 27, BOOT_L)
    box(c, 37, 31, 40, 34, BOOT)
    box(c, 37, 31, 40, 31, BOOT_L)
    # torso tirado de frente
    box(c, 17, 26, 30, 32, TUNIC)
    box(c, 17, 32, 30, 32, TUNIC_D)
    box(c, 17, 26, 30, 26, TUNIC_L)
    box(c, 25, 26, 26, 32, BELT)
    px(c, 25, 29, BUCKLE)
    px(c, 25, 30, BUCKLE)
    px(c, 20, 29, TUNIC_D)
    px(c, 22, 30, TUNIC_D)
    # brazos abiertos
    dib_brazo(c, [(30, 29), (34, 33), (36, 34)], (37, 35), abierta=True, lado=+1)
    dib_brazo(c, [(18, 28), (16, 24), (17, 22)], (18, 21), abierta=True, lado=-1)
    # cabeza de frente, apoyada
    box(c, 9, 25, 18, 34, SKIN)
    borrar(c, 9, 25)
    borrar(c, 18, 25)
    borrar(c, 9, 34)
    borrar(c, 18, 34)
    box(c, 10, 25, 17, 26, HAIR)
    box(c, 9, 27, 9, 30, HAIR)
    for x in (12, 16):
        px(c, x - 1, 28, OUT)
        px(c, x + 1, 28, OUT)
        px(c, x, 29, OUT)
        px(c, x - 1, 30, OUT)
        px(c, x + 1, 30, OUT)
    px(c, 14, 31, SKIN_D)
    box(c, 12, 32, 15, 32, MOUTH)
    px(c, 13, 32, TEETH)
    px(c, 11, 33, SKIN_D)
    px(c, 16, 33, SKIN_D)
    # sombrero caido de costado, sobre la cabeza
    box(c, 6, 20, 17, 23, HAT)
    box(c, 6, 23, 17, 23, HAT_D)
    box(c, 7, 20, 16, 20, HAT_L)
    box(c, 12, 16, 15, 22, HAT)
    box(c, 12, 16, 15, 17, HAT_BAND)
    box(c, 12, 18, 15, 19, HAT)
    pegar(b, c)
    # polvo y espada clavada
    polvo(b, 18, 19, 2)
    polvo(b, 25, 15, 2)
    polvo(b, 32, 18, 2)
    espada(b, 44, 22)
    return b


def frame_failure_back():
    b = canvas()
    c = canvas()
    # piernas hacia la izquierda
    box(c, 10, 28, 18, 30, PANTS)
    box(c, 10, 30, 18, 30, PANTS_D)
    box(c, 10, 31, 17, 33, PANTS)
    box(c, 10, 33, 17, 33, PANTS_D)
    box(c, 7, 27, 10, 30, BOOT)
    box(c, 7, 27, 10, 27, BOOT_L)
    box(c, 7, 31, 10, 34, BOOT)
    box(c, 7, 31, 10, 31, BOOT_L)
    # torso de espaldas (sin hebilla)
    box(c, 17, 26, 30, 32, TUNIC)
    box(c, 17, 26, 30, 26, TUNIC_D)
    box(c, 17, 32, 30, 32, TUNIC_D)
    box(c, 23, 26, 24, 32, TUNIC_D)
    box(c, 24, 26, 25, 32, BELT)
    px(c, 20, 29, TUNIC_D)
    px(c, 27, 30, TUNIC_D)
    # brazos
    dib_brazo(c, [(18, 28), (14, 32), (12, 33)], (11, 34), abierta=True, lado=-1)
    dib_brazo(c, [(29, 29), (31, 24), (31, 22)], (31, 21), abierta=True, lado=+1)
    # nuca (sin cara)
    box(c, 29, 25, 38, 34, HAIR)
    borrar(c, 29, 25)
    borrar(c, 38, 25)
    borrar(c, 29, 34)
    borrar(c, 38, 34)
    box(c, 30, 25, 37, 26, HAIR_L)
    box(c, 31, 27, 36, 33, HAIR)
    px(c, 32, 29, HAIR_L)
    px(c, 33, 30, HAIR_L)
    px(c, 34, 31, HAIR_L)
    px(c, 35, 29, HAIR_L)
    px(c, 36, 32, HAIR_L)
    box(c, 33, 34, 36, 34, SKIN)
    # sombrero caido al otro lado
    box(c, 20, 21, 31, 24, HAT)
    box(c, 20, 24, 31, 24, HAT_D)
    box(c, 21, 21, 30, 21, HAT_L)
    box(c, 24, 17, 27, 23, HAT)
    box(c, 24, 17, 27, 18, HAT_BAND)
    box(c, 24, 19, 27, 20, HAT)
    pegar(b, c)
    # polvo y espada clavada
    polvo(b, 19, 18, 2)
    polvo(b, 27, 14, 2)
    polvo(b, 34, 19, 2)
    espada(b, 4, 22)
    return b


def frame_bye(n):
    b = canvas()
    c = canvas()
    if n == 1:  # sombrero puesto + mano que se despide
        cuerpo(c, mouth=2)
        dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), lado=+1)
        dib_brazo(c, [(19, 19), (15, 16), (13, 13)], (12, 12), abierta=True, lado=-1)
        pegar(b, c)
        px(b, 8, 7, YELLOW)
        px(b, 9, 11, YELLOW_D)
    else:  # sombrero en la mano, cabeza descubierta
        cuerpo(c, mouth=1, sombrero=False)
        # pelo al descubierto
        box(c, 20, 9, 27, 10, HAIR)
        box(c, 19, 9, 19, 11, HAIR)
        box(c, 28, 9, 28, 11, HAIR)
        px(c, 21, 9, HAIR_L)
        px(c, 23, 9, HAIR_L)
        px(c, 25, 10, HAIR_L)
        px(c, 20, 9, HAIR_L)
        # sombrero en la mano, al costado
        box(c, 37, 18, 40, 21, HAT)
        box(c, 37, 18, 40, 18, HAT_L)
        box(c, 37, 20, 40, 20, HAT_BAND)
        box(c, 34, 22, 43, 23, HAT)
        box(c, 34, 23, 43, 23, HAT_D)
        box(c, 35, 22, 42, 22, HAT_L)
        dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
        dib_brazo(c, [(28, 19), (31, 21), (33, 22)], (34, 22), lado=+1)
        pegar(b, c)
    return b


def frame_jobs(n):
    b = canvas()
    c = canvas()
    if n == 1:  # tomando mate
        cuerpo(c, mouth=0)
        dib_mate(c, 29, 19)
        dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
        dib_brazo(c, [(28, 19), (30, 22), (29, 21)], (29, 21), lado=+1)
        line(c, 30, 18, 26, 15, STEEL_D, 1)
        px(c, 26, 15, STEEL)
        pegar(b, c)
        barra(b, 7)
        px(b, 23, 11, SKIN_D)
    else:  # mirando la barra
        cuerpo(c, mouth=1)
        dib_mate(c, 30, 23)
        dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
        dib_brazo(c, [(28, 19), (31, 23), (31, 25)], (31, 26), lado=+1)
        line(c, 31, 22, 27, 18, STEEL_D, 1)
        pegar(b, c)
        barra(b, 10)
    return b


def frame_yolo(n, superyolo=False):
    b = canvas()
    c = canvas()
    dx = -1 if n == 1 else 1
    dib_cohete(c, 11 + dx, 9)
    cuerpo(c, dx=dx, mouth=2)
    # correas del cohete al hombro
    px(c, 15 + dx, 13, BELT)
    px(c, 16 + dx, 14, BELT)
    px(c, 17 + dx, 15, BELT)
    if n == 1:
        dib_brazo(c, [(20 + dx, 19), (16 + dx, 21), (14 + dx, 24)],
                  (13 + dx, 25), abierta=True, lado=-1)
        dib_brazo(c, [(28 + dx, 19), (29 + dx, 23), (29 + dx, 26)],
                  (29 + dx, 27), lado=+1)
    else:
        dib_brazo(c, [(20 + dx, 19), (19 + dx, 23), (19 + dx, 26)],
                  (19 + dx, 27), lado=-1)
        dib_brazo(c, [(28 + dx, 19), (32 + dx, 21), (34 + dx, 24)],
                  (35 + dx, 25), abierta=True, lado=+1)
    pegar(b, c)
    dib_llama(b, 11 + dx, 9)
    vincha(b, dx)
    if superyolo:
        sol(b, 40, 6)
    return b


def frame_grandma(n):
    b = canvas()
    c = canvas()
    # aldeana: pollera larga y panuelo en vez de sombrero de paja
    cuerpo(c, largo=3, mouth=1, canas=True, sombrero=False, panuelo=True)
    # canas a los costados
    px(c, 19, 12, HAIR_G)
    px(c, 28, 12, HAIR_G)
    px(c, 19, 13, HAIR_G_D)
    px(c, 28, 13, HAIR_G_D)
    # ovillo de lana a los pies
    box(c, 31, 33, 34, 36, YARN)
    px(c, 32, 34, YARN_D)
    px(c, 33, 35, YARN_D)
    px(c, 31, 34, YARN_L)
    px(c, 33, 33, YARN_L)
    if n == 1:  # manos arriba: teje en alto
        line(c, 17, 19, 30, 19, NEEDLE, 1)
        line(c, 17, 23, 30, 18, NEEDLE, 1)
        box(c, 22, 19, 25, 20, YARN)
        line(c, 32, 33, 29, 22, YARN, 1)
        line(c, 29, 22, 25, 20, YARN_D, 1)
        dib_brazo(c, [(19, 19), (17, 23), (18, 22)], (18, 21), abierta=True, lado=-1)
        dib_brazo(c, [(28, 19), (30, 23), (29, 22)], (29, 21), abierta=True, lado=+1)
    else:  # manos abajo: la prenda en la falda
        line(c, 17, 22, 30, 22, NEEDLE, 1)
        line(c, 17, 26, 30, 22, NEEDLE, 1)
        box(c, 21, 23, 26, 26, YARN)
        box(c, 21, 26, 26, 26, YARN_D)
        px(c, 22, 24, YARN_L)
        line(c, 32, 33, 29, 27, YARN, 1)
        dib_brazo(c, [(19, 19), (17, 23), (18, 24)], (18, 25), abierta=True, lado=-1)
        dib_brazo(c, [(28, 19), (30, 23), (29, 24)], (29, 25), abierta=True, lado=+1)
    pegar(b, c)
    return b


def frame_write(n):
    b = canvas()
    c = canvas()
    if n == 1:  # martillo arriba
        cuerpo(c, mouth=0)
        dib_martillo(c, 29, 16, arriba=True)
        dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
        dib_brazo(c, [(28, 19), (29, 18), (29, 17)], (29, 17), lado=+1)
        pegar(b, c)
    else:  # martillo abajo (golpe)
        cuerpo(c, mouth=1)
        dib_martillo(c, 28, 26, arriba=False)
        dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
        dib_brazo(c, [(28, 19), (29, 23), (29, 25)], (29, 26), lado=+1)
        pegar(b, c)
        # chispas del golpe
        px(b, 37, 29, YELLOW)
        px(b, 38, 31, YELLOW)
        px(b, 36, 27, YELLOW_D)
        px(b, 39, 28, YELLOW_D)
    return b


# ── Entrega ────────────────────────────────────────────────────────────────
# estado: [(nombre de archivo, constructor)]
FRAMES = [
    ("hi", [("hi_01.png", lambda: frame_hi(1)),
            ("hi_02.png", lambda: frame_hi(2))]),
    ("idle", [("idle.png", lambda: frame_idle(1)),
              ("idle_blink.png", lambda: frame_idle(2))]),
    ("talk", [("talk_close.png", lambda: frame_talk(0)),
              ("talk_small.png", lambda: frame_talk(1)),
              ("talk_mid.png", lambda: frame_talk(2)),
              ("talk_wide.png", lambda: frame_talk(3)),
              ("talk.png", lambda: frame_talk(2))]),
    # los placeholders viejos de una pose se reescriben con la pose 1 para que
    # el ciclo no muestre al personaje anterior; quedan como duplicados
    ("ask", [("ask_01.png", lambda: frame_ask(1)),
             ("ask_02.png", lambda: frame_ask(2)),
             ("ask.png", lambda: frame_ask(1))]),
    ("success", [("success_01.png", lambda: frame_success(1)),
                 ("success_02.png", lambda: frame_success(2)),
                 ("success.png", lambda: frame_success(1))]),
    ("failure", [("failure_01.png", frame_failure_front),
                 ("failure_02.png", frame_failure_back),
                 ("failure.png", frame_failure_front)]),
    ("bye", [("bye_01.png", lambda: frame_bye(1)),
             ("bye_02.png", lambda: frame_bye(2)),
             ("bye.png", lambda: frame_bye(1))]),
    ("jobs", [("jobs_01.png", lambda: frame_jobs(1)),
              ("jobs_02.png", lambda: frame_jobs(2)),
              ("jobs.png", lambda: frame_jobs(1))]),
    ("yolo", [("yolo_01.png", lambda: frame_yolo(1)),
              ("yolo_02.png", lambda: frame_yolo(2)),
              ("yolo.png", lambda: frame_yolo(1)),
              ("yolo_blink.png", lambda: frame_yolo(1))]),
    ("super-yolo", [("super-yolo_01.png", lambda: frame_yolo(1, True)),
                    ("super-yolo_02.png", lambda: frame_yolo(2, True)),
                    ("super-yolo.png", lambda: frame_yolo(1, True)),
                    ("super-yolo_blink.png", lambda: frame_yolo(1, True))]),
    ("grandma", [("grandma_01.png", lambda: frame_grandma(1)),
                 ("grandma_02.png", lambda: frame_grandma(2)),
                 ("grandma.png", lambda: frame_grandma(1))]),
    ("write", [("write_01.png", lambda: frame_write(1)),
               ("write_02.png", lambda: frame_write(2)),
               ("write.png", lambda: frame_write(1))]),
]


def ihdr(path):
    """Lee el IHDR del PNG entregado (para autoverificacion)."""
    with open(path, "rb") as fh:
        data = fh.read(33)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("%s: no es PNG" % path)
    return struct.unpack(">IIBBBBB", data[16:29])


def main():
    escritos = {}   # estado -> [(archivo, ruta)]
    buffers = {}    # ruta -> bytearray RGBA dibujado
    for estado, frames in FRAMES:
        carpeta = os.path.join(SET_DIR, estado)
        os.makedirs(carpeta, exist_ok=True)
        for nombre, constructor in frames:
            buf = constructor()
            destino = os.path.join(carpeta, nombre)
            with open(destino, "wb") as fh:
                fh.write(encode_png(W, H, buf))
            escritos.setdefault(estado, []).append((nombre, destino))
            buffers[destino] = buf

    # ── Autoverificacion de la entrega ────────────────────────────────────
    for estado, frames in escritos.items():
        for nombre, ruta in frames:
            w, h, depth, ctype, comp, filt, inter = ihdr(ruta)
            assert (w, h) == (W, H), "%s: %dx%d" % (ruta, w, h)
            assert depth == 8, "%s: bit depth %d" % (ruta, depth)
            assert ctype == 6, "%s: color type %d" % (ruta, ctype)
            assert inter == 0, "%s: interlace %d" % (ruta, inter)
            alfas = set(buffers[ruta][i] for i in range(3, len(buffers[ruta]), 4))
            assert 0 in alfas, "%s: sin fondo transparente" % ruta
            assert 255 in alfas, "%s: sin pixeles opacos" % ruta
        poses = [n for n, _ in frames if n[:-4].endswith(("_01", "_02"))]
        if len(poses) == 2:
            assert buffers[frames[0][1]] != buffers[frames[1][1]], \
                "%s: poses identicas" % estado

    total = 0
    print("estado: frames y bytes")
    for estado, frames in escritos.items():
        linea = []
        for nombre, ruta in frames:
            tam = os.path.getsize(ruta)
            total += tam
            linea.append("%s=%dB" % (nombre, tam))
        print("  %-11s %s" % (estado, ", ".join(linea)))
    print("  total       %d PNG, %d bytes"
          % (sum(len(f) for f in escritos.values()), total))


if __name__ == "__main__":
    main()
