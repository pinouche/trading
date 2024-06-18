import threading
import time
from typing import Any

import pytest
from dotenv import dotenv_values
from trading.api.contracts.option_contracts import get_options_contract
from trading.api.ibapi_class import IBapi
from trading.utils import get_next_friday

env_vars = dotenv_values(".env")


@pytest.fixture()
def app() -> IBapi:
    def run_loop() -> None:
        appl.run()

    appl = IBapi()
    appl.connect(env_vars.get("IP_ADDRESS"),
                 int(env_vars.get("PORT")),
                 int(env_vars.get("CLIENT_ID")))

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    time.sleep(2)

    yield appl
    appl.disconnect()


@pytest.fixture()
def options_strikes(app: IBapi) -> list[float] | Any:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    option_contract = get_options_contract(ticker=ticker_symbol, expiry_date=date)
    app.reqContractDetails(app.nextorderId, option_contract)
    time.sleep(10)
    return app.options_strike_price_dict[ticker_symbol]
