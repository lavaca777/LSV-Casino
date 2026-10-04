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


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: float
    requested_at: datetime


class LoanRequestResponse(BaseModel):
    new_balance: float
    loan_amount: float


class WithdrawalRequest(BaseModel):
    amount: float = Field(gt=0)


class WithdrawalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    amount: float
    requested_at: datetime
    status: str


class GameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    min_bet: float
    max_bet: float
    house_edge: float


class CoinflipPlayRequest(BaseModel):
    bet: float = Field(gt=0)
    eleccion: str

    @field_validator("eleccion")
    @classmethod
    def validate_eleccion(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in ("cara", "cruz"):
            raise ValueError("eleccion must be 'cara' or 'cruz'")
        return value


class CoinflipPlayResponse(BaseModel):
    resultado: str
    eleccion: str
    moneda: str
    bet: float
    payout: float
    nuevo_balance: float


class BlackjackStartRequest(BaseModel):
    bet: float = Field(gt=0)


class BlackjackCard(BaseModel):
    palo: str
    rango: str


class BlackjackPlayResponse(BaseModel):
    """Respuesta compartida por start/hit/stand.

    Como blackjack se juega en varios pasos, no todos los campos vienen
    siempre: mientras la ronda sigue abierta (turn="player"), solo hay
    session_id/mano_jugador/turn; al terminar (turn="done") ya vienen
    manos_bots, resultado, payout y nuevo_balance.
    """

    session_id: str | None = None
    mano_jugador: list[BlackjackCard]
    manos_bots: list[list[BlackjackCard]] | None = None
    turn: str
    resultado: str | None = None
    payout: float | None = None
    nuevo_balance: float | None = None


class GameHistoryItem(BaseModel):
    """Una partida en el listado de historial."""

    id: uuid.UUID
    game_name: str
    date: datetime
    bet: float
    result: str | None
    payout: float
    balance_after: float


class GameHistoryList(BaseModel):
    total: int
    games: list[GameHistoryItem]


class GameHistoryDetail(GameHistoryItem):
    """Detalle de una partida (incluye las manos jugadas)."""

    player_hand: list
    bot_hands: list
    duration_seconds: float | None


class StatsResponse(BaseModel):
    """Estadísticas agregadas del jugador."""

    total_games: int
    total_games_won: int
    total_games_lost: int
    total_games_drawn: int
    win_rate: float
    current_streak: int
    longest_streak: int
    biggest_win: float
    total_wagered: float
    net_profit: float