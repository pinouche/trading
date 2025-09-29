import numpy as np
import pytest
from loguru import logger

from trading.core.strategy.get_strike_and_stock import (process_stock_ticker_iv,
                                                        get_current_stock_price,
                                                        pick_strikes_for_strategy)
from trading.api.api_actions.place_orders.place_option_orders import place_option_order
from trading.api.api_actions.place_orders.utils import wait_until_order_is_filled
from trading.api.api_actions.request_mkt_data.request_mkt_data import request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.ibapi_class import IBapi
from trading.api.contracts.strangle_option_contracts import get_options_strangle_contract
from trading.api.orders.option_orders import create_parent_order
from trading.utils import get_next_friday


# TODO: fix the test below

@pytest.mark.parametrize("ticker_symbol", ["TSLA"])
def test_place_short_order_strangle(app: IBapi, ticker_symbol: str) -> None:
    # === Get stock and mid-price ===
    expiry_date = get_next_friday()

    iv, strike_list = process_stock_ticker_iv(ticker_symbol,
                                              app,
                                              expiry_date)

    # current stock price
    stock_price = float(get_current_stock_price(app, ticker_symbol))

    dict_prices = pick_strikes_for_strategy(strike_list,
                                            stock_price,
                                            strategy="strangle",
                                            distance_n_strikes=0,
                                            wing_width_n_strikes=0)

    put_strike = dict_prices["put_short"]
    call_strike = dict_prices["call_short"]

    # === Define option contracts ===
    call_option_contract = get_options_contract(
        ticker=ticker_symbol,
        contract_strike=float(call_strike),
        expiry_date=expiry_date,
        right="C",
    )
    call_option_contract_details = get_contract_details(app, call_option_contract)[0]

    put_option_contract = get_options_contract(
        ticker=ticker_symbol,
        contract_strike=float(put_strike),
        expiry_date=expiry_date,
        right="P",
    )
    put_option_contract_details = get_contract_details(app, put_option_contract)[0]

    # === Get mid prices ===
    call_price_list = request_market_data_price(app, call_option_contract)
    call_premium = float(np.round(np.mean(call_price_list), 2))
    app.nextorderId += 1

    put_price_list = request_market_data_price(app, put_option_contract)
    put_premium = float(np.round(np.mean(put_price_list), 2))
    app.nextorderId += 1

    assert call_premium != put_premium, "very unlikely that call and put strikes are equal. please check."

    logger.info(f"Call strike price: {call_strike}, Put strike price: {put_strike}")
    logger.info(f"Call price: {call_premium}, Put price: {put_premium}")

    assert call_premium > 0, "call premium cannot be negative!"
    assert put_premium > 0, "put premium cannot be negative!"

    # === Create strangle BAG contract ===

    strangle_contract = get_options_strangle_contract(call_option_contract,
                                                      put_option_contract,
                                                      call_option_contract_details.contract.conId,
                                                      put_option_contract_details.contract.conId)

    # === Define combo order ===
    combo_limit_price = round(call_premium + put_premium, 2)*-1  # negative price (we sell a credit)
    combo_order = create_parent_order(
        app.nextorderId,
        "BUY",
        combo_limit_price,
        quantity=1,
        allornone=False
    )  # type: ignore[arg-type]

    # === Place strangle order ===
    place_option_order(app, strangle_contract, combo_order)

    # === Wait until filled ===
    wait_until_order_is_filled(app)
    app.nextorderId += 1  # type: ignore

    # === Assertions ===
    assert app.order_status[app.nextorderId - 1]["remaining"] == 0
    assert app.order_status[app.nextorderId - 1]["filled"] == 1

    app.disconnect()
