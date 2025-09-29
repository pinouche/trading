from ibapi.contract import Contract

from trading.api.ibapi_class import IBapi
from trading.core.data_models.option_chains import OptionsChain


def get_options_parameters(app: IBapi,
                           option_contract: Contract) -> OptionsChain:

    app.reqSecDefOptParams(
        reqId=app.nextorderId,
        underlyingSymbol=option_contract.symbol,
        futFopExchange="",
        underlyingSecType="STK",
        underlyingConId=option_contract.conId,
    )

    return app.options_chain_dict[app.nextorderId]