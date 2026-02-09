from ibapi.contract import Contract

from trading.api.ibapi_class import IBapi
from trading.core.data_models.option_chains import OptionsChain


def get_options_parameters(app: IBapi,
                           option_contract: Contract,
                           req_id: int | None = None) -> OptionsChain:
    if req_id is None:
        req_id = app.get_next_req_id()

    app.reqSecDefOptParams(
        reqId=req_id,
        underlyingSymbol=option_contract.symbol,
        futFopExchange="",
        underlyingSecType="STK",
        underlyingConId=option_contract.conId,
    )

    import time
    while req_id not in app.options_chain_dict:
        time.sleep(0.1)

    return app.options_chain_dict[req_id]