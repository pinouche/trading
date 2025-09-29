"""Strangle option contracts."""

from ibapi.contract import Contract, ComboLeg


def get_options_strangle_contract(call_contract: Contract,
                                  put_contract: Contract,
                                  call_conid: int,
                                  put_conid: int) -> Contract:
    """
    Create a BAG contract with two SELL legs: call and put.
    Requires that conId fields are already set on both legs (normally via reqContractDetails).
    """
    combo = Contract()
    combo.symbol = call_contract.symbol
    combo.secType = "BAG"
    combo.currency = call_contract.currency
    combo.exchange = "SMART"

    leg_call = ComboLeg()
    leg_call.conId = call_conid
    leg_call.ratio = 1
    leg_call.action = "SELL"
    leg_call.exchange = call_contract.exchange

    leg_put = ComboLeg()
    leg_put.conId = put_conid
    leg_put.ratio = 1
    leg_put.action = "SELL"
    leg_put.exchange = put_contract.exchange

    combo.comboLegs = [leg_call, leg_put]
    return combo