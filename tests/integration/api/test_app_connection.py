
from trading.api.api_actions.request_data.request_mkt_data import request_market_data_price_stock
from trading.api.ibapi_class import IBapi


def app_connection(appl: IBapi) -> None:
    assert isinstance(appl.nextorderId, int)
    assert appl.isConnected() is True
    assert appl.connState == 2


def data_is_live(appl: IBapi) -> None:
    request_market_data_price_stock(appl, "TSLA")
    assert appl.current_asset_price_dict[appl.nextorderId].market_is_live is True
    assert isinstance(appl.current_asset_price_dict[appl.nextorderId].price, list)
    assert len(appl.current_asset_price_dict[appl.nextorderId].price) == 2


def test_full_app(app: IBapi) -> None:

    app_connection(app)
    data_is_live(app)
    app.disconnect()
