"""Endpoints de juegos.

Incluye el catálogo (`GET /games`) y los endpoints de juego disponibles
(por ahora, cara o cruz). Los de blackjack se agregarán cuando exista su
servicio.
"""

from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Game
from app.schemas import CoinflipPlayRequest, CoinflipPlayResponse, GameResponse
from app.services import coinflip_service
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
