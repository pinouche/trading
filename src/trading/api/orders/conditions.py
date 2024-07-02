"""Create conditions for conditional orders"""

from ibapi.order_condition import (
    Create,
    ExecutionCondition,
    MarginCondition,
    OrderCondition,
    PercentChangeCondition,
    PriceCondition,
    TimeCondition,
    VolumeCondition,
)


def create_price_condition() -> PriceCondition:
    """Create condition."""
    price_condition = Create(OrderCondition.Price)
    return price_condition


def create_volume_condition() -> VolumeCondition:
    """Create condition."""
    volume_condition = Create(OrderCondition.Volume)
    return volume_condition


def create_time_condition() -> TimeCondition:
    """Create condition."""
    time_condition = Create(OrderCondition.Time)
    return time_condition


def create_percentchange_condition() -> PercentChangeCondition:
    """Create condition."""
    percentchange_condition = Create(OrderCondition.PercentChange)
    return percentchange_condition


def create_margin_condition() -> MarginCondition:
    """Create condition."""
    margin_condition = Create(OrderCondition.Margin)
    return margin_condition


def create_execution_condition() -> ExecutionCondition:
    """Create condition."""
    execution_condition = Create(OrderCondition.Execution)
    return execution_condition
