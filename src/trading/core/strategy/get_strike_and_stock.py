"""Fetch the option strikes for several stocks and returns the stock and strike for which the strike is closest to current price"""

import numpy as np
from loguru import logger

from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.api_actions.request_data.request_mkt_data import request_market_data_option_iv, request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi


def get_options_strikes(app: IBapi, ticker_symbol: str, date: str | None = None) -> list:
    """Retrieve the list of available strike prices for a given option contract."""
    contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    contract_details = get_contract_details(app, contract)

    return contract_details


def get_current_stock_price(app: IBapi, ticker_symbol: str) -> np.float64:
    """Retrieve the current stock price for a given ticker."""
    stock_contract = get_stock_contract(ticker=ticker_symbol)
    stock_price_list = request_market_data_price(app, stock_contract)
    mid_price: np.float64 = np.round(np.mean(np.array(stock_price_list)[:2]), 2)

    return mid_price


def process_stock_ticker_iv(stock_ticker: str,
                            app: IBapi,
                            expiry_date: str | None = None) -> tuple[float, float, float]:
    """Function to find the iv for a given stock option."""
    # get the available strike prices
    list_options_strike_price = get_options_strikes(app, stock_ticker, expiry_date)
    list_options_strike_price = np.array(list_options_strike_price)
    app.nextorderId += 1  # type: ignore

    # current stock price
    stock_price = get_current_stock_price(app, stock_ticker)

    # Find strikes below and above
    below_strikes = list_options_strike_price[list_options_strike_price <= stock_price]
    above_strikes = list_options_strike_price[list_options_strike_price >= stock_price]

    put_strike = np.max(below_strikes)
    call_strike = np.min(above_strikes)

    # get the corresponding put option contract and request details (we are interested in iv)
    option_contract = get_options_contract(ticker=stock_ticker,
                                           contract_strike=put_strike,
                                           expiry_date=expiry_date)
    iv_put = request_market_data_option_iv(app, option_contract)

    # get the corresponding call option contract and request details (we are interested in iv)
    option_contract = get_options_contract(ticker=stock_ticker,
                                           contract_strike=call_strike,
                                           expiry_date=expiry_date)
    iv_call = request_market_data_option_iv(app, option_contract)

    logger.info(f"Closest price for stock: {stock_ticker}, "
                f"put strike price: {put_strike},"
                f"call strike price: {call_strike},"
                f"stock price: {stock_price}, "
                f"average option iv is: {(iv_put+iv_call)*100/2}%")

    logger.info(f"current redId is {app.nextorderId}.")

    return iv, put_strike, call_strike  # type: ignore


def get_strike_for_highest_iv(app: IBapi,
                              stock_list: list,
                              expiry_date: str | None = None) -> tuple[str, float, float, float]:
    """Return the stock and the associated strike price with the highest implied volatility."""

    max_ticker = None
    max_iv = float("-inf")
    max_put = None
    max_call = None

    for ticker in stock_list:
        iv, strike_price_puts, strike_price_calls = process_stock_ticker_iv(ticker, app, expiry_date)
        if iv > max_iv:
            max_ticker = ticker
            max_iv = iv
            max_put = strike_price_puts
            max_call = strike_price_calls

    return max_ticker, max_iv, max_put, max_call
