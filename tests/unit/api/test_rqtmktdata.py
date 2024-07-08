
import numpy as np
from trading.api.api_actions.request_data.request_mkt_data import request_market_data
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.ibapi_class import IBapi
from trading.utils import get_next_friday


def test_request_data_options_contract(app: IBapi, options_strikes: list[float]) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    first_strike_price = options_strikes[0]
    app.nextorderId += 1  # type: ignore

    # define option contract and place order
    option_contract = get_options_contract(ticker=ticker_symbol, contract_strike=first_strike_price, expiry_date=date)
    price_list = request_market_data(app, option_contract)

    assert isinstance(price_list, list)
    assert len(price_list) == 2
    assert np.sum([isinstance(price, float) for price in price_list]) == 2

    app.nextorderId += 1  # type: ignore
    app.disconnect()
