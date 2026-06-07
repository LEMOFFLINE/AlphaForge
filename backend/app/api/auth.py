from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.models.user import User
from app.models.schemas import UserCreate, UserResponse, Token, LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 创建用户
    import uuid
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        id=user_id,
        email=user_data.email,
        hashed_password=hashed_password,
    )
    db.add(new_user)

    # 创建账户
    from app.models.user import Account
    account_id = str(uuid.uuid4())
    new_account = Account(
        id=account_id,
        user_id=user_id,
        initial_balance=float(user_data.initial_balance),
        current_balance=float(user_data.initial_balance),
    )
    db.add(new_account)

    db.commit()
    db.refresh(new_user)

    # 生成 token
    access_token = create_access_token(data={"sub": user_id})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user),
    )


@router.post("/login", response_model=Token)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.id})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout():
    # 在实际应用中，可能需要将 token 加入黑名单
    return {"message": "Successfully logged out"}
