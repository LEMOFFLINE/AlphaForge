from datetime import datetime, timedelta, timezone
from typing import Literal

from app.core.database import SessionLocal
from app.models.user import StockPriceHistory
from app.services.finnhub import finnhub
from app.services.stock_cache import stock_cache
from app.services.yahoo_chart import yahoo_chart

TrendRange = Literal["1d", "7d"]


class StockTrendService:
    async def get_trend(self, symbol: str, trend_range: TrendRange) -> dict | None:
        normalized_symbol = symbol.upper()
        market_trend = await yahoo_chart.get_trend(normalized_symbol, trend_range)
        if market_trend:
            return market_trend

        return await self._get_local_trend(normalized_symbol, trend_range)

    async def _get_local_trend(self, normalized_symbol: str, trend_range: TrendRange) -> dict | None:
        lookback = timedelta(days=1 if trend_range == "1d" else 7)
        start = datetime.utcnow() - lookback

        db = SessionLocal()
        try:
            rows = (
                db.query(StockPriceHistory)
                .filter(
                    StockPriceHistory.symbol == normalized_symbol,
                    StockPriceHistory.recorded_at >= start,
                )
                .order_by(StockPriceHistory.recorded_at.asc())
                .all()
            )
        finally:
            db.close()

        points_by_timestamp = {
            self._utc_timestamp(row.recorded_at): row.price
            for row in rows
        }
        points = [
            {"timestamp": timestamp, "price": price}
            for timestamp, price in sorted(points_by_timestamp.items())
        ]
        points = await self._with_quote_baseline(normalized_symbol, trend_range, points)

        if not points:
            return None

        return {
            "symbol": normalized_symbol,
            "range": trend_range,
            "timezone": "America/New_York",
            "points": points,
        }

    @staticmethod
    def _utc_timestamp(value: datetime) -> int:
        if value.tzinfo is None:
            return int(value.replace(tzinfo=timezone.utc).timestamp())
        return int(value.astimezone(timezone.utc).timestamp())

    @staticmethod
    async def _with_quote_baseline(
        symbol: str,
        trend_range: TrendRange,
        points: list[dict],
    ) -> list[dict]:
        quote = stock_cache.get_quote(symbol) or await finnhub.get_quote(symbol)
        if not quote:
            return points

        price = float(quote.get("price") or 0)
        change = float(quote.get("change") or 0)
        if price <= 0:
            return points

        quote_timestamp = int(quote.get("timestamp") or 0)
        if quote_timestamp > 0:
            points_by_timestamp = {point["timestamp"]: point["price"] for point in points}
            points_by_timestamp[quote_timestamp] = price
            points = [
                {"timestamp": timestamp, "price": point_price}
                for timestamp, point_price in sorted(points_by_timestamp.items())
            ]

        if trend_range != "1d" or abs(change) < 0.005:
            return points

        previous_close = price - change
        if previous_close <= 0:
            return points

        latest_timestamp = points[-1]["timestamp"] if points else int(datetime.now(timezone.utc).timestamp())
        has_movement = any(abs(point["price"] - previous_close) >= 0.005 for point in points)
        baseline_timestamp = latest_timestamp - 24 * 60 * 60
        baseline = {"timestamp": baseline_timestamp, "price": previous_close}
        if not points:
            return [baseline, {"timestamp": latest_timestamp, "price": price}]
        if has_movement and points[0]["timestamp"] <= baseline_timestamp:
            return points
        return [baseline, *points]


stock_trends = StockTrendService()
