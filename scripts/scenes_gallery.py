#!/usr/bin/env python3
"""Galería ×4 de las 24 escenas de un set de `emotes/` (por defecto `aoe`).

Dos derivados, ambos de solo lectura sobre `emotes/`:

- `docs/scenes/<estado>.png` (192×160): un PNG por estado desde el frame
  representativo de `emotes/aoe/<estado>/` para el README.
- `docs/galeria/<juego>.png`: hoja de contactos por juego con los 24 frames
  ×4 y, debajo de cada tile, una banda con el nombre de la acción (estado) y
  el frame usado, rotulada con `scripts/pixel_font.py` (fuente 3×5).

Solo stdlib (`struct`, `zlib`, `os`): decodifica la PNG 48×40 fuente, la
agranda ×4 con vecino más cercano y la vuelve a codificar.

Frame representativo por estado (primer candidato que exista, en este orden):
- `idle.png`, `think_04.png`, `talk_mid.png` (preferencias históricas)
- `<estado>_01.png`
- `<estado>.png`
- el primer PNG de la carpeta en orden alfabético (`failure/down_0N.png`)

La galería es solo documentación: el plugin nunca lee `docs/`. El script no
escribe en `emotes/` ni en `sounds/`.

Uso (desde cualquier carpeta):
    python3 gentle-emote-arcade/scripts/scenes_gallery.py
    python3 gentle-emote-arcade/scripts/scenes_gallery.py --check
    python3 gentle-emote-arcade/scripts/scenes_gallery.py --juego aoe --hoja
    python3 gentle-emote-arcade/scripts/scenes_gallery.py --juego aoe --hoja --check
    python3 gentle-emote-arcade/scripts/scenes_gallery.py \
        --emotes-dir /tmp/aoe --out-dir /tmp/galeria

`--hoja` (o `--juego`) escribe solo la hoja de contactos y no toca
`docs/scenes/`. `--check` con hoja compara únicamente
`docs/galeria/<juego>.png`: las hojas de otros juegos no son un error.

Códigos de salida: 0 ok, 1 `--check` encontró diferencias, 2 error de datos.
"""

import argparse
import importlib.util
import os
import struct
import sys
import zlib

SCALE = 4

# Las 24 escenas, en el orden del mapa (docs/MAPA-ESCENAS.md).
SCENES = (
    "hi", "idle", "think", "talk", "read", "write",
    "tool", "ask", "success", "failure", "compact", "delegate",
    "explore", "build", "verify", "judge", "review", "jira",
    "jobs", "yolo", "super-yolo", "remember", "grandma", "bye",
)

REP_FRAMES = {"idle": "idle.png", "think": "think_04.png", "talk": "talk_mid.png"}

SIGNATURE = b"\x89PNG\r\n\x1a\n"

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMOTES_ROOT = os.path.join(REPO_ROOT, "emotes")
DEFAULT_EMOTES = os.path.join(EMOTES_ROOT, "aoe")
DEFAULT_OUT = os.path.join(REPO_ROOT, "docs", "scenes")
DEFAULT_HOJA_DIR = os.path.join(REPO_ROOT, "docs", "galeria")

# Hoja de contactos por juego: tiles ×4 y una banda de etiqueta por escena.
SHEET_COLUMNS = 4
BAND_HEIGHT = 28
BAND_RULE_HEIGHT = 2
BAND_PAD = 4
BAND_TEXT_SCALE = 2
BAND_STATE_OFFSET = 4
BAND_FRAME_OFFSET = 16
SHEET_BG = (0x14, 0x17, 0x1D, 0xFF)
TILE_BG = (0x20, 0x24, 0x2C, 0xFF)
BAND_BG = (0x0E, 0x11, 0x16, 0xFF)
BAND_RULE = (0x3A, 0x42, 0x50, 0xFF)
BAND_STATE_COLOR = (0xF2, 0xE9, 0xD0, 0xFF)
BAND_FRAME_COLOR = (0x8F, 0xA3, 0xA8, 0xFF)

_FONT = None


class GalleryError(Exception):
    """Error de datos: frame faltante, PNG inválida o set incompleto."""


def rep_frame(state):
    """Nombre preferido del frame representativo (puede no existir en el set)."""
    return REP_FRAMES.get(state, state + "_01.png")


def _frame(folder, state):
    """Frame representativo tolerando los nombres propios de cada set.

    Orden: preferencia histórica (`idle.png`, `think_04.png`, `talk_mid.png`
    o `<estado>_01.png`), `<estado>.png` y, si ninguno existe, el primer PNG
    en orden alfabético (así `failure/down_01.png` entra sin renombrar arte).
    Devuelve `None` si la carpeta no tiene ningún PNG.
    """
    try:
        pngs = sorted(name for name in os.listdir(folder)
                      if name.lower().endswith(".png"))
    except OSError as exc:
        raise GalleryError("no se pudo leer %s: %s" % (folder, exc))
    if not pngs:
        return None
    for preferred in (rep_frame(state), state + ".png"):
        if preferred in pngs:
            return os.path.join(folder, preferred)
    return os.path.join(folder, pngs[0])


def _load_font():
    """Carga `pixel_font.py` del mismo directorio, sin depender de sys.path."""
    global _FONT
    if _FONT is not None:
        return _FONT
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pixel_font.py")
    spec = importlib.util.spec_from_file_location("arcade_pixel_font", path)
    if spec is None or spec.loader is None:
        raise GalleryError("no se pudo cargar %s" % path)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise GalleryError("no se pudo cargar %s: %s" % (path, exc))
    _FONT = module
    return _FONT


def read_png(path):
    """Devuelve (ancho, alto, bytes RGBA) de una PNG 8-bit RGBA sin interlace."""
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        raise GalleryError("no se pudo leer %s: %s" % (path, exc))

    if not data.startswith(SIGNATURE):
        raise GalleryError("%s: no es una PNG (firma inválida)" % path)

    pos = len(SIGNATURE)
    header = None
    idat = bytearray()
    while pos + 8 <= len(data):
        length, = struct.unpack(">I", data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + length
        body = data[pos + 8:end]
        crc_pos = end
        if len(body) != length or crc_pos + 4 > len(data):
            raise GalleryError("%s: chunk %r truncado" % (path, ctype))
        crc, = struct.unpack(">I", data[crc_pos:crc_pos + 4])
        if crc != (zlib.crc32(ctype + body) & 0xFFFFFFFF):
            raise GalleryError("%s: CRC inválido en chunk %r" % (path, ctype))
        pos = crc_pos + 4
        if ctype == b"IHDR":
            header = body
        elif ctype == b"IDAT":
            idat += body
        elif ctype == b"IEND":
            break

    if header is None or len(header) != 13:
        raise GalleryError("%s: falta IHDR" % path)
    if not idat:
        raise GalleryError("%s: falta IDAT" % path)
    width, height, depth, color, compression, filters, interlace = struct.unpack(
        ">IIBBBBB", header)
    if depth != 8 or color != 6:
        raise GalleryError(
            "%s: se esperaba PNG 8-bit RGBA, vino color=%d depth=%d"
            % (path, color, depth))
    if compression != 0 or filters != 0:
        raise GalleryError("%s: método de compresión/filtro no soportado" % path)
    if interlace != 0:
        raise GalleryError("%s: PNG interlazada no soportada" % path)
    if width <= 0 or height <= 0:
        raise GalleryError("%s: dimensiones inválidas %dx%d" % (path, width, height))

    try:
        raw = zlib.decompress(bytes(idat))
    except zlib.error as exc:
        raise GalleryError("%s: IDAT ilegible (%s)" % (path, exc))

    stride = width * 4
    expected = height * (stride + 1)
    if len(raw) != expected:
        raise GalleryError(
            "%s: %d bytes decodificados, se esperaban %d"
            % (path, len(raw), expected))

    out = bytearray()
    prev = bytearray(stride)
    for y in range(height):
        offset = y * (stride + 1)
        kind = raw[offset]
        line = bytearray(raw[offset + 1:offset + 1 + stride])
        if kind == 1:
            for x in range(4, stride):
                line[x] = (line[x] + line[x - 4]) & 0xFF
        elif kind == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif kind == 3:
            for x in range(stride):
                left = line[x - 4] if x >= 4 else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 0xFF
        elif kind == 4:
            for x in range(stride):
                left = line[x - 4] if x >= 4 else 0
                up = prev[x]
                ul = prev[x - 4] if x >= 4 else 0
                est = left + up - ul
                pa, pb, pc = abs(est - left), abs(est - up), abs(est - ul)
                if pa <= pb and pa <= pc:
                    pred = left
                elif pb <= pc:
                    pred = up
                else:
                    pred = ul
                line[x] = (line[x] + pred) & 0xFF
        elif kind != 0:
            raise GalleryError("%s: filtro PNG desconocido %d en fila %d"
                               % (path, kind, y))
        out += line
        prev = line
    return width, height, bytes(out)


def write_png(path, width, height, rgba):
    """Codifica PNG 8-bit RGBA sin interlace, filtro 0 por fila."""
    def chunk(ctype, body):
        raw = ctype + body
        return (struct.pack(">I", len(body)) + raw
                + struct.pack(">I", zlib.crc32(raw) & 0xFFFFFFFF))

    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgba[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = (SIGNATURE + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
    try:
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        raise GalleryError("no se pudo escribir %s: %s" % (path, exc))


def upscale(width, height, rgba, factor):
    """Vecino más cercano: cada píxel fuente se repite factor×factor."""
    stride = width * 4
    out = bytearray()
    for y in range(height):
        line = rgba[y * stride:(y + 1) * stride]
        row = bytearray()
        for x in range(width):
            row += line[x * 4:x * 4 + 4] * factor
        out += row * factor
    return width * factor, height * factor, bytes(out)


def build(emotes_dir, factor=SCALE):
    """Devuelve {estado: (ancho, alto, RGBA)} con la galería ya escalada."""
    if not os.path.isdir(emotes_dir):
        raise GalleryError("no existe el set: %s" % emotes_dir)
    present = {name for name in os.listdir(emotes_dir)
               if os.path.isdir(os.path.join(emotes_dir, name))}
    missing_states = [state for state in SCENES if state not in present]
    extra_states = sorted(present - set(SCENES))
    problems = []
    if missing_states:
        problems.append("faltan estados: " + ", ".join(missing_states))
    if extra_states:
        problems.append("estados sin documentar en SCENES: "
                        + ", ".join(extra_states))
    if problems:
        raise GalleryError("%s: %s" % (emotes_dir, "; ".join(problems)))

    missing_frames = []
    for state in SCENES:
        if _frame(os.path.join(emotes_dir, state), state) is None:
            missing_frames.append("%s/: sin PNG" % state)
    if missing_frames:
        raise GalleryError("faltan frames representativos en %s: %s"
                           % (emotes_dir, ", ".join(missing_frames)))

    resolved = frames(emotes_dir)
    gallery = {}
    for state in SCENES:
        gallery[state] = upscale(*read_png(resolved[state]), factor=factor)
    return gallery


def frames(emotes_dir):
    """{estado: ruta} con el frame representativo ya resuelto de cada escena."""
    resolved = {}
    for state in SCENES:
        path = _frame(os.path.join(emotes_dir, state), state)
        if path is None:
            raise GalleryError("%s: %s/ sin PNG" % (emotes_dir, state))
        resolved[state] = path
    return resolved


def _fill(canvas, width, x, y, w, h, color):
    """Pinta un rectángulo opaco; el llamador garantiza que cae en el lienzo."""
    row = bytes(color[:4]) * w
    for yy in range(y, y + h):
        offset = (yy * width + x) * 4
        canvas[offset:offset + w * 4] = row


def _compose(canvas, width, x, y, src_w, src_h, rgba):
    """Compone `rgba` source-over sobre el lienzo (fondo ya opaco)."""
    for sy in range(src_h):
        dst_row = ((y + sy) * width + x) * 4
        for sx in range(src_w):
            source = (sy * src_w + sx) * 4
            alpha = rgba[source + 3]
            if alpha == 0:
                continue
            dest = dst_row + sx * 4
            if alpha == 255:
                canvas[dest:dest + 4] = rgba[source:source + 4]
                continue
            dst_alpha = canvas[dest + 3]
            out_alpha = alpha + (dst_alpha * (255 - alpha)) // 255
            for channel in range(3):
                value = (rgba[source + channel] * alpha
                         + canvas[dest + channel] * dst_alpha
                         * (255 - alpha) // 255)
                canvas[dest + channel] = value // out_alpha
            canvas[dest + 3] = out_alpha


def sheet(gallery, resolved, factor=SCALE):
    """Hoja de contactos: tiles ×4 con banda de etiqueta (estado + frame)."""
    font = _load_font()
    tile_w = 48 * factor
    tile_h = 40 * factor
    rows = (len(SCENES) + SHEET_COLUMNS - 1) // SHEET_COLUMNS
    width = tile_w * SHEET_COLUMNS
    height = rows * (tile_h + BAND_HEIGHT)
    canvas = bytearray(bytes(SHEET_BG) * (width * height))
    for index, state in enumerate(SCENES):
        src_w, src_h, rgba = gallery[state]
        x0 = (index % SHEET_COLUMNS) * tile_w
        y0 = (index // SHEET_COLUMNS) * (tile_h + BAND_HEIGHT)
        _fill(canvas, width, x0, y0, tile_w, tile_h, TILE_BG)
        _compose(canvas, width, x0, y0, src_w, src_h, rgba)
        _fill(canvas, width, x0, y0 + tile_h, tile_w, BAND_HEIGHT, BAND_BG)
        _fill(canvas, width, x0, y0 + tile_h, tile_w, BAND_RULE_HEIGHT, BAND_RULE)
        for text, color, offset in (
                (font.normalize(state), BAND_STATE_COLOR, BAND_STATE_OFFSET),
                (font.normalize(os.path.basename(resolved[state])),
                 BAND_FRAME_COLOR, BAND_FRAME_OFFSET)):
            scale = BAND_TEXT_SCALE
            while scale > 1 and (font.text_size(text, scale)[0]
                                 > tile_w - 2 * BAND_PAD):
                scale -= 1
            font.draw(canvas, width, height, x0 + BAND_PAD,
                      y0 + tile_h + offset, text, color, scale=scale)
    return width, height, bytes(canvas)


def check_sheet(gallery, resolved, dest, factor=SCALE):
    """Compara la hoja en `dest` con la que se generaría (sin escribir)."""
    want_w, want_h, want = sheet(gallery, resolved, factor)
    problems = []
    if not os.path.isfile(dest):
        problems.append("falta %s" % dest)
    else:
        try:
            got_w, got_h, got = read_png(dest)
        except GalleryError as exc:
            problems.append(str(exc))
        else:
            if (got_w, got_h) != (want_w, want_h):
                problems.append("%s: %dx%d, se esperaba %dx%d"
                                % (dest, got_w, got_h, want_w, want_h))
            elif got != want:
                problems.append("%s: píxeles distintos de las escenas actuales"
                                % dest)
    if problems:
        for problem in problems:
            print("error: %s" % problem, file=sys.stderr)
        print("check: %d problema(s) en %s" % (len(problems), dest),
              file=sys.stderr)
        return 1
    print("check: hoja al día en %s (%dx%d)" % (dest, want_w, want_h))
    return 0


def check(gallery, out_dir):
    problems = []
    for state in SCENES:
        want_w, want_h, want = gallery[state]
        dest = os.path.join(out_dir, state + ".png")
        if not os.path.isfile(dest):
            problems.append("falta %s" % dest)
            continue
        try:
            got_w, got_h, got = read_png(dest)
        except GalleryError as exc:
            problems.append(str(exc))
            continue
        if (got_w, got_h) != (want_w, want_h):
            problems.append("%s: %dx%d, se esperaba %dx%d"
                            % (dest, got_w, got_h, want_w, want_h))
        elif got != want:
            problems.append("%s: píxeles distintos del frame actual" % dest)
    if os.path.isdir(out_dir):
        expected = {state + ".png" for state in SCENES}
        for name in sorted(os.listdir(out_dir)):
            if name.endswith(".png") and name not in expected:
                problems.append("sobra %s (no corresponde a ningún estado)"
                                % os.path.join(out_dir, name))
    if problems:
        for problem in problems:
            print("error: %s" % problem, file=sys.stderr)
        print("check: %d problema(s) en %s" % (len(problems), out_dir),
              file=sys.stderr)
        return 1
    print("check: %d PNG al día en %s" % (len(SCENES), out_dir))
    return 0


def _games():
    """Sets de sprites disponibles bajo `emotes/`."""
    if not os.path.isdir(EMOTES_ROOT):
        return []
    return sorted(name for name in os.listdir(EMOTES_ROOT)
                  if os.path.isdir(os.path.join(EMOTES_ROOT, name)))


def _resolve_set(args):
    """(carpeta del set, nombre para la hoja) según --juego / --emotes-dir."""
    if args.juego and args.emotes_dir:
        raise GalleryError("usá --juego o --emotes-dir, no ambos")
    if args.juego:
        games = _games()
        if args.juego not in games:
            raise GalleryError("no existe el juego %r en %s; disponibles: %s"
                               % (args.juego, EMOTES_ROOT,
                                  ", ".join(games) or "ninguno"))
        return os.path.join(EMOTES_ROOT, args.juego), args.juego
    if args.emotes_dir:
        return args.emotes_dir, os.path.basename(os.path.normpath(args.emotes_dir))
    return DEFAULT_EMOTES, os.path.basename(DEFAULT_EMOTES)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Genera la galería ×4 (192×160) de las 24 escenas de "
                    "emotes/<juego>/ en docs/scenes/ y, con --hoja, la hoja de "
                    "contactos rotulada en docs/galeria/<juego>.png.",
        epilog="Códigos de salida: 0 ok, 1 --check con diferencias, 2 error de datos.")
    parser.add_argument("--emotes-dir", default=None,
                        help="set de frames a leer (por defecto emotes/aoe/ del "
                             "repo, o emotes/<juego>/ con --juego)")
    parser.add_argument("--juego", default=None,
                        help="set emotes/<juego>/; implica --hoja")
    parser.add_argument("--hoja", action="store_true",
                        help="genera solo la hoja de contactos rotulada "
                             "(tiles ×4 + nombre de la acción y del frame)")
    parser.add_argument("--hoja-dir", default=DEFAULT_HOJA_DIR,
                        help="carpeta de la hoja (por defecto docs/galeria/)")
    parser.add_argument("--out-dir", default=DEFAULT_OUT,
                        help="carpeta de PNG de salida (por defecto docs/scenes/)")
    parser.add_argument("--check", action="store_true",
                        help="no escribe: compara la salida con lo que se generaría")
    args = parser.parse_args(argv)

    try:
        emotes_dir, set_name = _resolve_set(args)
        gallery = build(emotes_dir)
    except GalleryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    if args.hoja or args.juego:
        dest = os.path.join(args.hoja_dir, set_name + ".png")
        resolved = frames(emotes_dir)
        if args.check:
            try:
                return check_sheet(gallery, resolved, dest)
            except GalleryError as exc:
                print("error: %s" % exc, file=sys.stderr)
                return 2
        try:
            width, height, rgba = sheet(gallery, resolved)
            os.makedirs(args.hoja_dir, exist_ok=True)
            write_png(dest, width, height, rgba)
        except OSError as exc:
            print("error: no se pudo crear %s: %s" % (args.hoja_dir, exc),
                  file=sys.stderr)
            return 2
        except GalleryError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 2
        for state in SCENES:
            print("%-12s %-17s" % (state, os.path.basename(resolved[state])))
        print("hoja: %d escenas, %d columnas -> %s (%dx%d)"
              % (len(SCENES), SHEET_COLUMNS, dest, width, height))
        return 0

    if args.check:
        return check(gallery, args.out_dir)

    try:
        os.makedirs(args.out_dir, exist_ok=True)
        resolved = frames(emotes_dir)
        for state in SCENES:
            width, height, rgba = gallery[state]
            dest = os.path.join(args.out_dir, state + ".png")
            write_png(dest, width, height, rgba)
            print("%-12s %-17s -> %s (%dx%d)"
                  % (state, os.path.basename(resolved[state]), dest,
                     width, height))
    except GalleryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print("%d PNG en %s" % (len(SCENES), args.out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
