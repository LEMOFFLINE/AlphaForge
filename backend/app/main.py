import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import account_values, accounts, auth, orders, stocks
from app.core.cache import cache_client
from app.core.config import settings
from app.core.database import Base, engine
from app.services.stock_cache import stock_cache

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AlphaForge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(stocks.router, prefix="/api")
app.include_router(account_values.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(stock_cache.update_cache())


@app.on_event("shutdown")
async def shutdown_event():
    cache_client.close()


@app.get("/")
async def root():
    return {"message": "AlphaForge API"}


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "redis": "connected" if cache_client.healthcheck() else "unavailable",
    }
