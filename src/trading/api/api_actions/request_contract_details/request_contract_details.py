"""request contract details for a given contract"""

import time

from ibapi.contract import Contract, ContractDetails

from trading.api.ibapi_class import IBapi


def get_contract_details(app: IBapi, contract: Contract) -> list[ContractDetails]:
    """Request contract details for a given contract (e.g., stocks or options)."""
    app.reqContractDetails(app.nextorderId, contract)

    if contract.secType == "STK":
        while app.nextorderId not in app.stocks_contract_details_dict:
            time.sleep(0.1)

        return app.stocks_contract_details_dict[app.nextorderId]

    if contract.secType == "OPT":
        while app.nextorderId not in app.options_contract_details_dict:
            time.sleep(0.1)

        return app.options_contract_details_dict[app.nextorderId]

    else:
        raise ValueError(f"contact security type should be STK or OPT, got {contract.secType}.")
