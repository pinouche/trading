"""Iron Condor contracts."""

from ibapi.contract import Contract, ComboLeg


def get_options_iron_condor_contract(short_call_contract: Contract,
                                     long_call_contract: Contract,
                                     short_put_contract: Contract,
                                     long_put_contract: Contract,
                                     short_call_conid: int,
                                     long_call_conid: int,
                                     short_put_conid: int,
                                     long_put_conid: int) -> Contract:
    """
    Create a BAG contract for an Iron Condor with four legs:
      - SELL call (short call)
      - BUY call (long call, further OTM than the short call)
      - SELL put (short put)
      - BUY put (long put, further OTM than the short put)

    Requires that conId fields are already known for each option (via reqContractDetails).
    """
    combo = Contract()
    combo.symbol = short_call_contract.symbol
    combo.secType = "BAG"
    combo.currency = short_call_contract.currency
    combo.exchange = "SMART"

    # Short Call (SELL)
    leg_short_call = ComboLeg()
    leg_short_call.conId = short_call_conid
    leg_short_call.ratio = 1
    leg_short_call.action = "SELL"
    leg_short_call.exchange = short_call_contract.exchange

    # Long Call (BUY)
    leg_long_call = ComboLeg()
    leg_long_call.conId = long_call_conid
    leg_long_call.ratio = 1
    leg_long_call.action = "BUY"
    leg_long_call.exchange = long_call_contract.exchange

    # Short Put (SELL)
    leg_short_put = ComboLeg()
    leg_short_put.conId = short_put_conid
    leg_short_put.ratio = 1
    leg_short_put.action = "SELL"
    leg_short_put.exchange = short_put_contract.exchange

    # Long Put (BUY)
    leg_long_put = ComboLeg()
    leg_long_put.conId = long_put_conid
    leg_long_put.ratio = 1
    leg_long_put.action = "BUY"
    leg_long_put.exchange = long_put_contract.exchange

    combo.comboLegs = [leg_short_call, leg_long_call, leg_short_put, leg_long_put]
    return combo
