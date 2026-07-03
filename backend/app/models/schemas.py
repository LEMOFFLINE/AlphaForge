import re

from pydantic import BaseModel, EmailStr, Field, field_serializer, field_validator
from datetime import datetime
from typing import Literal
from app.models.user import OrderType, OrderStatus

SYMBOL_PATTERN = re.compile(r"^[A-Za-z0-9.^-]{1,16}$")


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    initial_balance: Literal[100000, 1000000, 10000000] = 100000


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse


# Login schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


# Account schemas
class AccountBase(BaseModel):
    initial_balance: float
    current_balance: float


class AccountResponse(AccountBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Position schemas
class PositionResponse(BaseModel):
    id: str
    account_id: str
    symbol: str
    shares: int
    avg_cost: float
    created_at: datetime

    class Config:
        from_attributes = True


# Order schemas
class OrderBase(BaseModel):
    account_id: str
    symbol: str = Field(min_length=1, max_length=16)
    type: OrderType
    shares: int = Field(gt=0, le=1_000_000)
    price: float = Field(gt=0, le=1_000_000, allow_inf_nan=False)

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not SYMBOL_PATTERN.fullmatch(normalized):
            raise ValueError("Invalid stock symbol")
        return normalized


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: str
    commission: float
    status: OrderStatus
    created_at: datetime

    @field_serializer('type')
    def serialize_type(self, order_type: OrderType) -> str:
        return order_type.value

    @field_serializer('status')
    def serialize_status(self, status: OrderStatus) -> str:
        return status.value

    class Config:
        from_attributes = True


# Stock schemas
class QuoteResponse(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int


class StockTrendPoint(BaseModel):
    timestamp: int
    price: float


class StockTrendResponse(BaseModel):
    symbol: str
    range: Literal["1d", "7d"]
    timezone: str = "America/New_York"
    points: list[StockTrendPoint]


# Account Value schemas
class AccountValueResponse(BaseModel):
    id: str
    account_id: str
    total_value: float
    cash_balance: float
    positions_value: float
    recorded_at: datetime

    class Config:
        from_attributes = True
