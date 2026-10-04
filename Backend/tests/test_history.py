import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.database import SessionLocal
from app.models import Game, GameResult, GameSession
from tests.conftest import register_user, set_balance


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def _game_id(db, name):
    return db.query(Game).filter(Game.name == name).first().id


def _crear_sesion(
    user_id,
    game_name="blackjack",
    bet=10,
    result="win",
    payout=20,
    balance_after=100,
    started_at=None,
    con_resultado=True,
):
    """Inserta una GameSession directamente (para controlar orden/cantidad)."""
    db = SessionLocal()
    try:
        inicio = started_at or datetime.now(timezone.utc)
        session = GameSession(
            user_id=uuid.UUID(str(user_id)),
            game_id=_game_id(db, game_name),
            bet=Decimal(str(bet)),
            result=result,
            payout=Decimal(str(payout)),
            balance_after=Decimal(str(balance_after)),
            started_at=inicio,
            ended_at=inicio + timedelta(seconds=30),
        )
        db.add(session)
        db.flush()
        if con_resultado:
            db.add(
                GameResult(
                    session_id=session.id,
                    result_type=result or "win",
                    player_hand=[{"palo": "espada", "rango": "A"}],
                    bot_hands=[[{"palo": "corazon", "rango": "K"}]],
                )
            )
        db.commit()
        return session.id
    finally:
        db.close()


# --- list -----------------------------------------------------------------

def test_list_requiere_auth(client):
    resp = client.get(f"/users/{uuid.uuid4()}/games")
    assert resp.status_code == 401


def test_list_otro_usuario_403(client):
    user_id, headers = _register_and_login(client)
    resp = client.get(f"/users/{uuid.uuid4()}/games", headers=headers)
    assert resp.status_code == 403


def test_list_vacio(client):
    user_id, headers = _register_and_login(client)
    resp = client.get(f"/users/{user_id}/games", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["games"] == []


def test_list_devuelve_partidas(client):
    user_id, headers = _register_and_login(client)
    _crear_sesion(user_id, bet=10, result="win", payout=20, balance_after=110)

    resp = client.get(f"/users/{user_id}/games", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    item = data["games"][0]
    assert item["game_name"] == "blackjack"
    assert item["bet"] == 10
    assert item["result"] == "win"
    assert item["payout"] == 20
    assert item["balance_after"] == 110
    assert "date" in item


def test_list_orden_mas_recientes_primero(client):
    user_id, headers = _register_and_login(client)
    base = datetime.now(timezone.utc)
    _crear_sesion(user_id, bet=1, started_at=base - timedelta(hours=2))
    _crear_sesion(user_id, bet=2, started_at=base - timedelta(hours=1))
    _crear_sesion(user_id, bet=3, started_at=base)

    resp = client.get(f"/users/{user_id}/games", headers=headers)
    bets = [g["bet"] for g in resp.json()["games"]]
    assert bets == [3, 2, 1]  # la más reciente primero


def test_list_paginacion(client):
    user_id, headers = _register_and_login(client)
    base = datetime.now(timezone.utc)
    for i in range(25):
        _crear_sesion(user_id, started_at=base + timedelta(minutes=i))

    resp = client.get(f"/users/{user_id}/games?limit=20&offset=0", headers=headers)
    data = resp.json()
    assert data["total"] == 25
    assert len(data["games"]) == 20

    resp = client.get(f"/users/{user_id}/games?limit=20&offset=20", headers=headers)
    data = resp.json()
    assert len(data["games"]) == 5


def test_list_filtro_por_juego(client):
    user_id, headers = _register_and_login(client)
    _crear_sesion(user_id, game_name="blackjack")
    _crear_sesion(user_id, game_name="blackjack")
    _crear_sesion(user_id, game_name="coinflip")

    resp = client.get(f"/users/{user_id}/games?game=blackjack", headers=headers)
    data = resp.json()
    assert data["total"] == 2
    assert all(g["game_name"] == "blackjack" for g in data["games"])

    resp = client.get(f"/users/{user_id}/games?game=coinflip", headers=headers)
    assert resp.json()["total"] == 1


# --- detail ---------------------------------------------------------------

def test_detail_devuelve_manos(client):
    user_id, headers = _register_and_login(client)
    session_id = _crear_sesion(user_id, bet=10, result="win", payout=20)

    resp = client.get(f"/users/{user_id}/games/{session_id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(session_id)
    assert data["game_name"] == "blackjack"
    assert data["player_hand"][0]["rango"] == "A"
    assert len(data["bot_hands"]) == 1
    assert data["duration_seconds"] == 30.0


def test_detail_inexistente_404(client):
    user_id, headers = _register_and_login(client)
    resp = client.get(f"/users/{user_id}/games/{uuid.uuid4()}", headers=headers)
    assert resp.status_code == 404


def test_detail_otro_usuario_403(client):
    user_id, headers = _register_and_login(client)
    session_id = _crear_sesion(user_id)

    otro = register_user(client, email="otrohist@example.com", username="otrohist")
    otros_headers = {"Authorization": f"Bearer {otro.json()['access_token']}"}

    # el usuario B intenta ver el historial del usuario A
    resp = client.get(
        f"/users/{user_id}/games/{session_id}", headers=otros_headers
    )
    assert resp.status_code == 403


# --- integración con juegos ----------------------------------------------

def test_coinflip_registra_balance_after(client):
    """Al jugar, la partida queda en el historial con el balance posterior."""
    from unittest.mock import patch

    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)

    with patch("app.games.coinflip.game.random.choice", return_value="cara"):
        play = client.post(
            "/games/coinflip/play",
            json={"bet": 10, "eleccion": "cara"},
            headers=headers,
        )
    assert play.json()["nuevo_balance"] == 110  # 100 - 10 + 20

    resp = client.get(f"/users/{user_id}/games?game=coinflip", headers=headers)
    item = resp.json()["games"][0]
    assert item["balance_after"] == 110
