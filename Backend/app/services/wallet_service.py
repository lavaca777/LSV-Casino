import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Wallet

MIN_BET = Decimal("5")


def get_wallet(db: Session, user_id: uuid.UUID) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )
    return wallet


def validate_bet(db: Session, user_id: uuid.UUID, amount: Decimal) -> Wallet:
    """Valida que la apuesta esté entre el mínimo y el balance disponible."""
    if amount < MIN_BET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Minimum bet is ${MIN_BET}",
        )
    wallet = get_wallet(db, user_id)
    if amount > wallet.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bet exceeds available balance",
        )
    return wallet


def update_balance(db: Session, user_id: uuid.UUID, delta: Decimal) -> Wallet:
    """Ajusta el balance del usuario en `delta` (positivo suma, negativo resta).

    Registra en `total_wagered` solo el monto apostado, nunca se resta.
    """
    wallet = get_wallet(db, user_id)
    wallet.balance += delta
    if delta < 0:
        wallet.total_wagered += -delta
    db.commit()
    db.refresh(wallet)
    return wallet
