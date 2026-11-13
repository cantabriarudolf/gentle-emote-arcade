# Catálogo de imágenes — gentle-emote-arcade

Catálogo por juego y estado: estado, acción que representa y ruta al thumbnail.

Las 24 escenas son las del plugin gentle-emote; todos los sets comparten el mismo

conjunto de estados. La acción (columna *Acción*) es el momento del agente.


Thumbnails disponibles en `docs/`: solo `aoe` tiene galería publicada

(`docs/scenes/<estado>.png` ×24 y `docs/galeria/aoe.png`). Para el resto,

la ruta apunta al primer frame del estado en `emotes/<set>/<estado>/`;

la serie completa se ve en `docs/demo/index.html` (puerto 8785).


## aoe

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 3 | `docs/scenes/hi.png` |
| `idle` | Esperando input | 2 | `docs/scenes/idle.png` |
| `think` | El modelo razona | 4 | `docs/scenes/think.png` |
| `talk` | El modelo responde | 5 | `docs/scenes/talk.png` |
| `read` | Lee código/memoria | 3 | `docs/scenes/read.png` |
| `write` | Edita código | 3 | `docs/scenes/write.png` |
| `tool` | Ejecuta otras herramientas | 4 | `docs/scenes/tool.png` |
| `ask` | Pregunta sí/no en pantalla | 3 | `docs/scenes/ask.png` |
| `success` | Terminó bien | 3 | `docs/scenes/success.png` |
| `failure` | Algo falló | 3 | `docs/scenes/failure.png` |
| `compact` | Compactación de contexto | 3 | `docs/scenes/compact.png` |
| `delegate` | Subagentes genéricos | 3 | `docs/scenes/delegate.png` |
| `explore` | Subagente explorador | 3 | `docs/scenes/explore.png` |
| `build` | Subagente implementa | 3 | `docs/scenes/build.png` |
| `verify` | Subagente verifica | 3 | `docs/scenes/verify.png` |
| `judge` | Subagente juzga | 3 | `docs/scenes/judge.png` |
| `review` | Subagente revisa | 3 | `docs/scenes/review.png` |
| `jira` | Subagente Jira | 3 | `docs/scenes/jira.png` |
| `jobs` | Jobs en background | 3 | `docs/scenes/jobs.png` |
| `yolo` | Modo YOLO | 3 | `docs/scenes/yolo.png` |
| `super-yolo` | Modo Super YOLO | 3 | `docs/scenes/super-yolo.png` |
| `remember` | Guarda memoria en Engram | 3 | `docs/scenes/remember.png` |
| `grandma` | Idle largo (30s) | 3 | `docs/scenes/grandma.png` |
| `bye` | Despedida | 3 | `docs/scenes/bye.png` |

Hoja de contactos del set: `docs/galeria/aoe.png`.

## aoe-yolo

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 3 | `emotes/aoe-yolo/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/aoe-yolo/idle/idle.png` |
| `think` | El modelo razona | 4 | `emotes/aoe-yolo/think/think_01.png` |
| `talk` | El modelo responde | 5 | `emotes/aoe-yolo/talk/talk.png` |
| `read` | Lee código/memoria | 3 | `emotes/aoe-yolo/read/read_01.png` |
| `write` | Edita código | 3 | `emotes/aoe-yolo/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 4 | `emotes/aoe-yolo/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 3 | `emotes/aoe-yolo/ask/ask_01.png` |
| `success` | Terminó bien | 3 | `emotes/aoe-yolo/success/success_01.png` |
| `failure` | Algo falló | 3 | `emotes/aoe-yolo/failure/down_01.png` |
| `compact` | Compactación de contexto | 3 | `emotes/aoe-yolo/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 3 | `emotes/aoe-yolo/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 3 | `emotes/aoe-yolo/explore/explore_01.png` |
| `build` | Subagente implementa | 3 | `emotes/aoe-yolo/build/build_01.png` |
| `verify` | Subagente verifica | 3 | `emotes/aoe-yolo/verify/verify_01.png` |
| `judge` | Subagente juzga | 3 | `emotes/aoe-yolo/judge/judge_01.png` |
| `review` | Subagente revisa | 3 | `emotes/aoe-yolo/review/review_01.png` |
| `jira` | Subagente Jira | 3 | `emotes/aoe-yolo/jira/jira_01.png` |
| `jobs` | Jobs en background | 3 | `emotes/aoe-yolo/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 3 | `emotes/aoe-yolo/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 3 | `emotes/aoe-yolo/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 3 | `emotes/aoe-yolo/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 3 | `emotes/aoe-yolo/grandma/grandma_01.png` |
| `bye` | Despedida | 3 | `emotes/aoe-yolo/bye/bye_01.png` |

## cs16

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/cs16/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/cs16/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/cs16/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/cs16/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/cs16/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/cs16/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 3 | `emotes/cs16/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/cs16/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/cs16/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/cs16/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/cs16/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/cs16/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/cs16/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/cs16/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/cs16/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/cs16/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/cs16/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/cs16/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/cs16/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/cs16/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/cs16/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/cs16/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/cs16/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/cs16/bye/bye_01.png` |

## cs16-yolo

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/cs16-yolo/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/cs16-yolo/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/cs16-yolo/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/cs16-yolo/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/cs16-yolo/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/cs16-yolo/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 3 | `emotes/cs16-yolo/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/cs16-yolo/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/cs16-yolo/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/cs16-yolo/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/cs16-yolo/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/cs16-yolo/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/cs16-yolo/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/cs16-yolo/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/cs16-yolo/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/cs16-yolo/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/cs16-yolo/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/cs16-yolo/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/cs16-yolo/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/cs16-yolo/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/cs16-yolo/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/cs16-yolo/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/cs16-yolo/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/cs16-yolo/bye/bye_01.png` |

## starcraft

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/starcraft/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/starcraft/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/starcraft/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/starcraft/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/starcraft/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/starcraft/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 2 | `emotes/starcraft/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/starcraft/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/starcraft/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/starcraft/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/starcraft/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/starcraft/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/starcraft/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/starcraft/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/starcraft/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/starcraft/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/starcraft/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/starcraft/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/starcraft/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/starcraft/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/starcraft/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/starcraft/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/starcraft/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/starcraft/bye/bye_01.png` |

## starcraft-yolo

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/starcraft-yolo/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/starcraft-yolo/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/starcraft-yolo/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/starcraft-yolo/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/starcraft-yolo/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/starcraft-yolo/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 2 | `emotes/starcraft-yolo/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/starcraft-yolo/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/starcraft-yolo/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/starcraft-yolo/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/starcraft-yolo/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/starcraft-yolo/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/starcraft-yolo/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/starcraft-yolo/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/starcraft-yolo/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/starcraft-yolo/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/starcraft-yolo/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/starcraft-yolo/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/starcraft-yolo/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/starcraft-yolo/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/starcraft-yolo/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/starcraft-yolo/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/starcraft-yolo/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/starcraft-yolo/bye/bye_01.png` |

## lol

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/lol/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/lol/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/lol/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/lol/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/lol/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/lol/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 2 | `emotes/lol/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/lol/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/lol/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/lol/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/lol/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/lol/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/lol/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/lol/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/lol/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/lol/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/lol/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/lol/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/lol/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/lol/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/lol/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/lol/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/lol/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/lol/bye/bye_01.png` |

## lol-yolo

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/lol-yolo/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/lol-yolo/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/lol-yolo/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/lol-yolo/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/lol-yolo/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/lol-yolo/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 2 | `emotes/lol-yolo/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/lol-yolo/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/lol-yolo/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/lol-yolo/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/lol-yolo/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/lol-yolo/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/lol-yolo/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/lol-yolo/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/lol-yolo/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/lol-yolo/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/lol-yolo/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/lol-yolo/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/lol-yolo/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/lol-yolo/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/lol-yolo/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/lol-yolo/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/lol-yolo/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/lol-yolo/bye/bye_01.png` |

## minecraft

| Estado | Acción | Frames | Thumbnail |
|---|---|---|---|
| `hi` | Sesión arranca | 2 | `emotes/minecraft/hi/hi_01.png` |
| `idle` | Esperando input | 2 | `emotes/minecraft/idle/idle.png` |
| `think` | El modelo razona | 2 | `emotes/minecraft/think/think_01.png` |
| `talk` | El modelo responde | 4 | `emotes/minecraft/talk/talk_close.png` |
| `read` | Lee código/memoria | 2 | `emotes/minecraft/read/read_01.png` |
| `write` | Edita código | 2 | `emotes/minecraft/write/write_01.png` |
| `tool` | Ejecuta otras herramientas | 3 | `emotes/minecraft/tool/tool_01.png` |
| `ask` | Pregunta sí/no en pantalla | 2 | `emotes/minecraft/ask/ask_01.png` |
| `success` | Terminó bien | 2 | `emotes/minecraft/success/success_01.png` |
| `failure` | Algo falló | 2 | `emotes/minecraft/failure/down_01.png` |
| `compact` | Compactación de contexto | 2 | `emotes/minecraft/compact/compact_01.png` |
| `delegate` | Subagentes genéricos | 2 | `emotes/minecraft/delegate/delegate_01.png` |
| `explore` | Subagente explorador | 2 | `emotes/minecraft/explore/explore_01.png` |
| `build` | Subagente implementa | 2 | `emotes/minecraft/build/build_01.png` |
| `verify` | Subagente verifica | 2 | `emotes/minecraft/verify/verify_01.png` |
| `judge` | Subagente juzga | 2 | `emotes/minecraft/judge/judge_01.png` |
| `review` | Subagente revisa | 2 | `emotes/minecraft/review/review_01.png` |
| `jira` | Subagente Jira | 2 | `emotes/minecraft/jira/jira_01.png` |
| `jobs` | Jobs en background | 2 | `emotes/minecraft/jobs/jobs_01.png` |
| `yolo` | Modo YOLO | 2 | `emotes/minecraft/yolo/yolo_01.png` |
| `super-yolo` | Modo Super YOLO | 2 | `emotes/minecraft/super-yolo/super-yolo_01.png` |
| `remember` | Guarda memoria en Engram | 2 | `emotes/minecraft/remember/remember_01.png` |
| `grandma` | Idle largo (30s) | 2 | `emotes/minecraft/grandma/grandma_01.png` |
| `bye` | Despedida | 2 | `emotes/minecraft/bye/bye_01.png` |
