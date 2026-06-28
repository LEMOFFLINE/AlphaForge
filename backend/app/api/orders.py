from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.schemas import OrderCreate, OrderResponse
from app.models.user import Account, Order, User
from app.services.trading import (
    AccountNotFoundError,
    InsufficientBalanceError,
    InsufficientPositionError,
    trading_service,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        order = trading_service.create_order(order_data, current_user, db)
    except AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except InsufficientBalanceError:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    except InsufficientPositionError:
        raise HTTPException(status_code=400, detail="Insufficient position")

    return OrderResponse.model_validate(order)


@router.get("/{account_id}", response_model=List[OrderResponse])
async def get_orders(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id,
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    orders = db.query(Order).filter(Order.account_id == account_id).order_by(Order.created_at.desc()).all()
    return [OrderResponse.model_validate(order) for order in orders]
