
from trading.api.ibapi_class import IBapi
from trading.core.api_actions.request_mkt_data import request_market_data
from trading.utils import config_load

config_vars = config_load("./config.yaml")


def app_connection(appl: IBapi) -> None:
    assert isinstance(appl.nextorderId, int)
    assert appl.isConnected() is True
    assert appl.connState == 2


def data_is_live(appl: IBapi) -> None:
    id_order = appl.nextorderId
    request_market_data(appl, "TSLA", id_order)
    assert appl.stock_current_price_dict[id_order].market_is_live is True
    assert isinstance(appl.stock_current_price_dict[id_order].price, list)
    assert len(appl.stock_current_price_dict[id_order].price) == 2


def test_full_app(app: IBapi) -> None:

    app_connection(app)
    data_is_live(app)
    app.disconnect()
