"""implement request live market data method"""

import time
from typing import Any

from ibapi.contract import Contract

from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.core.exceptions.checks import check_price_is_live_and_is_float


def request_market_data_price_stock(app: IBapi, ticker_symbol: str) -> None:
    """Request live point (i.e. not streaming: snapshot=True) market data for stocks."""
    contract = get_stock_contract(ticker_symbol)
    # Snapshot is set to True, which means we only request a single data point (and not a stream of data).
    app.reqMktData(app.nextorderId, contract, '', True, False, [])
    time.sleep(2)
    check_price_is_live_and_is_float(app, app.nextorderId)  # type: ignore


def request_market_data_price(app: IBapi, contract: Contract) -> list[float] | Any:
    """Request live point (i.e. not streaming: snapshot=True) market data for options or stocks."""
    app.reqMktData(app.nextorderId, contract, '', True, False, [])

    # this is the same data structure if it's a stock or option contract request
    while True:
        if app.nextorderId in app.current_asset_price_dict:
            break
        time.sleep(0.1)

    while True:
        if app.current_asset_price_dict[app.nextorderId]:
            break
        time.sleep(0.1)

    while True:
        if app.current_asset_price_dict[app.nextorderId].price:
            break
        time.sleep(0.1)

    while True:
        if len(app.current_asset_price_dict[app.nextorderId].price[-1]) == 2:
            break
        time.sleep(0.1)

    return app.current_asset_price_dict[app.nextorderId].price[-1]


def request_market_data_option_iv(app: IBapi, contract: Contract) -> list[float] | Any:
    """Request live option iv (i.e. not streaming: snapshot=True)."""
    if contract.secType != "OPT":
        raise ValueError(f"the contract secType must be OPT, got {contract.secType}")

    app.reqMktData(app.nextorderId, contract, '', True, False, [])

    while app.nextorderId not in app.current_option_iv_dict:
        time.sleep(0.1)

    while True:
        if isinstance(app.current_option_iv_dict[app.nextorderId], float):
            break
        time.sleep(0.1)

    return app.current_option_iv_dict[app.nextorderId]
