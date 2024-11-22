"""Pydantic-based data models to be used in the app"""

from typing import Annotated

from pydantic import BaseModel, Field


class ClientModel(BaseModel):
    """IBapi TWS client variables"""

    ip_address: str
    port: int
    client_id: int


class ConfigModel(BaseModel):
    """Config file model"""

    client_config: ClientModel
    stocks: list[str]
    wsb_to_include: list[str]
    wsb_to_exclude: list[str]
    green_color: str
    cash_to_trade: Annotated[float, Field(gt=0)]  # float, needs to be bigger then 0
    number_of_options: Annotated[
        int, Field(ge=0)
    ]  # int, needs to be bigger or equal to 1
    start_time_after_nine: Annotated[
        int, Field(ge=0)
    ]  # int, needs to be bigger or equal to 0
    minimum_volatility: str
    buffer_allowed_pennies: float
    waiting_time_to_readjust_order: int
    use_wsb: bool
    scraping_wsb: bool


class StockInfo(BaseModel):
    """Stock card with defined attributes"""

    price: list[list] = []
    market_is_live: bool = False
