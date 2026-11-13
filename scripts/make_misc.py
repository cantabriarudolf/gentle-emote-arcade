#!/usr/bin/env python3
"""Arma el pack misceláneo combinando un sonido de cada uno de los 5 packs.

No duplica WAVs: sounds/misc/seleccion.json guarda valores "pack/tallo" y el
resolver de apply_sounds.sh / index.ts / pruebas.py los resuelve contra el
pack origen. Re-ejecutar regenera el mismo archivo (semilla fija).
"""
import json
import os
import random
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONIDOS = os.path.join(RAIZ, "sounds")
PACKS = ["aoe", "minecraft", "cs16", "starcraft", "lol"]
EVENTOS = (
    "session.started",
    "agent.started",
    "agent.completed",
    "agent.failed",
    "agent.cancelled",
    "agent.attention",
    "subagent.queued",
    "subagent.running",
    "subagent.waiting",
    "subagent.completed",
    "subagent.failed",
    "subagent.cancelled",
    "subagent.timed_out",
    "context.high",
)


def leer_seleccion(pack):
    ruta = os.path.join(SONIDOS, pack, "seleccion.json")
    with open(ruta, encoding="utf-8") as fh:
        datos = json.load(fh)
    return datos.get("choices") or {}


def main():
    rng = random.Random(20250308)
    choices = {}
    for evento in EVENTOS:
        candidatos = []
        for pack in PACKS:
            tallo = (leer_seleccion(pack).get(evento))
            if tallo:
                candidatos.append((pack, tallo))
        if not candidatos:
            choices[evento] = None
            continue
        pack, tallo = rng.choice(candidatos)
        choices[evento] = "%s/%s" % (pack, tallo)

    destino_dir = os.path.join(SONIDOS, "misc")
    os.makedirs(destino_dir, exist_ok=True)
    destino = os.path.join(destino_dir, "seleccion.json")
    payload = {
        "schema": "gentle-emote-arcade.sounds/v1",
        "soundsDir": "sounds/misc",
        "choices": choices,
    }
    with open(destino, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("generado %s (%d eventos)" % (destino, len(choices)))


if __name__ == "__main__":
    main()
