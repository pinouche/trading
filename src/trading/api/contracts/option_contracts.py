"""create options contract object"""

from datetime import datetime

from ibapi.contract import Contract


def get_options_contract(ticker: str,
                         contract_strike: float | str = "",
                         expiry_date: str | None = None,
                         right: str = "C") -> Contract:

    contract = Contract()
    contract.symbol = ticker
    contract.secType = "OPT"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.strike = contract_strike
    contract.lastTradeDateOrContractMonth = expiry_date
    contract.right = right
    contract.multiplier = 100

    return contract


