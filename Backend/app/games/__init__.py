"""Motor de juegos modular.

`base.py` define la interfaz común (BaseGame) y cada juego vive en su propia
subcarpeta (ej. `blackjack/`).
"""

from app.games.base import BaseGame
from app.games.blackjack.game import BlackjackGame

__all__ = ["BaseGame", "BlackjackGame"]
