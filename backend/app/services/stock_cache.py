from datetime import datetime
from typing import Dict, Optional

from app.core.cache import cache_client
from app.core.config import settings
from app.services.alpha_vantage import alpha_vantage
from app.services.popular_stocks import POPULAR_STOCKS


class StockCache:
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._last_update: Optional[datetime] = None
        self._is_refreshing = False
        self._cache_ttl = settings.STOCK_CACHE_TTL_SECONDS
        self._quote_key_prefix = "stocks:quote:"
        self._popular_quotes_key = "stocks:popular_quotes"
        self._last_update_key = "stocks:last_update"

    async def update_cache(self):
        """Refresh popular stock quotes in Redis, with memory fallback."""
        if self._is_refreshing:
            return

        self._is_refreshing = True
        print(f"Updating stock cache at {datetime.now()}")
        popular_quotes = []

        try:
            for stock in POPULAR_STOCKS:
                symbol = stock["symbol"].upper()
                try:
                    quote = await alpha_vantage.get_quote(symbol)
                    if quote:
                        cached_quote = {
                            **quote,
                            "symbol": quote.get("symbol", symbol).upper(),
                            "name": stock["name"],
                        }
                        self._cache[symbol] = cached_quote
                        popular_quotes.append(self._to_popular_quote(cached_quote))
                        cache_client.set_json(
                            self._quote_key(symbol),
                            cached_quote,
                            ttl_seconds=self._cache_ttl,
                        )
                except Exception as e:
                    print(f"Error caching {symbol}: {e}")

            self._last_update = datetime.now()
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
            print(f"Stock cache updated: {len(self._cache)} stocks")
        finally:
            self._is_refreshing = False

    def get_cached_quotes(self) -> list:
        """Return cached popular quotes from Redis or the local process."""
        redis_quotes = cache_client.get_json(self._popular_quotes_key)
        if redis_quotes:
            return redis_quotes

        if not self._cache:
            return []

        return [self._to_popular_quote(data) for data in self._cache.values()]

    def is_expired(self) -> bool:
        """Check whether the quote cache needs a refresh."""
        redis_last_update = cache_client.get_json(self._last_update_key)
        if redis_last_update:
            try:
                last_update = datetime.fromisoformat(redis_last_update)
                elapsed = (datetime.now() - last_update).total_seconds()
                return elapsed > self._cache_ttl
            except ValueError:
                return True

        if self._last_update is None:
            return True

        elapsed = (datetime.now() - self._last_update).total_seconds()
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

    @staticmethod
    def _to_popular_quote(data: dict) -> dict:
        return {
            "symbol": data["symbol"],
            "name": data.get("name", ""),
            "price": data["price"],
            "change": data["change"],
            "change_percent": data["change_percent"],
        }


stock_cache = StockCache()
