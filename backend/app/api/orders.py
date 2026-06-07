from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
import uuid
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, Account, Order, Position, OrderType, OrderStatus
from app.models.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])

# 手续费配置
COMMISSION_FIXED = 5.0  # 固定费用 $5
COMMISSION_RATE = 0.001  # 0.1%


def calculate_commission(amount: float) -> float:
    return COMMISSION_FIXED + (amount * COMMISSION_RATE)


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 验证账户所有权
    account = db.query(Account).filter(
        Account.id == order_data.account_id,
        Account.user_id == current_user.id,
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 计算手续费
    commission = calculate_commission(order_data.shares * order_data.price)
    total_amount = order_data.shares * order_data.price + commission

    if order_data.type == "buy":
        # 买入：检查余额
        if account.current_balance < total_amount:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # 更新账户余额
        account.current_balance -= total_amount

        # 更新或创建持仓
        position = db.query(Position).filter(
            Position.account_id == order_data.account_id,
            Position.symbol == order_data.symbol,
        ).first()

        if position:
            # 更新平均成本
            total_shares = position.shares + order_data.shares
            total_cost = (position.avg_cost * position.shares) + (order_data.price * order_data.shares)
            position.avg_cost = total_cost / total_shares
            position.shares = total_shares
        else:
            position = Position(
                id=str(uuid.uuid4()),
                account_id=order_data.account_id,
                symbol=order_data.symbol,
                shares=order_data.shares,
                avg_cost=order_data.price,
            )
            db.add(position)

    else:  # sell
        # 卖出：检查持仓
        position = db.query(Position).filter(
            Position.account_id == order_data.account_id,
            Position.symbol == order_data.symbol,
        ).first()

        if not position or position.shares < order_data.shares:
            raise HTTPException(status_code=400, detail="Insufficient position")

        # 更新持仓
        position.shares -= order_data.shares
        if position.shares == 0:
            db.delete(position)

        # 更新账户余额
        account.current_balance += order_data.shares * order_data.price - commission

    # 创建订单记录
    order = Order(
        id=str(uuid.uuid4()),
        account_id=order_data.account_id,
        symbol=order_data.symbol,
        type=OrderType.BUY if order_data.type == "buy" else OrderType.SELL,
        shares=order_data.shares,
        price=order_data.price,
        commission=commission,
        status=OrderStatus.COMPLETED,
    )
    db.add(order)

    # 记录交易后的账户价值
    from app.api.account_values import calculate_account_value, AccountValue
    values = calculate_account_value(account, db)
    account_value = AccountValue(
        id=str(uuid.uuid4()),
        account_id=order_data.account_id,
        **values,
    )
    db.add(account_value)

    db.commit()
    db.refresh(order)

    return OrderResponse.model_validate(order)


@router.get("/{account_id}", response_model=List[OrderResponse])
async def get_orders(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 验证账户所有权
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id,
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    orders = db.query(Order).filter(Order.account_id == account_id).order_by(Order.created_at.desc()).all()
    return [OrderResponse.model_validate(order) for order in orders]
