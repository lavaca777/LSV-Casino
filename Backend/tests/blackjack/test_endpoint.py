"""
tests/blackjack/test_endpoint.py

Tests HTTP end-to-end para /games/blackjack/start, /hit, /stand.
A diferencia de coinflip, no hay un único punto para parchear y forzar
un resultado exacto (blackjack reparte con una Baraja completa, no un
solo random.choice), así que estos tests se enfocan en plumbing:
status codes, auth, validaciones y forma de la respuesta. Los
resultados exactos (win/draw/loss con cartas controladas) ya están
cubiertos en test_service.py.
"""

from tests.conftest import register_user, set_balance


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def _start(client, headers, bet=10):
    return client.post(
        "/games/blackjack/start", json={"bet": bet}, headers=headers
    )


def test_start_blackjack_requiere_auth(client):
    resp = client.post("/games/blackjack/start", json={"bet": 10})
    assert resp.status_code == 401


def test_start_blackjack_devuelve_mano_de_dos_cartas(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    resp = _start(client, headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["mano_jugador"]) == 2
    assert data["turn"] in ("player", "done")


def test_start_blackjack_descuenta_la_apuesta(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    _start(client, headers, bet=10)

    resp = client.get(f"/users/{user_id}/wallet", headers=headers)
    assert resp.json()["balance"] == 90


def test_start_blackjack_bajo_apuesta_minima(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    resp = _start(client, headers, bet=2)
    assert resp.status_code == 400


def test_start_blackjack_saldo_insuficiente(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 5)
    resp = _start(client, headers, bet=50)
    assert resp.status_code == 400


def test_start_blackjack_registra_sesion(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    resp = _start(client, headers)
    data = resp.json()

    # si la ronda quedó abierta, hay session_id; si fue blackjack
    # natural, ya vino resuelta pero también trae session_id.
    assert data["session_id"]


def test_hit_requiere_auth(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    session_id = _start(client, headers).json()["session_id"]
    resp = client.post(f"/games/blackjack/{session_id}/hit")
    assert resp.status_code == 401


def test_hit_sesion_inexistente_404(client):
    _, headers = _register_and_login(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.post(f"/games/blackjack/{fake_id}/hit", headers=headers)
    assert resp.status_code == 404


def test_hit_de_otro_usuario_403(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    inicio = _start(client, headers).json()

    if inicio["turn"] != "player":
        return  # blackjack natural, no hay ronda abierta para probar esto

    resp_otro = register_user(client, email="otro2@example.com", username="otro2")
    otro_headers = {"Authorization": f"Bearer {resp_otro.json()['access_token']}"}

    resp = client.post(
        f"/games/blackjack/{inicio['session_id']}/hit", headers=otro_headers
    )
    assert resp.status_code == 403


def test_stand_requiere_auth(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    session_id = _start(client, headers).json()["session_id"]
    resp = client.post(f"/games/blackjack/{session_id}/stand")
    assert resp.status_code == 401


def test_stand_sesion_inexistente_404(client):
    _, headers = _register_and_login(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.post(f"/games/blackjack/{fake_id}/stand", headers=headers)
    assert resp.status_code == 404


def test_flujo_completo_start_y_stand(client):
    """No controla las cartas, pero verifica que el flujo completo
    (start -> stand) responde con un resultado válido y consistente."""
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    inicio = _start(client, headers, bet=10)
    assert inicio.status_code == 200
    inicio_data = inicio.json()

    if inicio_data["turn"] == "done":
        # blackjack natural: ya vino resuelto en el start.
        resultado = inicio_data
    else:
        resp = client.post(
            f"/games/blackjack/{inicio_data['session_id']}/stand", headers=headers
        )
        assert resp.status_code == 200
        resultado = resp.json()

    assert resultado["resultado"] in ("win", "draw", "loss")
    assert resultado["turn"] == "done"
    assert resultado["nuevo_balance"] is not None

    # el balance final es consistente con el resultado
    resp = client.get(f"/users/{user_id}/wallet", headers=headers)
    assert resp.json()["balance"] == resultado["nuevo_balance"]


def test_get_session_requiere_auth(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    session_id = _start(client, headers).json()["session_id"]
    resp = client.get(f"/games/blackjack/{session_id}")
    assert resp.status_code == 401


def test_get_session_inexistente_404(client):
    _, headers = _register_and_login(client)
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = client.get(f"/games/blackjack/{fake_id}", headers=headers)
    assert resp.status_code == 404


def test_get_session_ronda_abierta(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    inicio = _start(client, headers).json()

    resp = client.get(
        f"/games/blackjack/{inicio['session_id']}", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["session_id"] == inicio["session_id"]
    assert data["turn"] in ("player", "done")


def test_get_session_ronda_terminada(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    inicio = _start(client, headers, bet=10).json()

    if inicio["turn"] == "player":
        client.post(
            f"/games/blackjack/{inicio['session_id']}/stand", headers=headers
        )

    resp = client.get(
        f"/games/blackjack/{inicio['session_id']}", headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["turn"] == "done"
    assert data["resultado"] in ("win", "draw", "loss")
    assert data["nuevo_balance"] is not None


def test_get_session_de_otro_usuario_403(client):
    user_id, headers = _register_and_login(client)
    set_balance(user_id, 100)
    inicio = _start(client, headers).json()

    resp_otro = register_user(client, email="otro3@example.com", username="otro3")
    otro_headers = {"Authorization": f"Bearer {resp_otro.json()['access_token']}"}

    resp = client.get(
        f"/games/blackjack/{inicio['session_id']}", headers=otro_headers
    )
    assert resp.status_code == 403