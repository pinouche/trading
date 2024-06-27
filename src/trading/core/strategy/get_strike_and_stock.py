"""Fetch the options strikes for several stocks and returns the stock and strike for which the strike is closest to current price"""

import numpy as np
from loguru import logger

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


def get_strike_and_stock(app: IBapi, stock_list: list, expiry_date: str | None = None) -> tuple[str, float]:
    """Return the stock and the associated strike price for which the current price of the stock is the closest to
    the strike price. The strike price has to be in-the-money (lower than the current stock price).
    """
    dict_stock_price = {}
    dict_options_strike_price = {}
    dict_result = {}

    for stock_ticker in stock_list:

        # define option contract
        option_contract = get_options_contract(ticker=stock_ticker, expiry_date=expiry_date)
        # request option contract info
        app.reqContractDetails(app.nextorderId, option_contract)
        # store the information
        condition = True
        while condition:
            try:
                condition = False
                dict_options_strike_price[stock_ticker] = app.options_strike_price_dict[stock_ticker]
            except KeyError:
                condition = True
        app.nextorderId += 1  # type: ignore

        # define the stock contract
        stock_contract = get_stock_contract(stock_ticker)
        # request the stock contract information
        app.reqMktData(app.nextorderId, stock_contract, '', True, False, [])
        condition = True
        while condition:
            try:
                price_list = app.stock_current_price_dict[app.nextorderId].price
                # compute the mid-point between current bid and ask
                if len(price_list) == 2:
                    mid_price = np.mean(np.array(price_list)[:2])
                    dict_stock_price[stock_ticker] = mid_price
                    condition = False
            except (IndexError, ValueError, KeyError, TypeError):
                condition = True
        app.nextorderId += 1  # type: ignore

        closest_strike_price = compute_closest_percentage(dict_options_strike_price[stock_ticker],
                                                          dict_stock_price[stock_ticker])
        logger.info(f"Closest price for stock: {stock_ticker}, strike price: {closest_strike_price}, "
                    f"stock price: {dict_stock_price[stock_ticker]}")
        dict_result[stock_ticker] = closest_strike_price

    stock_ticker = min(dict_result, key=dict_result.get)  # type: ignore
    min_value = dict_result[stock_ticker]

    return stock_ticker, min_value
