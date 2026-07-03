from datetime import datetime, timedelta
from typing import Literal

from app.core.database import SessionLocal
from app.models.user import StockPriceHistory

TrendRange = Literal["1d", "7d"]


class StockTrendService:
    def get_trend(self, symbol: str, trend_range: TrendRange) -> dict | None:
        normalized_symbol = symbol.upper()
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
            "points": [
                {
                    "timestamp": int(row.recorded_at.timestamp()),
                    "price": row.price,
                }
                for row in rows
            ],
        }


stock_trends = StockTrendService()
