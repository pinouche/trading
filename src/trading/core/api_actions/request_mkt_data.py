"""implement request live market data method"""

import time

from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.core.exceptions.checks import check_price_is_live_and_is_float


def request_market_data(app: IBapi, ticker_symbol: str) -> None:
    """Request live streaming market data."""
    contract = get_stock_contract(ticker_symbol)
    # Snapshot is set to True, which means we only request a single data point (and not a stream of data).
    app.reqMktData(app.nextorderId, contract, '', True, False, [])
    time.sleep(2)
    check_price_is_live_and_is_float(app, app.nextorderId)
    app.reqIds(-1)  # increment the next valid id (appl.nextorderId)
