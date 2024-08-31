"""Test request scanner function"""

import pytest
from trading.api.api_actions.market_scanner.request_market_scanner import request_scanner
from trading.api.ibapi_class import IBapi


@pytest.mark.parametrize(
    ("market_cap", "iv_percentile", "expected_data_bool"),
    [
        ("100000", "0.5", True),
        ("100000", "1.0", False)
    ])
def test_request_scanner(app: IBapi, market_cap: str, iv_percentile: str, expected_data_bool: bool) -> None:
    request_scanner(app, market_cap=market_cap, iv_percentile=iv_percentile)

    dictionary_data = app.scanner_data
    if expected_data_bool:
        assert len(dictionary_data) > 0
    else:
        assert len(dictionary_data) == 0

    app.disconnect()
