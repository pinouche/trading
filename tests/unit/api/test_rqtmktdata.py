import time

import numpy as np
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.ibapi_class import IBapi
from trading.utils import get_next_friday


def test_request_data_options_contract(app: IBapi) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    option_contract = get_options_contract(ticker=ticker_symbol, contract_strike=110.0, expiry_date=date)
    app.reqMktData(app.nextorderId, option_contract, '', True, False, [])
    time.sleep(2)
    assert isinstance(app.stock_current_price_dict[app.nextorderId].price, list)
    assert len(app.stock_current_price_dict[app.nextorderId].price) == 2
    assert np.sum([isinstance(price, float) for price in app.stock_current_price_dict[app.nextorderId].price]) == 2
    app.reqIds(-1)
    app.disconnect()
