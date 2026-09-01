from decimal import Decimal

import pytest

from app.database import SessionLocal
from app.models import User, Wallet
from app.services import wallet_service
from tests.conftest import register_user


@pytest.fixture()
def db_user(client):
    resp = register_user(client)
    user_id = resp.json()["user_id"]
    db = SessionLocal()
    user = db.get(User, user_id)
    yield db, user
    db.close()


def _set_balance(db, user_id, amount):
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    wallet.balance = amount
    db.commit()


def test_validate_bet_ok(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    wallet = wallet_service.validate_bet(db, user.id, Decimal("50"))
    assert wallet.balance == 100


def test_validate_bet_below_minimum(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    with pytest.raises(Exception) as exc:
        wallet_service.validate_bet(db, user.id, Decimal("4"))
    assert exc.value.status_code == 400


def test_validate_bet_exceeds_balance(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("10"))
    with pytest.raises(Exception) as exc:
        wallet_service.validate_bet(db, user.id, Decimal("11"))
    assert exc.value.status_code == 400


def test_update_balance_adds_money(db_user):
    db, user = db_user
    wallet_service.update_balance(db, user.id, Decimal("25"))
    assert wallet_service.get_wallet(db, user.id).balance == 25


def test_update_balance_subtracts_and_counts_wagered(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    wallet = wallet_service.update_balance(db, user.id, Decimal("-30"))
    assert wallet.balance == 70
    assert wallet.total_wagered == 30


def test_update_balance_win_does_not_count_wagered(db_user):
    db, user = db_user
    _set_balance(db, user.id, Decimal("100"))
    wallet = wallet_service.update_balance(db, user.id, Decimal("+20"))
    assert wallet.balance == 120
    assert wallet.total_wagered == 0
