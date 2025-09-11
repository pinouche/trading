"""Strangle option contracts."""

from ibapi.contract import Contract, ComboLeg


def get_options_strangle_contract(call_contract: Contract, put_contract: Contract) -> Contract:
    """
    Create a strangle (BAG contract) using the call and put contracts.
    """
    strangle = Contract()
    strangle.symbol = call_contract.symbol
    strangle.secType = "BAG"
    strangle.currency = call_contract.currency
    strangle.exchange = call_contract.exchange

    # Combo legs
    call_leg = ComboLeg()
    call_leg.conId = call_contract.conId  # unique contract ID from IB
    call_leg.ratio = 1
    call_leg.action = "SELL"  # short the call
    call_leg.exchange = call_contract.exchange

    put_leg = ComboLeg()
    put_leg.conId = put_contract.conId
    put_leg.ratio = 1
    put_leg.action = "SELL"  # short the put
    put_leg.exchange = put_contract.exchange

    strangle.comboLegs = [call_leg, put_leg]

    return strangle