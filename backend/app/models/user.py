from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    initial_balance = Column(Float, nullable=False)
    current_balance = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    positions = relationship("Position", back_populates="account")
    orders = relationship("Order", back_populates="account")


class OrderType(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Position(Base):
    __tablename__ = "positions"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)
    shares = Column(Integer, nullable=False)
    avg_cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="positions")


class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)
    type = Column(SQLEnum(OrderType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    shares = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus, values_callable=lambda x: [e.value for e in x]), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="orders")


class AccountValue(Base):
    """账户价值历史记录"""
    __tablename__ = "account_values"

    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    total_value = Column(Float, nullable=False)  # 总资产（现金+持仓市值）
    cash_balance = Column(Float, nullable=False)  # 现金余额
    positions_value = Column(Float, nullable=False)  # 持仓市值
    recorded_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account", back_populates="value_history")


class StockPriceHistory(Base):
    __tablename__ = "stock_price_history"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)


# Add relationship to Account
Account.value_history = relationship("AccountValue", back_populates="account", order_by=lambda: AccountValue.recorded_at.desc())
