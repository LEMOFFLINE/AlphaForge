from typing import Literal, Optional

import httpx

from app.core.config import settings

TrendRange = Literal["1d", "7d"]


class YahooChartService:
    def __init__(self):
        self.base_url = settings.YAHOO_CHART_BASE_URL

    async def get_trend(self, symbol: str, trend_range: TrendRange) -> Optional[dict]:
        normalized_symbol = symbol.upper()
        yahoo_symbol = normalized_symbol.replace(".", "-")
        range_param = "1d" if trend_range == "1d" else "7d"
        interval = "5m" if trend_range == "1d" else "1h"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/{yahoo_symbol}",
                    params={
                        "range": range_param,
                        "interval": interval,
                        "includePrePost": "false",
                    },
                    headers={"User-Agent": "AlphaForge/1.0"},
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as e:
            print(f"Error calling Yahoo chart for {normalized_symbol}: {e}")
            return None

        chart = data.get("chart") if isinstance(data, dict) else None
        results = chart.get("result") if isinstance(chart, dict) else None
        if not results:
            return None

        result = results[0]
        timestamps = result.get("timestamp") or []
        indicators = result.get("indicators") or {}
        quotes = indicators.get("quote") or []
        closes = quotes[0].get("close") if quotes else []
        if not timestamps or not closes:
            return None

        points = [
            {"timestamp": int(timestamp), "price": float(close)}
            for timestamp, close in zip(timestamps, closes)
            if close is not None
        ]
        if not points:
            return None

        return {
            "symbol": normalized_symbol,
            "range": trend_range,
            "timezone": "Asia/Shanghai",
            "points": points,
        }


yahoo_chart = YahooChartService()
