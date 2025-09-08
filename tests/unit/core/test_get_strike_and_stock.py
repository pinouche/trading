import pytest

from trading.core.strategy.get_strike_and_stock import get_strike_for_highest_iv

# We monkeypatch process_stock_ticker_iv so we don't need IB
def fake_process_stock_ticker_iv_factory(results):
    """Factory that returns a fake function cycling through preset results."""
    def fake_process_stock_ticker_iv(ticker, app, expiry_date):
        return results[ticker]
    return fake_process_stock_ticker_iv


@pytest.mark.parametrize(
    "stock_list, fake_results, expected",
    [
        (
            ["AAPL", "MSFT", "GOOG"],
            {
                "AAPL": (0.25, 150.0, 155.0),
                "MSFT": (0.40, 300.0, 310.0),
                "GOOG": (0.35, 2800.0, 2850.0),
            },
            ("MSFT", 0.40, 300.0, 310.0),
        ),
        (
            ["TSLA", "NFLX"],
            {
                "TSLA": (0.55, 700.0, 710.0),
                "NFLX": (0.55, 500.0, 510.0),  # tie → should return first seen (TSLA)
            },
            ("TSLA", 0.55, 700.0, 710.0),
        ),
        (
            ["AMZN"],
            {
                "AMZN": (0.20, 3300.0, 3350.0),
            },
            ("AMZN", 0.20, 3300.0, 3350.0),
        ),
    ],
)
def test_get_strike_for_highest_iv(monkeypatch, stock_list, fake_results, expected):
    # Monkeypatch process_stock_ticker_iv
    monkeypatch.setattr(
        "trading.core.strategy.get_strike_and_stock.process_stock_ticker_iv",
        fake_process_stock_ticker_iv_factory(fake_results),
    )

    result = get_strike_for_highest_iv(app=None, stock_list=stock_list, expiry_date=None)
    assert result == expected
