import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.config import settings

EMAIL_REGEX = r"^[a-z0-9.+-]+@[a-z0-9.-]+\.[a-z]{2,}$"


class UserRegister(BaseModel):
    email: str
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=settings.MIN_PASSWORD_LENGTH, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("username")
    @classmethod
    def strip_username(cls, value: str) -> str:
        return value.strip()


class UserLogin(BaseModel):
    email_or_username: str
    password: str


class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip().lower()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email format")
        return value

    @field_validator("username")
    @classmethod
    def strip_username(cls, value: str | None) -> str | None:
        return value.strip() if value else value


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=settings.MIN_PASSWORD_LENGTH, max_length=128)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    balance: float
    total_wagered: float
