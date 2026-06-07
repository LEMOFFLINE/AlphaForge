from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.alpha_vantage import alpha_vantage
from app.services.popular_stocks import POPULAR_STOCKS
from app.services.stock_cache import stock_cache
from app.models.schemas import QuoteResponse

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str):
    # 先从缓存获取
    cached = stock_cache.get_quote(symbol)
    if cached:
        return QuoteResponse(
            symbol=cached["symbol"],
            price=cached["price"],
            change=cached["change"],
            change_percent=cached["change_percent"],
            volume=cached.get("volume", 0),
        )

    # 缓存没有则从API获取
    quote = await alpha_vantage.get_quote(symbol)

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
async def search_symbols(q: str):
    results = await alpha_vantage.search_symbol(q)
    return results


@router.get("/daily/{symbol}")
async def get_daily_data(symbol: str):
    data = await alpha_vantage.get_daily_data(symbol)
    return data


@router.get("/popular")
async def get_popular_stocks():
    """获取热门美股列表"""
    return POPULAR_STOCKS


@router.get("/popular/quotes")
async def get_popular_quotes(background_tasks: BackgroundTasks):
    """获取热门股票实时报价（使用缓存）"""
    # 如果缓存过期，在后台更新
    if stock_cache.is_expired():
        background_tasks.add_task(stock_cache.update_cache)

    return stock_cache.get_cached_quotes()
