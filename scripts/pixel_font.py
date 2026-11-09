#!/usr/bin/env python3
"""Fuente mínima 3×5 para rotular los derivados del arcade (sin dependencias).

Cada glifo son cinco filas de tres caracteres: `#` pinta y `.` deja ver el
fondo. Cubre `A-Z`, `0-9` y los signos que aparecen en las etiquetas de la
galería (`-`, `_`, `.` y espacio). Las minúsculas se normalizan a mayúsculas y
cualquier carácter sin glifo ocupa su avance sin pintar, así una etiqueta rara
nunca rompe la hoja.

Uso típico desde `scenes_gallery.py`:

    import pixel_font
    ancho, alto = pixel_font.text_size("FAILURE", scale=2)
    pixel_font.draw(lienzo, ancho_lienzo, alto_lienzo, x, y,
                    "FAILURE", (0xF2, 0xE9, 0xD0, 0xFF), scale=2)

`draw()` compone source-over sobre un lienzo RGBA (bytes o bytearray) y no
toca nada fuera del recuadro del texto.
"""

GLYPH_WIDTH = 3
GLYPH_HEIGHT = 5
LETTER_SPACING = 1
ADVANCE = GLYPH_WIDTH + LETTER_SPACING

# 5 filas de 3 columnas por glifo. Se dibujan tal cual, sin antialias.
_GLYPHS = {
    " ": ("...",
          "...",
          "...",
          "...",
          "..."),
    "A": ("###",
          "#.#",
          "###",
          "#.#",
          "#.#"),
    "B": ("##.",
          "#.#",
          "##.",
          "#.#",
          "##."),
    "C": ("###",
          "#..",
          "#..",
          "#..",
          "###"),
    "D": ("##.",
          "#.#",
          "#.#",
          "#.#",
          "##."),
    "E": ("###",
          "#..",
          "##.",
          "#..",
          "###"),
    "F": ("###",
          "#..",
          "##.",
          "#..",
          "#.."),
    "G": ("###",
          "#..",
          "#.#",
          "#.#",
          "###"),
    "H": ("#.#",
          "#.#",
          "###",
          "#.#",
          "#.#"),
    "I": ("###",
          ".#.",
          ".#.",
          ".#.",
          "###"),
    "J": ("..#",
          "..#",
          "..#",
          "#.#",
          "###"),
    "K": ("#.#",
          "#.#",
          "##.",
          "#.#",
          "#.#"),
    "L": ("#..",
          "#..",
          "#..",
          "#..",
          "###"),
    "M": ("#.#",
          "###",
          "###",
          "#.#",
          "#.#"),
    "N": ("#.#",
          "##.",
          "###",
          ".##",
          "#.#"),
    "O": ("###",
          "#.#",
          "#.#",
          "#.#",
          "###"),
    "P": ("##.",
          "#.#",
          "##.",
          "#..",
          "#.."),
    "Q": ("###",
          "#.#",
          "#.#",
          "###",
          "..#"),
    "R": ("##.",
          "#.#",
          "##.",
          "#.#",
          "#.#"),
    "S": ("###",
          "#..",
          "###",
          "..#",
          "###"),
    "T": ("###",
          ".#.",
          ".#.",
          ".#.",
          ".#."),
    "U": ("#.#",
          "#.#",
          "#.#",
          "#.#",
          "###"),
    "V": ("#.#",
          "#.#",
          "#.#",
          "#.#",
          ".#."),
    "W": ("#.#",
          "#.#",
          "###",
          "###",
          "#.#"),
    "X": ("#.#",
          "#.#",
          ".#.",
          "#.#",
          "#.#"),
    "Y": ("#.#",
          "#.#",
          ".#.",
          ".#.",
          ".#."),
    "Z": ("###",
          "..#",
          ".#.",
          "#..",
          "###"),
    "0": ("###",
          "#.#",
          "#.#",
          "#.#",
          "###"),
    "1": (".#.",
          "##.",
          ".#.",
          ".#.",
          "###"),
    "2": ("###",
          "..#",
          "###",
          "#..",
          "###"),
    "3": ("###",
          "..#",
          "###",
          "..#",
          "###"),
    "4": ("#.#",
          "#.#",
          "###",
          "..#",
          "..#"),
    "5": ("###",
          "#..",
          "###",
          "..#",
          "###"),
    "6": ("###",
          "#..",
          "###",
          "#.#",
          "###"),
    "7": ("###",
          "..#",
          "..#",
          "..#",
          "..#"),
    "8": ("###",
          "#.#",
          "###",
          "#.#",
          "###"),
    "9": ("###",
          "#.#",
          "###",
          "..#",
          "###"),
    "-": ("...",
          "...",
          "###",
          "...",
          "..."),
    "_": ("...",
          "...",
          "...",
          "...",
          "###"),
    ".": ("...",
          "...",
          "...",
          "...",
          ".#."),
}


def glyph(char):
    """Devuelve las 5 filas del glifo o `None` si el carácter no tiene uno."""
    if len(char) != 1:
        return None
    return _GLYPHS.get(char.upper())


def normalize(text):
    """Mayúsculas, que es el único juego completo que tiene la fuente."""
    return text.upper()


def text_size(text, scale=1):
    """(ancho, alto) en píxeles de `text` dibujado a `scale`."""
    if scale < 1:
        raise ValueError("scale debe ser >= 1")
    count = len(text)
    if count == 0:
        return 0, GLYPH_HEIGHT * scale
    return count * ADVANCE * scale - LETTER_SPACING * scale, GLYPH_HEIGHT * scale


def draw(canvas, width, height, x, y, text, color, scale=1):
    """Compone `text` source-over sobre `canvas` (RGBA de `width`×`height`).

    Devuelve la cantidad de píxeles pintados. Los caracteres sin glifo ocupan
    su avance y no pintan; lo que cae fuera del lienzo se recorta.
    """
    if scale < 1:
        raise ValueError("scale debe ser >= 1")
    if len(canvas) != width * height * 4:
        raise ValueError("el lienzo no mide %dx%d RGBA" % (width, height))
    red, green, blue, alpha = color[:4]
    painted = 0
    for index, char in enumerate(normalize(text)):
        rows = glyph(char)
        if rows is None:
            continue
        base_x = x + index * ADVANCE * scale
        for gy, row in enumerate(rows):
            for gx, cell in enumerate(row):
                if cell != "#":
                    continue
                for dy in range(scale):
                    py = y + gy * scale + dy
                    if py < 0 or py >= height:
                        continue
                    for dx in range(scale):
                        px = base_x + gx * scale + dx
                        if px < 0 or px >= width:
                            continue
                        offset = (py * width + px) * 4
                        if alpha == 255:
                            canvas[offset:offset + 4] = bytes(color[:4])
                        elif alpha:
                            dst = canvas[offset:offset + 4]
                            dst_alpha = dst[3]
                            out_alpha = alpha + (dst_alpha * (255 - alpha)) // 255
                            for channel in range(3):
                                value = (color[channel] * alpha
                                         + dst[channel] * dst_alpha
                                         * (255 - alpha) // 255)
                                canvas[offset + channel] = value // out_alpha
                            canvas[offset + 3] = out_alpha
                        painted += 1
    return painted
