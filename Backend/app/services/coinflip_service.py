"""Servicio del juego Cara o Cruz.

Orquesta el flujo completo de una partida:
1. Validar la apuesta (mínimo y saldo disponible).
2. Ejecutar la lógica del juego (`CoinflipGame`).
3. Descontar la apuesta y pagar el payout en el wallet.
4. Registrar la sesión y el resultado en la base de datos.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.games.coinflip.game import CoinflipGame
from app.models import Game, GameResult, GameSession
from app.services import wallet_service


def _get_game_id(db: Session, name: str) -> uuid.UUID:
    """Busca el id del juego en el catálogo (tabla `games`)."""
    game = db.query(Game).filter(Game.name == name).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Game '{name}' not found in catalog",
        )
    return game.id


def play_coinflip(
    db: Session, user_id: uuid.UUID, bet: Decimal, eleccion: str
) -> dict:
    """Juega una ronda de cara o cruz y actualiza el wallet."""
    # 1. Validar apuesta (mínimo $5 y que no supere el saldo).
    wallet_service.validate_bet(db, user_id, bet)

    # 2. Ejecutar la partida.
    game = CoinflipGame()
    resultado = game.play(user_id, bet, eleccion=eleccion)
    payout = resultado["payout"]

    # 3. Descontar la apuesta y pagar el payout si ganó.
    wallet_service.update_balance(db, user_id, -bet)
    if payout > 0:
        wallet_service.update_balance(db, user_id, payout)

    # 4. Registrar la sesión y el detalle de la partida.
    #    (para coinflip guardamos la elección y el resultado del lanzamiento)
    session = GameSession(
        user_id=user_id,
        game_id=_get_game_id(db, game.name),
        bet=bet,
        ended_at=datetime.now(timezone.utc),
        result=resultado["resultado"],
        payout=payout,
    )
    db.add(session)
    db.flush()
    db.add(
        GameResult(
            session_id=session.id,
            result_type=resultado["resultado"],
            player_hand=[{"eleccion": resultado["eleccion"]}],
            bot_hands=[{"moneda": resultado["moneda"]}],
        )
    )
    db.commit()

    nuevo_balance = wallet_service.get_wallet(db, user_id).balance
    return {
        "resultado": resultado["resultado"],
        "eleccion": resultado["eleccion"],
        "moneda": resultado["moneda"],
        "bet": float(bet),
        "payout": float(payout),
        "nuevo_balance": float(nuevo_balance),
    }
