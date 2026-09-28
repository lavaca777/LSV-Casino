"""Clase BlackjackGame: adapta la lógica existente de `blackjack.py` a la
interfaz `BaseGame`.

A diferencia de un juego de una sola tirada (coinflip), blackjack se
juega en varios pasos: play() inicia la ronda (reparte y resuelve a los
bots, que no esperan input humano), pero el resultado final depende de
las decisiones del jugador -- así que se agregan hit()/stand() además
del contrato mínimo de BaseGame. Blackjack natural (21 con las primeras
2 cartas) se resuelve directo en play(), porque no tiene sentido pedir
más cartas con 21.
"""

from decimal import Decimal

from app.games.base import BaseGame
from app.games.blackjack.blackjack import (
    es_blackjack_natural,
    es_busted,
    jugar_ronda,
    resolver_ganador,
    valor_mano,
)
from app.games.blackjack.cartas import Baraja, Carta


def carta_a_dict(carta: Carta) -> dict:
    """Convierte una Carta a un dict serializable (para JSONB/respuestas JSON)."""
    return {"palo": carta.palo.value, "rango": carta.rango}


class BlackjackGame(BaseGame):
    """Implementación del contrato BaseGame para el juego de Blackjack."""

    name = "blackjack"
    min_bet = Decimal("5")
    max_bet = Decimal("999999")
    house_edge = Decimal("0.02")

    def get_rules(self) -> dict:
        return {
            "nombre": "Blackjack",
            "descripcion": (
                "Juega contra 2 bots. Acércate a 21 sin pasarte. "
                "Gana quien tenga la mano más alta sin superar 21."
            ),
            "min_bet": float(self.min_bet),
            "max_bet": float(self.max_bet),
            "acciones": ["hit", "stand"],
        }

    def get_house_edge(self) -> float:
        return float(self.house_edge)

    def play(self, user_id, bet: Decimal, baraja: Baraja | None = None, **opciones) -> dict:
        """Inicia una ronda: reparte la mano del jugador y resuelve los
        bots. Si el jugador saca blackjack natural, la ronda se resuelve
        aquí mismo; si no, devuelve turn="player" para que hit()/stand()
        sigan el juego.

        `baraja` es inyectable para tests deterministas; en producción
        se deja en None y se crea una baraja real.

        Devuelve, además de los datos serializables, "baraja" (el
        objeto vivo, para que hit() lo siga usando) -- es
        responsabilidad del llamador (el service) no exponer eso en
        una respuesta HTTP.
        """
        baraja = baraja or Baraja()
        mano_jugador = baraja.repartir_cartas(2)
        ronda = jugar_ronda(mano_jugador, baraja, num_bots=2)
        manos_bots = ronda["manos_bots"]

        resultado = None
        turn = "player"
        if es_blackjack_natural(mano_jugador):
            resultado = resolver_ganador(mano_jugador, manos_bots)
            turn = "done"

        return {
            "mano_jugador": mano_jugador,
            "manos_bots": manos_bots,
            "baraja": baraja,
            "turn": turn,
            "resultado": resultado,
        }

    def hit(self, mano_jugador: list[Carta], baraja: Baraja) -> dict:
        """El jugador pide una carta. Si se pasa, la ronda termina en derrota."""
        mano_jugador.append(baraja.repartir_carta())
        if es_busted(mano_jugador):
            return {"mano_jugador": mano_jugador, "turn": "done", "resultado": "loss"}
        return {"mano_jugador": mano_jugador, "turn": "player", "resultado": None}

    def stand(self, mano_jugador: list[Carta], manos_bots: list[list[Carta]]) -> dict:
        """El jugador se planta: se resuelve el resultado final."""
        resultado = resolver_ganador(mano_jugador, manos_bots)
        return {"mano_jugador": mano_jugador, "turn": "done", "resultado": resultado}