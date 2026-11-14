# Set `aoe-yolo` — gemelo YOLO de `aoe`

> **Este set se genera. No editar los PNG a mano.**

`aoe-yolo` es el gemelo de [`../aoe/`](../aoe/) para modo YOLO / Super-YOLO:
misma tabla de 24 escenas, mismos nombres de archivo, mismos tiempos.
El plugin lo elige solo mientras YOLO está activo (`findYoloSetDir` en
`src/emotes.ts`); si la carpeta no existe, cae al set base sin error.

## Cómo se usa

En `config.json` del plugin, para forzarlo a mano:

```json
{ "emotes": [{ "model": "*", "emote-set": "aoe-yolo" }] }
```

## Cómo se regenera

Cada estado lo dibuja un generador distinto. Solo dos aceptan `--set`, y
`gen_aoe_yolo.py` encadena esos dos:

```bash
cd <workspace>/AoE
python3 gentle-emote-arcade/scripts/sprites/gen_aoe_yolo.py
```

| Estados | Generador | ¿Acepta `--set aoe-yolo`? |
|---|---|---|
| `hi`, `idle`, `talk`, `ask`, `success`, `failure`, `bye`, `jobs`, `grandma`, `write` | `gen_aldeano.py` | sí (lo encadena `gen_aoe_yolo.py`) |
| `build`, `jira`, `review` | `gen_build_aoe.py` | sí (lo encadena `gen_aoe_yolo.py`) |
| `delegate`, `judge`, `remember`, `compact`, `verify` | `gen_monje.py` | **no**: escribe con ruta fija a `emotes/aoe` |
| `explore` | `gen_explore_aoe.py` | **no** |
| `yolo`, `super-yolo` | `gen_yolo_aoe.py` | **no** |

Los estados de la columna «no» se espejan copiando el PNG del set base:

```bash
for s in compact verify remember; do
  cp -p emotes/aoe/$s/*.png emotes/aoe-yolo/$s/
done
```

Ese `cp` es la fuente del bug de deriva: hasta que `gen_monje.py`,
`gen_explore_aoe.py` y `gen_yolo_aoe.py` acepten `--set` igual que los otros
dos, regenerar el set base deja el gemelo atrás en silencio.

## Estado actual (verificado 2026-11-14)

- Todo PNG del gemelo es **byte-idéntico** al de `emotes/aoe/`: hoy no hay
  ninguna diferencia de dibujo entre los dos sets.
- Mismos nombres de archivo y mismas 24 carpetas que el set base.
- `emotes.json` idéntico al del set base.
- Falta `ascii.yaml` (existe en `aoe`): sin él, el gemelo no tiene fallback
  ASCII para terminales sin imágenes.

## Reglas para no romper el par

1. Todo cambio de arte va en `aoe` primero; después se replica acá con el
   generador que lo dibuja o copiando el frame.
2. Los nombres de archivo de ambos sets tienen que seguir siendo los mismos:
   el gemelo se instala como set completo, no por estado.
3. Formato obligatorio, igual que el set base: PNG 48×40, 8-bit RGBA, sin
   interlace, alfa real, sin blur ni sombra.

## Relacionado

- [`../../README.md`](../../README.md) — qué es el proyecto e instalación.
- [`../../docs/BETA.md`](../../docs/BETA.md) — estado, verificación y checklist
  de publicación.
- [`../aoe/emotes.json`](../aoe/emotes.json) — timing (`cycle`, `frameMs`).
- `scripts/sprites/gen_aoe_yolo.py` — encadena los generadores con `--set`.
