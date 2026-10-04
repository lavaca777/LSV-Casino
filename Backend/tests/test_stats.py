import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.database import SessionLocal
from app.models import Game, GameSession, Wallet
from tests.conftest import register_user


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def _crear_sesion(user_id, result, bet=10, payout=0, minutes=0):
    """Inserta una GameSession finalizada directamente (orden por `minutes`)."""
    db = SessionLocal()
    try:
        gid = db.query(Game).filter(Game.name == "blackjack").first().id
        session = GameSession(
            user_id=uuid.UUID(str(user_id)),
            game_id=gid,
            bet=Decimal(str(bet)),
            result=result,
            payout=Decimal(str(payout)),
            balance_after=Decimal("0"),
            started_at=datetime.now(timezone.utc) + timedelta(minutes=minutes),
            ended_at=datetime.now(timezone.utc) + timedelta(minutes=minutes, seconds=20),
        )
        db.add(session)
        db.commit()
        return session.id
    finally:
        db.close()


def _set_wagered(user_id, amount):
    db = SessionLocal()
    try:
        wallet = db.query(Wallet).filter(Wallet.user_id == uuid.UUID(str(user_id))).first()
        wallet.total_wagered = Decimal(str(amount))
        db.commit()
    finally:
        db.close()


def _stats(client, user_id, headers):
    resp = client.get(f"/users/{user_id}/stats", headers=headers)
    assert resp.status_code == 200
    return resp.json()


# --- acceso ---------------------------------------------------------------

def test_stats_requiere_auth(client):
    resp = client.get(f"/users/{uuid.uuid4()}/stats")
    assert resp.status_code == 401


def test_stats_otro_usuario_403(client):
    _, headers = _register_and_login(client)
    resp = client.get(f"/users/{uuid.uuid4()}/stats", headers=headers)
    assert resp.status_code == 403


# --- métricas -------------------------------------------------------------

def test_stats_sin_partidas(client):
    user_id, headers = _register_and_login(client)
    data = _stats(client, user_id, headers)
    assert data["total_games"] == 0
    assert data["total_games_won"] == 0
    assert data["win_rate"] == 0
    assert data["current_streak"] == 0
    assert data["longest_streak"] == 0
    assert data["biggest_win"] == 0
    assert data["net_profit"] == 0


def test_stats_totales(client):
    user_id, headers = _register_and_login(client)
    _crear_sesion(user_id, "win", minutes=0)
    _crear_sesion(user_id, "win", minutes=1)
    _crear_sesion(user_id, "loss", minutes=2)
    _crear_sesion(user_id, "draw", minutes=3)

    data = _stats(client, user_id, headers)
    assert data["total_games"] == 4
    assert data["total_games_won"] == 2
    assert data["total_games_lost"] == 1
    assert data["total_games_drawn"] == 1


def test_stats_win_rate(client):
    user_id, headers = _register_and_login(client)
    # 3 victorias de 4 partidas -> 75%
    _crear_sesion(user_id, "win", minutes=0)
    _crear_sesion(user_id, "win", minutes=1)
    _crear_sesion(user_id, "win", minutes=2)
    _crear_sesion(user_id, "loss", minutes=3)

    data = _stats(client, user_id, headers)
    assert data["win_rate"] == 75.0


def test_stats_racha_actual(client):
    user_id, headers = _register_and_login(client)
    # win, win, loss, win, win, win -> racha actual 3
    for i, r in enumerate(["win", "win", "loss", "win", "win", "win"]):
        _crear_sesion(user_id, r, minutes=i)
    assert _stats(client, user_id, headers)["current_streak"] == 3


def test_stats_racha_actual_termina_en_no_win(client):
    user_id, headers = _register_and_login(client)
    # win, win, loss -> racha actual 0
    for i, r in enumerate(["win", "win", "loss"]):
        _crear_sesion(user_id, r, minutes=i)
    assert _stats(client, user_id, headers)["current_streak"] == 0


def test_stats_racha_mas_larga(client):
    user_id, headers = _register_and_login(client)
    # win, win, win, loss, win -> más larga 3
    for i, r in enumerate(["win", "win", "win", "loss", "win"]):
        _crear_sesion(user_id, r, minutes=i)
    data = _stats(client, user_id, headers)
    assert data["longest_streak"] == 3
    assert data["current_streak"] == 1


def test_stats_empate_no_corta_racha_actual(client):
    user_id, headers = _register_and_login(client)
    # win, draw, win -> racha actual 2 (el empate no corta)
    for i, r in enumerate(["win", "draw", "win"]):
        _crear_sesion(user_id, r, minutes=i)
    assert _stats(client, user_id, headers)["current_streak"] == 2


def test_stats_empate_no_corta_racha_mas_larga(client):
    user_id, headers = _register_and_login(client)
    # win, win, draw, win, loss, win -> más larga 3, actual 1
    for i, r in enumerate(["win", "win", "draw", "win", "loss", "win"]):
        _crear_sesion(user_id, r, minutes=i)
    data = _stats(client, user_id, headers)
    assert data["longest_streak"] == 3
    assert data["current_streak"] == 1


def test_stats_mayor_ganancia(client):
    user_id, headers = _register_and_login(client)
    _crear_sesion(user_id, "win", bet=10, payout=20, minutes=0)
    _crear_sesion(user_id, "win", bet=50, payout=100, minutes=1)
    _crear_sesion(user_id, "loss", bet=30, payout=0, minutes=2)

    assert _stats(client, user_id, headers)["biggest_win"] == 100.0


def test_stats_profit_loss(client):
    user_id, headers = _register_and_login(client)
    # bets: 10 + 20 = 30 ; payouts: 20 + 0 = 20 -> net -10
    _crear_sesion(user_id, "win", bet=10, payout=20, minutes=0)
    _crear_sesion(user_id, "loss", bet=20, payout=0, minutes=1)

    assert _stats(client, user_id, headers)["net_profit"] == -10.0


def test_stats_total_wagered_desde_wallet(client):
    user_id, headers = _register_and_login(client)
    _set_wagered(user_id, 250)
    assert _stats(client, user_id, headers)["total_wagered"] == 250.0
