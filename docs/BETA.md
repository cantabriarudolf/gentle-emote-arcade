# BETA — estado y checklist de publicación

Última verificación: 2026-11-07, sobre el árbol sin `.git` (repo todavía no
inicializado). Corte de esta versión: **beta AoE publicable** — entran los
dibujos del set `aoe`/`aoe-yolo` y los 13 wav configurados de `sounds/`; el
resto del material de trabajo queda afuera por `.gitignore` (sigue en disco).

## Resumen

- **`aoe` está en beta**: `hi`, `think` e `idle` ya son frames nuevos 48×40 de
  dos poses. `tool` y `success` siguen con un frame placeholder y se rehacen.
- **`aoe-yolo` está generado** desde `aoe` (gemelo YOLO / Super-YOLO).
- **`starcraft`, `lol`, `cs16` (+ sus `-yolo`) están en desarrollo**: solo
  `emotes.json`, cero frames. **`minecraft` es el próximo set a sumar**: no
  tiene nada todavía.
- **Audio AoE publicado**: 13 wav únicos + `sounds/seleccion.json` con 14
  eventos mapeados.
- **Fuera del repo**: 60 mp3 crudos (`datas/`), 60 previews y recortes
  (`previews/`), 1 JPG crudo de referencia, y `lab/` + `test/` del workspace.

## Propósito del audio

El objetivo no es decorar: es **entender auditivamente qué hace el agente** sin
mirar la pantalla. Cada evento de Gentle Shell tiene un sonido de AoE que se
entiende en el juego (aldeano que aparece, monje que empieza a convertir,
`wololo` del subagente, campana del pueblo cuando el contexto se llena). El
detalle del porqué, evento por evento, está en
[`MAPA-ESCENAS.md`](MAPA-ESCENAS.md).

## Estado por set

| Set | Frames | `emotes.json` | Estado |
|---|---|---|---|
| `aoe` | 33 PNG en 24 carpetas | sí | **beta** |
| `aoe-yolo` | 33 PNG en 24 carpetas | sí (idéntico a `aoe`) | generado, hereda |
| `starcraft` / `starcraft-yolo` | 0 | sí | en desarrollo |
| `lol` / `lol-yolo` | 0 | sí | en desarrollo |
| `cs16` / `cs16-yolo` | 0 | sí | en desarrollo |
| `minecraft` / `minecraft-yolo` | 0 | no | a sumar |

## Frames de `aoe` (33 PNG)

| Estado | Frames | Situación |
|---|---|---|
| `hi` | `hi_01.png`, `hi_02.png` | **nuevo** 48×40 |
| `think` | `think_01.png`, `think_02.png` | **nuevo** 48×40 |
| `idle` | `idle.png`, `idle_blink.png` | **nuevo** 48×40 (aldeano); `blink` es el mismo bitmap que `idle` (parpadeo pendiente) |
| `talk` | `talk_close`, `talk_small`, `talk_mid`, `talk_wide`, `talk` | 5 bocas con pesos; `talk_mid` es idéntico a `talk` |
| `yolo`, `super-yolo` | 2 + 2 | heredados; `*_blink` copia de `idle` |
| **`tool`** | `tool.png` | **a rehacer**: 1 placeholder (ariete) |
| **`success`** | `success.png` | **a rehacer**: 1 placeholder (monje + convertido) |
| `ask`, `build`, `bye`, `compact`, `delegate`, `explore`, `failure`, `grandma`, `jira`, `jobs`, `judge`, `read`, `remember`, `review`, `verify`, `write` | 1 c/u | placeholder de una pose: falta la tanda de 2 poses |

Referencia de la tanda completa de las 24 escenas:
[`../antigravity-pack/TANDA.md`](../antigravity-pack/TANDA.md).

## Audio publicado (`sounds/`)

| Evento | Archivo | Tamaño |
|---|---|---|
| `session.started`, `subagent.completed` | `aldeanospawn.wav` | 250 078 B |
| `agent.started` | `priestconversion.wav` | 364 622 B |
| `agent.completed` | `priestconverted.wav` | 534 632 B |
| `agent.failed` | `rogan.wav` | 102 732 B |
| `agent.cancelled` | `malesounddeath5.wav` | 235 086 B |
| `agent.attention` | `attack.wav` | 371 458 B |
| `subagent.queued` | `farmexhausted.wav` | 238 878 B |
| `subagent.running` | `wololo.wav` | 66 894 B |
| `subagent.waiting` | `interface-population-limit.wav` | 97 146 B |
| `subagent.failed` | `generic-male-death3.wav` | 166 258 B |
| `subagent.cancelled` | `generic-female-death3.wav` | 60 276 B |
| `subagent.timed_out` | `generic-siege-weapon-death.wav` | 143 226 B |
| `context.high` | `interface-town-bell1.wav` | 272 244 B |

- 13 archivos para 14 eventos: `aldeanospawn` cubre dos, no hay wav duplicado.
- Total: 2 903 530 B (~2,77 MiB) + `seleccion.json` (2 130 B).
- Formato (leído con `file`): RIFF/WAVE PCM 16 bit; 11 archivos estéreo
  44 100 Hz, `rogan` estéreo 48 000 Hz y `wololo` mono 22 050 Hz. Se
  normalizan en la config de audio, no acá.
- `seleccion.json` tiene dos formas del mismo mapeo: `choices` (evento →
  nombre sin extensión, portable) y `events` + `audioDir` (rutas absolutas de
  la máquina donde se generó). Publicar no lo hace portable por sí solo:
  reescribir las rutas `file:` o regenerarlo desde el lab es paso aparte.

### La selección todavía no está aplicada en la config viva

`sounds/seleccion.json` es la selección **v2** (carpeta `waw/v2`). La config de
notificaciones de Gentle Shell
(`~/.gentle-shell/config/gentle-ai/notifications.json`) hoy sigue apuntando a
los archivos de `waw/` (v1) para 11 eventos. Aplicar la v2 es un paso aparte,
con backup, y no lo hizo este corte.

## Verificación observada

### 1. Copia de los 13 wav + `seleccion.json`

```bash
cd AoE
mkdir -p gentle-emote-arcade/sounds
cp -p sounds/*.wav sounds/seleccion.json gentle-emote-arcade/sounds/
```

Comparación `md5sum` origen vs. copia, uno por uno: **14/14 OK** (13 wav +
`seleccion.json`), sin diferencias de bytes.

### 2. Frames nuevos

```bash
ls emotes/aoe/hi emotes/aoe/think
# emotes/aoe/hi: hi_01.png hi_02.png
# emotes/aoe/think: think_01.png think_02.png
```

Formato de los frames en entrega (IHDR leído con `struct`):

| Archivo | Tamaño | Bit depth | Color type | Interlace |
|---|---|---|---|---|
| `emotes/aoe/hi/hi_01.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/hi/hi_02.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/think/think_01.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/think/think_02.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/idle/idle.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/idle/idle_blink.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/tool/tool.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |
| `emotes/aoe/success/success.png` | 48×40 | 8 | 6 (RGBA) | 0 (no) |

`aoe-yolo` comparte bytes con `aoe` en `hi/*`, `think/*` e `idle/*` (mismos
md5); el resto lo dibuja con `yolo=True`.

### 3. `.gitignore` sobre el árbol real

Se verificó con un repo git descartable en `/tmp` (índice vacío, el `.git` del
proyecto no existe todavía) recorriendo los 232 archivos en disco:

| Grupo | Archivos | Resultado |
|---|---|---|
| `sounds/` (13 wav + `seleccion.json`) | 14 | **entran** |
| `emotes/aoe` + `emotes/aoe-yolo` | 66 PNG + json/yaml | **entran** |
| `docs/`, `scripts/`, `antigravity-pack/` (sin refs crudos) | — | **entran** |
| `datas/` | 63 | fuera |
| `previews/` | 60 | fuera |
| `antigravity-pack/refs/raw_idle.jpg` | 1 | fuera |
| `lab/`, `test/` | hipotéticos hoy | fuera por patrón |

Totales: **232 archivos en disco → 108 versionables (2,89 MiB)**, 124 fuera
(4,22 MiB). Los patrones `lab/`, `test/`, `__pycache__/` y `logs/` dan 0
coincidencias hoy: se dejan preventivos porque son artefactos del workspace.

## Qué quedó fuera y por qué

| Patrón | Qué deja afuera hoy | Por qué |
|---|---|---|
| `datas/` | 63 archivos: 60 mp3 de MyInstants + 3 `README.txt` (~3,3 MB) | material crudo de recopilación; el entregable es `sounds/` (13 wav). Los mp3 son muchos, con nombres de origen y cambian con cada tanda |
| `previews/` | 60 archivos (~944 KB): 51 previews ×8 + 9 recortes de trabajo | imágenes de revisión, no frames del plugin. Incluye copias equivocadas (`compact_01_preview.png` = `think_01_preview.png`) y previews de entregas que no se instalaron (`tool_01/02`, `success_01/02`) |
| `antigravity-pack/refs/*.jpg` | `raw_idle.jpg` (327 531 B, 1024×1024) | fuente cruda de referencia del brief de arte; la entrega es PNG 48×40 |
| `lab/`, `test/` | nada dentro del repo | son del workspace (lab de sonidos y banco de pruebas de frames); no son parte del plugin |
| `__pycache__/`, `*.pyc`, `logs/`, `*.log` | nada todavía | aparecen al correr `scripts/sprites/` o al depurar |
| `*~`, `*.bak`, `*.orig`, `*.rej`, `*.tmp`, `* copy.*`, `* Copy.*`, `*(1).*`, `*(2).*` | nada todavía | duplicados por nombre, nunca contenido |

Consecuencias documentadas de estos recortes:

- Los previews de `tool` y `success` (`previews/tool_01_preview.png`,
  `tool_02`, `success_01`, `success_02`) quedan **solo en disco local**. Al
  retomar esas dos escenas hay que mirarlos ahí antes de redibujar.
- `antigravity-pack/LEEME.md` lista `refs/raw_idle.jpg` como fuente de detalle;
  en el repo publicado ese archivo no está (`refs/idle.png` sí).
- Los `README.txt` por juego que describen la recopilación de mp3 no se
  publican: la trazabilidad queda en `docs/MAPA-ESCENAS*.md` y en
  `sounds/seleccion.json`.

## Duplicados conocidos (no se ignoran a propósito)

Archivos con bytes idénticos que **sí se publican**, porque ignorarlos
rompería sets o documentación:

| Grupo | Archivos | Por qué queda |
|---|---|---|
| Mapa AoE ×3 | `docs/MAPA-ESCENAS.md`, `docs/MAPA-ESCENAS-aoe.md`, `antigravity-pack/MAPA-ESCENAS-aoe.md` | `-aoe.md` es copia para el pack de arte; el nombre plano es el que enlaza el README |
| Ref base | `antigravity-pack/refs/idle.png` = `emotes/aoe/idle/idle.png` | el brief de arte necesita la referencia en su carpeta |
| Parpadeo | `idle_blink.png`, `yolo_blink.png`, `super-yolo_blink.png` = `idle.png` | el plugin espera esos nombres; falta dibujar el parpadeo real |
| Boca neutra | `talk_mid.png` = `talk.png` en cada set | pesos de `talk` en `emotes.json` |
| Audio entre eventos | `aldeanospawn.wav` para `session.started` y `subagent.completed` | es un archivo, dos eventos: no se duplica el wav |

El `.gitignore` solo excluye **duplicados por nombre** (copias/backups), nunca
contenido.

## Antes de pushear (decisiones que no toma este paso)

1. **Repo**: `git init` en `gentle-emote-arcade/`, revisar
   `git status --short` y confirmar que la lista coincide con los 108 archivos
   de acá. El árbol sigue sin `.git`; no se creó ni se pusheó nada.
2. **Licencia**: no hay `LICENSE`. Sin una, el repo queda "todos los derechos
   reservados" por defecto; elegir una si se quiere código reutilizable.
3. **Remoto**: crear el repo (o el fork de `efolchmontiel/gentle-emote`) y
   apuntar `origin`. Decidir si se publica como fork o como repo independiente
   con el crédito en el README.
4. **Aplicar el audio v2**: reescribir las rutas `file:` de `sounds/seleccion.json`
   a una carpeta estable y aplicarlas a
   `~/.gentle-shell/config/gentle-ai/notifications.json` con backup. Hoy la
   config viva apunta a `waw/` (v1).
5. **`antigravity-pack/`**: se publica como documentación del pipeline, con el
   `LEEME.md` aclarando que `refs/raw_idle.jpg` no viaja en el repo.

## Pendientes de arte

- `tool`: ariete + aldeanos, 2 poses (01 ariete atrás, 02 adelante).
- `success`: monje + unidad convertida de rodillas, 2 poses.
- Completar las 16 escenas que hoy tienen una sola pose (ver `TANDA.md`).
- `idle_blink` real (hoy es copia de `idle`).
- `emotes.json`: `tool` y `success` están en `cycle: loop`; si quedan de 2
  poses, revisar `frameMs` (`tool` 260 ms, `success` 420 ms).
- Sets `starcraft`, `lol`, `cs16`: faltan los frames; `emotes.json` ya está.
- `minecraft`: falta todo (set, `emotes.json`, mapa de escenas y audio).

---
Powered by Gentle Shell
