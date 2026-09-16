import uuid
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Loan
from app.services import wallet_service

LOAN_AMOUNT = Decimal("20")
# Solo se puede pedir préstamo si el saldo está por debajo de este monto.
LOAN_MAX_BALANCE = Decimal("5")


def request_loan(db: Session, user_id: uuid.UUID) -> tuple[Loan, Decimal]:
    """Suma $20 al balance y registra el préstamo.

    Solo se permite si el saldo actual es menor a $5 (para evitar acumular
    préstamos sin gastar). Sin límite diario por ahora.
    """
    wallet = wallet_service.get_wallet(db, user_id)
    if wallet.balance >= LOAN_MAX_BALANCE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can only request a loan when your balance is below ${LOAN_MAX_BALANCE}",
        )

    wallet.balance += LOAN_AMOUNT
    loan = Loan(user_id=user_id, amount=LOAN_AMOUNT)
    db.add(loan)
    db.commit()
    db.refresh(wallet)
    db.refresh(loan)
    return loan, wallet.balance


def get_loans_history(db: Session, user_id: uuid.UUID) -> list[Loan]:
    return (
        db.query(Loan)
        .filter(Loan.user_id == user_id)
        .order_by(Loan.requested_at.desc())
        .all()
    )
