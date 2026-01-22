"""
Sarasai - Data Source Integrations
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import requests
from typing import Optional, Dict
from datetime import datetime

from config.settings import settings


class AlphaVantageAPI:
    """Alpha Vantage API client for real stock data"""

    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = settings.ALPHA_VANTAGE_BASE_URL

    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        Get real-time stock quote from Alpha Vantage

        Args:
            symbol: Stock symbol (e.g., AAPL, GOOGL)

        Returns:
            Dictionary with stock data or None if failed
        """
        try:
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": symbol,
                "apikey": self.api_key,
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check if we got valid data
            if "Global Quote" not in data or not data["Global Quote"]:
                return None

            quote = data["Global Quote"]

            # Transform to our format
            return {
                "symbol": quote.get("01. symbol", symbol).upper(),
                "price": float(quote.get("05. price", 0)),
                "volume": int(float(quote.get("06. volume", 0))),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "last_updated": quote.get(
                    "07. latest trading day", datetime.now().strftime("%Y-%m-%d")
                ),
            }

        except Exception as e:
            print(f"Alpha Vantage API Error for {symbol}: {str(e)}")
            return None

    def get_company_overview(self, symbol: str) -> Optional[Dict]:
        """
        Get company overview (name, market cap, etc.)

        Args:
            symbol: Stock symbol

        Returns:
            Dictionary with company data or None if failed
        """
        try:
            params = {"function": "OVERVIEW", "symbol": symbol, "apikey": self.api_key}

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data or "Symbol" not in data:
                return None

            return {
                "name": data.get("Name", "Unknown"),
                "exchange": data.get("Exchange", "Unknown"),
                "currency": data.get("Currency", "USD"),
                "market_cap": int(float(data.get("MarketCapitalization", 0))),
                "pe_ratio": float(data.get("PERatio", 0))
                if data.get("PERatio") and data.get("PERatio") != "None"
                else None,
            }

        except Exception as e:
            print(f"Alpha Vantage Overview Error for {symbol}: {str(e)}")
            return None


# Singleton instance
alpha_vantage = AlphaVantageAPI()
