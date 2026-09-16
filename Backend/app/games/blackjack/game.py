"""Clase BlackjackGame: adapta la lógica existente de `blackjack.py` a la
interfaz `BaseGame`.
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


def _carta_a_dict(carta: Carta) -> dict:
    """Convierte una Carta a un dict serializable (para respuestas JSON)."""
    return {"palo": carta.palo.value, "rango": carta.rango}


class BlackjackGame(BaseGame):
    """Implementación del contrato BaseGame para el juego de Blackjack."""

    name = "blackjack"
    min_bet = Decimal("5")
    max_bet = Decimal("999999")
    house_edge = Decimal("0.02")

    def get_rules(self) -> dict:
        """Reglas del juego (texto para mostrar al usuario)."""
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
        """Ventaja de la casa (referencia informativa)."""
        return float(self.house_edge)

    def play(self, user_id, bet: Decimal, **opciones) -> dict:
        """Ejecuta una ronda completa y devuelve el resultado.

        Reparte las cartas, juega los bots y resuelve el ganador usando las
        funciones de `blackjack.py`. El parámetro `**opciones` se acepta por
        compatibilidad con BaseGame pero este juego no lo usa.

        PENDIENTE (para el servicio de juego):
        - TODO(payout): calcular el pago según el resultado
          (win = bet * 2, draw = bet, loss = 0).
        - TODO(wallet): actualizar el balance del usuario con el payout
          (usar `wallet_service.update_balance`).
        - TODO(persistencia): guardar la `GameSession` y el `GameResult`
          en la base de datos.
        - TODO(blackjack natural): definir si el blackjack natural (21 con 2
          cartas) paga distinto.

        Por ahora solo devuelve las manos y el resultado, sin tocar dinero.
        """
        baraja = Baraja()
        mano_jugador = baraja.repartir_cartas(2)

        ronda = jugar_ronda(mano_jugador, baraja, num_bots=2)
        mano_final = ronda["mano_jugador"]
        manos_bots = ronda["manos_bots"]

        resultado = resolver_ganador(mano_final, manos_bots)

        return {
            "user_id": user_id,
            "bet": float(bet),
            "mano_jugador": [_carta_a_dict(c) for c in mano_final],
            "manos_bots": [[_carta_a_dict(c) for c in mano] for mano in manos_bots],
            "total_jugador": valor_mano(mano_final),
            "resultado": resultado,
            "jugador_blackjack": es_blackjack_natural(mano_final),
            "jugador_pasado": es_busted(mano_final),
            # Payout y balance se completan en el servicio de juego.
            "payout": None,
            "nuevo_balance": None,
        }
