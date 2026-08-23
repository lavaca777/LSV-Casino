from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import TokenResponse, UserLogin, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(
    payload: UserRegister,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Registra un usuario y crea su wallet vacía."""
    return auth_service.register(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Autentica con email/username + contraseña y retorna un JWT."""
    return auth_service.login(db, payload, request)


@router.post("/logout")
def logout() -> dict[str, str]:
    """Logout stateless: el cliente descarta el token."""
    return {"message": "Logged out"}
