"""
Sarasai - Data Models
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


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


# Portfolio Models

class RecommendationAction(str, Enum):
    """Stock recommendation actions"""
    BUY = "buy"
    HOLD = "hold" 
    SELL = "sell"


class PortfolioHolding(BaseModel):
    """Individual portfolio holding"""
    
    symbol: str
    name: str
    quantity: int
    avg_purchase_price: float
    current_price: float
    total_invested: float
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    currency: str


class StockMetrics(BaseModel):
    """Technical and fundamental metrics for a stock"""
    
    symbol: str
    # Technical metrics
    rsi: Optional[float]
    moving_avg_50: Optional[float]
    moving_avg_200: Optional[float]
    bollinger_upper: Optional[float]
    bollinger_lower: Optional[float]
    macd: Optional[float]
    
    # Fundamental metrics  
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    debt_to_equity: Optional[float]
    roe: Optional[float]
    dividend_yield: Optional[float]
    
    # Momentum indicators
    price_change_1d: Optional[float]
    price_change_1w: Optional[float]
    price_change_1m: Optional[float]
    price_change_3m: Optional[float]


class NewsItem(BaseModel):
    """News article with sentiment"""
    
    title: str
    summary: str
    url: str
    published_date: datetime
    sentiment_score: float  # -1 to 1 (negative to positive)
    sentiment_label: str   # "positive", "neutral", "negative"
    source: str


class GuruRecommendation(BaseModel):
    """Recommendation from financial experts/analysts"""
    
    source: str
    analyst_name: str
    recommendation: RecommendationAction
    target_price: Optional[float]
    confidence_score: float  # 0-10
    reasoning: str
    date_published: datetime


class StockRecommendation(BaseModel):
    """Complete recommendation for a stock"""
    
    symbol: str
    name: str
    current_price: float
    recommendation: RecommendationAction
    confidence_score: float  # 0-10
    
    # Detailed reasoning
    reasoning_summary: str
    technical_analysis: str
    fundamental_analysis: str
    news_sentiment: str
    guru_consensus: str
    
    # Supporting data
    metrics: StockMetrics
    recent_news: List[NewsItem]
    guru_recommendations: List[GuruRecommendation]
    
    # Chart data for visualization
    chart_data: Optional[Dict]
    
    timestamp: datetime


class PortfolioAnalysis(BaseModel):
    """Complete portfolio analysis with recommendations"""
    
    total_invested: float
    current_value: float
    total_profit_loss: float
    total_profit_loss_percent: float
    
    holdings: List[PortfolioHolding]
    recommendations: List[StockRecommendation]
    
    # Portfolio level insights
    portfolio_risk_score: float  # 1-10 (low to high risk)
    diversification_score: float  # 1-10 (poor to well diversified)
    overall_sentiment: str
    
    analysis_timestamp: datetime


class PortfolioInput(BaseModel):
    """Input model for portfolio analysis"""
    
    holdings: List[Dict[str, Any]]  # [{"symbol": "AAPL", "quantity": 10, "avg_price": 150.0}, ...]
