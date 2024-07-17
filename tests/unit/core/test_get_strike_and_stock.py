"""Test function to find the closest value that is below current price."""

import pytest
from trading.core.strategy.get_strike_and_stock import compute_closest_percentage, get_extrema_from_dic


@pytest.mark.parametrize(
    ("strike_prices", "stock_price", "expected"),
    [
        ([100, 110, 120], 115, 110),
        ([90, 95, 105], 100, 95),
        ([200, 210, 220], 205, 200),
        ([150, 160, 170], 140, None),
        ([50, 70, 80], 100, 80)
    ]
)
def test_compute_closest_percentage(strike_prices: list[float], stock_price: float, expected: float) -> None:
    assert compute_closest_percentage(strike_prices, stock_price)[0] == expected


@pytest.mark.parametrize(
    ("initial_dict", "expected_stock_ticker", "expected_closest_strike_price"),
    [
        (
                {'AAPL': (0.25, 150), 'GOOGL': (0.30, 2800), 'AMZN': (0.28, 3400), 'TSLA': (0.35, 700)},
                'TSLA', 700
        ),
        (
                {'AAPL': (0.25, 150), 'MSFT': (0.40, 300), 'GOOGL': (0.30, 2800), 'AMZN': (0.28, 3400)},
                'MSFT', 300
        ),
        (
                {'AAPL': (0.25, 150), 'GOOGL': (0.30, 2800), 'AMZN': (0.28, 3400), 'TSLA': (1.1, 700)},
                'TSLA', 700
        ),
    ]
)
def test_get_highest_iv(initial_dict: dict[str, tuple[float, float]],
                        expected_stock_ticker: str,
                        expected_closest_strike_price: float) -> None:

    stock_ticker, closest_strike_price = get_extrema_from_dic(initial_dict, True)

    assert stock_ticker == expected_stock_ticker
    assert closest_strike_price == expected_closest_strike_price
