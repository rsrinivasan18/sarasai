"""
Sarasai - Business Logic Services
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import pandas as pd
from datetime import datetime
from typing import List
from fastapi import HTTPException

from core.models import StockData, StockListItem
from core.data_sources import alpha_vantage
from config.settings import settings


class StockService:
    """Service for stock data operations - Hybrid mode (Live + CSV fallback)"""

    def __init__(self):
        """Load mock data as fallback"""
        self.stocks_df = pd.read_csv(settings.MOCK_DATA_FILE)
        self.stocks_df.set_index("symbol", inplace=True)
        self.use_live_data = settings.DATA_SOURCE == "live"

    def get_stock(self, symbol: str) -> StockData:
        """
        Get stock data by symbol - tries live API first, falls back to CSV

        Args:
            symbol: Stock symbol (e.g., AAPL, RELIANCE.NS)

        Returns:
            StockData object

        Raises:
            HTTPException: If symbol not found
        """
        symbol_upper = symbol.upper()

        # Try live data first if enabled
        if self.use_live_data:
            live_data = self._get_live_stock(symbol_upper)
            if live_data:
                return live_data
            # If live fails, fall back to CSV
            print(f"Live data failed for {symbol_upper}, using CSV fallback")

        # CSV fallback
        return self._get_csv_stock(symbol_upper)

    def _get_live_stock(self, symbol: str) -> StockData:
        """Fetch from Alpha Vantage API"""
        try:
            # Get quote data
            quote = alpha_vantage.get_quote(symbol)
            if not quote:
                return None

            # Get company overview (for name, market cap, etc.)
            overview = alpha_vantage.get_company_overview(symbol)

            # Use overview if available, otherwise use defaults
            if overview:
                name = overview.get("name", "Unknown Company")
                market_cap = overview.get("market_cap", 0)
                pe_ratio = overview.get("pe_ratio")
                currency = overview.get("currency", "USD")
                exchange = overview.get("exchange", "Unknown")
            else:
                name = "Unknown Company"
                market_cap = 0
                pe_ratio = None
                currency = "USD"
                exchange = "Unknown"

            return StockData(
                symbol=symbol,
                name=name,
                current_price=quote["price"],
                market_cap=market_cap,
                pe_ratio=pe_ratio,
                day_high=quote["price"] * 1.02,  # Approximate
                day_low=quote["price"] * 0.98,  # Approximate
                volume=quote["volume"],
                currency=currency,
                exchange=exchange,
                data_source="live (Alpha Vantage)",
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            print(f"Live API error: {str(e)}")
            return None

    def _get_csv_stock(self, symbol: str) -> StockData:
        """Fetch from CSV fallback"""
        if symbol not in self.stocks_df.index:
            available = ", ".join(self.stocks_df.index.tolist())
            raise HTTPException(
                status_code=404,
                detail=f"Stock '{symbol}' not found. Available in CSV: {available}",
            )

        stock = self.stocks_df.loc[symbol]

        return StockData(
            symbol=symbol,
            name=stock["name"],
            current_price=float(stock["current_price"]),
            market_cap=float(stock["market_cap"]),
            pe_ratio=float(stock["pe_ratio"]) if pd.notna(stock["pe_ratio"]) else None,
            day_high=float(stock["day_high"]),
            day_low=float(stock["day_low"]),
            volume=int(stock["volume"]),
            currency=stock["currency"],
            exchange=stock["exchange"],
            data_source="CSV fallback",
            timestamp=datetime.now().isoformat(),
        )

    def list_stocks(self) -> List[StockListItem]:
        """Get list of all available stocks from CSV"""
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


# Singleton instance
stock_service = StockService()
