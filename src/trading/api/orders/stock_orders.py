"""Module to define stock order."""

from ibapi.order import Order


def create_parent_order(order_id: int, action: str, price: float, quantity: int) -> Order:
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
    order.allOrNone = True
    order.outsideRth = True

    return order


def create_profit_taker_child_order(parent_order_id: int, child_order_id: int, price: float, quantity: int) -> Order:
    """Implements stock order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    order = Order()
    order.orderId = child_order_id
    order.parentId = parent_order_id
    order.action = "SELL"
    order.tif = "DAY"
    order.totalQuantity = quantity
    order.orderType = 'LMT'
    order.lmtPrice = price
    order.allOrNone = True
    order.outsideRth = True

    return order
