import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Loan
from app.services import wallet_service

LOAN_AMOUNT = Decimal("20")


def request_loan(db: Session, user_id: uuid.UUID) -> tuple[Loan, Decimal]:
    """Suma $20 al balance y registra el préstamo (sin límite diario por ahora)."""
    wallet = wallet_service.get_wallet(db, user_id)
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
