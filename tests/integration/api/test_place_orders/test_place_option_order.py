import time

import numpy as np
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.option_orders import create_parent_order
from trading.core.strategy.get_strike_and_stock import compute_closest_percentage
from trading.utils import get_next_friday


def test_place_order_options_contract(app: IBapi) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    option_contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    stock_contract = get_stock_contract(ticker=ticker_symbol)

    # get the current price of the stock
    app.reqMktData(app.nextorderId, stock_contract, '', True, False, [])
    time.sleep(5)
    stock_price_list = app.stock_current_price_dict[app.nextorderId].price
    mid_price = np.mean(stock_price_list)
    app.nextorderId += 1  # type: ignore

    # get the available strike prices for the option contract
    app.reqContractDetails(app.nextorderId, option_contract)
    time.sleep(5)
    strike_price_list = app.options_strike_price_dict[ticker_symbol]
    closest_itm_strike = compute_closest_percentage(strike_price_list, mid_price)
    app.nextorderId += 1  # type: ignore

    # get the price of the options for given strike price
    contract = get_options_contract(ticker=ticker_symbol, contract_strike=closest_itm_strike, expiry_date=date)
    app.reqMktData(app.nextorderId, contract, '', True, False, [])
    time.sleep(2)
    mid_price = np.mean(app.stock_current_price_dict[app.nextorderId].price)
    app.nextorderId += 1  # type: ignore

    order = create_parent_order(app.nextorderId, "SELL", mid_price, 1)  # type: ignore[arg-type]
    app.placeOrder(app.nextorderId, contract, order)

    app.nextorderId += 1  # type: ignore
    app.disconnect()
