import numpy as np
from trading.api.api_actions.place_orders.place_option_orders import place_option_order
from trading.api.api_actions.place_orders.utils import wait_until_order_is_filled
from trading.api.api_actions.request_mkt_data.request_mkt_data import request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.option_orders import create_parent_order
from trading.utils import get_next_friday


def test_place_order_options_contract(app: IBapi, options_strikes: list[float]) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    stock_contract = get_stock_contract(ticker=ticker_symbol)
    stock_price_list = request_market_data_price(app, stock_contract)
    mid_price = np.mean(stock_price_list)

    # get the available strike prices for the option contract
    closest_strike_price = options_strikes[np.argmin(np.abs(mid_price-np.array(options_strikes)))]

    # get the price of the options for given strike price
    option_contract = get_options_contract(ticker=ticker_symbol, contract_strike=closest_strike_price, expiry_date=date)
    price_list = request_market_data_price(app, option_contract)

    mid_price = np.round(np.mean(price_list), 2)

    number_of_options = 1
    order_id = app.get_next_req_id()
    order = create_parent_order(order_id, "SELL", mid_price, number_of_options, False)  # type: ignore[arg-type]
    place_option_order(app, option_contract, order, order_id=order_id)

    # wait until the options order has been filled
    wait_until_order_is_filled(app, order_id=order_id)

    assert app.order_status[order_id]["remaining"] == 0
    assert app.order_status[order_id]["filled"] == number_of_options

    app.disconnect()
