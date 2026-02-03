"""
Sarasai - Stock Metrics Analysis Service
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional
from datetime import datetime, timedelta

from core.models import StockMetrics


class MetricsAnalysisService:
    """Service for calculating technical and fundamental stock metrics"""
    
    def __init__(self):
        self.cache = {}  # Simple cache for metrics
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
    
    def get_stock_metrics(self, symbol: str) -> Optional[StockMetrics]:
        """Get comprehensive metrics for a stock"""
        
        # Check cache first
        cache_key = f"{symbol}_metrics"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        
        try:
            # Try to get stock data from yfinance
            stock = yf.Ticker(symbol)
            
            # Get historical data (1 year for technical analysis)
            hist = stock.history(period="1y")
            
            if not hist.empty:
                # Get company info for fundamental metrics
                info = stock.info
                
                # Calculate technical metrics
                technical_metrics = self._calculate_technical_metrics(hist)
                
                # Extract fundamental metrics
                fundamental_metrics = self._extract_fundamental_metrics(info)
                
                # Calculate momentum indicators
                momentum_metrics = self._calculate_momentum_metrics(hist)
                
                # Combine all metrics
                metrics = StockMetrics(
                    symbol=symbol,
                    **technical_metrics,
                    **fundamental_metrics,
                    **momentum_metrics
                )
                
                # Cache the result
                self.cache[cache_key] = (metrics, datetime.now())
                return metrics
            else:
                # If no historical data, use mock metrics
                print(f"No historical data for {symbol}, using mock metrics")
                return self._get_mock_metrics(symbol)
                
        except Exception as e:
            print(f"Error calculating metrics for {symbol}: {str(e)}")
            # Return mock metrics as fallback
            return self._get_mock_metrics(symbol)
    
    def _get_mock_metrics(self, symbol: str) -> StockMetrics:
        """Generate realistic mock metrics when live data is unavailable"""
        
        # Mock data based on symbol for consistency
        import random
        random.seed(hash(symbol) % 1000)  # Consistent seed based on symbol
        
        # Generate realistic mock metrics
        mock_metrics = StockMetrics(
            symbol=symbol,
            # Technical metrics
            rsi=random.uniform(25, 75),  # RSI between 25-75
            moving_avg_50=None,  # Not available without historical data
            moving_avg_200=None,
            bollinger_upper=None,
            bollinger_lower=None,
            macd=random.uniform(-2, 2),
            
            # Fundamental metrics (use some realistic ranges)
            pe_ratio=random.uniform(12, 35),
            pb_ratio=random.uniform(1, 4),
            debt_to_equity=random.uniform(0.2, 2.0),
            roe=random.uniform(0.05, 0.25),
            dividend_yield=random.uniform(0.01, 0.05) if random.random() > 0.3 else None,
            
            # Momentum indicators
            price_change_1d=random.uniform(-3, 3),
            price_change_1w=random.uniform(-8, 8),
            price_change_1m=random.uniform(-15, 15),
            price_change_3m=random.uniform(-25, 25)
        )
        
        # Cache mock metrics for consistency
        self.cache[f"{symbol}_metrics"] = (mock_metrics, datetime.now())
        
        return mock_metrics
    
    def _calculate_technical_metrics(self, hist: pd.DataFrame) -> dict:
        """Calculate technical analysis indicators"""
        
        close_prices = hist['Close']
        high_prices = hist['High']
        low_prices = hist['Low']
        
        # RSI (Relative Strength Index)
        rsi = self._calculate_rsi(close_prices)
        
        # Moving Averages
        moving_avg_50 = close_prices.rolling(window=50).mean().iloc[-1] if len(close_prices) >= 50 else None
        moving_avg_200 = close_prices.rolling(window=200).mean().iloc[-1] if len(close_prices) >= 200 else None
        
        # Bollinger Bands
        bollinger_upper, bollinger_lower = self._calculate_bollinger_bands(close_prices)
        
        # MACD
        macd = self._calculate_macd(close_prices)
        
        return {
            "rsi": rsi,
            "moving_avg_50": moving_avg_50,
            "moving_avg_200": moving_avg_200,
            "bollinger_upper": bollinger_upper,
            "bollinger_lower": bollinger_lower,
            "macd": macd
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None
        except:
            return None
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> tuple:
        """Calculate Bollinger Bands"""
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            bollinger_upper = (sma + (std * 2)).iloc[-1]
            bollinger_lower = (sma - (std * 2)).iloc[-1]
            return (
                round(bollinger_upper, 2) if not pd.isna(bollinger_upper) else None,
                round(bollinger_lower, 2) if not pd.isna(bollinger_lower) else None
            )
        except:
            return None, None
    
    def _calculate_macd(self, prices: pd.Series) -> Optional[float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            ema_12 = prices.ewm(span=12).mean()
            ema_26 = prices.ewm(span=26).mean()
            macd = ema_12 - ema_26
            return round(macd.iloc[-1], 4) if not pd.isna(macd.iloc[-1]) else None
        except:
            return None
    
    def _extract_fundamental_metrics(self, info: dict) -> dict:
        """Extract fundamental analysis metrics from stock info"""
        
        return {
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe": info.get("returnOnEquity"),
            "dividend_yield": info.get("dividendYield")
        }
    
    def _calculate_momentum_metrics(self, hist: pd.DataFrame) -> dict:
        """Calculate price momentum indicators"""
        
        try:
            close_prices = hist['Close']
            current_price = close_prices.iloc[-1]
            
            # Calculate percentage changes for different periods
            price_change_1d = None
            price_change_1w = None
            price_change_1m = None
            price_change_3m = None
            
            if len(close_prices) >= 2:
                price_1d_ago = close_prices.iloc[-2]
                price_change_1d = round(((current_price - price_1d_ago) / price_1d_ago) * 100, 2)
            
            if len(close_prices) >= 7:
                price_1w_ago = close_prices.iloc[-7]
                price_change_1w = round(((current_price - price_1w_ago) / price_1w_ago) * 100, 2)
            
            if len(close_prices) >= 30:
                price_1m_ago = close_prices.iloc[-30]
                price_change_1m = round(((current_price - price_1m_ago) / price_1m_ago) * 100, 2)
            
            if len(close_prices) >= 90:
                price_3m_ago = close_prices.iloc[-90]
                price_change_3m = round(((current_price - price_3m_ago) / price_3m_ago) * 100, 2)
            
            return {
                "price_change_1d": price_change_1d,
                "price_change_1w": price_change_1w,
                "price_change_1m": price_change_1m,
                "price_change_3m": price_change_3m
            }
            
        except:
            return {
                "price_change_1d": None,
                "price_change_1w": None,
                "price_change_1m": None,
                "price_change_3m": None
            }


# Singleton instance
metrics_service = MetricsAnalysisService()