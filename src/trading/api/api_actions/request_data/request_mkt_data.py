"""implement request live market data method"""

import time

from ibapi.contract import Contract

from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.core.exceptions.checks import check_price_is_live_and_is_float


def request_market_data_stock(app: IBapi, ticker_symbol: str) -> None:
    """Request live point (i.e. not streaming: snapshot=True) market data for stocks."""
    contract = get_stock_contract(ticker_symbol)
    # Snapshot is set to True, which means we only request a single data point (and not a stream of data).
    app.reqMktData(app.nextorderId, contract, '', True, False, [])
    time.sleep(2)
    check_price_is_live_and_is_float(app, app.nextorderId)


def request_market_data(app: IBapi, contract: Contract) -> None:
    """Request live point (i.e. not streaming: snapshot=True) market data for options or stocks."""
    app.reqMktData(app.nextorderId, contract, '', True, False, [])

    # this is the same data structure if it's a stock or option contract request
    while app.nextorderId not in app.stock_current_price_dict:
        time.sleep(0.1)

    while True:
        if app.stock_current_price_dict[app.nextorderId]:
            break
        time.sleep(0.1)

    while True:
        if app.stock_current_price_dict[app.nextorderId].price:
            break
        time.sleep(0.1)
