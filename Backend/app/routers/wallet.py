from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import WalletResponse
from app.services import wallet_service
from app.utils.security import CurrentUser

router = APIRouter(tags=["wallet"])


@router.get("/users/{user_id}/wallet", response_model=WalletResponse)
def get_wallet(
    user_id: UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> WalletResponse:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own wallet",
        )
    return wallet_service.get_wallet(db, user_id)
