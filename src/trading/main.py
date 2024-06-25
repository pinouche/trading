"""main module that implements the trading app and connects to IBKR API."""

import threading
import time
from datetime import datetime

from dotenv import dotenv_values
from loguru import logger

from trading.api.ibapi_class import IBapi
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
    logger.info(f"The stock with the closest strike price is {stock_ticker}, and the strike price is {min_value}.")

    # TODO: Implement getting the price of the above option and fire a sell order (look at the test 'test_place_option_order').
    # number_of_options = 3
    # order = create_parent_order(app.nextorderId, "SELL", mid_price, number_of_options, False)  # type: ignore[arg-type]
    # app.placeOrder(app.nextorderId, contract, order)

    return appl


if __name__ == '__main__':
    app = main()
