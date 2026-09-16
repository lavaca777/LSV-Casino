"""Interfaz base para todos los juegos del casino.

Cada juego (blackjack, y los que se agreguen en el futuro) debe heredar de
`BaseGame` e implementar sus métodos. Así el resto del sistema (routers,
servicios, frontend) puede tratar a cualquier juego de la misma forma sin
saber cómo funciona por dentro.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class BaseGame(ABC):
    """Contrato común que todo juego debe cumplir.

    Atributos de clase (metadata del juego):
    - name: identificador corto, ej. "blackjack".
    - min_bet / max_bet: rango de apuesta permitido.
    - house_edge: ventaja de la casa (referencia informativa).
    """

    name: str
    min_bet: Decimal
    max_bet: Decimal
    house_edge: Decimal

    @abstractmethod
    def play(self, user_id: Any, bet: Decimal, **opciones) -> dict:
        """Ejecuta una partida y devuelve el resultado.

        `**opciones` permite pasar parámetros propios de cada juego
        (ej. la elección "cara"/"cruz" en coinflip). Los juegos que no los
        necesiten simplemente los ignoran.

        NOTA: la versión completa (payout y actualización de wallet) se
        implementará cuando exista el servicio de juego. Ver `game.py`.
        """
        raise NotImplementedError

    @abstractmethod
    def get_rules(self) -> dict:
        """Devuelve las reglas del juego para mostrarlas al usuario."""
        raise NotImplementedError

    @abstractmethod
    def get_house_edge(self) -> float:
        """Devuelve la ventaja de la casa."""
        raise NotImplementedError
