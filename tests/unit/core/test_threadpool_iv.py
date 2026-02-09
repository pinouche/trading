import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from trading.core.strategy.get_strike_and_stock import get_strike_for_highest_iv

def test_get_strike_for_highest_iv_threadpool():
    """
    Test that get_strike_for_highest_iv correctly uses ThreadPoolExecutor
    to process multiple tickers and returns the one with the highest IV.
    """
    # Mock IBapi instance
    mock_app = MagicMock()
    
    # Define tickers and their expected return values from process_stock_ticker_iv
    stock_list = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    
    # Mapping of ticker to (iv, strikes)
    mock_data = {
        "AAPL": (20.0, np.array([140.0, 150.0, 160.0])),
        "GOOGL": (25.0, np.array([2700.0, 2800.0, 2900.0])),
        "MSFT": (15.0, np.array([290.0, 300.0, 310.0])),
        "TSLA": (40.0, np.array([600.0, 700.0, 800.0])),
    }
    
    def side_effect(ticker, app, expiry_date=None):
        return mock_data[ticker]
    
    # Patch process_stock_ticker_iv which is called inside get_strike_for_highest_iv
    with patch("trading.core.strategy.get_strike_and_stock.process_stock_ticker_iv", side_effect=side_effect) as mock_process:
        ticker, iv, strikes = get_strike_for_highest_iv(mock_app, stock_list)
        
        # Verify the result is the one with highest IV (TSLA, 40.0)
        assert ticker == "TSLA"
        assert iv == 40.0
        assert np.array_equal(strikes, mock_data["TSLA"][1])
        
        # Verify that mock_process was called for each ticker in the list
        assert mock_process.call_count == len(stock_list)
        called_tickers = [call.args[0] for call in mock_process.call_args_list]
        assert set(called_tickers) == set(stock_list)

def test_get_strike_for_highest_iv_empty_list():
    """Test with an empty stock list."""
    mock_app = MagicMock()
    ticker, iv, strikes = get_strike_for_highest_iv(mock_app, [])
    
    assert ticker is None
    assert iv == float("-inf")
    assert strikes is None
