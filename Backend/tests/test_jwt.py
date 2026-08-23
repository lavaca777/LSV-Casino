from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings
from tests.conftest import register_user


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_token_has_expected_claims(client):
    resp = register_user(client)
    token = resp.json()["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["user_id"] == resp.json()["user_id"]
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_token_expires_after_24h(client):
    resp = register_user(client)
    payload = jwt.decode(
        resp.json()["access_token"], settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    assert exp - now >= timedelta(hours=23, minutes=59)


def test_expired_token_rejected(client):
    resp = register_user(client)
    user_id = resp.json()["user_id"]

    expired_payload = {
        "sub": user_id,
        "user_id": user_id,
        "email": "test@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    resp = client.get(f"/users/{user_id}", headers=_auth_headers(expired))
    assert resp.status_code == 401


def test_invalid_token_rejected(client):
    resp = register_user(client)
    user_id = resp.json()["user_id"]
    resp = client.get(f"/users/{user_id}", headers=_auth_headers("not.a.jwt"))
    assert resp.status_code == 401


def test_missing_token_rejected(client):
    resp = register_user(client)
    user_id = resp.json()["user_id"]
    resp = client.get(f"/users/{user_id}")
    assert resp.status_code == 401
