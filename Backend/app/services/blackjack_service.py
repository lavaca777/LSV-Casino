import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TypedDict

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.games.blackjack.cartas import Baraja, Carta
from app.games.blackjack.game import BlackjackGame, carta_a_dict
from app.models import Game, GameResult, GameSession
from app.services import wallet_service

_game = BlackjackGame()


class _RondaActiva(TypedDict):
    user_id: uuid.UUID
    bet: Decimal
    baraja: Baraja
    mano_jugador: list[Carta]
    manos_bots: list[list[Carta]]


_rondas_activas: dict[uuid.UUID, _RondaActiva] = {}


def _get_game_id(db: Session) -> uuid.UUID:
    """Busca el id de blackjack en el catálogo (tabla `games`)."""
    game = db.query(Game).filter(Game.name == _game.name).first()
    if game is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Game '{_game.name}' not found in catalog",
        )
    return game.id


def start_round(
    db: Session, user_id: uuid.UUID, bet: Decimal, baraja: Baraja | None = None
) -> dict:
    """Valida la apuesta, la descuenta, reparte y resuelve los bots.
    Si sale blackjack natural, se resuelve y paga de inmediato; si no,
    deja la ronda abierta para hit()/stand().
    """
    wallet_service.validate_bet(db, user_id, bet)
    wallet_service.update_balance(db, user_id, -bet)

    inicio = _game.play(user_id, bet, baraja=baraja)

    session = GameSession(
        user_id=user_id,
        game_id=_get_game_id(db),
        bet=bet,
        result=None,
        payout=Decimal("0"),
    )
    db.add(session)
    db.flush()  # para tener session.id disponible sin cerrar la transacción

    if inicio["turn"] == "done":
        return _finalizar(
            db, session, user_id, bet,
            inicio["mano_jugador"], inicio["manos_bots"], inicio["resultado"],
        )

    _rondas_activas[session.id] = {
        "user_id": user_id,
        "bet": bet,
        "baraja": inicio["baraja"],
        "mano_jugador": inicio["mano_jugador"],
        "manos_bots": inicio["manos_bots"],
    }
    db.commit()

    return {
        "session_id": str(session.id),
        "mano_jugador": [carta_a_dict(c) for c in inicio["mano_jugador"]],
        "turn": "player",
    }


def hit(db: Session, user_id: uuid.UUID, session_id: uuid.UUID) -> dict:
    """El jugador pide una carta."""
    ronda = _obtener_ronda(user_id, session_id)
    resultado = _game.hit(ronda["mano_jugador"], ronda["baraja"])

    if resultado["turn"] == "done":
        session = _get_session(db, session_id)
        return _finalizar(
            db, session, user_id, ronda["bet"],
            resultado["mano_jugador"], ronda["manos_bots"], resultado["resultado"],
        )

    return {
        "mano_jugador": [carta_a_dict(c) for c in resultado["mano_jugador"]],
        "turn": "player",
    }


def stand(db: Session, user_id: uuid.UUID, session_id: uuid.UUID) -> dict:
    """El jugador se planta."""
    ronda = _obtener_ronda(user_id, session_id)
    resultado = _game.stand(ronda["mano_jugador"], ronda["manos_bots"])
    session = _get_session(db, session_id)
    return _finalizar(
        db, session, user_id, ronda["bet"],
        resultado["mano_jugador"], ronda["manos_bots"], resultado["resultado"],
    )


def _finalizar(
    db: Session,
    session: GameSession,
    user_id: uuid.UUID,
    bet: Decimal,
    mano_jugador: list[Carta],
    manos_bots: list[list[Carta]],
    resultado: str,
) -> dict:
    """Paga el resultado, cierra la GameSession y crea el GameResult."""
    payout = _calcular_payout(resultado, bet)
    if payout > 0:
        wallet_service.update_balance(db, user_id, payout)

    session.ended_at = datetime.now(timezone.utc)
    session.result = resultado
    session.payout = payout
    db.add(
        GameResult(
            session_id=session.id,
            result_type=resultado,
            player_hand=[carta_a_dict(c) for c in mano_jugador],
            bot_hands=[[carta_a_dict(c) for c in mano] for mano in manos_bots],
        )
    )
    db.commit()

    _rondas_activas.pop(session.id, None)

    nuevo_balance = wallet_service.get_wallet(db, user_id).balance
    return {
        "session_id": str(session.id),
        "mano_jugador": [carta_a_dict(c) for c in mano_jugador],
        "manos_bots": [[carta_a_dict(c) for c in mano] for mano in manos_bots],
        "resultado": resultado,
        "payout": float(payout),
        "nuevo_balance": float(nuevo_balance),
        "turn": "done",
    }


def _calcular_payout(resultado: str, bet: Decimal) -> Decimal:
    """win: se devuelve la apuesta + la misma cantidad de ganancia (1:1).
    draw: se devuelve solo la apuesta. loss: nada, ya se descontó."""
    if resultado == "win":
        return bet * 2
    if resultado == "draw":
        return bet
    return Decimal("0")


def _obtener_ronda(user_id: uuid.UUID, session_id: uuid.UUID) -> _RondaActiva:
    ronda = _rondas_activas.get(session_id)
    if ronda is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Round not found"
        )
    if ronda["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This round belongs to another user",
        )
    return ronda


def _get_session(db: Session, session_id: uuid.UUID) -> GameSession:
    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return session