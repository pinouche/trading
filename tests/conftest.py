import threading
import time
from typing import Any

import numpy as np
import pytest
from dotenv import dotenv_values
from ibapi.contract import Contract
from loguru import logger
from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.api_actions.request_data.request_mkt_data import request_market_data_price
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.contracts.stock_contracts import get_stock_contract
from trading.api.ibapi_class import IBapi
from trading.utils import get_next_friday

env_vars = dotenv_values(".env")


@pytest.fixture(scope="session")
def client_id() -> dict[str, int]:
    return {
        "value": int(env_vars["CLIENT_ID"])
    }


# Fixture to create and initialize the IBapi application
@pytest.fixture()
def app(client_id: dict[str, int]) -> IBapi:
    def run_loop() -> None:
        appl.run()

    # Increment client ID
    client_id["value"] += 1

    appl = IBapi()
    appl.connect(env_vars.get("IP_ADDRESS"),
                 int(env_vars.get("PORT")),
                 client_id["value"])

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    while True:
        if isinstance(appl.nextorderId, int):
            logger.info('We are connected')
            break
        else:
            print('Waiting for connection... (retrying)')
            time.sleep(1)

    return appl


@pytest.fixture()
def ticker_symbol() -> str | list[str]:
    symbol = "TSLA"
    return symbol


@pytest.fixture()
def options_strikes(app: IBapi, ticker_symbol: str) -> list[float] | Any:
    date = get_next_friday()
    option_contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    contract_details = get_contract_details(app, option_contract)
    return contract_details


@pytest.fixture()
def current_stock_price(app: IBapi, ticker_symbol: str) -> float:

    stock_contract = get_stock_contract(ticker=ticker_symbol)
    stock_price_list = request_market_data_price(app, stock_contract)
    mid_price: float = np.round(np.mean(np.array(stock_price_list)[:2]), 2)

    return mid_price


@pytest.fixture()
def option_contract(current_stock_price: float, ticker_symbol: str, options_strikes: list[float]) -> Contract:
    date = get_next_friday()
    strike_price = options_strikes[np.argmin(np.abs(np.array(options_strikes) - current_stock_price))]
    return get_options_contract(ticker=ticker_symbol, contract_strike=strike_price, expiry_date=date)
