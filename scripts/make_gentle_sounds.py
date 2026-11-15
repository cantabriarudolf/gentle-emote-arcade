#!/usr/bin/env python3
"""Genera el pack `gentle` desde los clips de frases del streamer.

Los clips salen de scrapysound (extraídos del video con subtítulos) y el mapeo
evento → frase vive en `scrapysound/scrapysounds_task/audio_event_mapping.md`.
Este script toma, por evento, el clip más corto de la carpeta indicada, lo
convierte a WAV PCM mono 16 bit 44.1 kHz con GStreamer y escribe
`sounds/gentle/seleccion.json`. Idempotente: vuelve a generar lo mismo.

Uso:
    python3 scripts/make_gentle_sounds.py [CARPETA_DE_CLIPS]

Sin argumento usa `~/Documentos/Proyectos/scrapysound/work/video/clips`.
Requiere `gst-launch-1.0` (con decoder mp3) y no toca nada fuera de
`sounds/gentle/`.
"""
import hashlib
import json
import os
import re
import unicodedata
import subprocess
import sys
import tempfile
import wave

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(REPO, "sounds", "gentle")
CLIPS = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Documentos/Proyectos/scrapysound/work/video/clips"
)

# evento -> (carpeta de clips, tallo del wav). Repetimos carpeta cuando el mapeo
# no ofrece alternativa, con otro clip para no sonar idéntico.
PLAN = [
    ("session.started", "gentle_shell", "gentle-shell"),
    ("agent.started", "a_ver", "a-ver"),
    ("agent.completed", "espectacular", "espectacular"),
    ("agent.failed", "no", "no"),
    ("agent.cancelled", "así_no_más", "asi-no-mas"),
    ("agent.attention", "qué_les_parece", "que-les-parece"),
    ("subagent.queued", "a_ver", "a-ver-2"),
    ("subagent.running", "locura", "locura"),
    ("subagent.waiting", "bien", "bien"),
    ("subagent.completed", "ahí_está", "ahi-esta"),
    ("subagent.failed", "la_verdad_eh", "la-verdad-eh"),
    ("subagent.cancelled", "así_no_más", "asi-no-mas-2"),
    ("subagent.timed_out", "no", "no-2"),
    ("context.high", "locura", "locura-2"),
]

MAX_CANDIDATOS = 2
# Las tomas de «abuela» son casi idénticas: se queda la primera (la mejor) y punto.
ACTIVACION_MAX = 1
# "✓ New session started": frase completa y toma distinta de la que ya usa `context.high`.
NUEVA_SESION = ("locura", "esto es una locura", "esto-es-una-locura")
# Toma elegida a oído: frase completa, distinta de la que usan los eventos.
NUEVA_SESION_CLIP = "018_Esto_es_una_locura.mp3"
MIN_BYTES = 6 * 1024
MIN_SECS, MAX_SECS = 0.4, 4.5
# Las variaciones de «abuela» son frases completas: valen hasta el techo del contrato (10 s).
MAX_SECS_ACTIVACION = 9.5
# La frase de sesión nueva es una frase completa, como la activación.
MAX_SECS_NUEVA_SESION = 9.5
MAX_BYTES = 2 * 1024 * 1024


def normalizar(texto):
    sin = unicodedata.normalize("NFKD", texto.lower())
    sin = "".join(c for c in sin if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "_", sin).strip("_")


def puntaje(nombre, frase):
    """0 si el clip arranca con la frase, 1 si la menciona, 2 si es del tema pero otra cosa."""
    tallo = re.sub(r"^\d+_", "", normalizar(os.path.splitext(nombre)[0]))
    buscada = normalizar(frase)
    if tallo.startswith(buscada):
        return 0
    return 1 if buscada in tallo else 2


def convertir(mp3, wav):
    subprocess.run(
        [
            "gst-launch-1.0", "-q",
            "filesrc", f"location={mp3}", "!",
            "decodebin", "!",
            "audioconvert", "!",
            "audioresample", "!",
            "audio/x-raw,format=S16LE,channels=1,rate=44100", "!",
            "wavenc", "!",
            "filesink", f"location={wav}",
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )


def medir(wav):
    with wave.open(wav) as w:
        return w.getnchannels(), w.getframerate(), w.getsampwidth() * 8, w.getnframes() / w.getframerate()


def activacion_abuela(filas):
    """La mejor toma de «abuela» del corpus (raíz y subcarpetas), deduplicada por contenido."""
    unicos = {}
    for raiz, _, archivos in os.walk(CLIPS):
        for nombre in sorted(archivos):
            if not nombre.lower().endswith(".mp3") or "abuel" not in nombre.lower():
                continue
            with open(os.path.join(raiz, nombre), "rb") as fh:
                huella = hashlib.md5(fh.read()).hexdigest()
            unicos.setdefault(huella, os.path.join(raiz, nombre))
    tomas = sorted(unicos.values())[:ACTIVACION_MAX]
    stems = []
    for origen in tomas:
        stems.append(f"abuela-{len(stems) + 1}")
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "out.wav")
            convertir(origen, wav)
            canales, rate, bits, segs = medir(wav)
            if canales != 1 or rate != 44100 or bits != 16 or os.path.getsize(wav) > MAX_BYTES \
                    or not (MIN_SECS <= segs <= MAX_SECS_ACTIVACION):
                sys.exit(f"clip de abuela inválido: {os.path.basename(origen)} ({canales}ch {rate}Hz {segs:.2f}s)")
            os.replace(wav, os.path.join(DEST, f"{stems[-1]}.wav"))
        filas.append(("activación", stems[-1], "—", "—", os.path.basename(origen)))
    if not stems:
        print("aviso: no hay clips de «abuela» en el corpus; queda sólo el coin")
    # Limpia tomas viejas que ya no se usan (p.ej. abuela-2, abuela-3).
    for viejo in sorted(os.listdir(DEST)):
        if viejo.startswith("abuela-") and viejo.endswith(".wav") and viejo[:-4] not in stems:
            os.unlink(os.path.join(DEST, viejo))
            print(f"borrado {viejo} (toma descartada)")
    return stems


def nueva_sesion(filas, usados):
    """Frase icónica para el cartel de sesión nueva, sin repetir la toma de los eventos."""
    carpeta, frase, tallo = NUEVA_SESION
    origen = os.path.join(CLIPS, carpeta)
    candidatos = sorted(
        (f for f in os.listdir(origen) if f.lower().endswith(".mp3")),
        key=lambda f: (puntaje(f, frase), os.path.getsize(os.path.join(origen, f))),
    )
    # Primero la toma elegida; si no, cualquiera que arranque con la frase y esté libre.
    orden = [NUEVA_SESION_CLIP] + [c for c in candidatos if c != NUEVA_SESION_CLIP and puntaje(c, frase) == 0]
    for nombre in orden:
        if not os.path.isfile(os.path.join(origen, nombre)):
            continue
        ruta = os.path.join(origen, nombre)
        if ruta in usados or os.path.getsize(ruta) < MIN_BYTES:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            wav = os.path.join(tmp, "out.wav")
            try:
                convertir(ruta, wav)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue
            canales, rate, bits, segs = medir(wav)
            if canales != 1 or rate != 44100 or bits != 16 or os.path.getsize(wav) > MAX_BYTES \
                    or not (MIN_SECS <= segs <= MAX_SECS_NUEVA_SESION):
                continue
            os.replace(wav, os.path.join(DEST, f"{tallo}.wav"))
            filas.append(("sesión nueva", tallo, f"{segs:.2f}s", f"{os.path.getsize(os.path.join(DEST, tallo + '.wav')) // 1024}KB", nombre))
            return [tallo]
    print(f"aviso: sin clip válido para sesión nueva en {carpeta}/ («{frase}»)")
    return []


def main():
    if not os.path.isdir(CLIPS):
        sys.exit(f"no existe la carpeta de clips: {CLIPS}")
    usados = set()
    # La toma de «sesión nueva» se reserva: los eventos no la pueden usar.
    reservados = {os.path.join(CLIPS, NUEVA_SESION[0], NUEVA_SESION_CLIP)}
    choices = {}
    variantes = {}
    filas = []
    for evento, carpeta, tallo in PLAN:
        origen = os.path.join(CLIPS, carpeta)
        if not os.path.isdir(origen):
            sys.exit(f"no existe la carpeta de clips: {origen}")
        candidatos = sorted(
            (f for f in os.listdir(origen) if f.lower().endswith(".mp3")),
            key=lambda f: (puntaje(f, carpeta), os.path.getsize(os.path.join(origen, f))),
        )
        elegidos = []
        for nombre in candidatos:
            if len(elegidos) >= MAX_CANDIDATOS:
                break
            ruta = os.path.join(origen, nombre)
            if os.path.getsize(ruta) < MIN_BYTES or ruta in usados or ruta in reservados:
                continue
            destino_tallo = tallo if not elegidos else f"{tallo}-{len(elegidos) + 1}"
            with tempfile.TemporaryDirectory() as tmp:
                wav = os.path.join(tmp, "out.wav")
                try:
                    convertir(ruta, wav)
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                    continue
                canales, rate, bits, segs = medir(wav)
                bytes_ = os.path.getsize(wav)
                if canales != 1 or rate != 44100 or bits != 16 or bytes_ > MAX_BYTES:
                    continue
                if not (MIN_SECS <= segs <= MAX_SECS):
                    continue
                os.replace(wav, os.path.join(DEST, f"{destino_tallo}.wav"))
                elegidos.append((nombre, destino_tallo, segs, bytes_))
        if not elegidos:
            sys.exit(f"sin clip válido para {evento} en {carpeta}/")
        for nombre, _, _, _ in elegidos:
            usados.add(os.path.join(origen, nombre))
        choices[evento] = elegidos[0][1]
        if len(elegidos) > 1:
            variantes[evento] = [t for _, t, _, _ in elegidos[1:]]
        for nombre, nombre_tallo, segs, bytes_ in elegidos:
            filas.append((evento, nombre_tallo, f"{segs:.2f}s", f"{bytes_ // 1024}KB", nombre))

    activacion = activacion_abuela(filas)
    sesion_nueva = nueva_sesion(filas, usados)

    seleccion = {
        "schema": "gentle-emote-arcade.sounds/v1",
        "soundsDir": "sounds/gentle",
        "choices": choices,
        "variantes": variantes,
        # Activación del easter egg (no es un evento de la suite): la mejor toma de
        # «abuela» del corpus. `coin.wav` queda sólo como fallback del comando si
        # el pack no define ninguna.
        "activacionVariantes": activacion,
        # Frase del cartel "✓ New session started" (evento propio de Pi, no de la suite).
        "nuevaSesion": sesion_nueva,
    }
    with open(os.path.join(DEST, "seleccion.json"), "w", encoding="utf-8") as fh:
        json.dump(seleccion, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    for evento, tallo, segs, kb, nombre in filas:
        print(f"{evento:22s} {tallo:17s} {segs:>6s} {kb:>6s}  {nombre}")
    extra = sum(len(v) for v in variantes.values())
    print(f"\n{len(choices)} eventos + {extra} variantes -> {DEST}/seleccion.json")
    print(f"activación: {', '.join(activacion)}")
    print(f"sesión nueva: {', '.join(sesion_nueva) or '-'}")


if __name__ == "__main__":
    main()
