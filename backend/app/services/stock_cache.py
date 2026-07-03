import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from app.core.cache import cache_client
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import StockPriceHistory
from app.services.finnhub import finnhub
from app.services.popular_stocks import POPULAR_STOCKS


class StockCache:
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._last_update: Optional[datetime] = None
        self._is_refreshing = False
        self._refresh_interval = settings.STOCK_CACHE_REFRESH_INTERVAL_SECONDS
        self._cache_ttl = max(settings.STOCK_CACHE_TTL_SECONDS, self._refresh_interval * 2)
        self._quote_key_prefix = "stocks:quote:"
        self._popular_quotes_key = "stocks:popular_quotes"
        self._last_update_key = "stocks:last_update"

    async def run_periodic_refresh(self):
        """Continuously refresh popular quotes on a fixed start-to-start interval."""
        while True:
            started_at = asyncio.get_running_loop().time()
            await self.update_cache()
            elapsed = asyncio.get_running_loop().time() - started_at
            await asyncio.sleep(max(0, self._refresh_interval - elapsed))

    async def update_cache(self):
        """Refresh popular stock quotes in Redis, with memory fallback."""
        if self._is_refreshing:
            return

        self._is_refreshing = True
        refresh_time = datetime.utcnow()
        print(f"Updating stock cache at {refresh_time}")
        history_rows = []

        try:
            for stock in POPULAR_STOCKS:
                symbol = stock["symbol"].upper()
                try:
                    quote = await finnhub.get_quote(symbol)
                    if quote:
                        cached_quote = {
                            **quote,
                            "symbol": quote.get("symbol", symbol).upper(),
                            "name": stock["name"],
                        }
                        self._cache[symbol] = cached_quote
                        cache_client.set_json(
                            self._quote_key(symbol),
                            cached_quote,
                            ttl_seconds=self._cache_ttl,
                        )
                        history_rows.append(
                            StockPriceHistory(
                                id=str(uuid.uuid4()),
                                symbol=symbol,
                                price=float(cached_quote["price"]),
                                recorded_at=self._quote_recorded_at(cached_quote, refresh_time),
                            )
                        )
                except Exception as e:
                    print(f"Error caching {symbol}: {e}")

            self._record_price_history(history_rows, refresh_time)
            popular_quotes = self._current_popular_quotes()
            self._last_update = refresh_time
            cache_client.set_json(
                self._popular_quotes_key,
                popular_quotes,
                ttl_seconds=self._cache_ttl,
            )
            cache_client.set_json(
                self._last_update_key,
                self._last_update.isoformat(),
                ttl_seconds=self._cache_ttl,
            )
            print(f"Stock cache updated: {len(popular_quotes)} stocks")
        finally:
            self._is_refreshing = False

    def get_cached_quotes(self) -> list:
        """Return cached popular quotes from Redis or the local process."""
        redis_quotes = cache_client.get_json(self._popular_quotes_key)
        if redis_quotes:
            return redis_quotes

        if not self._cache:
            return []

        return self._current_popular_quotes()

    def is_expired(self) -> bool:
        """Check whether the quote cache needs a refresh."""
        redis_last_update = cache_client.get_json(self._last_update_key)
        if redis_last_update:
            try:
                last_update = datetime.fromisoformat(redis_last_update)
                elapsed = (datetime.utcnow() - last_update).total_seconds()
                return elapsed > self._cache_ttl
            except ValueError:
                return True

        if self._last_update is None:
            return True

        elapsed = (datetime.utcnow() - self._last_update).total_seconds()
        return elapsed > self._cache_ttl

    def get_quote(self, symbol: str) -> Optional[dict]:
        """Return a single cached quote by symbol."""
        normalized_symbol = symbol.upper()
        redis_quote = cache_client.get_json(self._quote_key(normalized_symbol))
        if redis_quote:
            return redis_quote

        return self._cache.get(normalized_symbol)

    def _quote_key(self, symbol: str) -> str:
        return f"{self._quote_key_prefix}{symbol.upper()}"

    def _record_price_history(self, rows: list[StockPriceHistory], refresh_time: datetime) -> None:
        if not rows:
            return

        db = SessionLocal()
        try:
            cutoff = refresh_time.replace(microsecond=0) - settings.STOCK_TREND_RETENTION_DAYS_DELTA
            db.query(StockPriceHistory).filter(StockPriceHistory.recorded_at < cutoff).delete()
            db.add_all(rows)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error recording stock price history: {e}")
        finally:
            db.close()

    def _current_popular_quotes(self) -> list:
        quotes = []
        for stock in POPULAR_STOCKS:
            symbol = stock["symbol"].upper()
            cached = self._cache.get(symbol)
            if cached:
                quotes.append(self._to_popular_quote(cached))
        return quotes

    @staticmethod
    def _to_popular_quote(data: dict) -> dict:
        return {
            "symbol": data["symbol"],
            "name": data.get("name", ""),
            "price": data["price"],
            "change": data["change"],
            "change_percent": data["change_percent"],
            "timestamp": data.get("timestamp"),
        }

    @staticmethod
    def _quote_recorded_at(data: dict, fallback: datetime) -> datetime:
        timestamp = int(data.get("timestamp") or 0)
        if timestamp <= 0:
            return fallback
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(tzinfo=None)


stock_cache = StockCache()
