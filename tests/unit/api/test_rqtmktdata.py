
import numpy as np
from ibapi.contract import Contract
from trading.api.api_actions.request_data.request_mkt_data import request_market_data_option_iv, request_market_data_price
from trading.api.ibapi_class import IBapi


def test_request_data_price_options_contract(app: IBapi, option_contract: Contract) -> None:

    price_list = request_market_data_price(app, option_contract)

    assert isinstance(price_list, list)
    assert len(price_list) == 2
    assert np.sum([isinstance(price, float) for price in price_list]) == 2

    app.nextorderId += 1  # type: ignore
    app.disconnect()


def test_request_data_iv_options_contract(app: IBapi, option_contract: Contract) -> None:

    implied_volatility = request_market_data_option_iv(app, option_contract)

    assert isinstance(implied_volatility, float)

    app.nextorderId += 1  # type: ignore
    app.disconnect()
