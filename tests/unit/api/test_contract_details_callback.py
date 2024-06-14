import time

from trading.api.contracts.option_contracts import get_options_contract
from trading.api.ibapi_class import IBapi
from trading.utils import get_next_friday


def test_options_contract(app: IBapi) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    option_contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    app.reqContractDetails(app.nextorderId, option_contract)
    time.sleep(5)
    assert ticker_symbol in app.options_strike_price_dict
    assert isinstance(app.options_strike_price_dict[ticker_symbol], list)
    assert isinstance(app.options_strike_price_dict[ticker_symbol][0], float)
    app.disconnect()
