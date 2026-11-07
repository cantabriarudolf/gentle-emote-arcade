# gentle-emote-arcade

El avatar de Gentle Shell, dibujado con sprites de videojuegos y acompañado con
los audios del mismo juego: la misma escena del agente, contada en imágenes y
en sonido.

Powered by Gentle Shell. Fork de
[efolchmontiel/gentle-emote](https://github.com/efolchmontiel/gentle-emote)
—que a su vez es fork de
[cgxeiji/pi-emote](https://github.com/cgxeiji/pi-emote)— para reemplazar el
Gentleman por sprites (y sonidos) de videojuegos.

> **Estado: beta AoE.** El set `aoe` tiene `hi`, `think` e `idle` en 48×40 con
> dos poses; `tool` y `success` siguen con un frame placeholder y se están
> rehaciendo. `starcraft`, `lol` y `cs16` están en desarrollo (solo
> `emotes.json`, sin frames) y `minecraft` es el próximo set a sumar. Detalle,
> verificación y checklist de publicación en [`docs/BETA.md`](docs/BETA.md).

## Idea

Gentle Shell escucha los eventos del agente (sesión, herramientas, subagentes,
contexto) y avisa con sonidos; gentle-emote escucha esos mismos eventos y
anima el avatar. Este proyecto usa la misma tabla de estados del plugin
original (24 escenas), pero dibuja cada escena con un personaje del juego
elegido, y **comparte la columna de escenas con el lab de sonidos** para que
imagen y sonido cuenten la misma historia.

El objetivo del agregado de audio es simple: **entender auditivamente qué está
haciendo el agente sin mirar la pantalla**. Un aldeano que respawnea al arrancar
la sesión, el monje que empieza la conversión cuando el modelo razona y el
`wololo` cuando un subagente está trabajando; si estás en otra ventana, el
juego te cuenta el estado.

Cada juego tiene un set base y un gemelo `-yolo` que hereda del base y agrega
el marcador de modo YOLO / Super-YOLO.

## Contexto AoE (listo)

Age of Empires II es el primer juego cerrado y el único publicable hoy:

- **Escenas**: las 24 del plugin, cada una con su unidad/acción de AoE y su
  justificación en el juego (`docs/MAPA-ESCENAS.md`).
- **Elenco**: aldeano (base), monje (conversión), caballería exploradora,
  ariete, herrera, guardián, rey, elefante, aldeana tejedora, castillo.
- **Audio**: 14 eventos de Gentle Shell mapeados a 13 wav de AoE
  (`sounds/seleccion.json`), con el porqué de cada elección en el mapa.
- **Pendiente para salir de beta**: `tool` y `success` (hoy placeholder) y las
  16 escenas que todavía tienen una sola pose.

| Set | Juego | Estado |
|---|---|---|
| `aoe` | Age of Empires II | **beta**: `hi`, `think`, `idle` nuevos 48×40; `tool` y `success` a rehacer |
| `aoe-yolo` | AoE II, gemelo YOLO | generado desde `aoe` (ver [`emotes/aoe-yolo/README.md`](emotes/aoe-yolo/README.md)) |
| `starcraft`, `starcraft-yolo` | StarCraft | en desarrollo: solo `emotes.json` |
| `lol`, `lol-yolo` | League of Legends | en desarrollo: solo `emotes.json` |
| `cs16`, `cs16-yolo` | Counter-Strike 1.6 | en desarrollo: solo `emotes.json` |
| `minecraft`, `minecraft-yolo` | Minecraft | a sumar: todavía sin `emotes.json` ni frames |

## Roadmap

1. **Ahora — beta AoE**: cerrar `tool` y `success`, completar la segunda pose
   de las 16 escenas que tienen una sola, parpadeo real de `idle`.
2. **Sonido AoE**: la selección v2 está en `sounds/`, pero todavía no está
   aplicada en la config viva de Gentle Shell (`notifications.json`); aplicarla
   con backup es un paso aparte, ver `docs/BETA.md`.
3. **Siguiente — StarCraft, LoL y CS 1.6**: ya tienen `emotes.json` y el mapa
   de escenas; faltan los frames y el cierre de la selección de audio.
4. **Después — Minecraft**: sumar set, mapa de escenas y audio.
5. Licencia y remoto: ver checklist en `docs/BETA.md`.

## Estructura

```
gentle-emote-arcade/
├── emotes/
│   ├── aoe/                 # set beta: 24 estados
│   │   ├── emotes.json      # timing: cycle, frameMs, pesos de talk
│   │   ├── ascii.yaml       # fallback ASCII (terminales sin imágenes)
│   │   ├── idle/            # único estado obligatorio: idle.png + idle_blink.png
│   │   ├── hi/              # hi_01.png + hi_02.png
│   │   ├── think/           # think_01.png + think_02.png
│   │   └── <estado>/        # una carpeta por escena, frames ordenados por nombre
│   ├── aoe-yolo/            # gemelo generado de aoe
│   ├── starcraft/ …         # sets en desarrollo (solo emotes.json)
│   └── cs16/
├── sounds/                  # 13 wav de AoE + seleccion.json (evento → sonido)
├── docs/                    # BETA.md y mapas de escenas por juego
├── scripts/sprites/         # generadores de PNG por código
└── antigravity-pack/        # brief de arte: LEEME, TANDA, FUENTES y refs
```

Fuera del repo, pero en disco (`.gitignore`): `datas/<juego>/` con los mp3
crudos de trabajo, `previews/` con los previews ×8 y recortes, y `lab/` +
`test/` del workspace. Ver [`docs/BETA.md`](docs/BETA.md).

## Formato de frames

- PNG 48×40, 8-bit RGBA, sin interlace, fondo transparente (alfa real).
- Una carpeta por estado; los frames se ordenan alfabéticamente (`_01`, `_02`, …).
- 2 poses por estado (3 solo si es caminar o golpear).
- `idle` es el único estado obligatorio; un estado sin frames simplemente no
  se anima, así que se puede empezar por `idle` e ir sumando escenas.
- Pixel art nítido: sin blur, sin sombra externa, sin GIF, sin sprite-sheet,
  sin JPG en la entrega.

## Sonidos

`emotes.json` define solo el timing de los sprites; los sonidos van por otro
canal. `sounds/` es la selección AoE publicada:

- **13 wav únicos** (2,9 MB) para **14 eventos**: `aldeanospawn` se usa dos
  veces (`session.started` y `subagent.completed`), así que no hay duplicados
  de archivo.
- `sounds/seleccion.json` guarda el mapeo `evento → archivo` en `choices`
  (portable, es el que se lee) y en `events`/`audioDir` las rutas absolutas de
  la máquina donde se generó.

Mapa vigente (v2):

| Evento | Sonido |
|---|---|
| `session.started` | `aldeanospawn` |
| `agent.started` | `priestconversion` |
| `agent.completed` | `priestconverted` |
| `agent.failed` | `rogan` |
| `agent.cancelled` | `malesounddeath5` |
| `agent.attention` | `attack` |
| `subagent.queued` | `farmexhausted` |
| `subagent.running` | `wololo` |
| `subagent.waiting` | `interface-population-limit` |
| `subagent.completed` | `aldeanospawn` |
| `subagent.failed` | `generic-male-death3` |
| `subagent.cancelled` | `generic-female-death3` |
| `subagent.timed_out` | `generic-siege-weapon-death` |
| `context.high` | `interface-town-bell1` |

Para usar los sonidos en otra máquina hay que reescribir las entradas `file:`
de `events` (o regenerar el `seleccion.json` desde el lab) apuntando a la copia
local de `sounds/`, y aplicar el resultado a la config de notificaciones de
Gentle Shell (`~/.gentle-shell/config/gentle-ai/notifications.json`).
**Hoy esa config todavía no recibió esta selección**: sigue apuntando a los
archivos de `waw/` (v1). Aplicarla es un paso aparte, con backup — ver
[`docs/BETA.md`](docs/BETA.md).

Los mp3 crudos de los que salió esta selección (`datas/<juego>/`, 60 archivos)
no se publican: no son el entregable y cambian con cada tanda.

## Instalación

1. Copiar `emotes/` a
   `~/.gentle-shell/agent/extensions/gentle-emote/emotes/` (global) o a
   `<proyecto>/.pi/extensions/gentle-emote/emotes/` (por proyecto).
2. Elegir el set en `config.json` del plugin:

   ```json
   { "emotes": [{ "model": "*", "emote-set": "aoe" }] }
   ```

   Cambiá `"aoe"` por `"aoe-yolo"`, `"starcraft"`, `"lol"` o `"cs16"` según el set.
3. `/reload` y `/emote demo` para ver las escenas.
4. Audio (opcional): copiar `sounds/` a una carpeta estable, apuntar ahí las
   rutas `file:` de `seleccion.json` y aplicar el mapa a la config de
   notificaciones de Gentle Shell.

## Generadores

Los frames salen de `scripts/sprites/*.py`, sin dependencias (solo stdlib:
`zlib`, `struct`, `os`). Escriben rutas relativas al workspace, así que hay
que correrlos desde la raíz del proyecto AoE:

```bash
cd <workspace>/AoE
python3 gentle-emote-arcade/scripts/sprites/gen_aoe_final.py   # set aoe
python3 gentle-emote-arcade/scripts/sprites/gen_aoe_yolo.py    # escribe /tmp/gen_yolo2.py
python3 /tmp/gen_yolo2.py                                      # recién ahí regenera aoe-yolo
```

Advertencias verificadas en el código actual:

- `gen_aoe_final.py` genera **una** pose por estado (`<estado>.png`): pisa
  todos los estados de una sola pose (incluidos `tool` y `success`) y también
  `idle`, `talk`, `yolo` y `super-yolo`; además agrega `hi.png` / `think.png`
  de un frame al lado de las poses nuevas `_01`/`_02`. No conviene correrlo
  hasta completar la tanda de 2 poses por estado, porque borra trabajo ya
  entregado.
- `gen_aoe_yolo.py` no ejecuta el generador parcheado: solo lo deja en
  `/tmp/gen_yolo2.py`, que hay que correr aparte (ver
  [`emotes/aoe-yolo/README.md`](emotes/aoe-yolo/README.md)).
- `gen_idle_aoe.py` y `gen_all_aoe.py` son versiones viejas: la primera apunta
  a una ruta que ya no existe (`gentle-emote-aoe/`, con guion) y la segunda
  genera una pose por estado. Quedan como historial.

## Documentación

- [`docs/BETA.md`](docs/BETA.md) — estado por set, verificación de frames y
  audio, qué quedó fuera del repo y checklist para publicar.
- [`docs/MAPA-ESCENAS.md`](docs/MAPA-ESCENAS.md) — las 24 escenas × sonido ×
  sprite AoE.
- `docs/MAPA-ESCENAS-{starcraft,lol,cs16}.md` — idem por juego (en desarrollo).
- [`antigravity-pack/`](antigravity-pack/) — brief de arte: `LEEME.md`,
  `TANDA.md` (las 24 poses pedidas), `FUENTES.md` y `refs/`.

## Créditos y aviso

- Plugin original: [cgxeiji/pi-emote](https://github.com/cgxeiji/pi-emote) vía
  [efolchmontiel/gentle-emote](https://github.com/efolchmontiel/gentle-emote).
- Frames: pixel art generado por `scripts/sprites/*.py` (48×40 RGBA).
- Audios: efectos de sonido de Age of Empires II, recopilados de MyInstants.
- Personajes, nombres y audios de los juegos pertenecen a sus respectivos
  dueños (Microsoft, Blizzard, Riot Games, Valve, Mojang). Proyecto personal y
  experimental, sin relación con ellos.
- Sin `LICENSE` todavía: por defecto, todos los derechos reservados.
- Los JPG crudos de referencia, los mp3 de trabajo, los previews y los logs no
  se versionan (ver [`.gitignore`](.gitignore)).

---
Powered by Gentle Shell
