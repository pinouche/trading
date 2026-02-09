"""implement request live market data method"""

import time
from typing import Any
from ibapi.contract import Contract

from trading.api.ibapi_class import IBapi



def request_market_data_price(app: IBapi, contract: Contract, req_id: int | None = None) -> list[float]:
    """Request live point (i.e. not streaming: snapshot=True) market data for options or stocks."""
    if req_id is None:
        req_id = app.get_next_req_id()
    app.reqMktData(req_id, contract, '', True, False, [])

    # this is the same data structure if it's a stock or option contract request
    while req_id not in app.current_asset_price_dict:
        time.sleep(0.1)

    while not app.current_asset_price_dict[req_id]:
        time.sleep(0.1)

    while not app.current_asset_price_dict[req_id].price:
        time.sleep(0.1)

    while len(app.current_asset_price_dict[req_id].price[-1]) != 2:
        time.sleep(0.1)

    return app.current_asset_price_dict[req_id].price[-1]


def request_market_data_option_iv(app: IBapi, contract: Contract, req_id: int | None = None) -> list[float] | Any:
    """Request live option iv (i.e. not streaming: snapshot=True)."""
    if contract.secType != "OPT":
        raise ValueError(f"the contract secType must be OPT, got {contract.secType}")

    if req_id is None:
        req_id = app.get_next_req_id()
    app.reqMktData(req_id, contract, '', True, False, [])

    while req_id not in app.current_option_iv_dict:
        time.sleep(0.1)

    while not isinstance(app.current_option_iv_dict[req_id], float):
        time.sleep(0.1)

    return app.current_option_iv_dict[req_id]
