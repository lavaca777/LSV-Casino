from tests.conftest import register_user


def _login(client):
    register_user(client)
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "test@example.com", "password": "password123"},
    )
    return resp.json()


def test_rate_limit_blocks_after_5_failures(client):
    for i in range(5):
        resp = client.post(
            "/auth/login",
            json={"email_or_username": "test@example.com", "password": "wrongpass"},
        )
        assert resp.status_code == 401

    resp = client.post(
        "/auth/login",
        json={"email_or_username": "test@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 429


def test_rate_limit_clears_on_success(client):
    data = _login(client)
    token = data["access_token"]
    user_id = data["user_id"]

    # 3 fallos
    for _ in range(3):
        client.post(
            "/auth/login",
            json={"email_or_username": "test@example.com", "password": "wrongpass"},
        )

    # login exitoso limpia el contador
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "test@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert token != resp.json()["access_token"]

    # aún autenticado en endpoints
    resp = client.get(f"/users/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
