"""utility functions used throughout the project."""

from datetime import datetime, timedelta

import yaml  # type: ignore


def config_load(PATH: str) -> dict:
    """load config file into a dict"""
    with open(PATH) as f:
        return dict(yaml.safe_load(f))


def get_next_friday() -> str:
    """Get the next Friday."""
    today = datetime.today()
    days_ahead = 4 - today.weekday()  # 4 is the index for Friday
    if days_ahead <= 0:
        days_ahead += 7
    next_friday = today + timedelta(days=days_ahead)
    return next_friday.strftime("%Y%m%d")
