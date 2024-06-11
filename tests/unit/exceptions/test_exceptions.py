import pytest
from trading.api.ibapi_class import IBapi
from trading.core.exceptions.checks import check_price_is_live_and_is_float
from trading.core.exceptions.exceptions import PriceNotFloatError, PriceNotLiveError


@pytest.mark.parametrize(("price", "market_is_live", "reqid", "ticker_symbol", "expected_error"), [
    (-1, True, 1, "TSLA", PriceNotFloatError),  # raises
    (-1, False, 1, "TSLA", PriceNotLiveError),  # raises
    (None, None, 1, "TSLA", PriceNotLiveError),  # raises
    (None, True, 1, "TSLA", PriceNotFloatError),  # raises
    (10.0, None, 1, "TSLA", PriceNotLiveError),  # raises
    (100.0, True, 1, "TSLA", None)  # does not raise

])
def test_check_price_is_live_and_is_float(app: IBapi,
                                          price: float | None,
                                          market_is_live: bool | None,
                                          reqid: int,
                                          ticker_symbol: str,
                                          expected_error: PriceNotLiveError | PriceNotFloatError | None) -> None:

    app.dic_orderid_to_ticker[reqid] = ticker_symbol
    app.stock_price_dic[ticker_symbol].price = price
    app.stock_price_dic[ticker_symbol].market_is_live = market_is_live

    if expected_error is None:
        print(expected_error)
        check_price_is_live_and_is_float(app, reqid)
    elif isinstance(expected_error, PriceNotLiveError):
        print(expected_error)
        with pytest.raises(PriceNotLiveError):
            check_price_is_live_and_is_float(app, reqid)
    elif isinstance(expected_error, PriceNotFloatError):
        print(expected_error)
        with pytest.raises(PriceNotFloatError):
            check_price_is_live_and_is_float(app, reqid)

    app.disconnect()
