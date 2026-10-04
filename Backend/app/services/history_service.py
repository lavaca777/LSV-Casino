"""Servicio de historial de partidas.

Lista y detalle de las partidas jugadas por un usuario. Las queries usan
JOIN con la tabla `games` para traer el nombre del juego sin caer en N+1
(sin consultar el juego por cada partida).
"""

import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Game, GameResult, GameSession


def list_sessions(
    db: Session,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
    game_name: str | None = None,
) -> tuple[int, list[dict]]:
    """Devuelve (total, partidas) ordenadas por fecha DESC, con paginación y filtro.

    - `limit` / `offset`: paginación (20 por página por defecto).
    - `game_name`: filtra por juego (ej. "blackjack"); None = todos.
    """
    query = (
        db.query(GameSession, Game.name)
        .join(Game, GameSession.game_id == Game.id)
        .filter(GameSession.user_id == user_id)
    )
    if game_name:
        query = query.filter(Game.name == game_name)

    total = query.count()
    rows = (
        query.order_by(GameSession.started_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return total, [_to_item(session, name) for session, name in rows]


def get_session_detail(
    db: Session, user_id: uuid.UUID, session_id: uuid.UUID
) -> dict:
    """Detalle de una partida (incluye las manos jugadas y su duración)."""
    row = (
        db.query(GameSession, Game.name, GameResult)
        .join(Game, GameSession.game_id == Game.id)
        .outerjoin(GameResult, GameResult.session_id == GameSession.id)
        .filter(GameSession.id == session_id, GameSession.user_id == user_id)
        .first()
    )
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game session not found"
        )

    session, game_name, game_result = row
    detail = _to_item(session, game_name)
    detail["player_hand"] = game_result.player_hand if game_result else []
    detail["bot_hands"] = game_result.bot_hands if game_result else []
    detail["duration_seconds"] = (
        (session.ended_at - session.started_at).total_seconds()
        if session.ended_at
        else None
    )
    return detail


def _to_item(session: GameSession, game_name: str) -> dict:
    return {
        "id": session.id,
        "game_name": game_name,
        "date": session.started_at,
        "bet": float(session.bet),
        "result": session.result,
        "payout": float(session.payout),
        "balance_after": float(session.balance_after),
    }
