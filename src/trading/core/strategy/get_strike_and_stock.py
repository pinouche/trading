"""Fetch the options strikes for several stocks and returns the stock and strike for which the strike is closest to current price"""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import numpy as np
from loguru import logger

from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.api_actions.request_data.request_mkt_data import request_market_data_option_iv, request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi


def compute_closest_percentage(strike_prices: np.array, stock_price: float) -> np.array:
    """Compute % difference between the closest strike and current stock price."""
    strike_prices = np.array(strike_prices)
    strike_prices = strike_prices[(strike_prices / stock_price) < 1]
    if len(strike_prices) == 0:
        return None
    closest_strike = strike_prices[np.argmax(strike_prices / stock_price)]

    return closest_strike


def get_highest_iv_from_dic(dict_result: dict[str, tuple[float, float]]) -> tuple[str, float]:
    """Retrieve the stock that has the highest iv for a given strike price."""
    # Sort the dictionary items by the iv value
    sorted_items = sorted(dict_result.items(), key=lambda item: item[1][0], reverse=True)
    stock_ticker, items = sorted_items[0]
    closest_strike_price = items[1]

    return stock_ticker, closest_strike_price


def get_options_strikes(app: IBapi, ticker_symbol: str, date: str | None = None) -> np.array:
    """Retrieve the list of available strike prices for a given option contract."""
    contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    contract_details = get_contract_details(app, contract)

    return np.array(contract_details)


def get_current_stock_price(app: IBapi, ticker_symbol: str) -> float:
    """Retrieve the current stock price for a given ticker."""
    stock_contract = get_stock_contract(ticker=ticker_symbol)
    stock_price_list = request_market_data_price(app, stock_contract)
    mid_price: float = np.round(np.mean(np.array(stock_price_list)[:2]), 2)

    return mid_price


def process_in_parallel(process_function: Callable[..., tuple[str, Any]], stock_list: list,
                        app: IBapi, expiry_date: str | None = None) -> dict[str, Any]:
    """Process a list of stock tickers in parallel using a specified processing function."""
    dict_result = {}

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_function, stock_ticker, app, expiry_date): stock_ticker for stock_ticker in stock_list}

        for future in as_completed(futures):
            stock_ticker = futures[future]
            try:
                result = future.result()
                dict_result[result[0]] = result[1]
            except (ValueError, IndexError) as e:
                logger.error(f"{stock_ticker} generated an exception: {e}")

    return dict_result


def process_stock_ticker_iv(stock_ticker: str, app: IBapi, expiry_date: str | None = None) -> tuple[str, tuple]:
    """Function to find the iv for a given stock option."""
    # get the available strike prices
    dict_options_strike_price = get_options_strikes(app, stock_ticker, expiry_date)
    app.nextorderId += 1  # type: ignore

    # current stock price
    stock_price = get_current_stock_price(app, stock_ticker)
    argmin = np.argmin(np.abs(dict_options_strike_price - stock_price))
    closest_strike_price = dict_options_strike_price[argmin]

    # get the corresponding option contract and request details (we are interested in iv)
    option_contract = get_options_contract(ticker=stock_ticker, contract_strike=closest_strike_price, expiry_date=expiry_date)
    iv = request_market_data_option_iv(app, option_contract)

    logger.info(f"Closest price for stock: {stock_ticker}, strike price: {closest_strike_price}, "
                f"stock price: {stock_price}, option iv is: {iv * 100}%")
    logger.info(f"current redId is {app.nextorderId}.")

    return stock_ticker, (iv, closest_strike_price)


def process_stock_ticker_for_closest_strike(stock_ticker: str, app: IBapi, expiry_date: str | None = None) -> tuple[str, float]:
    """Function to find the closest corresponding strike price for a given ticker."""
    # get the available strike prices
    dict_options_strike_price = get_options_strikes(app, stock_ticker, expiry_date)
    app.nextorderId += 1  # type: ignore

    # current stock price
    stock_price = get_current_stock_price(app, stock_ticker)

    closest_strike_price = compute_closest_percentage(dict_options_strike_price, stock_price)
    logger.info(f"Closest price for stock: {stock_ticker}, strike price: {closest_strike_price}, "
                f"stock price: {stock_price}")
    logger.info(f"current redId is {app.nextorderId}.")

    return stock_ticker, closest_strike_price


def get_strike_and_highest_iv_stock(app: IBapi, stock_list: list, expiry_date: str | None = None) -> tuple[str, float]:
    """Return the stock and the associated strike price with the highest implied volatility."""
    dict_result = process_in_parallel(process_stock_ticker_iv, stock_list, app, expiry_date)
    stock_ticker, closest_strike_price = get_highest_iv_from_dic(dict_result)  # type: ignore

    return stock_ticker, closest_strike_price


def get_strike_and_stock(app: IBapi, stock_list: list, expiry_date: str | None = None) -> tuple[str, float]:
    """Return the stock and the associated strike price for which the current price of the stock is the closest to
    the strike price. The strike price has to be in-the-money (lower than the current stock price).
    """
    dict_result = process_in_parallel(process_stock_ticker_for_closest_strike, stock_list, app, expiry_date)
    stock_ticker = min(dict_result, key=dict_result.get)  # type: ignore
    min_value = dict_result[stock_ticker]

    return stock_ticker, min_value
