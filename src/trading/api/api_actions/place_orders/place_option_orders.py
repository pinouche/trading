"""Script to place option order (buy or sell)"""

import time

from ibapi.contract import Contract
from ibapi.order import Order

from trading.api.ibapi_class import IBapi


def place_option_order(app: IBapi, contract: Contract, order: Order) -> None:
    """Place order to buy or sell an option (depending on the contract)."""
    app.placeOrder(app.nextorderId, contract, order)
    app.nextorderId += 1  # type: ignore


def wait_until_order_is_filled(app: IBapi) -> None:
    """wait until the order has been executed/received on TWS and make sure all the orders have been filled."""
    while app.nextorderId not in app.execution_details:
        time.sleep(0.2)

    while app.nextorderId not in app.order_status:
        time.sleep(0.2)

        # here we wait for all the options to have been sold before buying stocks
    while True:
        remaining = app.order_status[app.nextorderId]["remaining"]
        if remaining == 0:
            break
