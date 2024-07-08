import numpy as np
from trading.api.api_actions.place_orders.utils import wait_until_order_is_filled
from trading.api.api_actions.request_data.request_mkt_data import request_market_data
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
    stock_price_list = request_market_data(app, stock_contract)

    mid_price = np.mean(stock_price_list)
    app.nextorderId += 1  # type: ignore

    # get the available strike prices for the option contract
    closest_itm_strike = compute_closest_percentage(options_strikes, mid_price)

    # get the price of the options for given strike price
    option_contract = get_options_contract(ticker=ticker_symbol, contract_strike=closest_itm_strike, expiry_date=date)
    price_list = request_market_data(app, option_contract)

    mid_price = np.round(np.mean(price_list), 2)
    app.nextorderId += 1  # type: ignore

    number_of_options = 1
    order = create_parent_order(app.nextorderId, "SELL", mid_price, number_of_options, False)  # type: ignore[arg-type]
    app.placeOrder(app.nextorderId, option_contract, order)

    # wait until the options order has been filled
    wait_until_order_is_filled(app)

    assert app.order_status[app.nextorderId]["remaining"] == 0
    assert app.order_status[app.nextorderId]["filled"] == number_of_options

    app.nextorderId += 1  # type: ignore
    app.disconnect()
