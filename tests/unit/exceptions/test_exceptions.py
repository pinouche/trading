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
                                          price: list | int | None,
                                          market_is_live: bool,
                                          reqid: int,
                                          expected_error: PriceNotLiveError | PriceNotFloatError | None) -> None:

    app.current_asset_price_dict[reqid] = StockInfo()
    app.current_asset_price_dict[reqid].price.append(price)  # type: ignore
    app.current_asset_price_dict[reqid].market_is_live = market_is_live

    if expected_error is None:
        check_price_is_live_and_is_float(app, reqid)
    elif isinstance(expected_error, PriceNotLiveError):
        with pytest.raises(PriceNotLiveError):
            check_price_is_live_and_is_float(app, reqid)
    elif isinstance(expected_error, PriceNotFloatError):
        with pytest.raises(PriceNotFloatError):
            check_price_is_live_and_is_float(app, reqid)

    app.disconnect()
