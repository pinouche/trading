"""utility functions used throughout the project."""

from datetime import datetime, timedelta

import yaml

from trading.core.data_models.data_models import ConfigModel


def config_load(file_path: str) -> ConfigModel:
    """load config file into pydantic object"""
    with open(file_path) as file:
        config_data = yaml.safe_load(file)

    return ConfigModel(**config_data)


def get_next_friday() -> str:
    """Get the next Friday."""
    today = datetime.today()
    days_ahead = 4 - today.weekday()  # 4 is the index for Friday
    if days_ahead < 0:
        days_ahead += 7
    next_friday = today + timedelta(days=days_ahead)
    return next_friday.strftime("%Y%m%d")
