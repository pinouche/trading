"""Pydantic-based data models to be used in the app"""

from dotenv import dotenv_values
from pydantic import BaseModel

env_vars = dotenv_values(".env")


class StockInfo(BaseModel):
    """Stock card with defined attributes"""

    price: list[list] = []
    market_is_live: bool = False
