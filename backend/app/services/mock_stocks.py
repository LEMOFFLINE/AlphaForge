# 模拟股票数据（用于API限流时）
MOCK_STOCKS = {
    "AAPL": {"symbol": "AAPL", "price": 178.52, "change": 2.34, "change_percent": 1.33, "volume": 52000000},
    "MSFT": {"symbol": "MSFT", "price": 378.91, "change": -1.23, "change_percent": -0.32, "volume": 21000000},
    "GOOGL": {"symbol": "GOOGL", "price": 141.80, "change": 0.89, "change_percent": 0.63, "volume": 18000000},
    "AMZN": {"symbol": "AMZN", "price": 178.25, "change": 3.45, "change_percent": 1.97, "volume": 45000000},
    "TSLA": {"symbol": "TSLA", "price": 248.50, "change": -5.30, "change_percent": -2.09, "volume": 95000000},
    "NVDA": {"symbol": "NVDA", "price": 875.28, "change": 15.67, "change_percent": 1.82, "volume": 38000000},
    "META": {"symbol": "META", "price": 505.75, "change": 4.20, "change_percent": 0.84, "volume": 15000000},
    "BRK.B": {"symbol": "BRK.B", "price": 408.50, "change": -2.10, "change_percent": -0.51, "volume": 8000000},
}


def get_mock_quote(symbol: str) -> dict | None:
    """获取模拟股票报价"""
    return MOCK_STOCKS.get(symbol.upper())
