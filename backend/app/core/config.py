from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API
    API_V1_PREFIX: str = "/api"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/alphaforge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Alpha Vantage
    ALPHA_VANTAGE_API_KEY: str = "6NM9RLOVI80BJ8WY"
    ALPHA_VANTAGE_BASE_URL: str = "https://www.alphavantage.co/query"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
