"""Option chains data model."""

from typing import List
from pydantic import BaseModel


class OptionsChain(BaseModel):
    exchange: str
    underlyingConId: int
    tradingClass: str
    multiplier: int
    expirations: List[str]
    strikes: List[float]