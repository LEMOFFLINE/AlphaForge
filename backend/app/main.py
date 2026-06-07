from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, accounts, orders, stocks, account_values
from app.services.stock_cache import stock_cache

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AlphaForge API")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(stocks.router, prefix="/api")
app.include_router(account_values.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """启动时初始化股票缓存"""
    await stock_cache.update_cache()


@app.get("/")
async def root():
    return {"message": "AlphaForge API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
