from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, Account, Position
from app.models.schemas import AccountResponse, PositionResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("", response_model=List[AccountResponse])
async def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return [AccountResponse.model_validate(acc) for acc in accounts]


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
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

    return AccountResponse.model_validate(account)


@router.get("/{account_id}/positions", response_model=List[PositionResponse])
async def get_positions(
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

    positions = db.query(Position).filter(Position.account_id == account_id).all()
    return [PositionResponse.model_validate(pos) for pos in positions]
