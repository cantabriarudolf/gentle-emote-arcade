#!/usr/bin/env python3
"""Genera el emblema del repo a partir del casco de 32x32.

El hub de Gentle usa la primera imagen del README como icono, y lo muestra en
48x48: un PNG de 32 se ve borroso. Esto lo escala x3 con vecino más cercano, así
el navegador lo reduce a 48 sin inventar píxeles.

    python3 scripts/make_emblem.py

Entrada:  docs/assets/casco.png  (32x32 RGBA)
Salida:   docs/assets/casco-emblema.png (96x96 RGBA)
"""
import struct
import sys
import zlib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "docs" / "assets" / "casco.png"
SALIDA = RAIZ / "docs" / "assets" / "casco-emblema.png"
ESCALA = 3


def leer_chunks(datos: bytes):
    if not datos.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("no es un PNG")
    pos = 8
    while pos < len(datos):
        largo = int.from_bytes(datos[pos:pos + 4], "big")
        tipo = datos[pos + 4:pos + 8]
        cuerpo = datos[pos + 8:pos + 8 + largo]
        yield tipo, cuerpo
        pos += 12 + largo


def decodificar(ruta: Path):
    """Devuelve (ancho, alto, RGBA) de un PNG de 8 bits, color 2 o 6, sin entrelazar."""
    datos = ruta.read_bytes()
    ancho = alto = None
    color = None
    idat = b""
    for tipo, cuerpo in leer_chunks(datos):
        if tipo == b"IHDR":
            ancho, alto = struct.unpack(">II", cuerpo[:8])
            profundidad, color, _, _, entrelazado = cuerpo[8], cuerpo[9], cuerpo[10], cuerpo[11], cuerpo[12]
            if profundidad != 8 or color not in (2, 6) or entrelazado != 0:
                raise ValueError(f"formato no soportado: profundidad {profundidad}, color {color}, entrelazado {entrelazado}")
        elif tipo == b"IDAT":
            idat += cuerpo
    if ancho is None:
        raise ValueError("falta IHDR")
    canales = 4 if color == 6 else 3
    bpp = canales
    fila = ancho * canales
    plano = zlib.decompress(idat)
    previo = bytearray(fila)
    crudo = bytearray()
    pos = 0
    for _ in range(alto):
        filtro = plano[pos]
        pos += 1
        linea = bytearray(plano[pos:pos + fila])
        pos += fila
        if filtro == 1:
            for i in range(bpp, fila):
                linea[i] = (linea[i] + linea[i - bpp]) & 0xFF
        elif filtro == 2:
            for i in range(fila):
                linea[i] = (linea[i] + previo[i]) & 0xFF
        elif filtro == 3:
            for i in range(fila):
                a = linea[i - bpp] if i >= bpp else 0
                linea[i] = (linea[i] + ((a + previo[i]) >> 1)) & 0xFF
        elif filtro == 4:
            for i in range(fila):
                a = linea[i - bpp] if i >= bpp else 0
                b = previo[i]
                c = previo[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                linea[i] = (linea[i] + pred) & 0xFF
        elif filtro != 0:
            raise ValueError(f"filtro desconocido: {filtro}")
        crudo += linea
        previo = linea
    if canales == 3:
        rgba = bytearray(ancho * alto * 4)
        for i in range(ancho * alto):
            rgba[i * 4:i * 4 + 3] = crudo[i * 3:i * 3 + 3]
            rgba[i * 4 + 3] = 255
        crudo = rgba
        canales = 4
    return ancho, alto, bytes(crudo)


def escalar(ancho: int, alto: int, rgba: bytes, escala: int):
    """Vecino más cercano: cada píxel se repite en un bloque de escala x escala."""
    nuevo_ancho, nuevo_alto = ancho * escala, alto * escala
    salida = bytearray(nuevo_ancho * nuevo_alto * 4)
    for y in range(nuevo_alto):
        origen_y = y // escala
        for x in range(nuevo_ancho):
            origen_x = x // escala
            i = (origen_y * ancho + origen_x) * 4
            j = (y * nuevo_ancho + x) * 4
            salida[j:j + 4] = rgba[i:i + 4]
    return nuevo_ancho, nuevo_alto, bytes(salida)


def codificar(ancho: int, alto: int, rgba: bytes) -> bytes:
    def chunk(tipo: bytes, cuerpo: bytes) -> bytes:
        return (len(cuerpo).to_bytes(4, "big") + tipo + cuerpo
                + zlib.crc32(tipo + cuerpo).to_bytes(4, "big"))

    fila = ancho * 4
    crudo = b"".join(b"\x00" + rgba[y * fila:(y + 1) * fila] for y in range(alto))
    ihdr = ancho.to_bytes(4, "big") + alto.to_bytes(4, "big") + bytes([8, 6, 0, 0, 0])
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(crudo, 9)) + chunk(b"IEND", b""))


def main() -> int:
    if not ENTRADA.exists():
        print(f"falta {ENTRADA}", file=sys.stderr)
        return 1
    ancho, alto, rgba = decodificar(ENTRADA)
    n_ancho, n_alto, n_rgba = escalar(ancho, alto, rgba, ESCALA)
    SALIDA.write_bytes(codificar(n_ancho, n_alto, n_rgba))
    print(f"{ENTRADA.name} {ancho}x{alto} -> {SALIDA.name} {n_ancho}x{n_alto} (x{ESCALA})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
