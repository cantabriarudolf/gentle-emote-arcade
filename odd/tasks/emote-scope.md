# emote-scope — la selección de juego queda por proyecto

Alcance: que elegir juego (sprites + sonidos) en un proyecto no cambie el audio
ni los sprites de los demás. Estado: en curso.

## Specs

S1. Síntoma reportado: «he abierto una nueva sesion y tengo los dibujitos de
gentle pero consonidos de cs16».

S2. Regla: «al hacer un cambio en un proyecto esta replicando o las imagenes o
los sonidos en otros proyectos» no debe pasar. Elegir juego escribe sólo en el
proyecto elegido; ningún otro proyecto cambia su audio ni sus sprites.

S3. Modelo elegido: «Por proyecto, aplicado al abrir sesión».
Contrato literal de la opción aceptada:

```
select_game.sh / emote:juego
  └─ escribe: <proyecto>/.pi/extensions/gentle-emote/config.json
              <proyecto>/.pi/extensions/game-select/projects.json
  └─ NO toca: ~/.gentle-shell/config/gentle-ai/notifications.json

hook session_start(cwd)
  └─ lee projects.json[cwd] → aplica sonidos+sprites globales con backup
  └─ sin entrada → restaura default Gentle
```

S4. Limpieza acordada: «lo recomendado, debe quedar fino para su push». Es
decir: restaurar el global a Gentle, quitar los packs copiados a mano del dir
global, y dejar de parchear el paquete npm instalado.

S5. Los tests corren con `node --test tests/game-select.test.ts` en un sandbox
temporal y no tocan la config viva ni el audio real.

S6. Saldar los avisos no bloqueantes de la review: «en criollo, si hay algo que
saldar dale segun tu plan». Reglas derivadas de los advisories, en orden:
1. Un config que no parsea no se pisa: `setEmoteSet`, el bloque python de
   `select_game.sh` y la escritura viva del hook dejan el archivo intacto y lo
   reportan (R3-1, R3-2, R1-corrupt-baseline-wipe).
2. Los respaldos son atómicos y con nombre único: tmp + rename, sello con ms o
   sufijo, sin pisar un backup previo (R1-nonatomic-backup, R3-5, R4-2).
3. Un fallo de escritura tiene motivo propio: no se confunde con `sin-cambio`,
   y el hook avisa en la UI (R1-silent-apply-failure, R3-3, R4-1).
4. Retención de respaldos y copy de packs auto-reparable (R4-5, R4-4).
5. Un test ejercita que `session_start` con `reason: "reload"` aplica el audio
   (R3-4).

## Tasks

| ID | Qué | Specs | Ruta | Commit |
| --- | --- | --- | --- | --- |
| T1 | Documento de feature y reconciliación del plan | — | inline | — |
| T2 | Tests del contrato nuevo (selector project-only, hook por proyecto, baseline) | S1-S3, S5 | inline | C1 |
| T3 | Extensión: aplicar por proyecto al abrir sesión y dejar de escribir el global | S2, S3 | inline | C1 |
| T4 | Scripts: `select_game.sh` project-only, `apply_sounds.sh` explícito, fuera `patch_debug_log.sh` | S2, S3, S4 | inline | C2 |
| T5 | Limpieza del lado global en esta máquina (baseline, packs copiados, paquete npm) | S4 | inline | — |
| T6 | Docs (README, BETA) y verificación final | S1-S5 | inline | C3 |
| T7 | Saldar los advisories de la review (parseo, respaldos atómicos, fallo visible, retención, test de reload) | S6 | worker | C6 |

Cortes de revisión: C1 = 440 líneas (extensión + tests), C2 = 229 líneas
(scripts), C3 = docs. Rama `fix/emote-scope`.

## Log

L1. «hay un tema que debemos corregir, he abierto una nueva sesion y tengo los
dibujitos de gentle pero consonidos de cs16, creo que al hacer un cambio en un
proyecto esta replicando o las imagenes o los sonidos en otros proyectos»

L2. Decisión de alcance: «Por proyecto, aplicado al abrir sesión».

L3. Decisión de limpieza: «lo recomendado, debe quedar fino para su push».

L4. Diagnóstico verificado: `~/.gentle-shell/config/gentle-ai/notifications.json`
tiene los 14 eventos con `file:` absoluto a `sounds/cs16/` de este repo;
`scripts/select_game.sh:95-96` y `extensions/game-select/index.ts:595,617`
escriben global + proyecto en cada selección (README:160-162 lo documentaba);
`projects.json` muestra `guksys` y `newsthulasarira` en `cs16`. En AoE la capa
de proyecto decía `gentle`: de ahí los dibujos de gentle con sonido cs16.

L5. Corte 1 (C1, `61a579a`): extensión + tests, 440 líneas. `node --test`
41/41 verde. Se pasa el corte y sigue C2.

L6. Corte 2 (C2, `c52dc6f`): scripts, 229 líneas. `bash -n` en los cuatro y
smoke test de `select_game.sh` en un proyecto temporal: config creada, pack
copiado, mapa con la entrada y la config viva intacta.

L7. Limpieza global (T5): baseline = `notifications.json.bak-20261107-233953`
(estado previo al arcade, AoE v1 desde `~/Música/AudiosGentleShell/waw`), copiado
a `notifications.baseline.json` y aplicado a la config viva con backup del cs16.
`emote-set` global → `gentleman`. `gentleman.bak` fuera del paquete npm. Los
cuatro proyectos del mapa (AoE, Compass, newsthulasarira, guksys) quedaron con
su config y su pack locales, así nadie pierde el arte.

L8. Desvío consciente de S4: los 11 packs del dir global **no** se borraron.
Compass, newsthulasarira y guksys no tenían copia local y dependían de ese dir
para el arte; borrarlo les cambiaba los sprites. Queda como biblioteca
compartida (el `check_install.sh` lo avisa) y la selección ya no lo usa.

L9. Verificación final: `node --test tests/game-select.test.ts tests/packs.test.ts`
52/52. `check_install.sh` queda con 1 drift real: el paquete npm sigue parcheado
(`MAX_LOG_BYTES`); se arregla con `pi update`, que no corre este corte.

L10. C4: `notifications.json` se escribe con tmp + rename. Dos sesiones en
proyectos distintos comparten ese archivo (la última que abre manda), así que
una lectura nunca puede verlo a medio escribir.

L11. C5: `tests/select-game.test.ts` cubre el selector bash (config, pack y
mapa por proyecto; dos proyectos sin pisarse; `--dry-run` sin escrituras). Con
eso el corte de scripts deja de depender de una prueba manual: `Risk: none`.

L12. Review nativa: cerrada y aprobada (lineage `review-1e9f9f92d6fec840`,
authority burned), 14 advisories informativos, ninguno abre corrección. El
candado de lineage se resolvió reanudando, sin reset. El humano autorizó
saldarlos: «en criollo, si hay algo que saldar dale segun tu plan» → T7.
