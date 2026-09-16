from tests.conftest import register_user


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def test_list_games_requires_auth(client):
    resp = client.get("/games")
    assert resp.status_code == 401


def test_list_games_includes_blackjack(client):
    _, headers = _register_and_login(client)
    resp = client.get("/games", headers=headers)
    assert resp.status_code == 200
    games = resp.json()
    assert any(g["name"] == "blackjack" for g in games)
    blackjack = next(g for g in games if g["name"] == "blackjack")
    assert blackjack["min_bet"] == 5
