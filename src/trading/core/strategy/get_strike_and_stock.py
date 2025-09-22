"""Fetch the option strikes for several stocks and returns the stock and strike for which the strike is closest to current price"""

import numpy as np
from loguru import logger
from numpy import ndarray

from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.api_actions.request_mkt_data.request_mkt_data import request_market_data_option_iv, request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi


def get_options_strikes(app: IBapi, ticker_symbol: str, date: str | None = None) -> list[float]:
    option_contract = get_options_contract(ticker=ticker_symbol,
                                           expiry_date=date)
    option_chains = get_contract_details(app, option_contract)
    strike_prices = [details.contract.strike for details in option_chains]

    return sorted(strike_prices)


def get_current_stock_price(app: IBapi, ticker_symbol: str) -> np.float64:
    """Retrieve the current stock price for a given ticker."""
    stock_contract = get_stock_contract(ticker=ticker_symbol)
    stock_price_list = request_market_data_price(app, stock_contract)
    mid_price: np.float64 = np.round(np.mean(np.array(stock_price_list)[:2]), 2)

    return mid_price


def process_stock_ticker_iv(stock_ticker: str,
                            app: IBapi,
                            expiry_date: str | None = None) -> tuple[float, ndarray]:
    """Function to find the iv for a given stock option."""
    # get the available strike prices
    list_options_strike_price = get_options_strikes(app, stock_ticker, expiry_date)
    list_options_strike_price = np.array(list_options_strike_price)
    app.nextorderId += 1  # type: ignore

    # current stock price
    stock_price = get_current_stock_price(app, stock_ticker)

    # Find strikes below and above
    below_strikes = list_options_strike_price[list_options_strike_price < stock_price]
    above_strikes = list_options_strike_price[list_options_strike_price > stock_price]

    # get closest strikes to current price
    put_strike = below_strikes[-1]
    call_strike = above_strikes[0]

    assert put_strike < call_strike, "put strike price should be below the call strike price."

    # get the corresponding put option contract and request details (we are interested in iv)
    option_contract = get_options_contract(ticker=stock_ticker,
                                           contract_strike=float(put_strike),
                                           expiry_date=expiry_date)
    iv_put = request_market_data_option_iv(app, option_contract)

    # get the corresponding call option contract and request details (we are interested in iv)
    option_contract = get_options_contract(ticker=stock_ticker,
                                           contract_strike=float(call_strike),
                                           expiry_date=expiry_date)
    iv_call = request_market_data_option_iv(app, option_contract)
    iv = (iv_put+iv_call)*100/2

    logger.info(f"stock ticker: {stock_ticker}, "
                f"put strike price: {put_strike},"
                f"call strike price: {call_strike},"
                f"stock price: {stock_price}, "
                f"average option iv is: {iv}%")

    logger.info(f"current redId is {app.nextorderId}.")

    return iv, np.array(list_options_strike_price)  # type: ignore


def get_strike_for_highest_iv(app: IBapi,
                              stock_list: list,
                              expiry_date: str | None = None) -> tuple[str, float, ndarray]:
    """Return the stock and the associated strike price with the highest implied volatility."""

    max_ticker = None
    max_iv = float("-inf")
    max_strikes_list = None

    for ticker in stock_list:
        iv, list_strikes = process_stock_ticker_iv(ticker, app, expiry_date)
        if iv > max_iv:
            max_ticker = ticker
            max_iv = iv
            max_strikes_list = list_strikes

    return max_ticker, max_iv, max_strikes_list


def pick_strikes_for_strategy(strikes: ndarray,
                              stock_price: float,
                              strategy: str,
                              distance_n_strikes: int = 0,
                              wing_width_n_strikes: int = 0) -> dict[str, float]:
    """
    Select option strike(s) using number-of-strikes offsets from spot.

    Parameters:
      - :param strategy: one of {"put", "call", "strangle", "iron_condor"}
      - :param distance_n_strikes: non-negative integer indicating how many strikes away from the nearest OTM
          * put: short put = nearest OTM put (below spot) shifted further below by distance_n_strikes
          * call: short call = nearest OTM call (above spot) shifted further above by distance_n_strikes
          * strangle: both sides as above
          * iron_condor: short put/call as above
      - :param wing_width_n_strikes: positive integer for iron_condor; number of strikes between short and long on each side

    Returns:
      dict[str, float] with keys depending on strategy:
        - "put": {"put_short": strike}
        - "call": {"call_short": strike}
        - "strangle": {"put_short": strike, "call_short": strike}
        - "iron_condor": {
              "put_short": ..., "put_long": ...,
              "call_short": ..., "call_long": ...
          }
    """
    if distance_n_strikes < 0:
        raise ValueError("distance_n_strikes must be >= 0.")
    if strategy == "iron_condor" and wing_width_n_strikes <= 0:
        raise ValueError("For iron_condor, wing_width_n_strikes must be > 0.")

    n = strikes.size
    if n == 0:
        raise ValueError("No strikes available for the given ticker/expiry.")

    # Find nearest OTM indices relative to spot
    # below_idx: index of largest strike < spot
    # above_idx: index of smallest strike > spot (OTM call)
    below_idx = int(np.searchsorted(strikes, stock_price, side="left")) - 1
    above_idx = int(np.searchsorted(strikes, stock_price, side="right"))

    def require_idx(idx: int) -> None:
        if idx < 0 or idx >= n:
            raise ValueError("Requested number of strikes away is out of range for available strikes.")

    if strategy == "put":
        put_short_idx = below_idx - distance_n_strikes
        require_idx(put_short_idx)
        return {"put_short": float(strikes[put_short_idx])}

    elif strategy == "call":
        call_short_idx = above_idx + distance_n_strikes
        require_idx(call_short_idx)
        return {"call_short": float(strikes[call_short_idx])}

    elif strategy == "strangle":
        put_short_idx = below_idx - distance_n_strikes
        call_short_idx = above_idx + distance_n_strikes
        require_idx(put_short_idx)
        require_idx(call_short_idx)

        put_short = float(strikes[put_short_idx])
        call_short = float(strikes[call_short_idx])
        if not (put_short < stock_price < call_short):
            raise ValueError("Selected strangle strikes are not on opposite sides of spot.")
        return {"put_short": put_short, "call_short": call_short}

    elif strategy == "iron_condor":
        # Short legs offset by distance_n_strikes from nearest OTM
        put_short_idx = below_idx - distance_n_strikes
        call_short_idx = above_idx + distance_n_strikes
        require_idx(put_short_idx)
        require_idx(call_short_idx)

        # Long legs wing_width_n_strikes further OTM
        put_long_idx = put_short_idx - wing_width_n_strikes
        call_long_idx = call_short_idx + wing_width_n_strikes
        require_idx(put_long_idx)
        require_idx(call_long_idx)

        put_long = float(strikes[put_long_idx])
        put_short = float(strikes[put_short_idx])
        call_short = float(strikes[call_short_idx])
        call_long = float(strikes[call_long_idx])

        if not (put_long < put_short < stock_price < call_short < call_long):
            raise ValueError("Iron condor strikes do not form a valid OTM structure.")
        return {
            "put_short": put_short,
            "put_long": put_long,
            "call_short": call_short,
            "call_long": call_long,
        }

    else:
        raise ValueError("Unsupported strategy. Use one of: put, call, strangle, iron_condor.")

