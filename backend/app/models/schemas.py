from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime
from typing import Optional, Literal
from app.models.user import OrderType, OrderStatus


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    initial_balance: int = 100000  # 100K, 1M, or 10M


class UserResponse(BaseModel):
    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Token schema
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Login schema
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


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
    symbol: str
    type: OrderType
    shares: int
    price: float


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
