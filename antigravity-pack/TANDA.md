# TANDA — 24 estados (reemplazo total de `emotes/aoe/`)

2 poses por estado. Nombres `estado_01.png`, `estado_02.png`.

1. `hi/` — aldeano saludo. 01 mano arriba, 02 mano abajo.
2. `idle/` — YA ESTÁ (`idle.png` + `idle_blink.png`). No tocar.
3. `think/` — monje. 01 mano en barbilla bastón abajo, 02 cabeza ladeada bastón abajo.
4. `talk/` — YA ESTÁ (5 bocas con pesos). No tocar.
5. `read/` — scout a caballo con antorcha. 01 antorcha izq, 02 antorcha der.
6. `write/` — aldeano construyendo. 01 martillo arriba, 02 martillo abajo.
7. `tool/` — ariete + aldeanos. 01 ariete atrás, 02 ariete adelante.
8. `ask/` — aldeano. 01 globo Y, 02 globo N.
9. `success/` — monje + unidad convertida de rodillas. 01 brazos arriba, 02 brazos abajo.
10. `failure/` — aldeano caído. 01 de frente, 02 de espaldas. Polvo + espada clavada.
11. `compact/` — monje achicándose. 01 tamaño normal, 02 tamaño chico, misma túnica.
12. `delegate/` — monje repartiendo. 01 bastón en alto wololo, 02 señalando aldeanos.
13. `explore/` — scout con linterna + huellas. 01 paso 1, 02 paso 2.
14. `build/` — herrero soldando ariete. 01 chispa prendida, 02 apagada.
15. `verify/` — guardián escudo + sello verde. 01 sello arriba, 02 sello estampado.
16. `judge/` — rey/monje con mazo. 01 mazo arriba, 02 mazo abajo.
17. `review/` — monje escriba pluma roja + pergamino. 01 escribiendo, 02 levantando pluma.
18. `jira/` — castillo cohete madera. 01 despegando, 02 en el aire.
19. `jobs/` — aldeano mate + barra. 01 tomando, 02 mirando barra.
20. `yolo/` — aldeano vincha YOLO + cohete. 01 izq, 02 der.
21. `super-yolo/` — igual + sol. 01 izq, 02 der.
22. `remember/` — monje + elefante. 01 susurro, 02 trompa arriba.
23. `grandma/` — aldeana tejiendo. 01 manos arriba, 02 abajo.
24. `bye/` — aldeano sacándose sombrero. 01 puesto, 02 en mano.

`aoe-yolo/` no se pide: se duplica acá con `scripts/sprites/gen_aoe_yolo.py`.

## Encuadre (de las originales del proyecto)
Cuerpo entero siempre visible, de cabeza a pies, centrado, de frente o 3/4. El personaje ocupa el alto del cuadro con poco margen (el bastón del monje entra vertical justo). Fondo transparente, sin recortes de pies/cabeza/bastón.
