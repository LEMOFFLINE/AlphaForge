from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List
import uuid

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, Account, AccountValue, Position
from app.models.schemas import AccountValueResponse
from app.services.stock_cache import stock_cache

router = APIRouter(prefix="/account-values", tags=["account-values"])


def calculate_account_value(account: Account, db: Session) -> dict:
    """计算账户当前总价值"""
    # 获取所有持仓
    positions = db.query(Position).filter(Position.account_id == account.id).all()

    # 计算持仓市值
    positions_value = 0
    for pos in positions:
        # 从缓存获取实时价格
        quote = stock_cache.get_quote(pos.symbol)
        current_price = quote["price"] if quote else pos.avg_cost
        positions_value += current_price * pos.shares

    # 总资产 = 现金 + 持仓市值
    total_value = account.current_balance + positions_value

    return {
        "total_value": total_value,
        "cash_balance": account.current_balance,
        "positions_value": positions_value,
    }


@router.post("/record/{account_id}")
async def record_account_value(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """记录当前账户价值（手动触发或定时任务调用）"""
    # 验证账户所有权
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id,
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 计算当前价值
    values = calculate_account_value(account, db)

    # 检查今天是否已记录（避免重复）
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing = db.query(AccountValue).filter(
        AccountValue.account_id == account_id,
        func.date(AccountValue.recorded_at) == func.date(today),
    ).first()

    if existing:
        # 更新今天的记录
        existing.total_value = values["total_value"]
        existing.cash_balance = values["cash_balance"]
        existing.positions_value = values["positions_value"]
    else:
        # 创建新记录
        account_value = AccountValue(
            id=str(uuid.uuid4()),
            account_id=account_id,
            **values,
        )
        db.add(account_value)

    db.commit()
    return {"message": "Account value recorded"}


@router.get("/{account_id}", response_model=List[AccountValueResponse])
async def get_account_value_history(
    account_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取账户价值历史"""
    # 验证账户所有权
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id,
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 计算起始日期
    start_date = datetime.utcnow() - timedelta(days=days)

    # 查询历史记录
    history = db.query(AccountValue).filter(
        AccountValue.account_id == account_id,
        AccountValue.recorded_at >= start_date,
    ).order_by(AccountValue.recorded_at.asc()).all()

    # 如果没有历史记录，返回初始值
    if not history:
        # 创建一个初始记录
        initial_value = AccountValue(
            id=str(uuid.uuid4()),
            account_id=account_id,
            total_value=account.initial_balance,
            cash_balance=account.initial_balance,
            positions_value=0,
            recorded_at=account.created_at,
        )
        history = [initial_value]

    return history
