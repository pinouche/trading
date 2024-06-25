import time

import numpy as np
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.option_orders import create_parent_order
from trading.core.strategy.get_strike_and_stock import compute_closest_percentage
from trading.utils import get_next_friday


def test_place_order_options_contract(app: IBapi, options_strikes: list[float]) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    stock_contract = get_stock_contract(ticker=ticker_symbol)

    # get the current price of the stock
    app.reqMktData(app.nextorderId, stock_contract, '', True, False, [])

    while app.nextorderId not in app.stock_current_price_dict:
        time.sleep(1.0)

    stock_price_list = app.stock_current_price_dict[app.nextorderId].price
    mid_price = np.mean(stock_price_list)
    app.nextorderId += 1  # type: ignore

    # get the available strike prices for the option contract
    closest_itm_strike = compute_closest_percentage(options_strikes, mid_price)

    # get the price of the options for given strike price
    contract = get_options_contract(ticker=ticker_symbol, contract_strike=closest_itm_strike, expiry_date=date)
    app.reqMktData(app.nextorderId, contract, '', True, False, [])

    while app.nextorderId not in app.stock_current_price_dict:
        time.sleep(1.0)

    mid_price = np.mean(app.stock_current_price_dict[app.nextorderId].price)
    app.nextorderId += 1  # type: ignore

    number_of_options = 3
    order = create_parent_order(app.nextorderId, "SELL", mid_price, number_of_options, False)  # type: ignore[arg-type]
    app.placeOrder(app.nextorderId, contract, order)

    while app.nextorderId not in app.execution_details:
        time.sleep(0.2)

    while app.nextorderId not in app.order_status:
        time.sleep(0.2)

    # here we wait for all the options to have been sold before buying stocks
    while True:
        remaining = app.order_status[app.nextorderId]["remaining"]
        if remaining == 0:
            break

    assert app.order_status[app.nextorderId]["remaining"] == 0
    assert app.order_status[app.nextorderId]["filled"] == number_of_options

    app.nextorderId += 1  # type: ignore
    app.disconnect()
