"""request contract details for a given contract"""

import time
from typing import Any

from ibapi.contract import Contract

from trading.api.ibapi_class import IBapi


def get_contract_details(app: IBapi, contract: Contract) -> list | Any:
    """Request contract details for a given contract (e.g., stocks or options)."""
    app.reqContractDetails(app.nextorderId, contract)
    current_strike_list_len = 0

    if contract.secType == "STK":
        while app.nextorderId not in app.stocks_strike_price_dict:
            time.sleep(0.1)

        return app.stocks_strike_price_dict[app.nextorderId]

    elif contract.secType == "OPT":
        ticker_symbol = contract.symbol
        while ticker_symbol not in app.options_strike_price_dict:
            time.sleep(0.1)
        while True:
            if app.options_strike_price_dict[ticker_symbol]:
                if len(app.options_strike_price_dict[ticker_symbol]) > current_strike_list_len:
                    current_strike_list_len = len(app.options_strike_price_dict[ticker_symbol])
                else:
                    break
            time.sleep(0.2)

        return app.options_strike_price_dict[ticker_symbol]

    else:
        raise ValueError(f"contact security type should be STK or OPT, got {contract.secType}.")
