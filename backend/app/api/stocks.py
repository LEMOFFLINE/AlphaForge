from fastapi import APIRouter, HTTPException, Path, Query

from app.models.schemas import QuoteResponse, StockTrendResponse
from app.services.finnhub import finnhub
from app.services.popular_stocks import POPULAR_STOCKS
from app.services.stock_cache import stock_cache
from app.services.stock_trends import stock_trends

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str = Path(min_length=1, max_length=16, pattern=r"^[A-Za-z0-9.^-]+$")):
    cached = stock_cache.get_quote(symbol)
    if cached:
        return QuoteResponse(
            symbol=cached["symbol"],
            price=cached["price"],
            change=cached["change"],
            change_percent=cached["change_percent"],
            volume=cached.get("volume", 0),
        )

    quote = await finnhub.get_quote(symbol)

    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")

    return QuoteResponse(
        symbol=quote["symbol"],
        price=quote["price"],
        change=quote["change"],
        change_percent=quote["change_percent"],
        volume=quote["volume"],
    )


@router.get("/search")
async def search_symbols(q: str = Query(min_length=1, max_length=64)):
    results = await finnhub.search_symbol(q)
    return results


@router.get("/daily/{symbol}")
async def get_daily_data(symbol: str = Path(min_length=1, max_length=16, pattern=r"^[A-Za-z0-9.^-]+$")):
    data = await finnhub.get_daily_data(symbol)
    return data


@router.get("/trend/{symbol}", response_model=StockTrendResponse)
async def get_stock_trend(
    symbol: str = Path(min_length=1, max_length=16, pattern=r"^[A-Za-z0-9.^-]+$"),
    range: str = Query(default="1d", pattern=r"^(1d|7d)$"),
):
    trend = await stock_trends.get_trend(symbol, range)  # type: ignore[arg-type]
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.get("/popular")
async def get_popular_stocks():
    return POPULAR_STOCKS


@router.get("/popular/quotes")
async def get_popular_quotes():
    return stock_cache.get_cached_quotes()
