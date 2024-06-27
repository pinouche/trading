import pytest
from trading.api.ibapi_class import IBapi
from trading.core.data_models.data_models import StockInfo
from trading.core.exceptions.checks import check_price_is_live_and_is_float
from trading.core.exceptions.exceptions import PriceNotFloatError, PriceNotLiveError


@pytest.mark.parametrize(("price", "market_is_live", "reqid", "expected_error"), [
    (-1, True, 1, PriceNotFloatError),  # raises
    (-1, False, 1, PriceNotLiveError),  # raises
    (None, None, 1, PriceNotLiveError),  # raises
    (None, True, 1, PriceNotFloatError),  # raises
    ([10.0], None, 1, PriceNotLiveError),  # raises
    ([100.0, 101.0], True, 1, None)  # does not raise

])
def test_check_price_is_live_and_is_float(app: IBapi,
                                          price: float | None,
                                          market_is_live: bool | None,
                                          reqid: int,
                                          expected_error: PriceNotLiveError | PriceNotFloatError | None) -> None:

    app.stock_current_price_dict[reqid] = StockInfo()
    app.stock_current_price_dict[reqid].price = price
    app.stock_current_price_dict[reqid].market_is_live = market_is_live

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
