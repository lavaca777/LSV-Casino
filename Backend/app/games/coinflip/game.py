"""Juego Cara o Cruz.

El jugador elige "cara" o "cruz". Se lanza una moneda al aire; si acierta,
gana el doble de lo apostado. Es el juego más simple del casino y sirve para
probar el flujo completo (apuesta, resultado y payout).
"""

import random
from decimal import Decimal
from typing import Any

from app.games.base import BaseGame

CARAS = ("cara", "cruz")


class CoinflipGame(BaseGame):
    """Implementación del contrato BaseGame para Cara o Cruz."""

    name = "coinflip"
    min_bet = Decimal("5")
    max_bet = Decimal("999999")
    house_edge = Decimal("0")

    def get_rules(self) -> dict:
        return {
            "nombre": "Cara o Cruz",
            "descripcion": "Elige cara o cruz. Si aciertas, ganas el doble de tu apuesta.",
            "min_bet": float(self.min_bet),
            "max_bet": float(self.max_bet),
            "opciones": list(CARAS),
            "payout": "acierto = apuesta x2",
        }

    def get_house_edge(self) -> float:
        return float(self.house_edge)

    def play(self, user_id: Any, bet: Decimal, **opciones) -> dict:
        """Lanza la moneda y resuelve la apuesta.

        Opciones requeridas:
        - eleccion: "cara" o "cruz".

        Devuelve el resultado ("win"/"loss") y el payout (apuesta x2 si acierta).
        """
        eleccion = opciones.get("eleccion")
        if eleccion not in CARAS:
            raise ValueError("eleccion debe ser 'cara' o 'cruz'")

        moneda = random.choice(CARAS)
        gano = eleccion == moneda

        return {
            "user_id": user_id,
            "bet": bet,
            "eleccion": eleccion,
            "moneda": moneda,
            "resultado": "win" if gano else "loss",
            "payout": bet * 2 if gano else Decimal("0"),
        }
