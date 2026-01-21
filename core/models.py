"""
Sarasai - Data Models
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from pydantic import BaseModel
from typing import Optional, List


class StockData(BaseModel):
    """Stock data response model"""

    symbol: str
    name: str
    current_price: float
    market_cap: float
    pe_ratio: Optional[float]
    day_high: float
    day_low: float
    volume: int
    currency: str
    exchange: str
    data_source: str
    timestamp: str


class StockListItem(BaseModel):
    """Stock list item (summary)"""

    symbol: str
    name: str
    price: float
    currency: str
    exchange: str


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    data_source: str
    stocks_available: List[str]


class RootResponse(BaseModel):
    """Root endpoint response"""

    message: str
    status: str
    version: str
    data_mode: str
    available_stocks: int
    note: str
