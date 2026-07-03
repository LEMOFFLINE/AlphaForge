import asyncio
import contextlib
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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


SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _request_origin(headers) -> str | None:
    origin = headers.get("origin")
    if origin:
        return origin

    referer = headers.get("referer")
    if not referer:
        return None

    parsed = urlparse(referer)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


@app.middleware("http")
async def reject_untrusted_write_origins(request: Request, call_next):
    if request.method not in SAFE_METHODS:
        origin = _request_origin(request.headers)
        if origin is not None and origin not in settings.CORS_ORIGINS:
            return JSONResponse(
                status_code=403,
                content={"detail": "Untrusted request origin"},
            )

    return await call_next(request)


app.include_router(auth.router, prefix="/api")
app.include_router(accounts.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(stocks.router, prefix="/api")
app.include_router(account_values.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    app.state.stock_cache_task = asyncio.create_task(stock_cache.run_periodic_refresh())


@app.on_event("shutdown")
async def shutdown_event():
    stock_cache_task = getattr(app.state, "stock_cache_task", None)
    if stock_cache_task:
        stock_cache_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await stock_cache_task
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
