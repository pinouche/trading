"""Script to place option order (buy or sell)"""

from ibapi.contract import Contract
from ibapi.order import Order

from trading.api.ibapi_class import IBapi


def place_option_order(app: IBapi, contract: Contract, order: Order) -> None:
    """Place order to buy or sell an option (depending on the contract)."""
    app.placeOrder(app.nextorderId, contract, order)
    app.nextorderId += 1  # type: ignore
