#!/usr/bin/env python3
"""Galería ×4 de las 24 escenas de `emotes/aoe/` para el README.

Genera `docs/scenes/<estado>.png` (192×160) desde el frame representativo de
`emotes/aoe/<estado>/`. Solo stdlib (`struct`, `zlib`, `os`): decodifica la PNG
48×40 fuente, la agranda ×4 con vecino más cercano y la vuelve a codificar.

Frame representativo por estado:
- `idle`  -> `idle.png`
- `think` -> `think_04.png` (el frame con WOLOLO)
- `talk`  -> `talk_mid.png`
- resto   -> `<estado>_01.png`

La galería es solo documentación: el plugin nunca lee `docs/`. El script no
escribe en `emotes/` ni en `sounds/`.

Uso (desde cualquier carpeta):
    python3 gentle-emote-arcade/scripts/scenes_gallery.py
    python3 gentle-emote-arcade/scripts/scenes_gallery.py --check
    python3 gentle-emote-arcade/scripts/scenes_gallery.py \
        --emotes-dir /tmp/aoe --out-dir /tmp/galeria

Códigos de salida: 0 ok, 1 `--check` encontró diferencias, 2 error de datos.
"""

import argparse
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
DEFAULT_EMOTES = os.path.join(REPO_ROOT, "emotes", "aoe")
DEFAULT_OUT = os.path.join(REPO_ROOT, "docs", "scenes")


class GalleryError(Exception):
    """Error de datos: frame faltante, PNG inválida o set incompleto."""


def rep_frame(state):
    return REP_FRAMES.get(state, state + "_01.png")


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
        src = os.path.join(emotes_dir, state, rep_frame(state))
        if not os.path.isfile(src):
            missing_frames.append(os.path.join(state, rep_frame(state)))
    if missing_frames:
        raise GalleryError("faltan frames representativos en %s: %s"
                           % (emotes_dir, ", ".join(missing_frames)))

    gallery = {}
    for state in SCENES:
        src = os.path.join(emotes_dir, state, rep_frame(state))
        gallery[state] = upscale(*read_png(src), factor=factor)
    return gallery


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


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Genera la galería ×4 (192×160) de las 24 escenas de "
                    "emotes/aoe/ en docs/scenes/.",
        epilog="Códigos de salida: 0 ok, 1 --check con diferencias, 2 error de datos.")
    parser.add_argument("--emotes-dir", default=DEFAULT_EMOTES,
                        help="set de frames a leer (por defecto emotes/aoe/ del repo)")
    parser.add_argument("--out-dir", default=DEFAULT_OUT,
                        help="carpeta de PNG de salida (por defecto docs/scenes/)")
    parser.add_argument("--check", action="store_true",
                        help="no escribe: compara la salida con lo que se generaría")
    args = parser.parse_args(argv)

    try:
        gallery = build(args.emotes_dir)
    except GalleryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    if args.check:
        return check(gallery, args.out_dir)

    try:
        os.makedirs(args.out_dir, exist_ok=True)
        for state in SCENES:
            width, height, rgba = gallery[state]
            dest = os.path.join(args.out_dir, state + ".png")
            write_png(dest, width, height, rgba)
            print("%-12s %-17s -> %s (%dx%d)"
                  % (state, rep_frame(state), dest, width, height))
    except GalleryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    print("%d PNG en %s" % (len(SCENES), args.out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
