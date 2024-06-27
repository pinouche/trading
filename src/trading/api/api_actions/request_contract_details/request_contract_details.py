"""request contract details for a given contract"""

import time

from ibapi.contract import Contract

from trading.api.ibapi_class import IBapi


def get_contract_details(app: IBapi, contract: Contract) -> None:
    """Request contract details for a given contract (e.g., stocks or options)."""
    app.reqContractDetails(app.nextorderId, contract)

    if contract.secType == "STK":
        while app.nextorderId not in app.stocks_strike_price_dict:
            time.sleep(0.2)

    elif contract.secType == "OPT":
        ticker_symbol = contract.symbol
        while ticker_symbol not in app.options_strike_price_dict:
            time.sleep(0.2)
