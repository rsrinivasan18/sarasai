"""
Sarasai - Business Logic Services
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import pandas as pd
from datetime import datetime
from typing import List
from fastapi import HTTPException

from core.models import StockData, StockListItem
from config.settings import settings


class StockService:
    """Service for stock data operations"""

    def __init__(self):
        """Load stock data from CSV"""
        self.stocks_df = pd.read_csv(settings.MOCK_DATA_FILE)
        self.stocks_df.set_index("symbol", inplace=True)

    def get_stock(self, symbol: str) -> StockData:
        """
        Get stock data by symbol

        Args:
            symbol: Stock symbol (e.g., AAPL, RELIANCE.NS)

        Returns:
            StockData object

        Raises:
            HTTPException: If symbol not found
        """
        symbol_upper = symbol.upper()

        if symbol_upper not in self.stocks_df.index:
            available = ", ".join(self.stocks_df.index.tolist())
            raise HTTPException(
                status_code=404,
                detail=f"Stock '{symbol}' not found. Available: {available}",
            )

        stock = self.stocks_df.loc[symbol_upper]

        return StockData(
            symbol=symbol_upper,
            name=stock["name"],
            current_price=float(stock["current_price"]),
            market_cap=float(stock["market_cap"]),
            pe_ratio=float(stock["pe_ratio"]) if pd.notna(stock["pe_ratio"]) else None,
            day_high=float(stock["day_high"]),
            day_low=float(stock["day_low"]),
            volume=int(stock["volume"]),
            currency=stock["currency"],
            exchange=stock["exchange"],
            data_source=f"{settings.DATA_SOURCE} (CSV)",
            timestamp=datetime.now().isoformat(),
        )

    def list_stocks(self) -> List[StockListItem]:
        """
        Get list of all available stocks

        Returns:
            List of StockListItem objects
        """
        stocks_list = []
        for symbol, row in self.stocks_df.iterrows():
            stocks_list.append(
                StockListItem(
                    symbol=symbol,
                    name=row["name"],
                    price=float(row["current_price"]),
                    currency=row["currency"],
                    exchange=row["exchange"],
                )
            )
        return stocks_list

    def get_available_symbols(self) -> List[str]:
        """Get list of available stock symbols"""
        return self.stocks_df.index.tolist()

    def get_stock_count(self) -> int:
        """Get total number of stocks"""
        return len(self.stocks_df)


# Create singleton instance - THIS LINE IS CRITICAL!
stock_service = StockService()
