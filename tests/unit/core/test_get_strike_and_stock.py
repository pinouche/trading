"""Test function to find the closest value that is below current price."""

import pytest
from trading.core.strategy.get_strike_and_stock import compute_score


@pytest.mark.parametrize(
    ("input_data", "alpha_weight", "expected_key", "expected_value"),
    [
        (
            {'AAPL': (0.3, 5.0, 10.0), 'GOOGL': (0.4, 10.0, 15.0), 'AMZN': (0.5, 2.0, 20.0)},
            0.6,
            'GOOGL',
            15.0
        ),
        (
            {'MSFT': (0.1, 7.0, 5.0), 'TSLA': (0.2, 4.0, 12.0), 'NFLX': (0.15, 3.0, 7.0)},
            0.7,
            'MSFT',
            5.0
        ),
        (
            {'FB': (0.35, 6.0, 9.0), 'NVDA': (0.25, 8.0, 14.0), 'AMD': (0.4, 5.0, 13.0)},
            0.5,
            'NVDA',
            14.0
        ),
    ]
)
def test_compute_score(input_data: dict[str, tuple[float, float, float]],
                       alpha_weight: float,
                       expected_key: str,
                       expected_value: float) -> None:

    result_key, result_value = compute_score(input_data, alpha_weight)

    assert result_key == expected_key, f"Test failed: expected key {expected_key}, got {result_key}"
    assert result_value == expected_value, f"Test failed: expected value {expected_value}, got {result_value}"
