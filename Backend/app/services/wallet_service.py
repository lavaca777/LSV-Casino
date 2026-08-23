import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Wallet


def get_wallet(db: Session, user_id: uuid.UUID) -> Wallet:
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
        )
    return wallet
