#!/usr/bin/env python3
"""Modo demo por juego: la serie completa de las 24 escenas, frame por frame.

Sirve una página local (`docs/demo/index.html`) con un selector de juego, una
grilla de viñetas animadas y un modo «serie completa» que muestra todos los
frames de todos los estados. Los PNG se sirven **crudos** tal como están en
`emotes/<juego>/<estado>/`; el navegador los escala ×4 por CSS con
`image-rendering: pixelated`.

Rutas:
- `/` y `/index.html`  -> `docs/demo/index.html`
- `/api/juegos`        -> catálogo JSON (juegos, estados, frames y playback)
- `/img/<juego>/<estado>/<frame>.png` -> PNG crudo (whitelist del catálogo)
- `/api/refs` -> referencias subidas por estado
- `/ref/<juego>/<estado>/<archivo>` -> referencia subida (solo lectura)
- `POST /ref/<juego>/<estado>` -> sube la foto de referencia del estado (png/jpg/webp/gif, máx 3 MB)

El playback (loop/pingpong y milisegundos por frame) sale de `emotes.json` de
cada juego. Si un estado no trae entrada, se usan 500 ms y loop.

La etiqueta humana de cada estado (la viñeta de acción) se lee en el momento
de `docs/MAPA-ESCENAS-aoe.md`: no se duplica en el código.

Solo stdlib. Uso (desde cualquier carpeta):
    python3 gentle-emote-arcade/scripts/scenes_demo.py
    python3 gentle-emote-arcade/scripts/scenes_demo.py --port 0
    python3 gentle-emote-arcade/scripts/scenes_demo.py --check
    python3 gentle-emote-arcade/scripts/scenes_demo.py --emotes-dir /tmp/sets

Códigos de salida: 0 ok, 2 error de datos.
"""

import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlparse

# scenes_gallery es la fuente única de las 24 escenas y del decodificador PNG:
# se importa en lectura, no se modifica desde acá.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scenes_gallery import GalleryError, SCALE, SCENES, read_png  # noqa: E402

DEFAULT_FRAME_MS = 500
DEFAULT_CYCLE = "loop"
VALID_CYCLES = ("loop", "pingpong")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_EMOTES = os.path.join(REPO_ROOT, "emotes")
DEFAULT_INDEX = os.path.join(REPO_ROOT, "docs", "demo", "index.html")
DEFAULT_MAPA = os.path.join(REPO_ROOT, "docs", "MAPA-ESCENAS-aoe.md")
DEFAULT_REFS = os.path.join(REPO_ROOT, "docs", "refs")
DEFAULT_PORT = 8785

IMG_PREFIX = "/img/"
REF_PREFIX = "/ref/"
MAX_REF_BYTES = 3 * 1024 * 1024


class DemoError(Exception):
    """Error de datos: set incompleto, PNG inválida o mapa sin etiqueta."""


def display_path(path):
    """Ruta relativa al repo cuando cae adentro; absoluta si no."""
    try:
        rel = os.path.relpath(path, REPO_ROOT)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel


def load_labels(mapa_path):
    """Devuelve {estado: {"label", "sprite"}} desde la tabla del mapa AoE."""
    try:
        with open(mapa_path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        raise DemoError("no se pudo leer el mapa %s: %s" % (mapa_path, exc))

    labels = {}
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        cell = cells[1]
        if not (cell.startswith("`") and cell.endswith("`")):
            continue
        state = cell.strip("`")
        if state not in SCENES or state in labels:
            continue
        if not cells[2] or not cells[4]:
            continue
        labels[state] = {"label": cells[2], "sprite": cells[4]}

    missing = [state for state in SCENES if state not in labels]
    if missing:
        raise DemoError("el mapa %s no tiene viñeta para: %s"
                        % (mapa_path, ", ".join(missing)))
    return labels


def playback(emotes_json, state, game):
    """(cycle, frameMs) del estado; defaults si emotes.json no lo lista."""
    cycles = emotes_json.get("cycle") or {}
    frame_ms = emotes_json.get("frameMs") or {}
    if not isinstance(cycles, dict) or not isinstance(frame_ms, dict):
        raise DemoError("%s: cycle/frameMs de emotes.json no son objetos"
                        % game)
    cycle = cycles.get(state, DEFAULT_CYCLE)
    if cycle not in VALID_CYCLES:
        raise DemoError("%s: cycle inválido en %s: %r"
                        % (game, state, cycle))
    ms = frame_ms.get(state, DEFAULT_FRAME_MS)
    if isinstance(ms, bool) or not isinstance(ms, (int, float)) or ms <= 0:
        raise DemoError("%s: frameMs inválido en %s: %r" % (game, state, ms))
    return cycle, int(ms)


def game_frames(game, game_dir):
    """Valida el set y devuelve {estado: [(frame, ancho, alto), ...]}."""
    try:
        with open(os.path.join(game_dir, "emotes.json"), encoding="utf-8") as fh:
            emotes_json = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise DemoError("emotes.json ilegible: %s" % exc)
    if not isinstance(emotes_json, dict):
        raise DemoError("emotes.json no es un objeto JSON")

    present = {name for name in os.listdir(game_dir)
               if os.path.isdir(os.path.join(game_dir, name))}
    missing = [state for state in SCENES if state not in present]
    extra = sorted(present - set(SCENES))
    if missing:
        raise DemoError("faltan estados: " + ", ".join(missing))
    if extra:
        raise DemoError("estados fuera de SCENES: " + ", ".join(extra))

    frames = {}
    for state in SCENES:
        state_dir = os.path.join(game_dir, state)
        names = sorted(name for name in os.listdir(state_dir)
                       if name.lower().endswith(".png")
                       and os.path.isfile(os.path.join(state_dir, name)))
        if not names:
            raise DemoError("%s: el estado %s no tiene frames PNG"
                            % (game, state))
        entries = []
        for name in names:
            try:
                width, height, _ = read_png(os.path.join(state_dir, name))
            except GalleryError as exc:
                raise DemoError("%s/%s/%s: %s" % (game, state, name, exc))
            entries.append((name, width, height))
        frames[state] = entries
    return emotes_json, frames


def build_catalog(emotes_dir, mapa_path):
    """Arma el catálogo JSON que consume docs/demo/index.html."""
    if not os.path.isdir(emotes_dir):
        raise DemoError("no existe la carpeta de sets: %s" % emotes_dir)
    labels = load_labels(mapa_path)

    games = []
    skipped = []
    for game in sorted(os.listdir(emotes_dir)):
        game_dir = os.path.join(emotes_dir, game)
        if not os.path.isdir(game_dir):
            continue
        if game.startswith(".") or game.endswith(".bak"):
            continue
        if not os.path.isfile(os.path.join(game_dir, "emotes.json")):
            continue
        try:
            emotes_json, frames = game_frames(game, game_dir)
        except DemoError as exc:
            skipped.append({"game": game, "reason": str(exc)})
            continue

        clips = []
        for state in SCENES:
            cycle, frame_ms = playback(emotes_json, state, game)
            clip_frames = [{
                "file": name,
                "url": "%s%s/%s/%s" % (IMG_PREFIX, quote(game, safe=""),
                                       quote(state, safe=""),
                                       quote(name, safe="")),
                "w": width,
                "h": height,
            } for name, width, height in frames[state]]
            clips.append({
                "state": state,
                "label": labels[state]["label"],
                "sprite": labels[state]["sprite"],
                "cycle": cycle,
                "frameMs": frame_ms,
                "frames": clip_frames,
            })

        games.append({
            "game": game,
            "totalFrames": sum(len(clip["frames"]) for clip in clips),
            "clips": clips,
        })

    if not games:
        raise DemoError("no hay sets completos en %s" % emotes_dir)
    return {
        "scale": SCALE,
        "mapa": display_path(mapa_path),
        "games": games,
        "skipped": skipped,
    }


def frame_keys(catalog):
    """(juego, estado, frame) válidos: la whitelist del servidor."""
    keys = set()
    for game in catalog["games"]:
        for clip in game["clips"]:
            for frame in clip["frames"]:
                keys.add((game["game"], clip["state"], frame["file"]))
    return keys


def check_frame_parts(parts):
    """Los tres segmentos de /img/ deben ser basenames simples y no vacíos."""
    if len(parts) != 3:
        return False
    for part in parts:
        if not part or part != os.path.basename(part) or part in (".", ".."):
            return False
        if "\x00" in part:
            return False
    return True


def ref_tipo(body):
    """(extensión, content-type) por magic bytes, o (None, None)."""
    if body[:8] == b"\x89PNG\r\n\x1a\n":
        return ("png", "image/png")
    if body[:3] == b"\xff\xd8\xff":
        return ("jpg", "image/jpeg")
    if body[:4] == b"RIFF" and body[8:12] == b"WEBP":
        return ("webp", "image/webp")
    if body[:6] in (b"GIF87a", b"GIF89a"):
        return ("gif", "image/gif")
    return (None, None)


def ref_pares_validos(catalog):
    """(juego, estado) existentes en el catálogo."""
    pares = set()
    for game in catalog["games"]:
        for clip in game["clips"]:
            pares.add((game["game"], clip["state"]))
    return pares


class Handler(BaseHTTPRequestHandler):
    server_version = "EmoteScenesDemo/1.0"

    catalog = None
    frame_keys = frozenset()
    emotes_dir = DEFAULT_EMOTES
    index_path = DEFAULT_INDEX
    refs_dir = DEFAULT_REFS

    def log_message(self, fmt, *args):  # consola limpia, como el lab
        pass

    def _send(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if self.command == "HEAD":
            return
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def _send_index(self):
        try:
            with open(self.index_path, "rb") as fh:
                body = fh.read()
        except OSError:
            self._send(500, b"falta docs/demo/index.html\n",
                       "text/plain; charset=utf-8")
            return
        self._send(200, body, "text/html; charset=utf-8")

    def _send_image(self, path):
        parts = path[len(IMG_PREFIX):].split("/")
        if not check_frame_parts(parts):
            self._json(400, {
                "error": "ruta inválida: /img/<juego>/<estado>/<frame>.png"})
            return
        game, state, name = parts
        if not name.lower().endswith(".png"):
            self._json(400, {"error": "solo se sirven frames .png"})
            return
        if (game, state, name) not in self.frame_keys:
            self._json(404, {"error": "frame desconocido: %s/%s/%s"
                                      % (game, state, name)})
            return
        target = os.path.join(self.emotes_dir, game, state, name)
        try:
            with open(target, "rb") as fh:
                body = fh.read()
        except OSError as exc:
            self._json(404, {"error": "no se pudo leer el frame: %s" % exc})
            return
        self._send(200, body, "image/png")

    def _api_refs(self):
        items = []
        pares = ref_pares_validos(self.catalog)
        try:
            juegos = sorted(os.listdir(self.refs_dir))
        except OSError:
            juegos = []
        for game in juegos:
            dir_juego = os.path.join(self.refs_dir, game)
            if not os.path.isdir(dir_juego):
                continue
            for state in sorted(os.listdir(dir_juego)):
                if (game, state) not in pares:
                    continue
                d = os.path.join(dir_juego, state)
                if not os.path.isdir(d):
                    continue
                for name in sorted(os.listdir(d)):
                    if not os.path.isfile(os.path.join(d, name)):
                        continue
                    items.append({
                        "game": game, "state": state, "file": name,
                        "url": "%s%s/%s/%s" % (
                            REF_PREFIX, quote(game, safe=""),
                            quote(state, safe=""), quote(name, safe=""))})
        self._json(200, {"refs": items})

    def _send_ref(self, path):
        parts = path[len(REF_PREFIX):].split("/")
        if not check_frame_parts(parts):
            self._json(400, {"error": "ruta inválida: "
                                      "/ref/<juego>/<estado>/<archivo>"})
            return
        game, state, name = parts
        ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        tipos = {"png": "image/png", "jpg": "image/jpeg",
                 "jpeg": "image/jpeg", "webp": "image/webp",
                 "gif": "image/gif"}
        if ext not in tipos:
            self._json(400, {"error": "solo imágenes png/jpg/webp/gif"})
            return
        if (game, state) not in ref_pares_validos(self.catalog):
            self._json(404, {"error": "juego/estado desconocido"})
            return
        base = os.path.realpath(self.refs_dir)
        target = os.path.realpath(os.path.join(base, game, state, name))
        if not target.startswith(base + os.sep):
            self._json(400, {"error": "ruta fuera de refs"})
            return
        try:
            with open(target, "rb") as fh:
                body = fh.read()
        except OSError:
            self._json(404, {"error": "referencia inexistente"})
            return
        self._send(200, body, tipos[ext])

    def _recv_ref(self, path):
        parts = path[len(REF_PREFIX):].split("/")
        if (len(parts) != 2 or any(not seg or seg != os.path.basename(seg)
                                   or seg in (".", "..") or "\x00" in seg
                                   for seg in parts)):
            self._json(400, {"error": "ruta inválida: POST "
                                      "/ref/<juego>/<estado> con la imagen "
                                      "en el cuerpo"})
            return
        game, state = parts
        if (game, state) not in ref_pares_validos(self.catalog):
            self._json(404, {"error": "juego/estado desconocido"})
            return
        try:
            largo = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            largo = 0
        if largo <= 0 or largo > MAX_REF_BYTES:
            self._json(413, {"error": "cuerpo vacío o mayor a 3 MB"})
            return
        try:
            body = self.rfile.read(largo)
        except OSError:
            self._json(400, {"error": "no se pudo leer el cuerpo"})
            return
        if len(body) != largo:
            self._json(400, {"error": "cuerpo incompleto"})
            return
        ext, _ctype = ref_tipo(body)
        if ext is None:
            self._json(415, {"error": "solo imágenes png/jpg/webp/gif"})
            return
        d = os.path.join(self.refs_dir, game, state)
        try:
            os.makedirs(d, exist_ok=True)
        except OSError as exc:
            self._json(500, {"error": "no se pudo crear la carpeta: %s" % exc})
            return
        n = sum(1 for x in os.listdir(d) if x.startswith("ref_")) + 1
        while os.path.exists(os.path.join(d, "ref_%02d.%s" % (n, ext))):
            n += 1
        name = "ref_%02d.%s" % (n, ext)
        tmp = os.path.join(d, ".tmp-" + name)
        try:
            with open(tmp, "wb") as fh:
                fh.write(body)
            os.replace(tmp, os.path.join(d, name))
        except OSError as exc:
            self._json(500, {"error": "no se pudo guardar: %s" % exc})
            return
        self._json(200, {"ok": True, "game": game, "state": state,
                         "file": name,
                         "url": "%s%s/%s/%s" % (
                             REF_PREFIX, quote(game, safe=""),
                             quote(state, safe=""), quote(name, safe=""))})

    def do_POST(self):  # noqa: N802
        path = unquote(urlparse(self.path).path)
        if path.startswith(REF_PREFIX):
            self._recv_ref(path)
        else:
            self._json(404, {"error": "ruta desconocida: %s" % path})

    def do_GET(self):  # noqa: N802
        path = unquote(urlparse(self.path).path)
        if path in ("/", "/index.html"):
            self._send_index()
        elif path == "/api/juegos":
            self._json(200, self.catalog)
        elif path == "/api/refs":
            self._api_refs()
        elif path.startswith(REF_PREFIX):
            self._send_ref(path)
        elif path.startswith(IMG_PREFIX):
            self._send_image(path)
        else:
            self._json(404, {"error": "ruta desconocida: %s" % path})

    def do_HEAD(self):  # noqa: N802
        self.do_GET()


def print_check(catalog, index_path, refs_dir=None):
    print("demo: %d juego(s), %d frame(s), %d estado(s)"
          % (len(catalog["games"]), sum(g["totalFrames"]
                                        for g in catalog["games"]),
             len(SCENES)))
    for game in catalog["games"]:
        estados = len(game["clips"])
        if estados != len(SCENES):
            print("error: %s tiene %d estados" % (game["game"], estados),
                  file=sys.stderr)
            return 1
        print("  %-16s %3d frames" % (game["game"], game["totalFrames"]))
    for item in catalog["skipped"]:
        print("error: %s omitido (%s)" % (item["game"], item["reason"]),
              file=sys.stderr)
        return 1
    if not os.path.isfile(index_path):
        print("error: falta el HTML del demo: %s" % index_path, file=sys.stderr)
        return 1
    print("mapa: %s" % catalog["mapa"])
    if refs_dir is not None:
        total_refs = sum(len(ficheros) for _, _, ficheros
                         in os.walk(refs_dir)) if os.path.isdir(refs_dir) else 0
        print("refs: %d archivo(s) en %s" % (total_refs, refs_dir))
    print("html: %s" % display_path(index_path))
    print("check: ok")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Modo demo por juego: sirve docs/demo/index.html, el "
                    "catálogo /api/juegos y los PNG crudos de "
                    "emotes/<juego>/<estado>/ en /img/. El navegador escala "
                    "×4 por CSS (image-rendering: pixelated).",
        epilog="Códigos de salida: 0 ok, 2 error de datos.")
    parser.add_argument("--host", default="127.0.0.1",
                        help="interfaz de escucha (por defecto 127.0.0.1)")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help="puerto TCP; 0 elige uno libre (por defecto %d)"
                             % DEFAULT_PORT)
    parser.add_argument("--emotes-dir", default=DEFAULT_EMOTES,
                        help="carpeta de sets (por defecto emotes/ del repo)")
    parser.add_argument("--index", default=DEFAULT_INDEX,
                        help="HTML del demo (por defecto docs/demo/index.html)")
    parser.add_argument("--mapa", default=DEFAULT_MAPA,
                        help="mapa con las viñetas de acción "
                             "(por defecto docs/MAPA-ESCENAS-aoe.md)")
    parser.add_argument("--refs-dir", default=DEFAULT_REFS,
                        help="carpeta de fotos de referencia "
                             "(por defecto docs/refs/)")
    parser.add_argument("--check", action="store_true",
                        help="valida sets, mapa y HTML; no sirve")
    args = parser.parse_args(argv)

    try:
        catalog = build_catalog(args.emotes_dir, args.mapa)
    except DemoError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2

    if args.check:
        return 2 if print_check(catalog, args.index, args.refs_dir) else 0

    if not os.path.isfile(args.index):
        print("error: falta el HTML del demo: %s" % args.index,
              file=sys.stderr)
        return 2

    Handler.catalog = catalog
    Handler.frame_keys = frozenset(frame_keys(catalog))
    Handler.emotes_dir = args.emotes_dir
    Handler.index_path = args.index
    Handler.refs_dir = args.refs_dir
    try:
        httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    except OSError as exc:
        print("error: no se pudo escuchar en %s:%d: %s"
              % (args.host, args.port, exc), file=sys.stderr)
        return 2

    host, port = httpd.server_address[:2]
    print("demo en http://%s:%d  (%d juegos, %d frames, ×%d por CSS)"
          % (host, port, len(catalog["games"]),
             sum(game["totalFrames"] for game in catalog["games"]),
             catalog["scale"]), flush=True)
    print("Ctrl-C para detener", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("detenido", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
