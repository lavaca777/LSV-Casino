from __future__ import annotations

import random

from games.cartas import Baraja, Carta


def valor_mano(mano: list[Carta]) -> int:
    total = 0
    ases = 0

    for carta in mano:
        if carta.rango in ["J", "Q", "K"]:
            total += 10
        elif carta.rango == "A":
            ases += 1
            total += 11
        else:
            total += int(carta.rango)

    while total > 21 and ases > 0:
        total -= 10
        ases -= 1

    return total


def es_blackjack_natural(mano: list[Carta]) -> bool:
    return len(mano) == 2 and valor_mano(mano) == 21


def es_busted(mano: list[Carta]) -> bool:
    return valor_mano(mano) > 21


def es_mano_blanda(mano: list[Carta]) -> bool:
    tiene_as = any(c.rango == "A" for c in mano)
    return tiene_as and valor_mano(mano) != _total_duro(mano)


def _total_duro(mano: list[Carta]) -> int:
    total = 0
    for carta in mano:
        if carta.rango == "A":
            total += 1
        elif carta.rango in ("J", "Q", "K"):
            total += 10
        else:
            total += int(carta.rango)
    return total


def desicion_bot(mano: list[Carta], rng: random.Random | None = None) -> str:
    rng = rng or random
    valorbot = valor_mano(mano)
    if valorbot < 17:
        return "hit"
    if valorbot == 17 and es_mano_blanda(mano):
        return "hit" if rng.random() < 0.5 else "stand"
    return "stand"


def turno_bot(mano: list[Carta], baraja: Baraja, rng: random.Random | None = None) -> list[Carta]:
    while desicion_bot(mano, rng) == "hit" and not es_busted(mano):
        mano.append(baraja.repartir_carta())
    return mano


def jugar_ronda(mano_jugador: list[Carta], baraja: Baraja, num_bots: int = 2) -> dict:
    manos_bots = [
        turno_bot(baraja.repartir_cartas(2), baraja)
        for _ in range(num_bots)
    ]
    return {"manos_bots": manos_bots, "mano_jugador": mano_jugador}


def resolver_ganador(mano_jugador: list[Carta], manos_bots: list[list[Carta]]) -> str:
    if es_busted(mano_jugador):
        return "loss"

    total_jugador = valor_mano(mano_jugador)
    totales_bots = [valor_mano(h) for h in manos_bots]

    totales_bots_activos = [t for t in totales_bots if t <= 21]

    if not totales_bots_activos:
        return "win"  # todos los bots se pasaron

    mejor_bot = max(totales_bots_activos)
    if total_jugador > mejor_bot:
        return "win"
    if total_jugador == mejor_bot:
        return "draw"
    return "loss"