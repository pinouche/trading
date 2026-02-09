"""utilities concerning placing API orders."""

import time

import numpy as np

from trading.api.ibapi_class import IBapi


def wait_until_order_is_filled(app: IBapi, order_id: int | None = None, waiting_time: int = np.inf) -> bool:
    """wait until the order has been executed/received on TWS and make sure all the orders have been filled."""
    if order_id is None:
        # Fallback to current nextorderId - 1 if not provided, but it's better to pass it explicitly
        try:
            with app._lock:
                order_id = app.nextorderId - 1 if app.nextorderId is not None else None
        except AttributeError:
            order_id = app.nextorderId - 1 if hasattr(app, 'nextorderId') and app.nextorderId is not None else None

    if order_id is None:
        return False

    start_time = time.time()
    while order_id not in app.order_status:
        time.sleep(0.1)
        time_lapsed = time.time() - start_time
        if time_lapsed > waiting_time:
            return False

        # here we wait for all the options to have been sold before buying stocks
    while True:
        remaining = app.order_status[order_id]["remaining"]
        if remaining == 0:
            return True

        time.sleep(0.1)
        time_lapsed = time.time() - start_time
        if time_lapsed > waiting_time:
            return False
