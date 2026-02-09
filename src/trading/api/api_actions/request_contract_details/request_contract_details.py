"""request contract details for a given contract"""

import time

from ibapi.contract import Contract, ContractDetails

from trading.api.ibapi_class import IBapi


def get_contract_details(app: IBapi, contract: Contract, req_id: int | None = None) -> list[ContractDetails]:
    """Request contract details for a given contract (e.g., stocks or options)."""
    if req_id is None:
        req_id = app.get_next_req_id()
    app.reqContractDetails(req_id, contract)

    if contract.secType == "STK":
        while req_id not in app.stocks_contract_details_dict:
            time.sleep(0.1)
        contract_details = app.stocks_contract_details_dict[req_id]
        return contract_details

    if contract.secType == "OPT":
        while req_id not in app.options_contract_details_dict:
            time.sleep(0.1)
        contract_details = app.options_contract_details_dict[req_id]
        return contract_details

    else:
        raise ValueError(f"contact security type should be STK or OPT, got {contract.secType}.")
