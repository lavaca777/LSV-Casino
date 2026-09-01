import psycopg2

from app.config import settings
from tests.conftest import register_user


def _register_and_login(client):
    resp = register_user(client)
    data = resp.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["user_id"], headers


def _db_row(query, params):
    conn = psycopg2.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def test_wallet_created_on_register(client):
    resp = register_user(client)
    user_id = resp.json()["user_id"]
    row = _db_row(
        "SELECT balance, total_wagered FROM wallets WHERE user_id = %s", (user_id,)
    )
    assert row == (0, 0)


def test_get_wallet(client):
    user_id, headers = _register_and_login(client)
    resp = client.get(f"/users/{user_id}/wallet", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["balance"] == 0
    assert data["total_wagered"] == 0


def test_get_wallet_forbidden(client):
    user_id, headers = _register_and_login(client)
    other = register_user(client, email="other@example.com", username="otheruser")
    other_id = other.json()["user_id"]
    resp = client.get(f"/users/{other_id}/wallet", headers=headers)
    assert resp.status_code == 403


def test_request_loan_adds_20(client):
    user_id, headers = _register_and_login(client)
    resp = client.post(f"/users/{user_id}/loans/request", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["loan_amount"] == 20
    assert data["new_balance"] == 20

    resp = client.get(f"/users/{user_id}/wallet", headers=headers)
    assert resp.json()["balance"] == 20


def test_request_loan_no_daily_limit(client):
    user_id, headers = _register_and_login(client)
    for i in range(1, 6):  # 5 préstamos seguidos (antes el límite era 3/día)
        resp = client.post(f"/users/{user_id}/loans/request", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["new_balance"] == 20 * i


def test_loans_history(client):
    user_id, headers = _register_and_login(client)
    client.post(f"/users/{user_id}/loans/request", headers=headers)
    client.post(f"/users/{user_id}/loans/request", headers=headers)

    resp = client.get(f"/users/{user_id}/loans/history", headers=headers)
    assert resp.status_code == 200
    loans = resp.json()
    assert len(loans) == 2
    for loan in loans:
        assert loan["amount"] == 20
        assert "requested_at" in loan


def test_withdrawal_request(client):
    user_id, headers = _register_and_login(client)
    # darse saldo: pedir préstamos
    client.post(f"/users/{user_id}/loans/request", headers=headers)
    client.post(f"/users/{user_id}/loans/request", headers=headers)
    client.post(f"/users/{user_id}/loans/request", headers=headers)

    resp = client.post(
        f"/users/{user_id}/withdrawals/request",
        json={"amount": 50},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["amount"] == 50
    assert data["status"] == "approved"

    # el retiro SÍ descuenta el balance (60 - 50 = 10)
    resp = client.get(f"/users/{user_id}/wallet", headers=headers)
    assert resp.json()["balance"] == 10


def test_withdrawal_insufficient_balance(client):
    user_id, headers = _register_and_login(client)
    resp = client.post(
        f"/users/{user_id}/withdrawals/request",
        json={"amount": 50},
        headers=headers,
    )
    assert resp.status_code == 400


def test_withdrawal_request_invalid_amount(client):
    user_id, headers = _register_and_login(client)
    resp = client.post(
        f"/users/{user_id}/withdrawals/request",
        json={"amount": 0},
        headers=headers,
    )
    assert resp.status_code == 422


def test_withdrawals_history(client):
    user_id, headers = _register_and_login(client)
    # dar saldo: préstamos ($20 cada uno)
    for _ in range(3):
        client.post(f"/users/{user_id}/loans/request", headers=headers)
    client.post(f"/users/{user_id}/withdrawals/request", json={"amount": 10}, headers=headers)
    client.post(f"/users/{user_id}/withdrawals/request", json={"amount": 20}, headers=headers)

    resp = client.get(f"/users/{user_id}/withdrawals", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2
