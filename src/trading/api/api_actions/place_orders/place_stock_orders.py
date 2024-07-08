"""Place (submit) various order types to the TWS API"""

from ibapi.contract import Contract
from ibapi.order_condition import PriceCondition

from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.ibapi_class import IBapi
from trading.api.orders.conditions import create_price_condition
from trading.api.orders.stock_orders import create_child_order, create_parent_order
from trading.utils import config_load

config_vars = config_load("./config.yaml")


def place_simple_order(app: IBapi, contract: Contract, action: str, price: float, quantity: int,
                       price_condition: PriceCondition = None) -> None:
    """Place a limit order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    if action == "BUY":
        price += config_vars["buffer_allowed_pennies"]
    elif action == "SELL":
        price -= config_vars["buffer_allowed_pennies"]
    else:
        raise ValueError(f"Valid actions are [BUY, SELL], got {action}.")

    order = create_parent_order(app.nextorderId,  # type: ignore
                                action,
                                round(price, 2),
                                quantity)

    if price_condition is not None:
        order.conditions.append(price_condition)

    order.transmit = True
    app.placeOrder(app.nextorderId, contract, order)
    app.nextorderId += 1  # type: ignore


def place_profit_taker_order(app: IBapi, contract: Contract, price: float, quantity: int) -> None:
    """Place a limit order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    buy_price = round(price + config_vars["buffer_allowed_pennies"], 2)
    parent_order = create_parent_order(app.nextorderId,  # type: ignore
                                       "BUY",
                                       buy_price,
                                       quantity,
                                       False)
    parent_order.transmit = False
    # remove a cent as a buffer for order to trigger
    price_profit_taker = round(
        price * (1 + config_vars["percentage_profit_taking"] / 100) - config_vars["buffer_allowed_pennies"], 2)
    profit_taker_child_order = create_child_order(app.nextorderId,  # type: ignore
                                                  app.nextorderId + 1,  # type: ignore
                                                  "SELL",
                                                  price_profit_taker,
                                                  quantity,
                                                  False)
    profit_taker_child_order.transmit = True

    assert buy_price < price_profit_taker, f"Selling price {price_profit_taker} is below purchase price {buy_price}."

    app.placeOrder(parent_order.orderId, contract, parent_order)
    app.placeOrder(profit_taker_child_order.orderId, contract, profit_taker_child_order)
    app.nextorderId += 1  # type: ignore


def place_conditional_parent_child_orders(app: IBapi, contract: Contract, price: float) -> None:
    """Place a parent conditional buy order based on price and an attached conditional child order, also based on price.
    This is part of implementing the itm dynamic hedging strategy.
    """
    # create a sell order for stocks if price condition is met (price reaches the strike price)

    get_contract_details(app, contract)  # request contract details
    parent_price_condition = create_price_condition(contract, False, price)
    parent_order = create_parent_order(app.nextorderId,  # type: ignore
                                       "SELL",
                                       round(price - config_vars["buffer_allowed_pennies"], 2),
                                       config_vars["number_of_options"] * 100,
                                       False)
    parent_order.conditions.append(parent_price_condition)
    parent_order.transmit = True

    # create a buy order for stocks if price condition is met (price reaches the strike price)
    # child_price_condition = create_price_condition(contract, True, price)
    # child_order = create_child_order(app.nextorderId,  # type: ignore
    #                                  app.nextorderId + 1,  # type: ignore
    #                                  "BUY",
    #                                  round(price + config_vars["buffer_allowed_pennies"], 2),
    #                                  config_vars["number_of_options"] * 100,
    #                                  False)
    # child_order.conditions.append(child_price_condition)
    # child_order.transmit = True

    app.placeOrder(app.nextorderId, contract, parent_order)
    # app.placeOrder(child_order.orderId, contract, child_order)
    app.nextorderId += 1  # type: ignore
