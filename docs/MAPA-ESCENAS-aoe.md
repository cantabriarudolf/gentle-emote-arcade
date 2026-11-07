# Mapa de escenas: gentle-emote × Gentle Shell × AoE

Una fila por estado del plugin. Tres columnas conceptuales:

1. **Qué hace el agente** (evento de Gentle Shell / estado del plugin)
2. **Qué se escucha** (sonido del lab `waw/v2`, con su porqué)
3. **Qué se ve** (sprite de AoE a dibujar en el fork `gentle-emote-aoe`)

## Tabla

| # | Escena gentle-emote | Qué hace el agente | Sonido (porqué) | Sprite AoE a dibujar | Dónde aparece en el juego |
|---|---|---|---|---|---|
| 1 | `hi` | Sesión arranca | `aldeanospawn` — nace una unidad útil | Monje saliendo del monasterio | Monastery / spawn |
| 2 | `idle` | Esperando input | — (silencio) | Aldeano parado junto a la granja | Idle villager |
| 3 | `think` | El modelo razona | `priestconversion` — el monje está actuando sobre un objetivo | Sacerdote con mano en la barbilla, polvillo de fe | Monk idle |
| 4 | `talk` | El modelo responde | `rogan` — el aldeano responde al clic | Aldeano respondiendo | Villager ack |
| 5 | `read` | Lee código/memoria | — | Caballería exploradora con antorcha | Scout Cavalry |
| 6 | `write` | Edita código | — | Aldeano construyendo con andamio | Villager build |
| 7 | `tool` | Ejecuta otras herramientas | — | Ariete golpeando | Battering Ram |
| 8 | `ask` | Pregunta sí/no en pantalla | `interface-menu-select` — click neutro de UI | Aldeano con globo Y/N | Villager selected |
| 9 | `success` | Terminó bien | `priestconverted` — la unidad ya cambió de bando | Sacerdote con unidad convertida de rodillas | Conversion success |
| 10 | `failure` | Algo falló | `rogan` / `generic-male-death2` — no entendió / muerte larga = grave | Aldeano caído, polvo, espada clavada | Villager death |
| 11 | `compact` | Compactación de contexto | `interface-town-bell1` — la alarma suena en el pueblo | Monje achicándose, túnica intacta | Monk / Relic |
| 12 | `delegate` | Subagentes genéricos | `wololo` — un subagente está en proceso | Monje repartiendo aldeanos a tareas | Monk + villager group |
| 13 | `explore` | Subagente explorador | `wololo` | Caballería con linterna, huellas | Scout Cavalry |
| 14 | `build` | Subagente implementa | `priestconversion` | Herrera soldando el ariete | Blacksmith / Siege |
| 15 | `verify` | Subagente verifica | `interface-menu-select` | Guardián con escudo y sello verde | Town Center |
| 16 | `judge` | Subagente juzga | `interface-town-bell1` | Monje con mazo, sentencia | Monastery |
| 17 | `review` | Subagente revisa | `farmexhausted` — recurso en revisión | Monje con pluma roja y pergamino | Monk / Market |
| 18 | `jira` | Subagente Jira | `interface-victory` | Cohete de madera desde el castillo | Castle |
| 19 | `jobs` | Jobs en background | `interface-population-limit` — bloqueado, necesita acción | Aldeano tomando mate junto a la barra | Mill / Farm |
| 20 | `yolo` | Modo YOLO | `attack` — te están atacando, igual seguís | Aldeano con vincha YOLO y cohete | Wonder |
| 21 | `super-yolo` | Modo Super YOLO | `attack` | Aldeano YOLO con sol | Wonder / sol |
| 22 | `remember` | Guarda memoria en Engram | — | Monje susurrando al oído del elefante | Monk + Elephant |
| 23 | `grandma` | Idle largo (30s) | — | Aldeana tejiendo junto a la granja | Farm |
| 24 | `bye` | Despedida | `interface-defeat` — la partida se acabó | Aldeano sacándose el sombrero | Villager idle |

## Eventos de sonido sin escena directa del plugin

| Evento | Sonido | Porqué | Escena más cercana |
|---|---|---|---|
| `subagent.queued` | `farmexhausted` | recurso agotado, en cola | `delegate` |
| `subagent.waiting` | `interface-population-limit` | no podés producir sin construir | `jobs` |
| `subagent.timed_out` | `generic-siege-weapon-death` | la máquina se rompe: se trabó, no murió nadie | `failure` |
| `context.high` | `interface-town-bell1` | alarma del pueblo: el contexto se llena | `compact` |

## Reglas de consistencia

- **Cancelar ≠ fallar**: cancelación usa click/whoosh (`interface-*`), falla
  usa muerte o `rogan`. Nunca comparten sonido.
- **Una muerte corta = leve, una larga = grave**: `male-death1` (0.55s) leve,
  `male-death2` (1.38s) grave.
- **El sprite cuenta lo mismo que el sonido**: si el sonido es `wololo`
  (conversión en curso), la imagen es el monje actuando, no el aldeano
  construyendo.

## Contextos y recomendado vs actual (lab de sonidos)

Cada sonido tiene un contexto: nacimiento, apuro, cierre de partida,
conversión en curso, conversión lograda, fallo suave, muerte, colapso
mecánico, neutro de UI, alerta, bloqueado, fuera de tema. Cada evento
espera uno o dos contextos. Si elegís un sonido fuera de contexto, la UI
levanta warning visual y la imagen asociada cambia a la de ese contexto
(muerte → aldeano caído; neutro → globo Y/N; etc.).

Recomendado (propuesta) vs actual (config viva):

| Evento | Actual | Recomendado | Estado |
|---|---|---|---|
| session.started | aldeanospawn | aldeanospawn | ✓ |
| session.shutdown | silenciado | interface-defeat | ⚠️ difiere |
| agent.started | priestconversion | priestconversion | ✓ |
| agent.completed | priestconverted | priestconverted | ✓ |
| agent.failed | rogan | rogan | ✓ |
| agent.cancelled | malesounddeath5 | interface-whoosh | ⚠️ difiere (muerte vs neutro) |
| agent.attention | attack | attack | ✓ |
| subagent.queued | farmexhausted | farmexhausted | ✓ |
| subagent.running | wololo | wololo | ✓ |
| subagent.waiting | silenciado | interface-population-limit | ⚠️ difiere |
| subagent.completed | aldeanospawn | aldeanospawn | ✓ |
| subagent.failed | malesounddeath5 | generic-male-death2 | ⚠️ difiere (variante) |
| subagent.cancelled | silenciado | interface-menu-select | ⚠️ difiere |
| subagent.timed_out | malesounddeath5 | generic-siege-weapon-death | ⚠️ difiere (muerte vs máquina) |
| context.high | builtin:attention | interface-town-bell1 | ⚠️ difiere (builtin vs archivo) |

## Emblemáticos: lugar garantizado

9 sonidos emblemáticos, badge `◆ emblemático` en la UI, cada uno con su
evento recomendado (sin duplicados):

| Sonido | Evento recomendado | Porqué es emblemático |
|---|---|---|
| `aldeanospawn` | `session.started` | el "shh-ha" de nacimiento |
| `priestconversion` | `agent.started` | el monje convirtiendo en curso |
| `priestconverted` | `agent.completed` | la conversión consumada |
| `rogan` | `agent.failed` | el "¿Rogan?" del aldeano |
| `attack` | `agent.attention` | el cuerno de aviso de ataque |
| `farmexhausted` | `subagent.queued` | el "farm exhausted" |
| `wololo` | `subagent.running` | el cántico de conversión más famoso |
| `malesounddeath5` | `subagent.failed` | la muerte masculina clásica #5 |
| `startthegamealready` | alternativa de `session.started` | taunt 14, saludo de sesión |

`session.shutdown` es inerte: nunca suena, queda en silencio.

## Ajuste v3: muertes femeninas y aldeanospawn

- `agent.cancelled` → `generic-female-death1` (0.44s)
- `subagent.cancelled` → `generic-female-death3` (0.34s)
- `subagent.failed` se queda con `malesounddeath5` (1.33s, grave)
- `session.started` → `startthegamealready` (una vez por proceso, saludo largo)
- `subagent.completed` → `aldeanospawn` (nacimiento frecuente; evita duplicar
  `interface-villager-spawn` que es el mismo contenido)

## Estimación de equivalencia perceptual (2026-11-06)

Método: duración + correlación de envolvente RMS (20ms). La correlación de
waveform cruda da ~0 entre rips distintos del mismo sonido (distinto
encoder/fase), por eso manda la envolvente + duración:

| Par | Δ duración | Env. RMS | Veredicto |
|---|---|---|---|
| `aldeanospawn` vs `interface-villager-spawn` | 0.01s | +0.929 | **MISMO sonido** |
| `malesounddeath5` vs `generic-male-death2` | 0.05s | +0.870 | **MISMO sonido** (tu #5 = su #2) |
| `malesounddeath5` vs `death1/3/4/6` | 0.39–0.89s | -0.57..+0.37 | tomas distintas |
| `priestconverted` vs `interface-enemy-convert-success` | 0.13s | +0.928 | **MISMO sonido** |
| `priestconversion` vs `generic-monk-convert` | 0.08s | +0.772 | **MISMO sonido** |
| `attack` vs `interface-attack-warning-general` | 0.17s | +0.530 | **MISMO sonido** |
| `farmexhausted` vs `interface-farm-exhausted` | 0.02s | +0.140 | **MISMO sonido** (distinto EQ) |

Regla: cada grupo perceptual se usa en **un solo evento**. Los "otro rip"
quedan como alternativa etiquetada, nunca como segundo recomendado.

## v4: duplicados eliminados

De la carpeta de trabajo `v2/` se movieron a `v2/duplicados/` (fuera del
repertorio, recuperables) los 6 rips alternativos del mismo sonido:

- `interface-villager-spawn` (dupe de `aldeanospawn`)
- `interface-farm-exhausted` (dupe de `farmexhausted`)
- `generic-monk-convert` (dupe de `priestconversion`)
- `interface-enemy-convert-success` (dupe de `priestconverted`)
- `interface-attack-warning-general` (dupe de `attack`)
- `generic-male-death2` (dupe de `malesounddeath5`)

`v2/` queda con 30 archivos, uno por sonido del juego. Además, ningún
recomendado aparece como opción de otro evento (cruces candidatos: 0).
Las únicas apariciones cruzadas restantes son el `ACTUAL` leído de la
config viva, que se muestra para comparar hasta que guardes la nueva
selección.
