from datetime import datetime, timedelta, timezone
from typing import Literal

from app.core.database import SessionLocal
from app.models.user import StockPriceHistory
from app.services.yahoo_chart import yahoo_chart

TrendRange = Literal["1d", "7d"]


class StockTrendService:
    async def get_trend(self, symbol: str, trend_range: TrendRange) -> dict | None:
        normalized_symbol = symbol.upper()
        market_trend = await yahoo_chart.get_trend(normalized_symbol, trend_range)
        if market_trend:
            return market_trend

        return self._get_local_trend(normalized_symbol, trend_range)

    def _get_local_trend(self, normalized_symbol: str, trend_range: TrendRange) -> dict | None:
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

        if not rows:
            return None

        return {
            "symbol": normalized_symbol,
            "range": trend_range,
            "timezone": "America/New_York",
            "points": [
                {
                    "timestamp": self._utc_timestamp(row.recorded_at),
                    "price": row.price,
                }
                for row in rows
            ],
        }

    @staticmethod
    def _utc_timestamp(value: datetime) -> int:
        if value.tzinfo is None:
            return int(value.replace(tzinfo=timezone.utc).timestamp())
        return int(value.astimezone(timezone.utc).timestamp())


stock_trends = StockTrendService()
