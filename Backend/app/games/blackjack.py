import __future__ from annotations
from games.cartas import Carta

def valor_mano (mano: list[Carta]) -> int:
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
    total_duro = sum(
        11 if c.rango == "A" else (10 if c.rango in ("J", "Q", "K") else int(c.rango))
        for c in mano
    )
    tiene_as = any(c.rango == "A" for c in mano)
    return tiene_as and total_duro <= 21 and valor_mano(mano) != total_duro

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
    valorbot = valor_mano(mano)
    if valorbot < 17:
        return "hit"
    if valorbot >= 17 and es_mano_blanda(mano):
        return "hit" if rng.random() < 0.5 else "stand"
    return "stand"

def turno_bot(mano: list[Carta], baraja: Baraja, rng: random.Random | None = None) -> list[Carta]:
    while desicion_bot(mano, rng) == "hit" and not es_busted(mano):
        mano += baraja.repartir_carta(1)
    return mano

def jugar_ronda(mano_jugador: list[Carta], baraja: Baraja, num_bots: int = 2) -> dict:

    manos_bots = [turno_bot(baraja.repartir_carta(2), baraja, None) for _ in range(num_bots)]
    return {"manos_bots": manos_bots, "mano_jugador": mano_jugador}
 
 
def resolve_winner(mano_jugador: list[Carta], manos_bots: list[list[Carta]]) -> str:
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
