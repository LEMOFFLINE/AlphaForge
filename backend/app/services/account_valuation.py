from sqlalchemy.orm import Session

from app.models.user import Account, Position
from app.services.stock_cache import stock_cache


def calculate_account_value(account: Account, db: Session) -> dict:
    positions = db.query(Position).filter(Position.account_id == account.id).all()

    positions_value = 0
    for position in positions:
        quote = stock_cache.get_quote(position.symbol)
        current_price = quote["price"] if quote else position.avg_cost
        positions_value += current_price * position.shares

    total_value = account.current_balance + positions_value

    return {
        "total_value": total_value,
        "cash_balance": account.current_balance,
        "positions_value": positions_value,
    }
