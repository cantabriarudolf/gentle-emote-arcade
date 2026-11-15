# gentle-frases — frases emblemáticas y variaciones del pack `gentle`

Pack oculto `gentle` (alias `abuela`): pasar de un clip fijo por evento a
**candidatos con variación**, incluyendo las frases emblemáticas del corpus de
scrapysound (por ejemplo «abuela» y sus variaciones), que hoy quedan afuera.

## Specs

**S1 — menú en cualquier proyecto (pedido textual).**

> hago reload en otro proyecto incluso saliendo y abriendo nuevamente la sesion y
> no me muestra el nuevo menu

`extensions/game-select/index.ts` se instala **global** en
`~/.gentle-shell/agent/extensions/game-select/index.ts` (symlink al repo). El
`projects.json` sigue viviendo junto al arcade, así cada proyecto recuerda su
juego aunque arranques desde otra carpeta.

**S2 — el trabajo va por worker sobre scrapysound (pedido textual).**

> tambien debes mediante un worker gestione con el proyecto scrappysound sonbre
> la solicitud de gentle que hicimios, faltan frases emblematicas, scrappysound
> hacia eso, por ejemplo el abuela y sus variaciones

**S3 — faltan frases emblemáticas.** El pack actual elige, por evento, el clip
más corto que **arranca** con la frase. Eso descarta las frases emblemáticas del
corpus (las que la tabla de muletillas del mapeo destaca). El pack debe incluir
esas frases y, cuando existan, sus variaciones.

**S4 — variaciones, no un archivo fijo.** `sounds/gentle/seleccion.json` mantiene
`choices` (principal por evento) y suma `variantes: { evento: [tallo, …] }`. Al
aplicar el pack, el comando elige **al azar** entre el principal y sus variantes,
con un parámetro inyectable para que los tests sean deterministas. El easter egg
usa `activacionVariantes: [tallo, …]` con la misma regla y `coin` como fallback.

**S5 — contrato de audio** (ya vigente en `docs/BETA.md` y `sounds/gentle/README.md`):
WAV PCM (RIFF, format 1), mono o estéreo, ≤ 2 MiB y ≤ 10 s. Se convierte con
`gst-launch-1.0` (no hay ffmpeg en la máquina).

**S6 — no inventar.** Si una frase no está en el corpus de clips
(`~/Documentos/Proyectos/scrapysound/work/video/clips/<frase>/`), se reporta como
ausente; no se fabrica audio ni se usa otra frase en su lugar.

**S7 — procedencia.** El pack y su tabla evento → frase → clip siguen
documentados en `sounds/gentle/README.md`, con el aviso de voz sin licencia
verificada.

## Tasks

| ID | Tarea | Specs | Ruta | Commit |
|---|---|---|---|---|
| T1 | Extensión global + README de instalación | S1 | inline (parent) | no |
| T2 | Corpus: catálogo de frases emblemáticas y «abuela»; variantes en script, pack y extensión; tests | S2-S7 | worker | no |
| T3 | Verificación: tests, `check_install.sh`, 14 eventos y variantes cableadas | S3-S7 | inline (parent) | no |

## Log

**L1 — pedido (verbatim).**

> qie raro, hago reload en otro proyecto incluso saliendo y abriendo nuevamente la sesion y no me muestra el nuevo menu, tambien debes mediante un worker gestione con el proyecto scrappysound sonbre la solicitud de gentle que hicimios, faltan frases emblematicas, scrappysound hacia eso, por ejemplo el abuela y sus variaciones

**L2 — decisión de licencia (ya tomada por el owner).** Los clips de voz del
streamer van **al repo** con atribución y aviso de licencia sin verificar.

**L3 — estado previo.** Pack `gentle` con 14 clips fijos + `coin.wav`; escenas
`gentle`/`gentle-yolo` del fork ya importadas (76 PNG cada una).
