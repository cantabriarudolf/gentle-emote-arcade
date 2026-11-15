# Publicación en Gentle Hub

Dejar `gentle-emote-arcade` ordenado, licenciado y publicable como entrada del
Gentle Hub. El fork formal queda **fuera** de este feature: se decide después.

## Specs

**S1 — README.** «necesito que actualices el readme, en el debes agradecer de donde
viene forkeado mas sus agradecimientos y que te cuelgas para apaortar una capa
auditiva a aquellos que interactuan bla bla mejorando bla bla permitiendo no estar
viendo la pantalla para entender que proyecto y que cosa esta sucediendo»
(L1). Cumplido en `README.md` (`## Gracias`, `## Créditos y linaje`, intro).

**S2 — Gracias sutiles.** «tambien aprovecha de incluir que esto fue gracias a
gentleshell y scrappysound (aqui es una capa a lo que hacemos sin decirlo en la
cara, tiene que sonar sutil y elegante sin darle mucho protagonismo pero que se
sepa)» (L2). Cumplido en `README.md` (`## Gracias` + pie `motor · Gentle Shell`).

**S3 — Licencia.** «indicame que tipo de licencia debiera tener este proyecto es
para la comunidad de gentle y quiero subirlo al hub del sitio» (L1). Decidido:
Apache-2.0 de raíz ya vigente, más la cadena MIT declarada en un `NOTICE.md` y en
los `LICENSE` de cada pack de arte.

**S4 — Orden antes de publicar.** «previamente necesitamos ordenarlo un poco mas ya
que posteriormente deberemos hacer el fork formal para que quede marcado ya que
entiendo eso hoy aun no es» (L1). Nada se publica ni se forkea hasta que T1–T9
estén cerradas.

**S5 — Ningún evento audible se pierde.** «me dio la impresion que hubieron
procesos entre el entrer y la respuesta que escalaron a un evento que deberia
tener sonido […] habria tambien que evaluar si esta sucediendo en el resto de los
juegos ya que no debiera suceder» (L3). Ningún pack puede mapear el mismo archivo
a dos familias distintas de evento (`session.*`, `agent.*`, `subagent.*`), y el
evento terminal del turno no puede ser acústicamente igual a un evento intermedio.

**S6 — Zona gris aceptada, y dicho así.** «zona gris es la decisicion (opcion a)»
(L6). Los 59 rips trackeados en `sounds/` se quedan donde están y se publican. Lo
que no se acepta es el silencio documental: cada pack declara de dónde sale su
audio, quién lo posee y que el repo no reclama permiso que no tiene.

**S7 — Plan antes de tocar el repo.** «haz el plan […] y lo que estimes para que
quede ordenadito, luego de eso nos preocupamos del formalizar el fork» (L4).

**S8 — Ningún pack mudo.** «por ejemplo new sesion started en aoe no tiene sonido,
esto en los otros juegos tampoco debiera suceder» (L5). Toda clave opcional del
schema (`nuevaSesion`, `activacionVariantes`/`activation`, `variantes`) tiene que
tener un fallback definido y observable: la ausencia de la clave no puede
traducirse en silencio.

**S9 — Rotación sólo en `gentle`.** «seria solo para gentle lo demas tal como está»
(L8). El pack `gentle` rota la frase del Enter en cada mensaje; los otros seis
packs conservan su `agent.started` fijo y su cableado actual.

**S10 — Desinstalar deja fábrica.** «si se desinstala tiene que dejar los sonidos que
venian por defecto en gentle shell» (L9). Al desinstalar, `notifications.json` vuelve
a `builtin:error` / `builtin:attention` / `builtin:success` según prioridad y `null`
en el resto, sin apagar `enabled` ni tocar los límites de tiempo.

## Tasks

| ID | Tarea | S# | Ruta | Commit |
|---|---|---|---|---|
| T1 | `NOTICE.md` con la cadena MIT (Eiji Onchi + efolchmontiel, 2026) y trackear `emotes/gentle/LICENSE`, `emotes/gentle-yolo/LICENSE` y los 157 PNG de `gentle*`. Hoy el README enlaza un archivo que no está en git. | S3 | inline | `docs(license): NOTICE y arte de gentle bajo aviso MIT` |
| T2 | `scripts/check_packs.py`: valida 14 eventos, que todo archivo referenciado exista (resolviendo `pack/tallo`), y que ninguna familia de evento comparta archivo. Test-first. | S5 | inline | `test(packs): validador de cobertura y colisiones` |
| T3 | Resolver las 5 colisiones reales: cs16 `ctwin` (agent.completed/subagent.completed) y `fallback`; minecraft `villager-yes` y `villager-ambient`; aoe `aldeanospawn`. Stings propios Apache-2.0, cortos (<1 s). | S5 | worker | `fix(packs): sonidos distintos por familia de evento` |
| T4 | Política de zona gris (decisión a): mantener los 59 rips y la voz en `sounds/`, y fijar el aviso en `docs/AVISO-AUDIO.md` — procedencia por pack, dueño de cada marca, y que no hay permiso verificado. Sin borrar audio. | S6 | inline | `docs: aviso de audio por pack y alcance de la zona gris` |
| T5 | Documentar el scheduler real en README: un solo slot pendiente, TTL 2 s, prioridad 0–3, mínimo 1 s entre sonidos. Que set `a` no signifique «todo suena». | S5 | inline | `docs: cómo reparte el canal el scheduler` |
| T6 | Arreglar `docs/BETA.md`: `:327` dice «no hay `LICENSE`» contra el Apache-2.0 de la raíz; conteos 442/5,72 MiB desactualizados; paths `sounds/*/mp3/` que no existen. | S3, S4 | inline | `docs: BETA al día con licencia y tamaños` |
| T7 | Procedencia o baja de `antigravity-pack/refs/ref-villager-moddb.png` (captura de terceros, trackeada, sin nota). | S4 | inline | `docs(antigravity): procedencia de la referencia` |
| T8 | Higiene: `.gitignore` para `emotes/*-backup.bak/` (37 archivos sueltos) y decidir los WAV/MP3 extra sin trackear (`lol` 29/15, `minecraft` 27/14, `starcraft` 29/15). | S4 | inline | `chore: basura y audio suelto fuera del índice` |
| T9 | Commits por unidad de trabajo sobre los 7 archivos modificados y el árbol untracked. Hoy `main` está 2 adelante de `origin/main`. | S4 | inline | serie de commits por unidad |
| T10 | Metadatos del hub: descripción ≤120 caracteres sin el nombre del repo, 3–6 topics, y la entrada declarando que deriva de `efolchmontiel/gentle-emote` (ya listado como `extension`/`resource`). | S3, S4 | inline | `docs(hub): metadatos de la entrada` |
| T11 | `sonidoNuevaSesion` (`extensions/game-select/index.ts:250`) devuelve `null` cuando el pack no trae `nuevaSesion`, y sólo `gentle` la trae: `/new` es mudo en 6 de 7 packs. Fallback a `choices["session.started"]`, más la validación de las tres claves opcionales en T2. | S8 | inline | `fix(packs): sesión nueva con sonido en todos los packs` |
| T12 | Rotación por mensaje **sólo en `gentle`**: `sonidoRotativo` sortea principal + `variantes` al reproducir (no al aplicar), `pi.on("turn_start")` la dispara cuando el pack activo es `gentle`, y ese evento se escribe `null` en `notifications.json` para no duplicar con el scheduler. Pool inicial de 4 frases. | S9 | inline | `feat(gentle): rotación de frases por ocurrencia` |
| T13 | `scripts/restore_notifications.ts` + `scripts/uninstall.sh`: al desinstalar, `audio.events` vuelve a los `builtin:` de fábrica por prioridad, con backup y sin tocar `enabled` ni los tiempos. | S10 | inline | `feat(uninstall): restaurar los sonidos de fábrica` |

Fuera de alcance: fork formal y PR aguas arriba (se decide después de T1–T9).

## Log

**L1** — «necesito que actualices el readme, en el debes agradecer de donde viene
forkeado mas sus agradecimientos y que te cuelgas para apaortar una capa auditiva
a aquellos que interactuan bla bla mejorando bla bla permitiendo no estar viendo
la pantalla para entender que proyecto y que cosa esta sucediendo bla bla, tambien
indicame que tipo de licencia debiera tener este proyecto es para la comunidad de
gentle y quiero subirlo al hub del sitio previamente necesitamos ordenarlo un poco
mas ya que posteriormente deberemos hacer el fork formal para que quede marcado ya
que entiendo eso hoy aun no es, que opinas?»

**L2** — «tambien aprovecha de incluir que esto fue gracias a gentleshell y
scrappysound (aqui es una capa a lo que hacemos sin decirlo en la cara, tiene que
sonar sutil y elegante sin darle mucho protagonismo pero que se sepa), que opinas?»

**L3** — «quiero que hagas una ultima revision primero atendiendo esto: "cargue el
perfil cs16 y cargo el sonido inicial, escribi y envie enter y tambien salio un
sonido, me dio la respuesta y tambien me dio un sonido pero me dio la impresion
que hubieron procesos entre el entrer y la respuesta que escalaron a un evento que
deberia tener sonido (esto necesito confirmar) " si es asi como lo describo y se
tuvo que hacer la correccion eventual para cs16 habria tambien que evaluar si esta
sucediendo en el resto de los juegos ya que no debiera suceder.»

**L4** — «y tambien haz el plan respecto a lo que recomendaste como el orden
propuesto antes de publicar y lo que estimes para que quede ordenadito, luego de
eso nos preocupamos del formalizar el fork»

**L5** — «por ejemplo new sesion started en aoe no tiene sonido, esto en los otros
juegos tampoco debiera suceder»

**L6** — «zona gris es la decisicion (opcion a), algo mas que necesites de mi o ya
puedes continuar.»

**L7** — «y respecgto al sonido de gentle en particular como tenemos mas voces de el
cuando mandamos un enter, si analizas el audio es muy pero muy bueno da la
sensacion de que te esta boludiando el gentle, pero si le mandas un nuevo mensaje
se repite el sonido (creo) y ahi pierde el chiste. por eso podrias apoyarte de
scrappysound para que en este modalidad gentle en particular pueda rotar cuando
existen este tipo de casos, o el easteregg seria que gentle tendria un sonido en
particular para temas muy necesarios de indentificar y para el resto ir rotando
con lafinalidad de que de la sensacion de boludeo y buena onda. que opinas?»

**L8** — «seria solo para gentle lo demas tal como está»

**L9** — «si se desinstala tiene que dejar los sonidos que venian por defecto en
gentle shell, que mas queda pendiente?»

**E1 — evidencia S1/S2.** `README.md` reescrito: intro de capa auditiva, `## Gracias`
con los cuatro créditos, tabla de linaje, tabla de licencia por capas. Sin commit.

**E2 — evidencia S5 (mecanismo).** `gentle-pi/lib/notification-scheduler.ts`: un
solo `pending` («Keep just one candidate, not an accumulating queue»), `NOTIFICATION_TTL_MS = 2000`,
`due = Math.max(pending.readyAt, lastStart + minimumIntervalMs)`, y descarte
silencioso al vencer. `notification-policy.ts:21-23`: prioridad 3 = `.failed`/`.timed_out`,
2 = `agent.attention`/`context.high`, 1 = `.completed`, 0 = el resto.
`notification-service.ts:115` filtra `session.shutdown` → 14 eventos soportados.

**E3 — evidencia S5 (alcance).** Los 7 packs mapean los 14 eventos y ningún archivo
referenciado falta. Colisiones por pack: `cs16` 2, `minecraft` 2, `aoe` 1;
`gentle`, `lol`, `starcraft` 0. `misc` sano: `resolverArchivo` (`extensions/game-select/index.ts:316`)
resuelve `pack/tallo` contra `sounds/<pack>/`. En los 7 packs, 7 de 14 eventos son
prioridad 0.

**E4 — evidencia S5 (indistinguibilidad).** En `cs16`, `agent.completed` y
`subagent.completed` comparten `ctwin.wav`: el fin del turno y el fin de un hijo
suenan idénticos. Duraciones `cs16`: 0,88 s (`roger`) a 1,93 s (`getout`);
`agent.started` (`go.wav`) 1,33 s, contra 1 s de intervalo mínimo.

**E5 — causa del reporte.** Confirmado: sí hubo eventos intermedios y sí sonaron;
lo que no se puede distinguir al oído es cuál es cuál. Defecto de cableado común a
todos los packs, peor en `cs16` por la colisión del evento terminal.

**E6 — evidencia S3/S4.** `emotes/gentle/LICENSE` y `emotes/gentle-yolo/LICENSE`
son `??` (untracked), y los 157 PNG de `gentle*` también. `sounds/*/` trackea 59
rips de juego. `datas/` está en `.gitignore` y ningún código lo lee.

**E7 — evidencia S8.** `nuevaSesion` existe sólo en `sounds/gentle/seleccion.json`;
los otros 6 packs (`aoe`, `cs16`, `lol`, `minecraft`, `misc`, `starcraft`) traen
sólo `schema`, `soundsDir` y `choices`. `sonidoNuevaSesion`
(`extensions/game-select/index.ts:250-266`) retorna `null` sin avisar cuando la
clave falta. La traza de esta máquina lo registra: `/tmp/game-select.log:648`
`2026-11-15T22:16:00.465Z nueva sesion -> - (pack aoe)`, contra seis entradas
anteriores con `pack gentle` → `esto-es-una-locura.wav`. La misma forma de falla
aparece en `activacionVariantes` (sólo `gentle` trae; sin `coin.wav`, los otros
packs no tienen sonido de activación) y en `variantes`.

**E9 — evidencia S5/L7 (por qué se repite).** `NotificationSound`
(`gentle-pi/lib/notification-policy.ts:19`) es `builtin:<id> | file:<ruta absoluta> | null`:
**un** archivo por evento, validado en `isNotificationSound` (`:82-93`) con ruta
absoluta obligatoria. `notificationSoundFor` (`:114`) devuelve ese valor fijo. Las
`variantes` del pack se sortean dentro de `planSonidos`, o sea **al aplicar el pack**,
no al reproducir: por eso cada mensaje suena igual. El SDK expone a las extensiones
`session_start`, `turn_start`, `turn_end`, `agent_before_settle` y `tool_execution_*`,
pero no los eventos internos (`subagent.*`, `context.high`, `agent.attention`).

**E10 — material para rotar (S9).** `sounds/gentle/` ya trae 27 WAV: 14 principales
más las tomas `-2`, así que no hace falta extraer nada nuevo con scrapysound. El
pool de `agent.started` quedó en 4 frases libres (`a-ver`, `a-ver-2`, `locura`,
`que-les-parece`), sin pisar los eventos de identidad ni `nuevaSesion`.
`pi.on("turn_start")` está soportado por la extensión API
(`pi-coding-agent/dist/core/extensions/types.d.ts:1256`).

**E11 — evidencia S10.** Los defaults salen de `DEFAULT_NOTIFICATION_SETTINGS`
(`notification-policy.ts:39-45`): prioridad 3 → `builtin:error`, 2 → `builtin:attention`,
1 → `builtin:success`, 0 → `null`. `restaurarPorDefecto` reescribe sólo
`audio.events`, deja backup fechado y conserva `enabled` y `minimumIntervalMs`.
Probado con `--dry-run` real; el restore efectivo no se ejecutó para no pisar el
pack cs16 activo.

**E8 — decisión S6.** L6 elige la opción (a). T4 deja de mover audio y pasa a
fijar el aviso. Riesgo aceptado por el dueño con conocimiento del alcance: marcas
de Microsoft (AoE), Valve (CS 1.6), Blizzard (StarCraft), Riot (LoL) y Mojang
(Minecraft), más la voz de Gentleman Programming en `sounds/gentle/`.
