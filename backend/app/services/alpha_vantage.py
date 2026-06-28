import asyncio
from typing import Optional

import httpx

from app.core.config import settings


class AlphaVantageService:
    def __init__(self):
        self.base_url = settings.ALPHA_VANTAGE_BASE_URL
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self._last_request_time = 0
        self._min_interval = 12

    async def _rate_limit(self):
        now = asyncio.get_event_loop().time()
        time_since_last = now - self._last_request_time
        if time_since_last < self._min_interval:
            await asyncio.sleep(self._min_interval - time_since_last)
        self._last_request_time = asyncio.get_event_loop().time()

    async def get_quote(self, symbol: str) -> Optional[dict]:
        await self._rate_limit()

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
            "apikey": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if "Note" in data or "Information" in data:
                    print(f"Alpha Vantage API limit reached: {data.get('Note', data.get('Information'))}")
                    return None

                quote = data.get("Global Quote", {})
                if not quote or not quote.get("05. price"):
                    print(f"Alpha Vantage quote not found for {symbol}: {data}")
                    return None

                return {
                    "symbol": quote.get("01. symbol", symbol).upper(),
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": float(quote.get("10. change percent", "0").replace("%", "")),
                    "volume": int(quote.get("06. volume", 0)),
                }
        except (httpx.HTTPError, ValueError, KeyError) as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    async def get_daily_data(self, symbol: str, outputsize: str = "compact") -> Optional[dict]:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol.upper(),
            "outputsize": outputsize,
            "apikey": self.api_key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()

    async def search_symbol(self, keywords: str) -> Optional[list]:
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "apikey": self.api_key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
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
