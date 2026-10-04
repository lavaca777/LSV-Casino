"""
tests/blackjack/test_service.py

Tests para blackjack_service.py: start_round, hit, stand.
Sigue el mismo patrón que test_wallet_service.py (fixture db_user con
BD real vía TestClient, no mocks).
"""

import uuid
from decimal import Decimal

import pytest

from app.database import SessionLocal
from app.games.blackjack.cartas import Carta, Palo
from app.models import GameResult, GameSession, User, Wallet
from app.services import blackjack_service as bs
from tests.conftest import register_user


def C(rango: str, palo: Palo = Palo.CORAZON) -> Carta:
    return Carta(palo, rango)


class BarajaFija:
    """Baraja falsa que reparte cartas predefinidas, para tests deterministas."""

    def __init__(self, cartas: list[Carta]):
        self._cartas = list(cartas)

    def repartir_carta(self) -> Carta:
        carta, self._cartas = self._cartas[0], self._cartas[1:]
        return carta

    def repartir_cartas(self, n: int) -> list[Carta]:
        cartas, self._cartas = self._cartas[:n], self._cartas[n:]
        return cartas


@pytest.fixture()
def db_user(client):
    resp = register_user(client)
    user_id = resp.json()["user_id"]
    db = SessionLocal()
    user = db.get(User, user_id)
    yield db, user
    db.close()


@pytest.fixture(autouse=True)
def _reset_rondas_activas():
    """_rondas_activas es un dict de módulo -- clean_db no lo toca, así
    que lo limpiamos manualmente para que un test fallido no deje una
    ronda abierta que contamine el siguiente."""
    bs._rondas_activas.clear()
    yield
    bs._rondas_activas.clear()


def _set_balance(db, user_id, amount):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    wallet.balance = amount
    db.commit()


def _get_balance(db, user_id) -> Decimal:
    return db.query(Wallet).filter(Wallet.user_id == user_id).first().balance


# --- start_round -------------------------------------------------------

def test_start_round_deducts_bet(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("5"), C("4"), C("10"), C("7"), C("9"), C("8")])
    bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    assert _get_balance(db, user.id) == 90


def test_start_round_below_minimum_raises(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    with pytest.raises(Exception) as exc:
        bs.start_round(db, user.id, Decimal("4"))
    assert exc.value.status_code == 400
    assert _get_balance(db, user.id) == 100  # no se tocó el saldo


def test_start_round_deals_two_cards_and_opens_round(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("5"), C("4"), C("10"), C("7"), C("9"), C("8")])
    resultado = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    assert resultado["turn"] == "player"
    assert len(resultado["mano_jugador"]) == 2
    assert uuid.UUID(resultado["session_id"]) in bs._rondas_activas


def test_start_round_natural_blackjack_resolves_immediately(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("A"), C("K"), C("10"), C("7"), C("9"), C("8")])
    resultado = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    assert resultado["turn"] == "done"
    assert resultado["resultado"] == "win"
    assert _get_balance(db, user.id) == 110  # -10 apuesta + 20 payout
    assert uuid.UUID(resultado["session_id"]) not in bs._rondas_activas


# --- hit -----------------------------------------------------------------

def test_hit_adds_a_card(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("5"), C("4"), C("10"), C("7"), C("9"), C("8"), C("2")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    resultado = bs.hit(db, user.id, uuid.UUID(inicio["session_id"]))
    assert len(resultado["mano_jugador"]) == 3
    assert resultado["turn"] == "player"


def test_hit_bust_closes_round_as_loss(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("10"), C("9"), C("10"), C("7"), C("9"), C("8"), C("K")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    resultado = bs.hit(db, user.id, uuid.UUID(inicio["session_id"]))
    assert resultado["turn"] == "done"
    assert resultado["resultado"] == "loss"
    assert _get_balance(db, user.id) == 90  # ya se descontó, sin payout extra
    assert uuid.UUID(inicio["session_id"]) not in bs._rondas_activas


def test_hit_unknown_session_raises_404(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    with pytest.raises(Exception) as exc:
        bs.hit(db, user.id, uuid.uuid4())
    assert exc.value.status_code == 404


def test_hit_wrong_user_raises_403(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("5"), C("4"), C("10"), C("7"), C("9"), C("8")])
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    with pytest.raises(Exception) as exc:
        bs.hit(db, uuid.uuid4(), uuid.UUID(inicio["session_id"]))
    assert exc.value.status_code == 403


# --- stand ---------------------------------------------------------------

def test_stand_win_pays_double(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("10"), C("9"), C("10"), C("7"), C("9"), C("8")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    resultado = bs.stand(db, user.id, uuid.UUID(inicio["session_id"]))
    assert resultado["resultado"] == "win"
    assert resultado["payout"] == 20.0
    assert _get_balance(db, user.id) == 110


def test_stand_draw_returns_bet(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("10"), C("7"), C("10"), C("7"), C("9"), C("8")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    resultado = bs.stand(db, user.id, uuid.UUID(inicio["session_id"]))
    assert resultado["resultado"] == "draw"
    assert _get_balance(db, user.id) == 100  # -10 + 10 devuelta


def test_stand_loss_pays_nothing(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("2"), C("3"), C("10"), C("8"), C("9"), C("8")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    resultado = bs.stand(db, user.id, uuid.UUID(inicio["session_id"]))
    assert resultado["resultado"] == "loss"
    assert _get_balance(db, user.id) == 90


def test_stand_creates_game_session_and_result(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("10"), C("9"), C("10"), C("7"), C("9"), C("8")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    session_id = uuid.UUID(inicio["session_id"])
    bs.stand(db, user.id, session_id)

    session = db.query(GameSession).filter(GameSession.id == session_id).first()
    assert session.ended_at is not None
    assert session.result == "win"
    assert session.payout == Decimal("20")

    game_result = (
        db.query(GameResult).filter(GameResult.session_id == session_id).first()
    )
    assert game_result is not None
    assert game_result.result_type == "win"
    assert len(game_result.player_hand) == 2


def test_stand_wrong_user_raises_403(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija(
        [C("10"), C("9"), C("10"), C("7"), C("9"), C("8")]
    )
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    with pytest.raises(Exception) as exc:
        bs.stand(db, uuid.uuid4(), uuid.UUID(inicio["session_id"]))
    assert exc.value.status_code == 403


def test_stand_unknown_session_raises_404(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    with pytest.raises(Exception) as exc:
        bs.stand(db, user.id, uuid.uuid4())
    assert exc.value.status_code == 404
    

# --- get_session ---------------------------------------------------------

def test_get_session_ronda_abierta(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("5"), C("4"), C("10"), C("7"), C("9"), C("8")])
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    session_id = uuid.UUID(inicio["session_id"])

    estado = bs.get_session(db, user.id, session_id)
    assert estado["turn"] == "player"
    assert len(estado["mano_jugador"]) == 2
    assert estado["session_id"] == str(session_id)


def test_get_session_ronda_terminada(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("10"), C("9"), C("10"), C("7"), C("9"), C("8")])
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    session_id = uuid.UUID(inicio["session_id"])
    bs.stand(db, user.id, session_id)

    estado = bs.get_session(db, user.id, session_id)
    assert estado["turn"] == "done"
    assert estado["resultado"] == "win"
    assert estado["payout"] == 20.0
    assert len(estado["manos_bots"]) == 2
    assert estado["nuevo_balance"] == 110.0


def test_get_session_inexistente_404(db_user):
    db, user = db_user
    with pytest.raises(Exception) as exc:
        bs.get_session(db, user.id, uuid.uuid4())
    assert exc.value.status_code == 404


def test_get_session_otro_usuario_403(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("5"), C("4"), C("10"), C("7"), C("9"), C("8")])
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)
    with pytest.raises(Exception) as exc:
        bs.get_session(db, uuid.uuid4(), uuid.UUID(inicio["session_id"]))
    assert exc.value.status_code == 403


def test_get_session_ronda_perdida_404(db_user):
    """Si el backend se reinicia, la ronda abierta se pierde (memoria) pero la
    sesión sigue en la BD sin resultado: no es recuperable."""
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    baraja = BarajaFija([C("5"), C("4"), C("10"), C("7"), C("9"), C("8")])
    inicio = bs.start_round(db, user.id, Decimal("10"), baraja=baraja)

    bs._rondas_activas.clear()  # simula un reinicio del backend

    with pytest.raises(Exception) as exc:
        bs.get_session(db, user.id, uuid.UUID(inicio["session_id"]))
    assert exc.value.status_code == 404