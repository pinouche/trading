"""Create and request market scanner data."""

import time

from ibapi.scanner import ScannerSubscription
from ibapi.tag_value import TagValue

from trading.api.ibapi_class import IBapi


def request_scanner(app: IBapi, market_cap: str = "100000", iv_over_hv: str = "100", iv_percentile: str = "0.8") -> None:
    """Scanner request."""
    sub = ScannerSubscription()
    sub.instrument = "STK"
    sub.locationCode = "STK.US.MAJOR"
    sub.scanCode = "HIGH_OPT_IMP_VOLAT"

    scan_options: list = []
    filter_options = [
        TagValue("marketCapAbove1e6", market_cap),
        TagValue("impVolatOverHistAbove", iv_over_hv),
        TagValue("ivPercntl13wAbove", iv_percentile)
        ]

    app.reqScannerSubscription(app.nextorderId, sub, scan_options, filter_options)

    time.sleep(2.0)


def get_scanner_ticker_list(app: IBapi) -> list[str]:
    """Retrieve stock list that are returned in the scanner."""
    ticker_list = []
    if app.scanner_data:
        ticker_list = [val[0].contract.symbol for val in app.scanner_data.values()]

    return ticker_list
