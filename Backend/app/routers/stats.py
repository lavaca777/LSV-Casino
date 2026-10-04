"""Endpoints de estadísticas del jugador."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import StatsResponse
from app.services import stats_service
from app.utils.security import CurrentUser

router = APIRouter(tags=["stats"])


def _ensure_owner(current_user: User, user_id: UUID) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own stats",
        )


@router.get("/users/{user_id}/stats", response_model=StatsResponse)
def get_stats(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> StatsResponse:
    """Estadísticas del jugador calculadas sobre su historial de partidas."""
    _ensure_owner(current_user, user_id)
    return stats_service.get_stats(db, user_id)
