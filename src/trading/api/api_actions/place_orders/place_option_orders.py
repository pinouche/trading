"""Script to place option order (buy or sell)"""

from ibapi.contract import Contract
from ibapi.order import Order

from trading.api.ibapi_class import IBapi


def place_option_order(app: IBapi, contract: Contract, order: Order, order_id: int | None = None) -> int:
    """Place order to buy or sell an option (depending on the contract)."""
    if order_id is None:
        order_id = app.get_next_req_id()
    app.placeOrder(order_id, contract, order)
    return order_id
