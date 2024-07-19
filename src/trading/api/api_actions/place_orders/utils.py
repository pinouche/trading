"""utilities concerning placing API orders."""

import time

import numpy as np

from trading.api.ibapi_class import IBapi


def wait_until_order_is_filled(app: IBapi, waiting_time: int = np.inf) -> bool:
    """wait until the order has been executed/received on TWS and make sure all the orders have been filled."""
    start_time = time.time()

    while app.nextorderId-1 not in app.order_status:  # type: ignore
        time.sleep(0.1)
        time_lapsed = time.time() - start_time
        if time_lapsed > waiting_time:
            return False

        # here we wait for all the options to have been sold before buying stocks
    while True:
        remaining = app.order_status[app.nextorderId-1]["remaining"]  # type: ignore
        if remaining == 0:
            return True

        time.sleep(0.1)
        time_lapsed = time.time() - start_time
        if time_lapsed > waiting_time:
            return False
