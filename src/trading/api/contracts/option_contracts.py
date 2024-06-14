"""create options contract object"""

from datetime import datetime

from ibapi.contract import Contract


def get_options_contract(ticker: str, contract_strike: int | str = "",
                         expiry_date: str | None = None, right: str = "C") -> Contract:
    """Return the option contract object."""
    if expiry_date == "today":
        expiry_date = datetime.now().strftime("%Y%m%d")
    elif expiry_date is None:
        expiry_date = ""

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
