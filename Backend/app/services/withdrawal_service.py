import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Withdrawal
from app.services import wallet_service


def request_withdrawal(db: Session, user_id: uuid.UUID, amount: Decimal) -> Withdrawal:
    """Registra un retiro aprobado y descuenta el monto del balance."""
    wallet = wallet_service.get_wallet(db, user_id)
    if amount > wallet.balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient balance for withdrawal",
        )

    wallet.balance -= amount
    withdrawal = Withdrawal(user_id=user_id, amount=amount, status="approved")
    db.add(withdrawal)
    db.commit()
    db.refresh(withdrawal)
    return withdrawal


def get_withdrawals(db: Session, user_id: uuid.UUID) -> list[Withdrawal]:
    return (
        db.query(Withdrawal)
        .filter(Withdrawal.user_id == user_id)
        .order_by(Withdrawal.requested_at.desc())
        .all()
    )
