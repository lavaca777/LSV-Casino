from tests.conftest import register_user


def test_register_success(client):
    resp = register_user(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user_id"]


def test_register_creates_wallet(client):
    resp = register_user(client)
    assert resp.status_code == 201
    user_id = resp.json()["user_id"]
    token = resp.json()["access_token"]

    # la wallet existe con saldo 0 vía el usuario autenticado (endpoint del feature 002)
    import psycopg2
    from app.config import settings

    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT balance, total_wagered FROM wallets WHERE user_id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    assert row == (0, 0)


def test_register_duplicate_email(client):
    register_user(client)
    resp = register_user(client, email="test@example.com", username="otro_user")
    assert resp.status_code == 409


def test_register_duplicate_username(client):
    register_user(client)
    resp = register_user(client, email="otro@example.com", username="testuser")
    assert resp.status_code == 409


def test_register_short_password(client):
    resp = register_user(client, password="short")
    assert resp.status_code == 422


def test_register_invalid_email(client):
    resp = register_user(client, email="not-an-email")
    assert resp.status_code == 422


def test_login_success_by_email(client):
    register_user(client)
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "test@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


def test_login_success_by_username(client):
    register_user(client)
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "testuser", "password": "password123"},
    )
    assert resp.status_code == 200


def test_login_wrong_password(client):
    register_user(client)
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "test@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/auth/login",
        json={"email_or_username": "ghost@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


def test_logout(client):
    resp = client.post("/auth/logout")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Logged out"}
