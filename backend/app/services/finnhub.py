import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

from app.core.config import settings


class FinnhubService:
    def __init__(self):
        self.base_url = settings.FINNHUB_BASE_URL
        self.api_key = settings.FINNHUB_API_KEY
        self._last_request_time = 0.0
        self._min_interval = settings.FINNHUB_MIN_INTERVAL_SECONDS
        self._max_retries = max(0, settings.FINNHUB_MAX_RETRIES)
        self._retry_delay = max(0.0, settings.FINNHUB_RETRY_DELAY_SECONDS)

    async def _rate_limit(self):
        now = asyncio.get_running_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            await asyncio.sleep(self._min_interval - elapsed)
        self._last_request_time = asyncio.get_running_loop().time()

    async def _get(self, path: str, params: dict) -> Optional[dict | list]:
        if not self.api_key:
            print("Finnhub API key is missing")
            return None

        request_params = {**params, "token": self.api_key}

        for attempt in range(self._max_retries + 1):
            await self._rate_limit()
            try:
                async with httpx.AsyncClient(timeout=20.0) as client:
                    response = await client.get(f"{self.base_url}{path}", params=request_params)
                    response.raise_for_status()
                    data = response.json()

                    if isinstance(data, dict) and data.get("error"):
                        print(f"Finnhub API error: {data['error']}")
                        return None

                    return data
            except (httpx.HTTPError, ValueError) as e:
                if attempt >= self._max_retries:
                    print(f"Error calling Finnhub {path}: {e}")
                    return None
                await asyncio.sleep(self._retry_delay)

        return None

    async def get_quote(self, symbol: str) -> Optional[dict]:
        normalized_symbol = symbol.upper()
        data = await self._get("/quote", {"symbol": normalized_symbol})
        if not isinstance(data, dict):
            return None

        price = float(data.get("c") or 0)
        if price <= 0:
            print(f"Finnhub quote not found for {normalized_symbol}: {data}")
            return None

        return {
            "symbol": normalized_symbol,
            "price": price,
            "change": float(data.get("d") or 0),
            "change_percent": float(data.get("dp") or 0),
            "volume": 0,
            "timestamp": int(data.get("t") or 0),
        }

    async def search_symbol(self, query: str) -> list:
        data = await self._get("/search", {"q": query})
        if not isinstance(data, dict):
            return []

        results = data.get("result") or []
        return [
            {
                "symbol": match.get("symbol"),
                "name": match.get("description"),
                "type": match.get("type"),
                "region": "",
            }
            for match in results[:10]
        ]

    async def get_daily_data(self, symbol: str) -> Optional[dict]:
        today = datetime.now(timezone.utc)
        start = today - timedelta(days=120)
        return await self._get(
            "/stock/candle",
            {
                "symbol": symbol.upper(),
                "resolution": "D",
                "from": int(start.timestamp()),
                "to": int(today.timestamp()),
            },
        )


finnhub = FinnhubService()
