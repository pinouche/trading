"""utilities concerning placing API orders."""

import time

from trading.api.ibapi_class import IBapi


def wait_until_order_is_filled(app: IBapi) -> None:
    """wait until the order has been executed/received on TWS and make sure all the orders have been filled."""
    while app.nextorderId-1 not in app.order_status:  # type: ignore
        time.sleep(0.1)

        # here we wait for all the options to have been sold before buying stocks
    while True:
        remaining = app.order_status[app.nextorderId-1]["remaining"]  # type: ignore
        if remaining == 0:
            break
        time.sleep(0.1)
