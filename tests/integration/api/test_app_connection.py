"""Test if app is connected and data is live."""

import time

from trading.api.ibapi_class import IBapi
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.core.exceptions.checks import check_price_is_live_and_is_float


def request_market_data_price_stock(app: IBapi, ticker_symbol: str) -> None:
    """Request live point (i.e. not streaming: snapshot=True) market data for stocks."""
    contract = get_stock_contract(ticker_symbol)
    # Snapshot is set to True, which means we only request a single data point (and not a stream of data).
    req_id = app.get_next_req_id()
    app.reqMktData(req_id, contract, '', True, False, [])
    while req_id not in app.current_asset_price_dict:
        time.sleep(1)
    check_price_is_live_and_is_float(app, req_id)  # type: ignore


def app_connection(appl: IBapi) -> None:
    with appl._lock:
        next_id = appl.nextorderId
    assert isinstance(next_id, int)
    assert appl.isConnected() is True
    assert appl.connState == 2


def data_is_live(appl: IBapi) -> None:
    contract = get_stock_contract("TSLA")
    req_id = appl.get_next_req_id()
    appl.reqMktData(req_id, contract, '', True, False, [])
    while req_id not in appl.current_asset_price_dict:
        time.sleep(1)
    assert appl.current_asset_price_dict[req_id].market_is_live is True  # type: ignore
    assert isinstance(appl.current_asset_price_dict[req_id].price, list)  # type: ignore
    assert len(appl.current_asset_price_dict[req_id].price[-1]) == 2  # type: ignore


def test_full_app(app: IBapi) -> None:

    app_connection(app)
    data_is_live(app)
    app.disconnect()
