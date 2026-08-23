import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import PasswordChange, UserResponse, UserUpdate
from app.services import user_service
from app.utils.security import CurrentUser

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    _ensure_owner(current_user, user_id)
    return user_service.get_user_by_id(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    _ensure_owner(current_user, user_id)
    return user_service.update_user(db, current_user, payload)


@router.put("/{user_id}/password")
def change_password(
    user_id: uuid.UUID,
    payload: PasswordChange,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    _ensure_owner(current_user, user_id)
    user_service.change_password(db, current_user, payload)
    return {"message": "Password updated"}


def _ensure_owner(current_user: User, user_id: uuid.UUID) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own profile",
        )
