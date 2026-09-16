from unittest.mock import patch

import psycopg2

from app.config import settings
from tests.conftest import register_user, set_balance


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def test_play_coinflip_gana(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 60)

    with patch("app.games.coinflip.game.random.choice", return_value="cara"):
        resp = client.post(
            "/games/coinflip/play",
            json={"bet": 20, "eleccion": "cara"},
            headers=headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["resultado"] == "win"
    assert data["moneda"] == "cara"
    assert data["payout"] == 40
    assert data["nuevo_balance"] == 80  # 60 - 20 + 40


def test_play_coinflip_pierde(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 60)

    with patch("app.games.coinflip.game.random.choice", return_value="cruz"):
        resp = client.post(
            "/games/coinflip/play",
            json={"bet": 20, "eleccion": "cara"},
            headers=headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["resultado"] == "loss"
    assert data["payout"] == 0
    assert data["nuevo_balance"] == 40  # 60 - 20


def test_play_coinflip_registra_sesion(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 60)

    with patch("app.games.coinflip.game.random.choice", return_value="cara"):
        client.post(
            "/games/coinflip/play",
            json={"bet": 20, "eleccion": "cara"},
            headers=headers,
        )

    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT result, payout FROM game_sessions WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    assert row is not None
    assert row[0] == "win"


def test_play_coinflip_bajo_apuesta_minima(client):
    _, headers = _register_and_login(client)
    resp = client.post(
        "/games/coinflip/play",
        json={"bet": 2, "eleccion": "cara"},
        headers=headers,
    )
    assert resp.status_code == 400


def test_play_coinflip_saldo_insuficiente(client):
    _, headers = _register_and_login(client)
    resp = client.post(
        "/games/coinflip/play",
        json={"bet": 100, "eleccion": "cara"},
        headers=headers,
    )
    assert resp.status_code == 400


def test_play_coinflip_eleccion_invalida(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 60)
    resp = client.post(
        "/games/coinflip/play",
        json={"bet": 20, "eleccion": "otro"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_play_coinflip_requiere_auth(client):
    resp = client.post(
        "/games/coinflip/play",
        json={"bet": 20, "eleccion": "cara"},
    )
    assert resp.status_code == 401
