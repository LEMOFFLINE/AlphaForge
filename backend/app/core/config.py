from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str = "/api"
    SECRET_KEY: str = Field(min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ACCESS_TOKEN_COOKIE_NAME: str = "alphaforge_access_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/alphaforge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    STOCK_CACHE_TTL_SECONDS: int = 7200
    STOCK_CACHE_REFRESH_INTERVAL_SECONDS: int = 3600
    STOCK_TREND_RETENTION_DAYS: int = 8

    # Alpha Vantage
    ALPHA_VANTAGE_API_KEY: str = ""
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"
    FINNHUB_API_KEY: str = ""
    FINNHUB_BASE_URL: str = "https://finnhub.io/api/v1"
    FINNHUB_MIN_INTERVAL_SECONDS: float = 1.1
    YAHOO_CHART_BASE_URL: str = "https://query1.finance.yahoo.com/v8/finance/chart"

    @property
    def STOCK_TREND_RETENTION_DAYS_DELTA(self):
        from datetime import timedelta

        return timedelta(days=self.STOCK_TREND_RETENTION_DAYS)

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
