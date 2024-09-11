"""Test request scanner function"""

import datetime

import pytest
import pytz  # type: ignore
from trading.api.api_actions.market_scanner.request_market_scanner import request_scanner
from trading.api.ibapi_class import IBapi


@pytest.mark.parametrize(
    ("market_cap", "implied_vol", "expected_data_bool"),
    [
        ("100000", "1", True),  # 100 billion market cap
        ("10000000", None, False)  # 10 trillion
    ])
def test_request_scanner(app: IBapi, market_cap: str, implied_vol: str | None, expected_data_bool: bool) -> None:
    cet = pytz.timezone('CET')
    current_time_cet = datetime.datetime.now(cet)
    ten_pm_cet = cet.localize(datetime.datetime.combine(current_time_cet, datetime.time(22, 00)))

    if current_time_cet > ten_pm_cet:
        implied_vol = None

    request_scanner(app, market_cap=market_cap, implied_vol=implied_vol)

    dictionary_data = app.scanner_data
    if expected_data_bool:
        assert len(dictionary_data) > 0
    else:
        assert len(dictionary_data) == 0

    app.disconnect()
