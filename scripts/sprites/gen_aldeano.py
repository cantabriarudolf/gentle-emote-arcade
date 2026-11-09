#!/usr/bin/env python3
"""Dibuja por codigo los estados del ALDEANO de AoE (48x40, 8-bit RGBA).

Base visual: referencia del aldeano musculoso de AoE I, vista frontal: torso
desnudo y piel clara, pelo marron medio, barba corta, pantalon azul holgado,
cinturon marron trenzado con hebilla plateada y brazaletes trenzados en los
antebrazos. Sin sombrero, sin tunica y sin botas: los pies van descalzos. Un
solo personaje y una sola paleta: cada pose solo mueve brazos, boca y los
accesorios de la escena. La abuela (`grandma`) es el otro personaje del set y
conserva su tunica larga y su panuelo.

El cuerpo entero se dibuja en una capa y se pega con un unico contorno de 1 px
(dilatacion del alfa): silueta limpia de sprite clasico, sin brochazos, con
sombreado interno para separar brazos, cinturon y pliegues.

Estados que genera (carpeta dentro de `emotes/aoe/`), con los nombres exactos
que hay en el set (`_03` repite la pose 1: son frames que ya estaban en el
ciclo y no se borran):

    hi/         hi_01, hi_02, hi_03              saludo (mano arriba / abajo)
    idle/       idle, idle_blink                 parpadeo del mismo aldeano
    talk/       talk_close, talk_small,
                talk_mid, talk_wide, talk        cuatro bocas + neutral
    ask/        ask_01, ask_02, ask_03           globo Y / globo N
    success/    success_01, success_02,
                success_03                       brazos arriba / brazos afuera
    failure/    down_01, down_02, down_03        caido de frente / de espaldas
    bye/        bye_01, bye_02, bye_03           saludo arriba / de espaldas
    jobs/       jobs_01, jobs_02, jobs_03        tomando mate / mirando la barra
    grandma/    grandma_01, grandma_02,
                grandma_03                       aldeana tejiendo (manos arriba/abajo)
    write/      write_01, write_02, write_03     martillo arriba / abajo

Los estados de escena que no son aldeanos ya no viven aca: `explore` (camello
arquero) lo dibuja `gen_explore_aoe.py`, `build`, `jira` y `review` los dibuja
`gen_build_aoe.py`, y `yolo` / `super-yolo` (el auto cobra) los dibuja
`gen_yolo_aoe.py`. Los tres reusan las primitivas y la paleta de este modulo.

Solo stdlib (struct + zlib): no usa PIL ni red. Uso, desde la raiz del repo:

    python3 gentle-emote-arcade/scripts/sprites/gen_aldeano.py
    python3 gentle-emote-arcade/scripts/sprites/gen_aldeano.py --set aoe-yolo

El set por defecto es `emotes/aoe`; `--set aoe-yolo` reescribe el gemelo YOLO
con el mismo dibujo. Los nombres de archivo son exactamente los del set, sin
alias nuevos: correr el script no agrega ni borra PNG (tampoco los de las
escenas que ahora dibujan los otros generadores).

Al final verifica el IHDR de cada PNG (48x40, bit depth 8, color type 6,
interlace 0), que haya alfa real (0 y 255) y que las dos poses del ciclo no
sean el mismo bitmap; imprime la lista `estado: frames y bytes`.
"""

import os
import struct
import sys
import zlib

W, H = 48, 40

ROOT = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..")
)

# Sets que comparten este dibujo: `aoe` y su gemelo YOLO. Cualquier otro
# nombre se rechaza, asi el script nunca escribe fuera de emotes/<set>/.
SETS = ("aoe", "aoe-yolo")


def set_elegido(argv):
    """Nombre del set a escribir: `--set aoe` (defecto) o `--set aoe-yolo`."""
    nombre = "aoe"
    resto = list(argv)
    if "--set" in resto:
        i = resto.index("--set")
        if i + 1 >= len(resto):
            raise SystemExit("--set necesita un valor: %s" % " | ".join(SETS))
        nombre = resto[i + 1]
    if nombre not in SETS:
        raise SystemExit(
            "set desconocido: %s (permitidos: %s)" % (nombre, ", ".join(SETS))
        )
    return nombre


SET_NAME = set_elegido(sys.argv[1:])
SET_DIR = os.path.join(ROOT, "emotes", SET_NAME)

# Guarda: si la ruta no es el set pedido del repo, no escribe nada.
if not os.path.isfile(os.path.join(SET_DIR, "emotes.json")):
    raise SystemExit(
        "no encuentro emotes/%s/emotes.json en %s: correr el script desde "
        "gentle-emote-arcade/" % (SET_NAME, SET_DIR)
    )

# ── Paleta (una sola para todo el set) ──────────────────────────────────────
OUT = (26, 18, 12)          # contorno
SKIN = (240, 196, 158)      # piel clara del aldeano
SKIN_L = (252, 222, 190)
SKIN_D = (198, 148, 112)
HAIR = (110, 74, 40)        # pelo marron medio
HAIR_L = (148, 106, 62)
BEARD = (96, 62, 34)        # barba corta
BEARD_D = (74, 46, 24)
HAIR_G = (198, 196, 188)    # canas de la abuela
HAIR_G_D = (148, 146, 140)
TUNIC = (126, 92, 52)       # tunica de la abuela (ya no del aldeano)
TUNIC_L = (152, 114, 66)
TUNIC_D = (96, 68, 36)
BELT = (124, 84, 44)        # cinturon trenzado
BELT_L = (162, 118, 66)
BELT_D = (88, 58, 30)
BUCKLE = (198, 204, 216)    # hebilla plateada
BUCKLE_D = (140, 148, 164)
BRACER = (132, 90, 50)      # brazaletes trenzados
BRACER_L = (172, 124, 74)
BRACER_D = (92, 60, 32)
PANTS = (58, 88, 152)       # pantalon azul holgado
PANTS_L = (88, 122, 186)
PANTS_D = (38, 60, 112)
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
MAGENTA = (232, 62, 152)     # marca YOLO (calcomania del auto cobra)
MAGENTA_D = (176, 34, 108)
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
def dib_piernas(c, dx=0, falda=False):
    """Pantalon azul holgado del aldeano o pollera larga de la abuela."""
    if falda:
        # pollera larga: tapa el pantalon y deja los pies descalzos a la vista
        box(c, 19 + dx, 28, 28 + dx, 33, TUNIC)
        box(c, 19 + dx, 28, 28 + dx, 28, TUNIC_L)
        box(c, 19 + dx, 33, 28 + dx, 33, TUNIC_D)
        box(c, 19 + dx, 28, 19 + dx, 33, TUNIC_D)
        box(c, 28 + dx, 28, 28 + dx, 33, TUNIC_D)
        for x in (21, 23, 25, 27):
            px(c, x + dx, 30, TUNIC_D)
            px(c, x + dx, 31, TUNIC_L)
    else:
        # piernas: dos bloques anchos separados por una linea en sombra
        box(c, 20 + dx, 28, 23 + dx, 33, PANTS)
        box(c, 24 + dx, 28, 27 + dx, 33, PANTS)
        box(c, 23 + dx, 28, 24 + dx, 33, PANTS_D)
        box(c, 20 + dx, 28, 20 + dx, 33, PANTS_D)
        box(c, 27 + dx, 28, 27 + dx, 33, PANTS_D)
        box(c, 21 + dx, 29, 22 + dx, 29, PANTS_L)
        box(c, 25 + dx, 29, 26 + dx, 29, PANTS_L)
        px(c, 21 + dx, 32, PANTS_D)     # pliegues de la tela holgada
        px(c, 26 + dx, 32, PANTS_D)
    # pies descalzos (el aldeano ya no usa botas)
    box(c, 19 + dx, 34, 23 + dx, 36, SKIN)
    box(c, 24 + dx, 34, 28 + dx, 36, SKIN)
    box(c, 19 + dx, 36, 23 + dx, 36, SKIN_D)
    box(c, 24 + dx, 36, 28 + dx, 36, SKIN_D)
    box(c, 20 + dx, 34, 22 + dx, 34, SKIN_L)
    box(c, 25 + dx, 34, 27 + dx, 34, SKIN_L)
    px(c, 22 + dx, 35, SKIN_D)          # dedos
    px(c, 27 + dx, 35, SKIN_D)


def dib_torso(c, dx=0, desnudo=True, espalda=False):
    """Torso del aldeano (desnudo y musculoso) o tunica larga de la abuela."""
    if desnudo:
        # hombros anchos y cintura angosta: la V del torso musculoso
        box(c, 18 + dx, 18, 29 + dx, 19, SKIN)
        box(c, 19 + dx, 20, 28 + dx, 23, SKIN)
        box(c, 20 + dx, 24, 27 + dx, 25, SKIN)
        box(c, 18 + dx, 18, 18 + dx, 19, SKIN_D)
        box(c, 29 + dx, 18, 29 + dx, 19, SKIN_D)
        box(c, 20 + dx, 24, 20 + dx, 25, SKIN_D)
        box(c, 27 + dx, 24, 27 + dx, 25, SKIN_D)
        if espalda:
            box(c, 23 + dx, 21, 23 + dx, 24, SKIN_D)    # columna
            box(c, 21 + dx, 20, 22 + dx, 20, SKIN_L)    # omoplatos
            box(c, 25 + dx, 20, 26 + dx, 20, SKIN_L)
        else:
            # pectorales: luz arriba y linea en sombra abajo
            box(c, 20 + dx, 20, 22 + dx, 20, SKIN_L)
            box(c, 25 + dx, 20, 27 + dx, 20, SKIN_L)
            box(c, 21 + dx, 21, 22 + dx, 21, SKIN_D)
            box(c, 25 + dx, 21, 26 + dx, 21, SKIN_D)
            px(c, 23 + dx, 22, SKIN_D)                  # esternon
            px(c, 24 + dx, 22, SKIN_D)
            px(c, 22 + dx, 23, SKIN_D)                  # abdomen
            px(c, 25 + dx, 23, SKIN_D)
            box(c, 23 + dx, 24, 24 + dx, 24, SKIN_D)
        # cinturon marron trenzado y grueso, con hebilla plateada
        box(c, 20 + dx, 26, 27 + dx, 27, BELT)
        for x in range(21 + dx, 27 + dx, 2):
            px(c, x, 26, BELT_L)
        for x in range(20 + dx, 27 + dx, 2):
            px(c, x, 27, BELT_D)
        box(c, 23 + dx, 26, 24 + dx, 27, BUCKLE)
        px(c, 23 + dx, 26, (232, 236, 244))
        px(c, 24 + dx, 27, BUCKLE_D)
        return
    # tunica marron de la abuela
    L, R = 19 + dx, 28 + dx
    ruedo = 27
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
    px(c, 23 + dx, 25, BELT_D)
    # ruedo
    box(c, L, ruedo, R, ruedo, TUNIC_D)
    px(c, 21 + dx, ruedo - 1, TUNIC_D)
    px(c, 26 + dx, ruedo - 1, TUNIC_D)


def dib_cabeza(c, dx=0, blink=False, mouth=1, cara=True, canas=False,
               barba=True):
    """Cara de frente con pelo corto y barba; `cara=False` dibuja la nuca."""
    pelo = HAIR_G if canas else HAIR
    pelo_l = HAIR_G_D if canas else HAIR_L
    # pelo: melena corta con volumen arriba (el aldeano ya no usa sombrero)
    box(c, 22 + dx, 7, 25 + dx, 7, pelo)
    box(c, 21 + dx, 8, 26 + dx, 8, pelo)
    box(c, 20 + dx, 9, 27 + dx, 9, pelo)
    px(c, 23 + dx, 7, pelo_l)
    px(c, 24 + dx, 7, pelo_l)
    px(c, 21 + dx, 8, pelo_l)
    px(c, 26 + dx, 8, pelo_l)
    # cara redondeada (esquinas comidas)
    box(c, 20 + dx, 10, 27 + dx, 16, SKIN)
    borrar(c, 20 + dx, 10)
    borrar(c, 27 + dx, 10)
    borrar(c, 20 + dx, 16)
    borrar(c, 27 + dx, 16)
    # pelo sobre la frente y patillas
    box(c, 20 + dx, 10, 27 + dx, 10, pelo)
    box(c, 20 + dx, 11, 20 + dx, 13, pelo)
    box(c, 27 + dx, 11, 27 + dx, 13, pelo)
    px(c, 22 + dx, 10, pelo_l)
    px(c, 24 + dx, 10, pelo_l)
    if not cara:
        # nuca: todo pelo, sin facciones
        box(c, 21 + dx, 11, 26 + dx, 15, pelo)
        px(c, 21 + dx, 11, pelo_l)
        px(c, 23 + dx, 11, pelo_l)
        px(c, 24 + dx, 12, pelo_l)
        px(c, 25 + dx, 13, pelo_l)
        px(c, 22 + dx, 14, pelo_l)
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
    # barba corta: bigote, patillas y menton
    if barba:
        px(c, 22 + dx, 13, BEARD)
        px(c, 25 + dx, 13, BEARD)
        box(c, 20 + dx, 14, 21 + dx, 15, BEARD)
        box(c, 26 + dx, 14, 27 + dx, 15, BEARD)
        box(c, 22 + dx, 15, 25 + dx, 15, BEARD)
        box(c, 21 + dx, 16, 26 + dx, 16, BEARD_D)
        px(c, 23 + dx, 16, BEARD)
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
    # menton (limpio si no hay barba) y cuello
    if not barba:
        px(c, 22 + dx, 15, SKIN_D)
        px(c, 25 + dx, 15, SKIN_D)
    box(c, 22 + dx, 17, 25 + dx, 17, SKIN)
    px(c, 25 + dx, 17, SKIN_D)


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


def dib_brazalete(c, codo, muneca):
    """Brazalete de cuero trenzado: dos vueltas en el antebrazo."""
    for t, luz, sombra in ((0.35, BRACER_L, BRACER), (0.65, BRACER, BRACER_D)):
        x = int(round(codo[0] + (muneca[0] - codo[0]) * t))
        y = int(round(codo[1] + (muneca[1] - codo[1]) * t))
        box(c, x - 1, y, x + 1, y, sombra)
        px(c, x, y, luz)


def dib_brazo(c, pts, mano_en=None, abierta=False, lado=-1,
              brazo_desnudo=True, brazaletes=True):
    """Brazo de 3 px sobre la capa del cuerpo.

    `lado=-1` para el brazo izquierdo (sombra a la derecha) y `+1` para el
    derecho (sombra a la izquierda): el borde oscuro marca el pliegue del brazo
    desnudo contra el torso (o contra la tunica de la abuela).
    """
    color = SKIN if brazo_desnudo else TUNIC
    borde = OUT if brazo_desnudo else TUNIC_D
    for a, b in zip(pts, pts[1:]):
        line(c, a[0], a[1], b[0], b[1], color, 3)
    if brazaletes and brazo_desnudo and len(pts) >= 3:
        dib_brazalete(c, pts[1], pts[2])
    for a, b in zip(pts, pts[1:]):
        if abs(a[1] - b[1]) >= abs(a[0] - b[0]):
            line(c, a[0] - lado, a[1], b[0] - lado, b[1], borde, 1)
    if mano_en:
        dib_mano(c, mano_en[0], mano_en[1], abierta)


def cuerpo(c, dx=0, blink=False, mouth=1, cara=True, canas=False,
           panuelo=False, desnudo=True, barba=True, espalda=False,
           falda=False):
    """Pega piernas, torso, cabeza y panuelo en la capa `c`."""
    dib_piernas(c, dx, falda=falda)
    dib_torso(c, dx, desnudo=desnudo, espalda=espalda)
    dib_cabeza(c, dx, blink=blink, mouth=mouth, cara=cara, canas=canas,
               barba=barba)
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
    # piernas hacia la derecha (pantalon azul y pies descalzos)
    box(c, 29, 28, 37, 30, PANTS)
    box(c, 29, 30, 37, 30, PANTS_D)
    box(c, 30, 31, 37, 33, PANTS)
    box(c, 30, 33, 37, 33, PANTS_D)
    box(c, 37, 27, 40, 30, SKIN)
    box(c, 37, 27, 40, 27, SKIN_L)
    box(c, 37, 30, 40, 30, SKIN_D)
    box(c, 37, 31, 40, 34, SKIN)
    box(c, 37, 31, 40, 31, SKIN_L)
    box(c, 37, 34, 40, 34, SKIN_D)
    # torso desnudo tirado de frente
    box(c, 17, 26, 30, 32, SKIN)
    box(c, 17, 32, 30, 32, SKIN_D)
    box(c, 17, 26, 30, 26, SKIN_L)
    box(c, 17, 26, 17, 32, SKIN_D)
    px(c, 20, 29, SKIN_D)       # pectoral
    px(c, 22, 30, SKIN_D)       # abdomen
    px(c, 24, 28, SKIN_D)
    # cinturon trenzado y hebilla, vistos de costado
    box(c, 25, 26, 26, 32, BELT)
    px(c, 25, 29, BUCKLE)
    px(c, 25, 30, BUCKLE)
    px(c, 26, 28, BELT_L)
    px(c, 26, 31, BELT_D)
    # brazos abiertos, con brazalete
    dib_brazo(c, [(30, 29), (34, 33), (36, 34)], (37, 35), abierta=True, lado=+1)
    dib_brazo(c, [(18, 28), (16, 24), (17, 22)], (18, 21), abierta=True, lado=-1)
    # cabeza de frente, apoyada
    box(c, 9, 25, 18, 34, SKIN)
    borrar(c, 9, 25)
    borrar(c, 18, 25)
    borrar(c, 9, 34)
    borrar(c, 18, 34)
    # pelo y barba corta
    box(c, 10, 25, 17, 26, HAIR)
    box(c, 9, 27, 9, 30, HAIR)
    px(c, 12, 25, HAIR_L)
    px(c, 15, 26, HAIR_L)
    box(c, 10, 33, 17, 34, BEARD)
    box(c, 11, 34, 16, 34, BEARD_D)
    for x in (12, 16):
        px(c, x - 1, 28, OUT)
        px(c, x + 1, 28, OUT)
        px(c, x, 29, OUT)
        px(c, x - 1, 30, OUT)
        px(c, x + 1, 30, OUT)
    px(c, 14, 31, SKIN_D)
    box(c, 12, 32, 15, 32, MOUTH)
    px(c, 13, 32, TEETH)
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
    # piernas hacia la izquierda (pantalon azul y pies descalzos)
    box(c, 10, 28, 18, 30, PANTS)
    box(c, 10, 30, 18, 30, PANTS_D)
    box(c, 10, 31, 17, 33, PANTS)
    box(c, 10, 33, 17, 33, PANTS_D)
    box(c, 7, 27, 10, 30, SKIN)
    box(c, 7, 27, 10, 27, SKIN_L)
    box(c, 7, 30, 10, 30, SKIN_D)
    box(c, 7, 31, 10, 34, SKIN)
    box(c, 7, 31, 10, 31, SKIN_L)
    box(c, 7, 34, 10, 34, SKIN_D)
    # torso de espaldas (sin hebilla)
    box(c, 17, 26, 30, 32, SKIN)
    box(c, 17, 26, 30, 26, SKIN_D)
    box(c, 17, 32, 30, 32, SKIN_D)
    box(c, 23, 26, 24, 32, SKIN_D)   # columna
    box(c, 25, 26, 26, 32, BELT)     # cinturon trenzado, de espaldas
    px(c, 25, 29, BELT_L)
    px(c, 25, 31, BELT_D)
    px(c, 20, 29, SKIN_L)            # omoplato
    px(c, 27, 30, SKIN_L)
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
    if n == 1:  # saludo de despedida, mano arriba
        cuerpo(c, mouth=2)
        dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), lado=+1)
        dib_brazo(c, [(19, 19), (15, 16), (13, 13)], (12, 12), abierta=True, lado=-1)
        pegar(b, c)
        px(b, 8, 7, YELLOW)
        px(b, 9, 11, YELLOW_D)
    else:  # de espaldas, alejandose (ya no hay sombrero que llevarse)
        cuerpo(c, mouth=1, cara=False, espalda=True)
        dib_brazo(c, [(19, 19), (18, 23), (18, 26)], (18, 27), lado=-1)
        dib_brazo(c, [(28, 19), (29, 23), (29, 26)], (29, 27), lado=+1)
        pegar(b, c)
        polvo(b, 20, 37, 1)
        polvo(b, 28, 37, 1)
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


def frame_grandma(n):
    b = canvas()
    c = canvas()
    # abuela: pollera larga y panuelo; el aldeano nuevo no tiene sombrero
    cuerpo(c, mouth=1, canas=True, panuelo=True, desnudo=False, barba=False,
           falda=True)
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
        dib_brazo(c, [(19, 19), (17, 23), (18, 22)], (18, 21), abierta=True,
                  lado=-1, brazaletes=False)
        dib_brazo(c, [(28, 19), (30, 23), (29, 22)], (29, 21), abierta=True,
                  lado=+1, brazaletes=False)
    else:  # manos abajo: la prenda en la falda
        line(c, 17, 22, 30, 22, NEEDLE, 1)
        line(c, 17, 26, 30, 22, NEEDLE, 1)
        box(c, 21, 23, 26, 26, YARN)
        box(c, 21, 26, 26, 26, YARN_D)
        px(c, 22, 24, YARN_L)
        line(c, 32, 33, 29, 27, YARN, 1)
        dib_brazo(c, [(19, 19), (17, 23), (18, 24)], (18, 25), abierta=True,
                  lado=-1, brazaletes=False)
        dib_brazo(c, [(28, 19), (30, 23), (29, 24)], (29, 25), abierta=True,
                  lado=+1, brazaletes=False)
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
# Los nombres son exactamente los PNG que hay en `emotes/aoe/` (y en su gemelo
# `emotes/aoe-yolo/`): sin alias nuevos, para que correr el script no agregue ni
# borre archivos. Las poses que el ciclo pide de mas repiten la pose 1; las que
# vienen de tandas viejas (`_03`) usan la misma pose, asi no queda arte anterior.
#
# `explore`, `build`, `jira`, `review`, `yolo` y `super-yolo` no estan en esta
# tabla a proposito: los dibujan `gen_explore_aoe.py`, `gen_build_aoe.py` y
# `gen_yolo_aoe.py`, que comparten estas primitivas. Correr este script no los
# pisa.
FRAMES = [
    ("hi", [("hi_01.png", lambda: frame_hi(1)),
            ("hi_02.png", lambda: frame_hi(2)),
            ("hi_03.png", lambda: frame_hi(1))]),
    ("idle", [("idle.png", lambda: frame_idle(1)),
              ("idle_blink.png", lambda: frame_idle(2))]),
    ("talk", [("talk_close.png", lambda: frame_talk(0)),
              ("talk_small.png", lambda: frame_talk(1)),
              ("talk_mid.png", lambda: frame_talk(2)),
              ("talk_wide.png", lambda: frame_talk(3)),
              ("talk.png", lambda: frame_talk(2))]),
    ("ask", [("ask_01.png", lambda: frame_ask(1)),
             ("ask_02.png", lambda: frame_ask(2)),
             ("ask_03.png", lambda: frame_ask(1))]),
    ("success", [("success_01.png", lambda: frame_success(1)),
                 ("success_02.png", lambda: frame_success(2)),
                 ("success_03.png", lambda: frame_success(1))]),
    ("failure", [("down_01.png", frame_failure_front),
                 ("down_02.png", frame_failure_back),
                 ("down_03.png", frame_failure_front)]),
    ("bye", [("bye_01.png", lambda: frame_bye(1)),
             ("bye_02.png", lambda: frame_bye(2)),
             ("bye_03.png", lambda: frame_bye(1))]),
    ("jobs", [("jobs_01.png", lambda: frame_jobs(1)),
              ("jobs_02.png", lambda: frame_jobs(2)),
              ("jobs_03.png", lambda: frame_jobs(1))]),
    ("grandma", [("grandma_01.png", lambda: frame_grandma(1)),
                 ("grandma_02.png", lambda: frame_grandma(2)),
                 ("grandma_03.png", lambda: frame_grandma(1))]),
    ("write", [("write_01.png", lambda: frame_write(1)),
               ("write_02.png", lambda: frame_write(2)),
               ("write_03.png", lambda: frame_write(1))]),
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
    print("  total       %d PNG, %d bytes en emotes/%s/"
          % (sum(len(f) for f in escritos.values()), total, SET_NAME))


if __name__ == "__main__":
    main()
