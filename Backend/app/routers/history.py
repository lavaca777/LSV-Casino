"""Endpoints de historial de partidas.

Listado (con paginación y filtro por juego) y detalle de cada partida
del usuario autenticado.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import GameHistoryDetail, GameHistoryList
from app.services import history_service
from app.utils.security import CurrentUser

router = APIRouter(tags=["history"])


def _ensure_owner(current_user: User, user_id: UUID) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own game history",
        )


@router.get("/users/{user_id}/games", response_model=GameHistoryList)
def list_user_games(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    game: str | None = None,
) -> GameHistoryList:
    """Lista las partidas del usuario (más recientes primero).

    Parámetros de query: `limit` (máx 100), `offset` y `game` (filtro opcional).
    """
    _ensure_owner(current_user, user_id)
    total, games = history_service.list_sessions(db, user_id, limit, offset, game)
    return GameHistoryList(total=total, games=games)


@router.get("/users/{user_id}/games/{session_id}", response_model=GameHistoryDetail)
def get_user_game(
    user_id: UUID,
    session_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> GameHistoryDetail:
    """Detalle de una partida del usuario (incluye las manos jugadas)."""
    _ensure_owner(current_user, user_id)
    return history_service.get_session_detail(db, user_id, session_id)
