"""main module that implements the trading app and connects to IBKR API."""

import threading
import time
from datetime import datetime

import numpy as np
from dotenv import dotenv_values
from loguru import logger

from trading.api.api_actions.place_orders.place_option_orders import place_option_order
from trading.api.api_actions.place_orders.place_stock_orders import place_simple_order
from trading.api.api_actions.place_orders.utils import wait_until_order_is_filled
from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.api_actions.request_data.request_mkt_data import request_market_data
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.option_orders import create_parent_order
from trading.core.strategy.get_strike_and_stock import get_strike_and_stock
from trading.utils import config_load, get_next_friday

env_vars = dotenv_values(".env")
config_vars = config_load("./config.yaml")


def main() -> IBapi:
    """connect to IBapi TWS client"""
    def run_loop() -> None:
        appl.run()

    appl = IBapi()
    appl.connect(env_vars.get("IP_ADDRESS"),
                 int(env_vars.get("PORT")),
                 int(env_vars.get("CLIENT_ID")))

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via orderid
    while True:
        if isinstance(appl.nextorderId, int):
            logger.info('We are connected')
            break
        else:
            logger.info('Waiting for connection... (retrying)')
            time.sleep(1)

    # Get the list of stocks we are interested in
    stock_list = config_vars["stocks"]
    expiry_date = datetime.today().strftime("%Y%m%d")

    # The strategy works on 0DTE options.
    if datetime.today().weekday() != 4:
        # raise ValueError("Today is not a Friday, cannot run the delta hedging strategy!")
        expiry_date = get_next_friday()

    stock_ticker, min_value = get_strike_and_stock(appl, stock_list, expiry_date)
    appl.nextorderId += 1  # type: ignore
    logger.info(f"The stock with the closest strike price is {stock_ticker}, and the strike price is {min_value}.")

    # define option contract and request data for it.
    contract = get_options_contract(ticker=stock_ticker, contract_strike=min_value, expiry_date=expiry_date, right="C")
    get_contract_details(appl, contract)
    request_market_data(appl, contract)

    # compute the mid-point for the option price (ask+bid)/2.
    mid_price = np.round(np.mean(appl.stock_current_price_dict[appl.nextorderId].price), 2)
    appl.nextorderId += 1  # type: ignore

    logger.info(f"the mid price is {mid_price}")

    # create an option sell order and fire it
    order = create_parent_order(appl.nextorderId,
                                "SELL",
                                mid_price,
                                config_vars["number_of_options"],
                                False)  # type: ignore[arg-type]
    place_option_order(appl, contract, order)

    # make sure the order has been executed, received on TWS and all option orders are filled before proceeding.
    wait_until_order_is_filled(appl)

    logger.info("It does not wait to see whether or not it is finished!!")

    # get the stock contract for the above ticker
    stock_contract = get_stock_contract(ticker=stock_ticker)
    # Get the current stock price
    request_market_data(app, stock_contract)
    price_list = app.stock_current_price_dict[app.nextorderId].price
    mid_price = np.round(np.mean(np.array(price_list)[:2]), 2)
    place_simple_order(appl, stock_ticker, "BUY", mid_price, config_vars["number_of_options"]*100)

    # TODO: Proceed to stocks orders (2 conditional orders, one parent and one child)

    #
    get_contract_details(app, stock_contract)
    app.options_strike_price_dict[app.nextorderId]
    app.nextorderId += 1  # type: ignore

    return appl


if __name__ == '__main__':
    app = main()
    app.disconnect()
