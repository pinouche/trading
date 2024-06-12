"""implement request live market data method"""

import time

from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.core.exceptions.checks import check_price_is_live_and_is_float


def request_market_data(app: IBapi, ticker_symbol: str, nextorderid: int | None = None) -> None:
    """Request live streaming market data."""
    if nextorderid is None:
        nextorderid = app.nextorderId

    contract = get_stock_contract(ticker_symbol)
    # Snapshot is set to True, which means we only request a single data point (and not a stream of data).
    app.reqMktData(nextorderid, contract, '', True, False, [])
    time.sleep(2)
    check_price_is_live_and_is_float(app, nextorderid)
    app.reqIds(-1)  # increment the next valid id (appl.nextorderId)
