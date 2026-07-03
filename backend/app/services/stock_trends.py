from datetime import datetime, timedelta, timezone
from typing import Literal

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.user import StockPriceHistory

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
            if row.recorded_at != bucket:
                continue
            points_by_timestamp[self._utc_timestamp(bucket)] = row.price

        points = [
            {"timestamp": timestamp, "price": price}
            for timestamp, price in sorted(points_by_timestamp.items())
        ]

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


stock_trends = StockTrendService()
