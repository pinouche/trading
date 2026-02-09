"""main module that implements the trading app and connects to IBKR API."""

import datetime
import threading
import time
import numpy as np
import pytz  # type: ignore
from loguru import logger

from trading.api.api_actions.market_scanner.request_market_scanner import (
    get_scanner_ticker_list,
    request_scanner,
)
from trading.api.api_actions.place_orders.place_option_orders import place_option_order
from trading.api.api_actions.place_orders.place_stock_orders import (
    place_conditional_parent_child_orders,
    place_simple_order,
)
from trading.api.api_actions.place_orders.utils import wait_until_order_is_filled
from trading.api.api_actions.request_contract_details.request_contract_details import (
    get_contract_details,
)
from trading.api.api_actions.request_mkt_data.request_mkt_data import (
    request_market_data_price,
)
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.strangle_option_contracts import get_options_strangle_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.option_orders import create_parent_order
from trading.core.strategy.get_strike_and_stock import (
    get_strike_for_highest_iv,
)
from trading.utils import config_load, get_next_friday, compute_number_of_options_to_trade

config_vars = config_load("./config.yaml")


def main() -> IBapi:
    """connect to IBapi TWS client"""

    def run_loop() -> None:
        appl.run()

    appl = IBapi()
    appl.connect(
        config_vars.client_config.ip_address,
        config_vars.client_config.port,
        config_vars.client_config.client_id,
    )

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via orderid
    while True:
        with appl._lock:
            next_id = appl.nextorderId
        if isinstance(next_id, int):
            logger.info("We are connected")
            break
        else:
            logger.info("Waiting for connection... (retrying)")
            time.sleep(1)

    # Get the list of stocks we are interested in
    stock_list = config_vars.stocks
    buffer_allowed_pennies = config_vars.buffer_allowed_pennies

    # request scanner and get stocks with iv >= config_vars.minimum_volatility%
    implied_vol = float(config_vars.minimum_volatility) / np.sqrt(252)
    request_scanner(appl, implied_vol=str(implied_vol))
    scanner_stocks = get_scanner_ticker_list(appl)

    logger.info(
        f"Stocks from Scanner are: {scanner_stocks}. Stocks from list are: {stock_list}."
    )
    stock_list = [stock for stock in stock_list if stock in scanner_stocks]

    if config_vars.use_wsb and not stock_list:  # only if we want to use wsb and stock list is empty
        stock_list = config_vars.wsb_to_include
        logger.info(f"We are going to use WSB stocks {stock_list}")
        if stock_list is None:
            raise ValueError("We are using WSB ticker but we got None.")
    elif not config_vars.use_wsb and not stock_list:  # if we do not use wsb and the list is empty, revert back to the original list
        stock_list = config_vars.stocks

    expiry_date = datetime.datetime.today().strftime("%Y%m%d")
    assert config_vars.todays_date == expiry_date, f"date in config {config_vars.todays_date} does not match today's date!"

    # The strategy works on 0DTE options, and we want to run it after 10 am and on Fridays.
    if datetime.datetime.today().weekday() != 4:
        if config_vars.test_mode:
            expiry_date = get_next_friday()
        else:
            raise ValueError(
                "Today is not a Friday, cannot run the delta hedging strategy!"
            )

    minutes_after_nine = config_vars.start_time_after_nine
    cet = pytz.timezone("CET")
    current_time_cet = datetime.datetime.now(cet)
    ten_am_cet = cet.localize(
        datetime.datetime.combine(
            current_time_cet, datetime.time(9, minutes_after_nine)
        )
    )
    # we want the program to execute only after the time set in the config file, unless we are in test mode
    if current_time_cet < ten_am_cet and not config_vars.test_mode:
        raise ValueError(
            "Today is Friday, but we do not want to run the strategy before 10 am!"
        )

    logger.info("Start the parallel computing...")
    # Here, we could use several defined strategies
    stock_ticker, iv, list_strikes = get_strike_for_highest_iv(appl,
                                                              stock_list,
                                                              expiry_date)

    if stock_ticker is None:
        logger.error("No valid stock found from the list with available strikes above and below spot.")
        return appl

    logger.info(
        f"Stock ticker: {stock_ticker}"
        f"Implied volatility: {iv}"
    )

    # Get the current stock price
    stock_contract = get_stock_contract(ticker=stock_ticker)
    price_list = request_market_data_price(appl, stock_contract)
    bid_price, ask_price = price_list[-2], price_list[-1]
    stock_price = np.round((ask_price + bid_price) / 2, 2)

    number_of_options = compute_number_of_options_to_trade(stock_ticker,
                                                           stock_price)

    # Find strikes below and above
    below_strikes = list_strikes[list_strikes < stock_price]
    above_strikes = list_strikes[list_strikes > stock_price]

    # get closest strikes to current price
    put_strike = below_strikes[-1]
    call_strike = above_strikes[0]

    # define option contract and request data for it.
    call_option_contract = get_options_contract(
        ticker=stock_ticker,
        contract_strike=call_strike,
        expiry_date=expiry_date,
        right="C",
    )

    put_option_contract = get_options_contract(
        ticker=stock_ticker,
        contract_strike=put_strike,
        expiry_date=expiry_date,
        right="P",
    )

    # sell the strangle
    bool_status = False
    premium: float = 0
    while not bool_status:
        # request the price list for call side and compute the mid-point for the option price (ask+bid)/2
        call_price_list = request_market_data_price(appl, call_option_contract)
        call_premium = float(np.round(np.mean(call_price_list), 2))

        # request the price list for put side and compute the mid-point for the option price (ask+bid)/2
        put_price_list = request_market_data_price(appl, put_option_contract)
        put_premium = float(np.round(np.mean(put_price_list), 2))

        assert call_premium > 0, "call premium cannot be negative!"
        assert put_premium > 0, "put premium cannot be negative!"

        # Fetch conIds for the combo legs
        call_details = get_contract_details(appl, call_option_contract)
        put_details = get_contract_details(appl, put_option_contract)

        call_conid = call_details[0].contract.conId
        put_conid = put_details[0].contract.conId

        strangle_contract = get_options_strangle_contract(call_option_contract,
                                                          put_option_contract,
                                                          call_conid,
                                                          put_conid)

        # create an option sell order and fire it
        combo_limit_price = round(put_premium + call_premium - config_vars.buffer_allowed_pennies, 2)
        combo_order_id = appl.get_next_req_id()
        combo_order = create_parent_order(
            combo_order_id, "SELL", combo_limit_price, number_of_options, False
        )  # type: ignore[arg-type]

        place_option_order(appl, strangle_contract, combo_order, order_id=combo_order_id)
        # make sure the order has been executed, received on TWS and all option orders are filled before proceeding.
        bool_status = wait_until_order_is_filled(
            appl, order_id=combo_order_id, waiting_time=config_vars.waiting_time_to_readjust_order
        )


    # get the stock contract for the above ticker
    stock_contract = get_stock_contract(ticker=stock_ticker)

    # Get the current stock price
    price_list = request_market_data_price(appl, stock_contract)
    bid_price, ask_price = price_list[-2], price_list[-1]
    mid_price = np.round((ask_price + bid_price) / 2, 2)

    # place order to buy the stock
    place_simple_order(
        app=appl,
        contract=stock_contract,
        action="BUY",
        price=mid_price + buffer_allowed_pennies,
        quantity=number_of_options * 100,
        order_type="LMT",
        outside_hours=True,
    )  # set the order to midprice (to auto track price changes)

    _ = wait_until_order_is_filled(appl)

    logger.info("We are now placing the conditional order")
    print("We are now placing the conditional order")

    # place a parent sell order if condition is reached with an attached child buy conditional order.
    place_conditional_parent_child_orders(appl, stock_contract, float(put_strike), put_premium + call_premium, number_of_options)

    return appl


if __name__ == "__main__":

    logger.info(f"Currently running in test_mode={config_vars.test_mode}. Make sure this variable is "
                f"set to False for a real run!")

    response = input("Continue execution? (y/n): ")
    if response.lower() != 'y':
        print("Execution aborted")
        exit()

    app = main()
    app.disconnect()
