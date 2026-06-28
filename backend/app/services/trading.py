import uuid

from sqlalchemy.orm import Session

from app.models.schemas import OrderCreate
from app.models.user import Account, AccountValue, Order, OrderStatus, OrderType, Position, User
from app.services.account_valuation import calculate_account_value

COMMISSION_FIXED = 5.0
COMMISSION_RATE = 0.001


class TradingError(Exception):
    pass


class AccountNotFoundError(TradingError):
    pass


class InsufficientBalanceError(TradingError):
    pass


class InsufficientPositionError(TradingError):
    pass


def calculate_commission(amount: float) -> float:
    return COMMISSION_FIXED + (amount * COMMISSION_RATE)


class TradingService:
    def create_order(self, order_data: OrderCreate, current_user: User, db: Session) -> Order:
        account = self._get_owned_account(order_data.account_id, current_user.id, db)
        commission = calculate_commission(order_data.shares * order_data.price)

        if order_data.type == OrderType.BUY:
            self._buy(account, order_data, commission, db)
        else:
            self._sell(account, order_data, commission, db)

        order = Order(
            id=str(uuid.uuid4()),
            account_id=order_data.account_id,
            symbol=order_data.symbol.upper(),
            type=order_data.type,
            shares=order_data.shares,
            price=order_data.price,
            commission=commission,
            status=OrderStatus.COMPLETED,
        )
        db.add(order)
        self._record_account_value(account, order_data.account_id, db)

        db.commit()
        db.refresh(order)
        return order

    def _get_owned_account(self, account_id: str, user_id: str, db: Session) -> Account:
        account = db.query(Account).filter(
            Account.id == account_id,
            Account.user_id == user_id,
        ).first()

        if not account:
            raise AccountNotFoundError()

        return account

    def _buy(self, account: Account, order_data: OrderCreate, commission: float, db: Session) -> None:
        total_amount = order_data.shares * order_data.price + commission
        if account.current_balance < total_amount:
            raise InsufficientBalanceError()

        account.current_balance -= total_amount

        position = db.query(Position).filter(
            Position.account_id == order_data.account_id,
            Position.symbol == order_data.symbol.upper(),
        ).first()

        if position:
            total_shares = position.shares + order_data.shares
            total_cost = (position.avg_cost * position.shares) + (order_data.price * order_data.shares)
            position.avg_cost = total_cost / total_shares
            position.shares = total_shares
            return

        position = Position(
            id=str(uuid.uuid4()),
            account_id=order_data.account_id,
            symbol=order_data.symbol.upper(),
            shares=order_data.shares,
            avg_cost=order_data.price,
        )
        db.add(position)

    def _sell(self, account: Account, order_data: OrderCreate, commission: float, db: Session) -> None:
        position = db.query(Position).filter(
            Position.account_id == order_data.account_id,
            Position.symbol == order_data.symbol.upper(),
        ).first()

        if not position or position.shares < order_data.shares:
            raise InsufficientPositionError()

        position.shares -= order_data.shares
        if position.shares == 0:
            db.delete(position)

        account.current_balance += order_data.shares * order_data.price - commission

    def _record_account_value(self, account: Account, account_id: str, db: Session) -> None:
        values = calculate_account_value(account, db)
        account_value = AccountValue(
            id=str(uuid.uuid4()),
            account_id=account_id,
            **values,
        )
        db.add(account_value)


trading_service = TradingService()
