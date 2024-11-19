"""Module to define stock order."""

from ibapi.order import Order


def create_parent_order(order_id: int, action: str, price: float, quantity: int, allornone: bool = True) -> Order:
    """Implements stock order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    order = Order()
    order.orderId = order_id
    order.action = action
    order.tif = "DAY"
    order.totalQuantity = quantity
    order.orderType = 'LMT'
    order.lmtPrice = price
    order.allOrNone = allornone
    order.algoStrategy = "Adaptive"
    order.eTradeOnly = False
    order.firmQuoteOnly = False

    return order
