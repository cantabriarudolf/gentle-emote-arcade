# Pack `gentle` — frases del stream

Catorce frases de **Gentleman Programming** sacadas de un video suyo, una por
evento de la suite. Es el pack oculto del easter egg (`abuela` / `gentle`), y es
el único que no viene de un videojuego.

## Cómo se armó

1. Se extrajeron los clips del video con
   [scrapysound](https://github.com/cantabriarudolf/scrapysound) (audio +
   subtítulos + recortes por timestamp). Los clips quedan fuera del repo, en
   `scrapysound/work/video/clips/<frase>/`.
2. El mapeo evento → frase está en
   `scrapysound/scrapysounds_task/audio_event_mapping.md`.
3. `python3 scripts/make_gentle_sounds.py [CARPETA_DE_CLIPS]` elige, por evento,
   los clips que **arrancan** con la frase (o la mencionan) — hasta dos por
   evento — y las variaciones de «abuela», los convierte a WAV PCM mono 16 bit
   44.1 kHz con GStreamer y reescribe `seleccion.json`.

## Variaciones

`seleccion.json` guarda un principal por evento (`choices`), las alternativas
(`variantes`) y la activación del easter egg (`activacionVariantes`). Al aplicar
el pack, el comando elige **al azar** entre las opciones de cada evento: volvé a
aplicarlo (`/emote:juego gentle` o `scripts/select_game.sh gentle`) y cambia la
toma. Los tests fijan el azar con un RNG inyectable.

La activación del easter egg tiene **una sola toma**: `abuela-1`. El corpus tenía
tres tomas de la misma frase; se escucharon y se quedó la mejor — las otras dos se
descartaron (el script borra los `abuela-*.wav` que ya no usa). `coin.wav` sigue en
el disco como *fallback* del comando para un pack sin activación propia, pero con
este pack **no suena**.

| Activación | Clip |
|---|---|
| `abuela-1` | `001_Abuela_sali_video_de_gente_.mp3` (7,75 s, frase completa) |

## Mapeo

| Evento | Frase | Clip elegido |
|---|---|---|
| `session.started` | gentle shell | `007_meterlo_en_Gentle_Shell_No_no_es_que.mp3` |
| `agent.started` | a ver | `056_A_ver_.mp3` |
| `agent.completed` | espectacular | `013_espectacular_.mp3` |
| `agent.failed` | no | `394_no_.mp3` |
| `agent.cancelled` | así no más | `020_as_no_m_s_.mp3` |
| `agent.attention` | qué les parece | `007__Qu_les_parece_.mp3` |
| `subagent.queued` | a ver | `095_A_ver_.mp3` |
| `subagent.running` | locura | `007_locura_.mp3` |
| `subagent.waiting` | bien | `202_Bien_.mp3` |
| `subagent.completed` | ahí está | `022_ah_est_.mp3` |
| `subagent.failed` | la verdad eh | `003_la_verdad_eh.mp3` |
| `subagent.cancelled` | así no más | `019_as_no_m_s_.mp3` |
| `subagent.timed_out` | no | `430__no_.mp3` |
| `context.high` | locura | `017_Esto_es_una_locura_.mp3` |

Cada fila puede tener una segunda toma (`<tallo>-2.wav`) elegida de la misma
carpeta de frases; la tabla de arriba muestra la principal.

`coin.wav` es aparte: es el sonido de activación del easter egg (`activation` en
`seleccion.json`), no un evento de la suite.

## Sesión nueva

El cartel **«✓ New session started»** no lo cubre la suite: su evento
`session.started` suena **sólo al arrancar el proceso**, no en sesión nueva
(`/new`), reload, resume ni fork. Por eso lo engancha la extensión de selección:
escucha `session_start` de Pi y, cuando el motivo es `new`, reproduce la frase del
pack (`nuevaSesion`).

| Clave | Clip | Duración |
|---|---|---|
| `nuevaSesion: ["esto-es-una-locura"]` | `018_Esto_es_una_locura.mp3` → `esto-es-una-locura.wav` | 4,75 s |

Es una toma **reservada**: los 14 eventos no pueden usarla, así el saludo de
sesión nueva nunca se confunde con un evento de la partida. La frase de
activación (`abuela-1`) sigue sonando **sólo al aplicar el pack**, no acá.

## Licencia: sin verificar

La voz es de **Gentleman Programming** y salió de un video público suyo. No hay
permiso confirmado para redistribuirla. Igual que los mp3 de `starcraft` y `lol`,
este pack viaja en el repo **para pruebas locales**: antes de publicar de verdad
hay que decidir si se quita, se reemplaza o se pide permiso. El resto de los
audios del repo tiene el mismo cuidado documentado en `docs/BETA.md`.
