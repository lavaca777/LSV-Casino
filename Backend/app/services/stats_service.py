"""Servicio de estadísticas del jugador.

Calcula métricas sobre las partidas finalizadas del usuario (`GameSession`
con `result` no nulo). No usa tabla nueva: todo se deriva del historial y
del wallet.
"""

import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import GameSession
from app.services import wallet_service


def get_stats(db: Session, user_id: uuid.UUID) -> dict:
    """Calcula y devuelve todas las estadísticas del usuario."""
    # Se traen solo las columnas necesarias, en orden cronológico (para rachas).
    filas = (
        db.query(GameSession.result, GameSession.bet, GameSession.payout)
        .filter(GameSession.user_id == user_id, GameSession.result.isnot(None))
        .order_by(GameSession.started_at.asc())
        .all()
    )

    total = len(filas)
    won = sum(1 for r, _, _ in filas if r == "win")
    lost = sum(1 for r, _, _ in filas if r == "loss")
    drawn = sum(1 for r, _, _ in filas if r == "draw")

    total_bet = sum((bet for _, bet, _ in filas), Decimal("0"))
    total_payout = sum((payout for _, _, payout in filas), Decimal("0"))
    biggest_win = max((payout for _, _, payout in filas), default=Decimal("0"))

    win_rate = round((won / total) * 100, 2) if total else 0.0
    net_profit = total_payout - total_bet

    total_wagered = wallet_service.get_wallet(db, user_id).total_wagered

    return {
        "total_games": total,
        "total_games_won": won,
        "total_games_lost": lost,
        "total_games_drawn": drawn,
        "win_rate": win_rate,
        "current_streak": _current_streak([r for r, _, _ in filas]),
        "longest_streak": _longest_streak([r for r, _, _ in filas]),
        "biggest_win": float(biggest_win),
        "total_wagered": float(total_wagered),
        "net_profit": float(net_profit),
    }


def _current_streak(results: list[str]) -> int:
    """Victorias consecutivas desde la última partida hacia atrás.

    Los empates no cortan la racha (se ignoran); una derrota sí la corta.
    """
    streak = 0
    for resultado in reversed(results):
        if resultado == "win":
            streak += 1
        elif resultado == "loss":
            break
        # "draw": neutral, no corta ni suma
    return streak


def _longest_streak(results: list[str]) -> int:
    """Máxima cantidad de victorias consecutivas en todo el historial.

    Los empates no cortan la racha (se ignoran); una derrota la reinicia.
    """
    longest = 0
    actual = 0
    for resultado in results:
        if resultado == "win":
            actual += 1
            longest = max(longest, actual)
        elif resultado == "loss":
            actual = 0
        # "draw": neutral, no corta ni suma
    return longest
