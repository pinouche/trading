"""Test if app is connected and data is live."""

import time

from trading.api.ibapi_class import IBapi
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.core.exceptions.checks import check_price_is_live_and_is_float


def request_market_data_price_stock(app: IBapi, ticker_symbol: str) -> None:
    """Request live point (i.e. not streaming: snapshot=True) market data for stocks."""
    contract = get_stock_contract(ticker_symbol)
    # Snapshot is set to True, which means we only request a single data point (and not a stream of data).
    app.reqMktData(app.nextorderId, contract, '', True, False, [])
    while app.nextorderId not in app.current_asset_price_dict:
        time.sleep(1)
    check_price_is_live_and_is_float(app, app.nextorderId)  # type: ignore


def app_connection(appl: IBapi) -> None:
    assert isinstance(appl.nextorderId, int)
    assert appl.isConnected() is True
    assert appl.connState == 2


def data_is_live(appl: IBapi) -> None:
    request_market_data_price_stock(appl, "TSLA")
    print("THIS IS THE DICT", appl.current_asset_price_dict)
    assert appl.current_asset_price_dict[appl.nextorderId].market_is_live is True  # type: ignore
    assert isinstance(appl.current_asset_price_dict[appl.nextorderId].price, list)  # type: ignore
    assert len(appl.current_asset_price_dict[appl.nextorderId].price[-1]) == 2  # type: ignore


def test_full_app(app: IBapi) -> None:

    app_connection(app)
    data_is_live(app)
    app.disconnect()
