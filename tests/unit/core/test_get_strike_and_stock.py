"""Test function to find the closest value that is below current price."""

import pytest
from trading.core.strategy.get_strike_and_stock import compute_closest_percentage


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
    assert compute_closest_percentage(strike_prices, stock_price) == expected
