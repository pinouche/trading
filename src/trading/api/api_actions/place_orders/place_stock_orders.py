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
                       price_condition: PriceCondition = None,
                       order_type: str = "LMT",
                       outside_hours: bool = True) -> None:
    """Place a limit order.
    action: str (SELL OR BUY)
    price: float (price for the limit order)
    quantity: int (number of shares)
    """
    if action == "BUY":
        price += config_vars.buffer_allowed_pennies
    elif action == "SELL":
        price -= config_vars.buffer_allowed_pennies
    else:
        raise ValueError(f"Valid actions are [BUY, SELL], got {action}.")

    order = create_parent_order(app.nextorderId,  # type: ignore
                                action,
                                round(price, 2),
                                quantity,
                                True,
                                order_type,
                                outside_hours)

    if price_condition is not None:
        order.conditions.append(price_condition)

    order.transmit = True
    app.placeOrder(app.nextorderId, contract, order)


def place_conditional_parent_child_orders(app: IBapi,
                                          contract: Contract,
                                          strike_price: float,
                                          premium: float,
                                          number_of_options: int) -> None:
    """Place a parent conditional buy order based on price and an attached conditional child order, also based on price.
    This is part of implementing the itm dynamic hedging strategy.

    Args:
        - app: IBapi object class
        - contract: stock contract type
        - strike_price: strike price of the underlying option
        - purchase_price: stock price of the shares bought
        - premium: premium received on the call option sold
        - number_of_options: number of options we are trading
    """
    # create a sell order for stocks if price condition is met (price reaches the strike price)

    contract_details = get_contract_details(app, contract)[-1]  # request contract details: returns a list of contract object
    parent_price_condition = create_price_condition(contract_details, False, strike_price)
    parent_order = create_parent_order(app.nextorderId,  # type: ignore
                                       "SELL",
                                       round(strike_price - config_vars.buffer_allowed_pennies, 2),
                                       number_of_options * 100,
                                       False)
    parent_order.conditions.append(parent_price_condition)
    parent_order.transmit = False

    # create a buy order for stocks if price condition is met (price reaches the strike price)
    child_price_condition = create_price_condition(contract_details, True, strike_price + premium)
    child_order = create_child_order(app.nextorderId,  # type: ignore
                                     app.nextorderId + 1,  # type: ignore
                                     "BUY",
                                     round(strike_price + premium + config_vars.buffer_allowed_pennies, 2),
                                     number_of_options * 100,
                                     False)
    child_order.conditions.append(child_price_condition)
    child_order.transmit = True

    app.placeOrder(app.nextorderId, contract, parent_order)
    app.placeOrder(child_order.orderId, contract, child_order)
    app.nextorderId += 1  # type: ignore
