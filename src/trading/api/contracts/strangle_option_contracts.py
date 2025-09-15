"""Strangle option contracts."""

from ibapi.contract import Contract, ComboLeg


def get_options_strangle_contract(call_contract: Contract,
                                  put_contract: Contract) -> Contract:
    strangle = Contract()
    strangle.symbol = call_contract.symbol
    strangle.secType = "BAG"
    strangle.currency = call_contract.currency
    strangle.exchange = "SMART"

    # Combo legs
    call_leg = ComboLeg()
    call_leg.conId = call_contract.conId  # must come from reqContractDetails
    call_leg.ratio = 1
    call_leg.action = "SELL"
    call_leg.exchange = call_contract.exchange

    put_leg = ComboLeg()
    put_leg.conId = put_contract.conId
    put_leg.ratio = 1
    put_leg.action = "SELL"
    put_leg.exchange = put_contract.exchange

    strangle.comboLegs = []
    strangle.comboLegs.append(call_leg)
    strangle.comboLegs.append(put_leg)

    return strangle