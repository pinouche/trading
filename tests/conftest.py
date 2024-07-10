import threading
import time
from typing import Any

import pytest
from dotenv import dotenv_values
from ibapi.contract import Contract
from loguru import logger
from trading.api.api_actions.request_contract_details.request_contract_details import get_contract_details
from trading.api.contracts.option_contracts import get_options_contract
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
def options_strikes(app: IBapi) -> list[float] | Any:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    option_contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    contract_details = get_contract_details(app, option_contract)

    return contract_details


@pytest.fixture()
def option_contract(options_strikes: list[float]) -> Contract:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    strike_price = options_strikes[0]
    return get_options_contract(ticker=ticker_symbol, contract_strike=strike_price, expiry_date=date)
