# BETA — estado y checklist de publicación

Última verificación: 2026-11-08, sobre el árbol de trabajo (repo local `main`,
sin remoto). Corte de esta versión: **beta AoE publicable** — entran los dibujos
del set `aoe`/`aoe-yolo` y los 13 wav configurados de `sounds/aoe/`. Los packs
`minecraft`, `cs16`, `starcraft` y `lol` también están en `sounds/`, pero fuera
de beta: los dos últimos son mp3 sin licencia verificada. El resto del material
de trabajo (60 mp3 de `datas/`, previews, lab) queda afuera por `.gitignore`
(sigue en disco).

## Resumen

- **`aoe` está en beta**: los 24 estados ya son arte propio 48×40 con movimiento (2-4 poses en loop, frames con texto extra en `think`, `failure`, `hi`, `yolo`, `super-yolo`).
- **`aoe-yolo` está generado** desde `aoe` (gemelo YOLO / Super-YOLO).
- **`starcraft`, `lol`, `cs16` (+ sus `-yolo`) están en desarrollo**: solo
  `emotes.json`, cero frames. **`minecraft` es el próximo set a sumar**: no
  tiene nada todavía.
- **Audio**: `aoe` completo (13 wav + `seleccion.json`, 14 eventos);
  `minecraft` (13 mp3) y `cs16` (12 wav) descargados con `seleccion.json`;
  `starcraft` y `lol` curados de `datas/` (14 mp3 cada uno + `seleccion.json`),
  **sin licencia verificada**.
- **Fuera del repo**: 60 mp3 crudos (`datas/`), 60 previews y recortes
  (`previews/`), 1 JPG crudo de referencia, y `lab/` + `test/` del workspace.
  Las copias curadas de `sounds/starcraft/` y `sounds/lol/` sí están en el
  árbol, con la advertencia de licencia de arriba.

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
| `aoe` | 57 PNG en 24 carpetas | sí | **beta** |
| `aoe-yolo` | 57 PNG en 24 carpetas | sí (idéntico a `aoe`) | generado, hereda |
| `starcraft` / `starcraft-yolo` | 0 | sí | en desarrollo |
| `lol` / `lol-yolo` | 0 | sí | en desarrollo |
| `cs16` / `cs16-yolo` | 0 | sí | en desarrollo |
| `minecraft` / `minecraft-yolo` | 0 | no | a sumar |

## Packs de sonido

Todos los juegos tienen su pack en `sounds/<juego>/`: audios con nombres
cortos y un `seleccion.json` portable (schema
`gentle-emote-arcade.sounds/v1`, `soundsDir` relativo y `choices` sin
extensión). Estado al 2026-11-08:

| Juego | Carpeta | Audio | Eventos | `seleccion.json` | Tamaño | Estado |
|---|---|---|---|---|---|---|
| Age of Empires II | `sounds/aoe/` | 13 wav | 14 (1 repetido) | portable | 2,9 MB | **completo** (beta) |
| Minecraft | `sounds/minecraft/` | 13 mp3 | 14 (12 únicos; `piston` sin uso) | portable | 568 KB | descargado, sin probar |
| Counter-Strike 1.6 | `sounds/cs16/` | 12 wav | 14 (12 únicos) | portable | 405 KB | descargado, sin probar |
| StarCraft | `sounds/starcraft/` | 14 mp3 | 14 (1:1) | portable | 408 KB | curado de `datas/starcraft/`, licencia sin verificar |
| League of Legends | `sounds/lol/` | 14 mp3 | 14 (1:1) | portable | 583 KB | curado de `datas/lol/`, licencia sin verificar |

Total: 71 archivos (66 audio + 5 `seleccion.json`), 4 868 629 B (~4,64 MiB).

StarCraft y LoL se curaron **por nombre**: un archivo distinto por evento,
elegido entre los 20 mp3 de cada `datas/`. No hubo escucha crítica ni prueba en
vivo. Los 28 mp3 son copias byte a byte de `datas/` con nombre corto, y no
tienen licencia verificada (ver el aviso del README).

### Mapeo StarCraft (`sounds/starcraft/`)

| Evento | Archivo | Origen en `datas/starcraft/` |
|---|---|---|
| `session.started` | `hell-its-about-time.mp3` | `hell-its-about-time.mp3` |
| `agent.started` | `scv-orders-received.mp3` | `scv-orders-received.mp3` |
| `agent.completed` | `marine-good-to-go.mp3` | `marine-good-to-go.mp3` |
| `agent.failed` | `base-attack.mp3` | `terrain-base-attack.mp3` |
| `agent.cancelled` | `easy-thrusters.mp3` | `easy-thrusters.mp3` |
| `agent.attention` | `need-a-light.mp3` | `need-a-light-firebat.mp3` |
| `subagent.queued` | `orders-captain.mp3` | `orders-captain-scv.mp3` |
| `subagent.running` | `protoss-fighting.mp3` | `protoss-fighting.mp3` |
| `subagent.waiting` | `medic-terrain.mp3` | `medic-terrain.mp3` |
| `subagent.completed` | `operational.mp3` | `starcraft-battlecruiser-quotes-audiotrimmer_YasKSmW.mp3` |
| `subagent.failed` | `life-for-aiur.mp3` | `protoss-life-for-aiur.mp3` |
| `subagent.cancelled` | `exterminator.mp3` | `starcraft-1-ghost-quote-exterminator.mp3` |
| `subagent.timed_out` | `overtime.mp3` | `overtime.mp3` |
| `context.high` | `all-hands.mp3` | `all-hands.mp3` |

### Mapeo League of Legends (`sounds/lol/`)

| Evento | Archivo | Origen en `datas/lol/` |
|---|---|---|
| `session.started` | `first-blood.mp3` | `league-of-legends-first-blood-sound.mp3` |
| `agent.started` | `rammus-ok.mp3` | `league-of-legends-rammus-ok.mp3` |
| `agent.completed` | `penta-kill.mp3` | `league-of-legends-penta-kill-4.mp3` |
| `agent.failed` | `ally-slain.mp3` | `lol-an-ally-has-been-slain.mp3` |
| `agent.cancelled` | `what-was-that-move.mp3` | `faker-what-was-that-move.mp3` |
| `agent.attention` | `missing.mp3` | `missing.mp3` |
| `subagent.queued` | `ping-push.mp3` | `lol-ping-push.mp3` |
| `subagent.running` | `triple-kill.mp3` | `league-of-legends-trible-kill-4.mp3` |
| `subagent.waiting` | `ping-enemy-missing.mp3` | `lol-ping-enemy-missing.mp3` |
| `subagent.completed` | `quadra-kill.mp3` | `lol-quadra-kill-se.mp3` |
| `subagent.failed` | `enemy-penta.mp3` | `enemy-penta.mp3` |
| `subagent.cancelled` | `seraphineult.mp3` | `seraphineult.mp3` |
| `subagent.timed_out` | `defeat.mp3` | `defeat_90KWHvE.mp3` |
| `context.high` | `ping-caution.mp3` | `lol-ping-caution.mp3` |

### Dudas de la curación

- **StarCraft sin candidato literal por nombre**: `agent.cancelled`
  (`easy-thrusters`, «aflojar»), `subagent.waiting` (`medic-terrain`),
  `subagent.cancelled` (`exterminator`) y `subagent.running`
  (`protoss-fighting`). `agent.failed` usa `base-attack`, que es alarma de
  ataque más que fallo.
- **LoL sin candidato literal por nombre**: `agent.cancelled`
  (`what-was-that-move`), `subagent.cancelled` (`seraphineult`),
  `subagent.running` (`triple-kill`) y `subagent.queued` (`ping-push`).
  `subagent.timed_out` usa `defeat`, que es fin de partida, no reloj.
- **No se escuchó ningún archivo**: la curación es solo por nombre. Si un
  sonido no encaja al probarlo en vivo, se cambia el `choices` sin tocar los
  mp3.
- Los nombres de `datas/` no viajan: el `seleccion.json` es la fuente de
  verdad del mapeo y estas dos tablas guardan la trazabilidad.

## Frames de `aoe` (57 PNG, todos con movimiento salvo indicación)

| Estado | Frames | Situación |
|---|---|---|
| `hi` | `hi_01.png`, `hi_02.png`, `hi_03.png` | **nuevo** 48×40; `hi_03` dice HELLO. (frame extra) |
| `think` | `think_01..04.png` | **nuevo** 48×40; cura con WOLOLO (`think_04` con texto, frame extra) |
| `idle` | `idle.png`, `idle_blink.png` | **nuevo** 48×40 (aldeano + parpadeo) |
| `talk` | `talk_close`, `talk_small`, `talk_mid`, `talk_wide` | 4 bocas con pesos |
| `yolo`, `super-yolo` | 3 + 3 | con texto (`yolo_03`, `super-yolo_03`, frames extra) |
| **`tool`** | `tool_01..03.png` | **nuevo** 48×40 (ariete 3 tiempos) |
| **`success`** | `success_01.png`, `success_02.png` | **nuevo** 48×40 (festejo) |
| `ask`, `build`, `bye`, `compact`, `delegate`, `explore`, `failure`, `grandma`, `jira`, `jobs`, `judge`, `read`, `remember`, `review`, `verify`, `write` | 2 c/u (`failure` 3 con ROGAN?) | arte propio con movimiento |

Referencia de la tanda completa de las 24 escenas:
[`../antigravity-pack/TANDA.md`](../antigravity-pack/TANDA.md).

## Audio publicado (`sounds/aoe/`)

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
- Total: 2 903 530 B (~2,77 MiB) + `seleccion.json` (689 B).
- Formato (leído con `file`): RIFF/WAVE PCM 16 bit; 11 archivos estéreo
  44 100 Hz, `rogan` estéreo 48 000 Hz y `wololo` mono 22 050 Hz. Se
  normalizan en la config de audio, no acá.
- `seleccion.json` guarda el mapeo en `choices` (evento → nombre sin
  extensión, portable: se resuelve contra `soundsDir`).

### La selección todavía no está aplicada en la config viva

`sounds/aoe/seleccion.json` es la selección **v2** (carpeta `waw/v2`). La config de
notificaciones de Gentle Shell
(`~/.gentle-shell/config/gentle-ai/notifications.json`) hoy sigue apuntando a
los archivos de `waw/` (v1) para 11 eventos. Aplicar la v2 es un paso aparte,
con backup, y no lo hizo este corte.

## Verificación observada

### 1. Copia de los 13 wav + `seleccion.json`

```bash
cd AoE
mkdir -p gentle-emote-arcade/sounds/aoe
cp -p <workspace>/sounds/*.wav <workspace>/sounds/seleccion.json gentle-emote-arcade/sounds/aoe/
```

Comparación `md5sum` origen vs. copia, uno por uno: **14/14 OK** (13 wav +
`seleccion.json`), sin diferencias de bytes.

### 2. Packs StarCraft y LoL (14 mp3 cada uno)

Origen: los 20 mp3 de `datas/starcraft/` y los 20 de `datas/lol/`. Se eligió un
archivo distinto por evento y se copió con nombre corto:

```bash
cd gentle-emote-arcade
cp -p datas/starcraft/<origen>.mp3 sounds/starcraft/<corto>.mp3
cp -p datas/lol/<origen>.mp3 sounds/lol/<corto>.mp3
md5sum datas/<juego>/<origen>.mp3 sounds/<juego>/<corto>.mp3   # 28 pares
file sounds/starcraft/*.mp3 sounds/lol/*.mp3
```

Resultado observado:

- `md5sum`: **28/28 OK** (14 StarCraft + 14 LoL), copia byte a byte.
- `file`: **28/28 son audio MP3** (ID3 + MPEG ADTS layer III). Bitrates
  56–192 kbps; 19 estéreo (44,1/48 kHz) y 9 mono (22,05 kHz), según el origen.
- `seleccion.json`: schema `gentle-emote-arcade.sounds/v1`, `soundsDir`
  `sounds/starcraft` / `sounds/lol`, 14 eventos en el mismo orden que
  `sounds/aoe/seleccion.json`, `choices` sin extensión, sin nombres huérfanos
  ni archivos faltantes.
- Tamaños usados: StarCraft 407 745 B (14 mp3) + 671 B de JSON; LoL 582 687 B
  (14 mp3) + 632 B de JSON.

### 3. Frames nuevos

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

### 4. `.gitignore` sobre el árbol real

Se verificó con `git ls-files -o -i --exclude-standard` sobre el árbol actual
(el repo local ya está inicializado) recorriendo los 442 archivos en disco:

| Grupo | Archivos | Resultado |
|---|---|---|
| `sounds/` (aoe 14, minecraft 14, cs16 13, starcraft 15, lol 15) | 71 | **entran** |
| `emotes/aoe` + `emotes/aoe-yolo` | 151 (74 PNG + json/yaml por set) | **entran** |
| `docs/`, `scripts/`, `antigravity-pack/` (sin refs crudos) | — | **entran** |
| `datas/` | 63 | fuera |
| `previews/` | 60 | fuera |
| `antigravity-pack/refs/raw_idle.jpg` | 1 | fuera |
| `lab/`, `test/` | hipotéticos hoy | fuera por patrón |

Totales: **442 archivos en disco → 280 versionables (5,72 MiB)**, 162 fuera
(4,26 MiB). Los patrones `lab/`, `test/`, `__pycache__/` y `logs/` dan 0
coincidencias hoy: se dejan preventivos porque son artefactos del workspace.

## Qué quedó fuera y por qué

| Patrón | Qué deja afuera hoy | Por qué |
|---|---|---|
| `datas/` | 63 archivos: 60 mp3 de MyInstants + 3 `README.txt` (~3,3 MB) | material crudo de recopilación; lo publicado son los packs cortos de `sounds/<juego>/`. Los mp3 son muchos, con nombres de origen y cambian con cada tanda |
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
  `sounds/aoe/seleccion.json`.

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
   reservados" por defecto; elegir una si se quiere código reutilizable. Aparte:
   los mp3 de `sounds/starcraft/` y `sounds/lol/` no tienen licencia verificada;
   decidir si se publican, se quitan o se reemplazan antes de pushear.
3. **Remoto**: crear el repo (o el fork de `efolchmontiel/gentle-emote`) y
   apuntar `origin`. Decidir si se publica como fork o como repo independiente
   con el crédito en el README.
4. **Aplicar el audio v2**: aplicar `sounds/aoe/seleccion.json` (portable,
   solo nombres) a `~/.gentle-shell/config/gentle-ai/notifications.json` con
   backup. `scripts/select_game.sh aoe` ya hace el backup y escribe las rutas
   `file:` resolviendo `sounds/aoe/`. Hoy la config viva apunta a `waw/` (v1).
5. **`antigravity-pack/`**: se publica como documentación del pipeline, con el
   `LEEME.md` aclarando que `refs/raw_idle.jpg` no viaja en el repo.

## Pendientes de arte

- `tool`: ariete + aldeanos, 2 poses (01 ariete atrás, 02 adelante).
- `success`: monje + unidad convertida de rodillas, 2 poses.
- Revisar `frameMs` de `tool` (260 ms) y `success` (420 ms) con las poses nuevas.
- Sets `starcraft`, `lol`, `cs16`: faltan los frames; `emotes.json` ya está.
- `minecraft`: falta el set y su `emotes.json`; el audio ya está en
  `sounds/minecraft/`.
- Audio: `starcraft` y `lol` se curaron **por nombre**, sin escucha crítica ni
  prueba en vivo; revisar los eventos flojos (ver "Dudas de la curación") y
  resolver la licencia antes de publicar.

---
Powered by Gentle Shell
