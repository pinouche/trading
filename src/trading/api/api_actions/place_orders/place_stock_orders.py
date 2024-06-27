"""Place (submit) various order types to the TWS API"""

from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.stock_orders import create_parent_order, create_profit_taker_child_order
from trading.utils import config_load

config_vars = config_load("./config.yaml")


def place_simple_order(app: IBapi, ticker_symbol: str, action: str, price: float, quantity: int) -> None:
    """Place a limit order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    contract = get_stock_contract(ticker_symbol)

    if action == "BUY":
        price += 0.01
    elif action == "SELL":
        price -= 0.01
    else:
        raise ValueError(f"Valid actions are [BUY, SELL], got {action}.")

    order = create_parent_order(app.nextorderId,  # type: ignore
                                action,
                                round(price, 2),
                                quantity)
    order.transmit = True
    app.placeOrder(app.nextorderId, contract, order)
    app.reqIds(-1)  # increment the next valid id (appl.nextorderId)


def place_profit_taker_order(app: IBapi, ticker_symbol: str, price: float, quantity: int) -> None:
    """Place a limit order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    contract = get_stock_contract(ticker_symbol)
    buy_price = round(price+0.01, 2)
    parent_order = create_parent_order(app.nextorderId,  # type: ignore
                                       "BUY",
                                       buy_price,
                                       quantity)
    parent_order.transmit = False
    # remove a cent as a buffer for order to trigger
    price_profit_taker = round(price*(1+config_vars["percentage_profit_taking"]/100)-0.01, 2)
    profit_taker_child_order = create_profit_taker_child_order(app.nextorderId,  # type: ignore
                                                               app.nextorderId+1,  # type: ignore
                                                               price_profit_taker, quantity)
    profit_taker_child_order.transmit = True

    assert buy_price < price_profit_taker, f"Selling price {price_profit_taker} is below purchase price {buy_price}."

    app.placeOrder(parent_order.orderId, contract, parent_order)
    app.placeOrder(profit_taker_child_order.orderId, contract, profit_taker_child_order)
    app.reqIds(-1)  # increment the next valid id (appl.nextorderId)
