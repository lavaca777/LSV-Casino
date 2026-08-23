from decimal import Decimal

from fastapi import HTTPException, Request, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import User, Wallet
from app.schemas import TokenResponse, UserLogin, UserRegister
from app.utils.rate_limiter import login_rate_limiter
from app.utils.security import create_access_token, hash_password, verify_password


def _rate_limit_key(email_or_username: str, request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    return f"{email_or_username.lower()}:{ip}"


def register(db: Session, payload: UserRegister) -> TokenResponse:
    email = payload.email.lower()
    username = payload.username

    existing = db.query(User).filter(
        or_(User.email == email, User.username == username)
    ).first()
    if existing is not None:
        if existing.email == email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()

    wallet = Wallet(user_id=user.id, balance=Decimal("0"), total_wagered=Decimal("0"))
    db.add(wallet)
    db.commit()
    db.refresh(user)

    token = create_access_token(user)
    return TokenResponse(access_token=token, user_id=user.id)


def login(db: Session, payload: UserLogin, request: Request) -> TokenResponse:
    identifier = payload.email_or_username.strip().lower()
    key = _rate_limit_key(identifier, request)

    if login_rate_limiter.is_blocked(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Try again in 1 minute",
        )

    user = db.query(User).filter(
        or_(User.email == identifier, User.username == identifier)
    ).first()

    if user is None or not verify_password(payload.password, user.password_hash):
        login_rate_limiter.register_failure(key)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    login_rate_limiter.clear(key)
    token = create_access_token(user)
    return TokenResponse(access_token=token, user_id=user.id)
