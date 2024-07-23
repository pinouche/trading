"""Implement checks and raise errors"""

import numpy as np

from trading.api.ibapi_class import IBapi
from trading.core.exceptions.exceptions import PriceNotFloatError, PriceNotLiveError


def check_price_is_live_and_is_float(app: IBapi, stock_request_id: int) -> None:
    """Perform some checks for a request on a given stock."""
    if not app.current_asset_price_dict[stock_request_id].market_is_live:
        raise PriceNotLiveError("Terminating process due to price not being live.")

    if not isinstance(app.current_asset_price_dict[stock_request_id].price[-1], list):
        raise PriceNotFloatError(f"Terminating process due to price not being of float type: "
                                 f"got type {type(app.current_asset_price_dict[stock_request_id].price)}")

    else:
        if np.sum(np.array(app.current_asset_price_dict[stock_request_id].price[-1]) < 0) != 0:  # type: ignore
            raise PriceNotFloatError(f"Terminating process due to price being negative: "
                                     f"got price {app.current_asset_price_dict[stock_request_id].price}")
