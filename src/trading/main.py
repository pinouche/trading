"""main module that implements the trading app and connects to IBKR API."""

import threading
import time
from datetime import datetime

import numpy as np
from dotenv import dotenv_values
from loguru import logger

from trading.api.api_actions.place_orders.place_stock_orders import place_conditional_parent_child_orders, place_simple_order
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

    stock_ticker, strike_price = get_strike_and_stock(appl, stock_list, expiry_date)
    appl.nextorderId += 1  # type: ignore
    logger.info(f"The stock with the closest strike price is {stock_ticker}, and the strike price is {strike_price}.")

    # define option contract and request data for it.
    contract = get_options_contract(ticker=stock_ticker, contract_strike=strike_price, expiry_date=expiry_date, right="C")
    _ = get_contract_details(appl, contract)
    price_list = request_market_data(appl, contract)

    # compute the mid-point for the option price (ask+bid)/2.
    mid_price = np.round(np.mean(price_list), 2)
    appl.nextorderId += 1  # type: ignore

    logger.info(f"the mid price is {mid_price}")

    # create an option sell order and fire it
    create_parent_order(appl.nextorderId,
                                "SELL",
                                mid_price,
                                config_vars["number_of_options"],
                                False)  # type: ignore[arg-type]
    # place_option_order(appl, contract, order)
    #
    # # make sure the order has been executed, received on TWS and all option orders are filled before proceeding.
    # wait_until_order_is_filled(appl)

    logger.info("It does not wait to see whether or not it is finished!!")

    # get the stock contract for the above ticker
    stock_contract = get_stock_contract(ticker=stock_ticker)
    # Get the current stock price
    price_list = request_market_data(appl, stock_contract)
    mid_price = np.round(np.mean(np.array(price_list)[:2]), 2)

    # place order to buy the stock
    place_simple_order(appl, stock_contract, "BUY", mid_price, config_vars["number_of_options"]*100)

    logger.info("We are here now!")

    # place a parent sell order if condition is reached with an attached child buy conditional order.
    place_conditional_parent_child_orders(appl, stock_contract, strike_price, mid_price)

    return appl


if __name__ == '__main__':
    app = main()
    app.disconnect()
