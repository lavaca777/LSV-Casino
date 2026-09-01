from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import (
    LoanRequestResponse,
    LoanResponse,
    WalletResponse,
    WithdrawalRequest,
    WithdrawalResponse,
)
from app.services import loan_service, wallet_service, withdrawal_service
from app.utils.security import CurrentUser

router = APIRouter(tags=["wallet"])


def _ensure_owner(current_user: User, user_id: UUID) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own wallet",
        )


@router.get("/users/{user_id}/wallet", response_model=WalletResponse)
def get_wallet(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> WalletResponse:
    _ensure_owner(current_user, user_id)
    return wallet_service.get_wallet(db, user_id)


@router.post("/users/{user_id}/loans/request", response_model=LoanRequestResponse)
def request_loan(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> LoanRequestResponse:
    _ensure_owner(current_user, user_id)
    loan, new_balance = loan_service.request_loan(db, user_id)
    return LoanRequestResponse(
        new_balance=float(new_balance), loan_amount=float(loan.amount)
    )


@router.get("/users/{user_id}/loans/history", response_model=list[LoanResponse])
def get_loans_history(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[LoanResponse]:
    _ensure_owner(current_user, user_id)
    return loan_service.get_loans_history(db, user_id)


@router.post("/users/{user_id}/withdrawals/request", response_model=WithdrawalResponse)
def request_withdrawal(
    user_id: UUID,
    payload: WithdrawalRequest,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> WithdrawalResponse:
    _ensure_owner(current_user, user_id)
    amount = Decimal(str(payload.amount))
    return withdrawal_service.request_withdrawal(db, user_id, amount)


@router.get("/users/{user_id}/withdrawals", response_model=list[WithdrawalResponse])
def get_withdrawals(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> list[WithdrawalResponse]:
    _ensure_owner(current_user, user_id)
    return withdrawal_service.get_withdrawals(db, user_id)
