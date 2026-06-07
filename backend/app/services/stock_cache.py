from datetime import datetime
from typing import Dict, Optional
from app.services.alpha_vantage import alpha_vantage
from app.services.popular_stocks import POPULAR_STOCKS


class StockCache:
    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._last_update: Optional[datetime] = None
        self._cache_ttl = 300  # 缓存5分钟

    async def update_cache(self):
        """更新所有热门股票的缓存"""
        print(f"Updating stock cache at {datetime.now()}")
        for stock in POPULAR_STOCKS:
            symbol = stock["symbol"]
            try:
                quote = await alpha_vantage.get_quote(symbol)
                if quote:
                    self._cache[symbol] = {
                        **quote,
                        "name": stock["name"],
                    }
            except Exception as e:
                print(f"Error caching {symbol}: {e}")

        self._last_update = datetime.now()
        print(f"Stock cache updated: {len(self._cache)} stocks")

    def get_cached_quotes(self) -> list:
        """获取所有缓存的股票报价"""
        if not self._cache:
            return []

        return [
            {
                "symbol": data["symbol"],
                "name": data.get("name", ""),
                "price": data["price"],
                "change": data["change"],
                "change_percent": data["change_percent"],
            }
            for data in self._cache.values()
        ]

    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        if self._last_update is None:
            return True

        elapsed = (datetime.now() - self._last_update).total_seconds()
        return elapsed > self._cache_ttl

    def get_quote(self, symbol: str) -> Optional[dict]:
        """获取单个股票的缓存报价"""
        return self._cache.get(symbol)


# 全局缓存实例
stock_cache = StockCache()
