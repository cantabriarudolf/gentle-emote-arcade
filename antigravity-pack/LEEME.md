# Ve a la carpeta y lee esto — Antigravity Pack AoE

Sos Antigravity. Tu carpeta de trabajo es `gentle-emote-arcade/antigravity-pack/`.

Leé en este orden:
1. Este archivo (`LEEME.md`) entero.
2. `MAPA-ESCENAS-aoe.md` (qué escena = qué sprite = qué sonido).
3. `refs/` (cómo se ve el aldeano base).

No generes nada hasta leer los 3. Al terminar devolvé solo PNGs sueltos.

## Qué es esto
Fork `gentle-emote-arcade`: el avatar Gentleman se reemplaza por sprites de Age of Empires que actúan lo mismo que el agente en Gentle Shell, y se complementa con los audios del juego para entender auditivamente qué está haciendo el agente. 24 estados. El set activo es `emotes/aoe/`, su gemelo YOLO es `emotes/aoe-yolo/` (ese lo generamos acá, no lo pidas).

Este brief se publica como documentación del pipeline de arte. En el repo viajan `emotes/` (los dos sets AoE) y `sounds/` (13 wav + `seleccion.json`); `datas/` (mp3 crudos), `previews/` (previews ×8 y recortes) y `lab/` + `test/` quedan fuera por `.gitignore`, aunque siguen en el disco del autor.

## Base que no se toca
- `refs/idle.png` (48×40): el aldeano final. Mismo personaje, misma paleta en todo.
- `refs/raw_idle.jpg` (1024×1024): fuente para detalle. **No viaja en el repo publicado** (`.gitignore` lo excluye); si trabajás desde un clon y te falta, pedila o ampliá `refs/idle.png`.
- `refs/idle_preview.png` (384×320 = ×8): solo para ver en grande.

## Formato obligatorio (si no cumple, se rechaza)
- PNG `48×40`, 8-bit RGBA, no interlazado, fondo transparente (alfa real, no blanco/negro).
- Pixel art nítido, sin blur, sin sombra externa.
- 1 archivo por pose: `estado_01.png`, `estado_02.png` (ej: `tool_01.png`, `tool_02.png`).
- Movimiento = 2 poses por estado. 3 solo si es caminar/golpear. 1 quieto solo si se indica.
- Nada de gif, nada de sprite-sheet, nada de JPG en la entrega. Preview ×8 aparte solo para revisar.

## Elenco (dinámico, no solo aldeano y monje)
- Aldeano (sombrero paja, túnica marrón) = ref base. Estados físicos.
- Monje (túnica crema, capucha, **bastón largo con cruz que levanta en wololo**). Estados de conversión.
- Secundarios cotejados en la wiki (ver `FUENTES.md`): Scout a caballo, Ariete + aldeanos, Herrero, Guardián/Campeón con escudo, Rey con mazo, Elefante, Aldeana tejiendo, Castillo + cohete madera.

## Tanda a entregar
Ver `TANDA.md`: los 24 estados con sus poses c/u. Ya instalados con movimiento.

## Dónde cotejar formas (si dudás de un personaje, mirá acá antes de inventar)
Ver `FUENTES.md` con links exactos a Fandom, Sprites, ModDB y qué descargar de cada uno.

## Qué mirar antes de redibujar `tool` y `success`
Las entregas anteriores de esas dos escenas viven en `previews/` (`tool_01_preview.png`, `tool_02_preview.png`, `success_01_preview.png`, `success_02_preview.png`). No se publican: están solo en el disco del autor.
