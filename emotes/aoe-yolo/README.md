# Set `aoe-yolo` — gemelo YOLO de `aoe`

> **Este set se genera. No editar los PNG a mano.**

`aoe-yolo` es el gemelo de [`../aoe/`](../aoe/) para modo YOLO / Super-YOLO:
misma tabla de 24 escenas, mismos nombres de archivo, misma estructura de
carpetas. La única diferencia es que el aldeano lleva la franja magenta de
YOLO en la cara (filas 13-14 del sprite) y los estados `yolo` / `super-yolo`
dibujan el marcador extra.

## Cómo se usa

En `config.json` del plugin:

```json
{ "emotes": [{ "model": "*", "emote-set": "aoe-yolo" }] }
```

## Cómo se regenera

Lo genera `scripts/sprites/gen_aoe_yolo.py` a partir del generador del set
base, sin duplicar código: lee `gen_aoe_final.py`, le aplica reemplazos de
texto y escribe la versión parcheada en `/tmp/gen_yolo2.py`.

| Reemplazo | Efecto |
|---|---|
| `base_dir="…/emotes/aoe"` → `…/emotes/aoe-yolo` | escribe en este set |
| inyecta `kw=dict(kw); kw["yolo"]=True` en el loop de estados | todos los estados con franja YOLO |
| agrega `yolo=True` a las llamadas de `talk` e `idle` | bocas y parpadeo con franja |
| agrega un `pass` en el loop de `talk` | mantiene el cuerpo indentado válido |

Pasos, desde la raíz del workspace AoE (los scripts usan rutas relativas):

```bash
cd <workspace>/AoE
python3 gentle-emote-arcade/scripts/sprites/gen_aoe_yolo.py
python3 /tmp/gen_yolo2.py
```

`gen_aoe_yolo.py` **no ejecuta** el generador parcheado: solo lo deja escrito
en `/tmp/gen_yolo2.py`. Si no corrés el segundo comando, no se regenera nada.

## Estado actual (verificado)

- 33 PNG en 24 carpetas: los mismos nombres que `emotes/aoe/`.
- `emotes.json` es **byte-idéntico** al de `aoe` (y al de todos los sets):
  `md5 92e3741fa2f0eb6bc2b0f6451a4a2a8c`.
- Idénticos byte a byte con `aoe`: `hi/hi_01.png`, `hi/hi_02.png`,
  `idle/idle.png`, `idle/idle_blink.png`, `think/think_01.png`,
  `think/think_02.png`, `yolo/*`, `super-yolo/*`. Son frames **copiados** del
  set base, no regenerados con `yolo=True`; por eso `idle` todavía no tiene
  la franja magenta.
- Distintos de `aoe` (dibujados con `yolo=True`): `ask`, `build`, `bye`,
  `compact`, `delegate`, `explore`, `failure`, `grandma`, `jira`, `jobs`,
  `judge`, `read`, `remember`, `review`, `success`, `talk/*`, `tool`,
  `verify`, `write`.
- Falta `ascii.yaml` (existe en `aoe`): sin él, el gemelo no tiene fallback
  ASCII para terminales sin imágenes.

## Reglas para no romper el par

1. Todo cambio de arte va en `aoe` primero; después se replica acá con el
   generador o copiando el frame y marcándolo con la franja YOLO.
2. Los nombres de archivo de ambos sets tienen que seguir siendo los mismos:
   el gemelo se instala como set completo, no por estado.
3. `tool` y `success` heredan el pendiente del set base (una pose placeholder
   cada uno): rehacerlos en `aoe` y regenerar.
4. **No correr el generador ahora sin querer regenerar todo**: escribiría
   `idle.png` / `idle_blink.png` con franja YOLO (pisando los actuales),
   reescribiría `talk`, `tool`, `success` y `yolo` / `super-yolo`, y agregaría
   placeholders de un frame `hi.png` y `think.png` al lado de las poses nuevas
   `hi_01`/`hi_02` y `think_01`/`think_02`. Esperar a cerrar la tanda de 2
   poses por estado (ver [`../../antigravity-pack/TANDA.md`](../../antigravity-pack/TANDA.md)).
5. Formato obligatorio, igual que el set base: PNG 48×40, 8-bit RGBA, sin
   interlace, alfa real, sin blur ni sombra.

## Relacionado

- [`../../README.md`](../../README.md) — qué es el proyecto e instalación.
- [`../../docs/BETA.md`](../../docs/BETA.md) — estado, verificación y checklist
  de publicación.
- [`../aoe/emotes.json`](../aoe/emotes.json) — timing (`cycle`, `frameMs`).
- `scripts/sprites/gen_aoe_yolo.py` — el generador descripto arriba.
