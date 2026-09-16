"""Datos iniciales (seed) del catálogo de juegos.

Inserta los juegos disponibles en la tabla `games` si aún no existen.
"""

from sqlalchemy.orm import Session

from app.games.blackjack.game import BlackjackGame
from app.games.coinflip.game import CoinflipGame
from app.models import Game

# Juegos disponibles en el catálogo.
JUEGOS = (BlackjackGame, CoinflipGame)


def seed_games(db: Session) -> None:
    """Registra los juegos del catálogo que aún no existan."""
    for juego_clase in JUEGOS:
        juego = juego_clase()
        existente = db.query(Game).filter(Game.name == juego.name).first()
        if existente is not None:
            continue

        db.add(
            Game(
                name=juego.name,
                min_bet=juego.min_bet,
                max_bet=juego.max_bet,
                house_edge=juego.house_edge,
            )
        )
    db.commit()
