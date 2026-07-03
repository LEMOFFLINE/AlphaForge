from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.user import StockPriceHistory
from app.services.finnhub import finnhub
from app.services.stock_cache import stock_cache

TrendRange = Literal["1d", "7d"]


class StockTrendService:
    async def get_trend(self, symbol: str, trend_range: TrendRange) -> dict | None:
        normalized_symbol = symbol.upper()
        return await self._get_local_trend(normalized_symbol, trend_range)

    async def _get_local_trend(self, normalized_symbol: str, trend_range: TrendRange) -> dict | None:
        hours = 24 if trend_range == "1d" else 7 * 24
        end = self._hour_bucket(datetime.utcnow())
        start = end - timedelta(hours=hours)

        db = SessionLocal()
        try:
            rows = (
                db.query(StockPriceHistory)
                .filter(
                    StockPriceHistory.symbol == normalized_symbol,
                    StockPriceHistory.recorded_at >= start,
                    StockPriceHistory.recorded_at <= end,
                )
                .order_by(StockPriceHistory.recorded_at.asc())
                .all()
            )
        except SQLAlchemyError as e:
            print(f"Error loading stock price history for {normalized_symbol}: {e}")
            rows = []
        finally:
            db.close()

        points_by_timestamp = {}
        for row in rows:
            bucket = self._hour_bucket(row.recorded_at)
            points_by_timestamp[self._utc_timestamp(bucket)] = row.price

        points = [
            {"timestamp": timestamp, "price": price}
            for timestamp, price in sorted(points_by_timestamp.items())
        ]
        points = await self._with_quote_baseline(normalized_symbol, trend_range, points, start, end)

        if not points:
            return None

        return {
            "symbol": normalized_symbol,
            "range": trend_range,
            "timezone": "Asia/Shanghai",
            "points": points,
        }

    @staticmethod
    def _utc_timestamp(value: datetime) -> int:
        if value.tzinfo is None:
            return int(value.replace(tzinfo=timezone.utc).timestamp())
        return int(value.astimezone(timezone.utc).timestamp())

    @staticmethod
    def _hour_bucket(value: datetime) -> datetime:
        return value.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    async def _with_quote_baseline(
        symbol: str,
        trend_range: TrendRange,
        points: list[dict],
        start: datetime,
        end: datetime,
    ) -> list[dict]:
        quote = stock_cache.get_quote(symbol) or await finnhub.get_quote(symbol)
        if not quote:
            return points

        price = float(quote.get("price") or 0)
        change = float(quote.get("change") or 0)
        if price <= 0:
            return points

        points_by_timestamp = {point["timestamp"]: point["price"] for point in points}
        end_timestamp = StockTrendService._utc_timestamp(end)
        points_by_timestamp[end_timestamp] = price

        if trend_range != "1d" or abs(change) < 0.005:
            return [
                {"timestamp": timestamp, "price": point_price}
                for timestamp, point_price in sorted(points_by_timestamp.items())
            ]

        previous_close = price - change
        if previous_close <= 0:
            return [
                {"timestamp": timestamp, "price": point_price}
                for timestamp, point_price in sorted(points_by_timestamp.items())
            ]

        start_timestamp = StockTrendService._utc_timestamp(start)
        points_by_timestamp.setdefault(start_timestamp, previous_close)
        return [
            {"timestamp": timestamp, "price": point_price}
            for timestamp, point_price in sorted(points_by_timestamp.items())
        ]


stock_trends = StockTrendService()
