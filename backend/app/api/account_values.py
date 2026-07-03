import uuid
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.database import get_db
from app.models.schemas import AccountValueResponse
from app.models.user import Account, AccountValue, User
from app.services.account_valuation import calculate_account_value

router = APIRouter(prefix="/account-values", tags=["account-values"])


@router.post("/record/{account_id}")
async def record_account_value(
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

    values = calculate_account_value(account, db)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    existing = db.query(AccountValue).filter(
        AccountValue.account_id == account_id,
        func.date(AccountValue.recorded_at) == func.date(today),
    ).first()

    if existing:
        existing.total_value = values["total_value"]
        existing.cash_balance = values["cash_balance"]
        existing.positions_value = values["positions_value"]
    else:
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
    days: int = Query(default=30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id,
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    start_date = datetime.utcnow() - timedelta(days=days)
    history = db.query(AccountValue).filter(
        AccountValue.account_id == account_id,
        AccountValue.recorded_at >= start_date,
    ).order_by(AccountValue.recorded_at.asc()).all()

    if not history:
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
