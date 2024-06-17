import time

from trading.api.contracts.option_contracts import get_options_contract
from trading.api.ibapi_class import IBapi
from trading.api.orders.option_orders import create_parent_order
from trading.utils import get_next_friday


def test_options_contract(app: IBapi) -> None:
    ticker_symbol = "TSLA"
    date = get_next_friday()
    contract = get_options_contract(ticker=ticker_symbol, contract_strike=110.0, expiry_date=date)
    app.reqMktData(app.nextorderId, contract, '', True, False, [])
    time.sleep(2)

    mid_price = app.stock_current_price_dict[app.nextorderId].price

    app.reqIds(-1)

    order = create_parent_order(app.nextorderId, "SELL", mid_price, 1) # type: ignore[arg-type]
    app.placeOrder(app.nextorderId, contract, order)

    app.reqIds(-1)
    app.disconnect()
