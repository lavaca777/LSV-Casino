import sys
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
from main import app  # noqa: E402
from app.database import SessionLocal, engine, init_db  # noqa: E402
from app.models import Wallet  # noqa: E402
from app.utils.rate_limiter import login_rate_limiter  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    """Crea las tablas (si no existen), vacía los datos y resetea el rate limiter."""
    init_db()
    login_rate_limiter.reset()
    with engine.connect() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE withdrawals, loans, wallets, users RESTART IDENTITY CASCADE"
            )
        )
        conn.commit()
    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


def register_user(client: TestClient, email="test@example.com", username="testuser", password="password123"):
    return client.post(
        "/auth/register",
        json={"email": email, "username": username, "password": password},
    )


def set_balance(user_id, amount):
    """Fija el saldo del usuario directamente en la BD (para tests).

    Se usa para preparar escenarios sin depender de la regla de préstamos
    (que ahora solo permite pedir si el saldo es menor a $5).
    """
    db = SessionLocal()
    try:
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        wallet.balance = Decimal(str(amount))
        db.commit()
    finally:
        db.close()
