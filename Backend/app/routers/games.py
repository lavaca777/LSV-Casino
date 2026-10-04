"""Endpoints de juegos.

Incluye el catálogo (`GET /games`) y los endpoints de juego disponibles:
cara o cruz (una sola tirada) y blackjack (en varios pasos: start/hit/stand).
"""

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Game
from app.schemas import (
    BlackjackPlayResponse,
    BlackjackStartRequest,
    CoinflipPlayRequest,
    CoinflipPlayResponse,
    GameResponse,
)
from app.services import blackjack_service, coinflip_service
from app.utils.security import CurrentUser

router = APIRouter(prefix="/games", tags=["games"])


@router.get("", response_model=list[GameResponse])
def list_games(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[Game]:
    """Lista los juegos disponibles en el catálogo."""
    return db.query(Game).order_by(Game.name).all()


@router.post("/coinflip/play", response_model=CoinflipPlayResponse)
def play_coinflip(
    payload: CoinflipPlayRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> CoinflipPlayResponse:
    """Juega una ronda de cara o cruz y actualiza el saldo del usuario."""
    return coinflip_service.play_coinflip(
        db, current_user.id, Decimal(str(payload.bet)), payload.eleccion
    )


@router.post(
    "/blackjack/start",
    response_model=BlackjackPlayResponse,
    response_model_exclude_none=True,
)
def start_blackjack(
    payload: BlackjackStartRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Inicia una ronda de blackjack: descuenta la apuesta, reparte y
    resuelve los bots. Si sale blackjack natural, ya viene resuelta."""
    return blackjack_service.start_round(
        db, current_user.id, Decimal(str(payload.bet))
    )
 
 
@router.post(
    "/blackjack/{session_id}/hit",
    response_model=BlackjackPlayResponse,
    response_model_exclude_none=True,
)
def hit_blackjack(
    session_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """El jugador pide una carta en una ronda abierta."""
    return blackjack_service.hit(db, current_user.id, session_id)
 
 
@router.post(
    "/blackjack/{session_id}/stand",
    response_model=BlackjackPlayResponse,
    response_model_exclude_none=True,
)
def stand_blackjack(
    session_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """El jugador se planta: se resuelve el resultado final."""
    return blackjack_service.stand(db, current_user.id, session_id)


@router.get(
    "/blackjack/{session_id}",
    response_model=BlackjackPlayResponse,
    response_model_exclude_none=True,
)
def get_blackjack_session(
    session_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Consulta el estado de una sesión (ronda abierta o terminada).

    Útil para retomar una ronda tras recargar la página.
    """
    return blackjack_service.get_session(db, current_user.id, session_id)
