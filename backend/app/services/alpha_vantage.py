import httpx
import json
import asyncio
from typing import Optional
from app.core.config import settings
from app.services.mock_stocks import get_mock_quote


class AlphaVantageService:
    def __init__(self):
        self.base_url = settings.ALPHA_VANTAGE_BASE_URL
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self._last_request_time = 0
        self._min_interval = 12  # 最小请求间隔（秒），每分钟最多5次

    async def _rate_limit(self):
        """简单的限流控制"""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self._last_request_time
        if time_since_last < self._min_interval:
            await asyncio.sleep(self._min_interval - time_since_last)
        self._last_request_time = asyncio.get_event_loop().time()

    async def get_quote(self, symbol: str) -> Optional[dict]:
        """获取实时报价"""
        # 先尝试模拟数据
        mock_data = get_mock_quote(symbol)
        if mock_data:
            return mock_data

        await self._rate_limit()

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                data = response.json()

                # 检查是否达到限流
                if "Note" in data or "Information" in data:
                    print(f"Alpha Vantage API limit reached: {data.get('Note', data.get('Information'))}")
                    # 使用模拟数据
                    return get_mock_quote(symbol)

                quote = data.get("Global Quote", {})
                if not quote or not quote.get("05. price"):
                    return get_mock_quote(symbol)

                return {
                    "symbol": quote.get("01. symbol", symbol),
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
                    "volume": int(quote.get("06. volume", 0)),
                }
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return get_mock_quote(symbol)

    async def get_daily_data(self, symbol: str, outputsize: str = "compact") -> Optional[dict]:
        """获取日线数据"""
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": outputsize,
            "apikey": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            return response.json()

    async def search_symbol(self, keywords: str) -> Optional[list]:
        """搜索股票代码"""
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, params=params)
            data = response.json()

            matches = data.get("bestMatches", [])
            if not matches:
                return []

            return [
                {
                    "symbol": match.get("1. symbol"),
                    "name": match.get("2. name"),
                    "type": match.get("3. type"),
                    "region": match.get("4. region"),
                }
                for match in matches[:10]
            ]


alpha_vantage = AlphaVantageService()
