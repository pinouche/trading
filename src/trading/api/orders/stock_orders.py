"""Module to define stock order."""

from ibapi.order import Order


def create_parent_order(order_id: int, action: str, price: float, quantity: int, all_or_none: bool = True,
                        order_type: str = "LMT", outside_hours: bool = True) -> Order:
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
    order.orderType = order_type
    order.lmtPrice = price
    order.allOrNone = all_or_none
    order.outsideRth = outside_hours
    order.eTradeOnly = False
    order.firmQuoteOnly = False

    return order


def create_child_order(parent_order_id: int, child_order_id: int,
                       action: str, price: float, quantity: int, all_or_none: bool = True,
                       order_type: str = "LMT",
                       outside_hours: bool = True) -> Order:
    """Implements stock order.
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    order = Order()
    order.orderId = child_order_id
    order.parentId = parent_order_id
    order.action = action
    order.tif = "DAY"
    order.totalQuantity = quantity
    order.orderType = order_type
    order.lmtPrice = price
    order.allOrNone = all_or_none
    order.outsideRth = outside_hours

    return order
