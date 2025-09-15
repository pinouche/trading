import numpy as np
import pytest
from loguru import logger

from trading.core.strategy.get_strike_and_stock import process_stock_ticker_iv
from trading.api.api_actions.place_orders.place_option_orders import place_option_order
from trading.api.api_actions.place_orders.utils import wait_until_order_is_filled
from trading.api.api_actions.request_mkt_data.request_mkt_data import request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.ibapi_class import IBapi
from trading.api.contracts.strangle_option_contracts import get_options_strangle_contract
from trading.api.orders.option_orders import create_parent_order
from trading.utils import get_next_friday


@pytest.mark.parametrize("ticker_symbol", ["TSLA"])
def test_place_order_strangle(app: IBapi, ticker_symbol: str) -> None:
    # === Get stock and mid-price ===
    expiry_date = get_next_friday()

    # TODO: use reqSecDefOptParams instead of reqContractDetails to get all the strike prices

    iv, put_strike, call_strike = process_stock_ticker_iv(ticker_symbol,
                                                          app,
                                                          expiry_date)

    print("PUT STRIKE", put_strike)
    print("CALL STRIKE", call_strike)

    # === Define option contracts ===
    call_option_contract = get_options_contract(
        ticker=ticker_symbol,
        contract_strike=call_strike,
        expiry_date=expiry_date,
        right="C",
    )
    call_option_contract_details = get_contract_details(app, call_option_contract)

    put_option_contract = get_options_contract(
        ticker=ticker_symbol,
        contract_strike=put_strike,
        expiry_date=expiry_date,
        right="P",
    )
    put_option_contract_details = get_contract_details(app, put_option_contract)

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

    print("CALL conId:", put_option_contract_details.conId)
    print("PUT conId:", call_option_contract_details.conId)

    assert 2 == 3

    strangle_contract = get_options_strangle_contract(call_option_contract,
                                                      put_option_contract)

    print("STRANGLE CONTRACT", strangle_contract)

    # === Define combo order ===
    app.nextorderId += 1
    combo_limit_price = round(call_premium + put_premium, 2)
    combo_order = create_parent_order(
        app.nextorderId,
        "SELL",
        combo_limit_price,
        1,
        True
    )  # type: ignore[arg-type]

    print("COMBO LIMIT PRICE", combo_limit_price)

    # === Place strangle order ===
    place_option_order(app, strangle_contract, combo_order)

    print("WE ARE HERE")

    # === Wait until filled ===
    wait_until_order_is_filled(app)
    app.nextorderId += 1  # type: ignore

    # === Assertions ===
    assert app.order_status[app.nextorderId - 1]["remaining"] == 0
    assert app.order_status[app.nextorderId - 1]["filled"] == 1

    app.disconnect()
