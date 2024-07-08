"""Create conditions for conditional orders"""

from ibapi.contract import Contract
from ibapi.order_condition import Create, OrderCondition, PriceCondition


def create_price_condition(contract: Contract, isMore: bool, price_condition: float) -> PriceCondition:
    """Create price condition."""
    condition = Create(OrderCondition.Price)
    condition.conId = contract.conId
    condition.exchange = contract.exchange
    condition.isMore = isMore  # if True, the order is triggered when the price goes above our condition.price
    condition.triggerMethod = condition.TriggerMethodEnum.Last
    condition.price = price_condition

    return condition
