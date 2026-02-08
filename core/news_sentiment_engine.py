"""
Real-time News Integration and Sentiment Analysis Engine
Provides news-based insights for investment decisions
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import random
import re

from .config_service import config_service


@dataclass
class NewsItem:
    """Individual news article data"""
    title: str
    summary: str
    source: str
    published_at: datetime
    sentiment_score: float  # -1 (negative) to 1 (positive)
    relevance_score: float  # 0 to 1
    url: Optional[str] = None
    categories: List[str] = None


@dataclass
class StockNewsAnalysis:
    """News analysis for a specific stock"""
    symbol: str
    overall_sentiment: float
    news_count: int
    positive_news_count: int
    negative_news_count: int
    recent_headlines: List[str]
    key_themes: List[str]
    sentiment_trend: str  # "improving", "declining", "stable"
    impact_score: float  # 0-100, higher = more likely to affect stock price


class NewsConfig:
    """News source configuration"""
    
    def __init__(self):
        self.config = config_service.load_config("news")
        
    def get_sources(self) -> List[str]:
        return self.config.get("sources", ["reuters", "bloomberg", "cnbc", "financial_times"])
    
    def get_keywords_for_symbol(self, symbol: str) -> List[str]:
        """Get search keywords for a specific stock symbol"""
        symbol_keywords = self.config.get("symbol_keywords", {})
        
        # Default keywords based on symbol
        default_keywords = [symbol.replace(".SI", "").replace(".NS", "")]
        
        return symbol_keywords.get(symbol, default_keywords)


class MockNewsProvider:
    """Mock news provider for development and testing"""
    
    def __init__(self):
        self.config = NewsConfig()
        self._load_mock_data()
    
    def _load_mock_data(self):
        """Load mock news data for testing"""
        self.mock_news = {
            "AAPL": [
                {
                    "title": "Apple Reports Strong Q4 Earnings Beat Expectations",
                    "summary": "Apple Inc. reported quarterly earnings that exceeded analyst expectations, driven by strong iPhone sales and services revenue growth.",
                    "sentiment": 0.7,
                    "source": "Reuters",
                    "categories": ["earnings", "technology"]
                },
                {
                    "title": "Apple Faces Regulatory Challenges in EU Markets", 
                    "summary": "European regulators are investigating Apple's App Store policies, potentially leading to significant changes in business model.",
                    "sentiment": -0.4,
                    "source": "Financial Times",
                    "categories": ["regulation", "legal"]
                },
                {
                    "title": "Apple's AI Strategy Gains Momentum with New Features",
                    "summary": "Apple's latest AI integration across devices shows promising adoption rates and positive user feedback.",
                    "sentiment": 0.5,
                    "source": "Bloomberg",
                    "categories": ["technology", "ai", "innovation"]
                }
            ],
            "DBS.SI": [
                {
                    "title": "DBS Bank Reports Record Quarterly Profits",
                    "summary": "DBS Group Holdings announced record quarterly profits, benefiting from rising interest rates and strong loan growth in Southeast Asia.",
                    "sentiment": 0.8,
                    "source": "Straits Times",
                    "categories": ["earnings", "banking"]
                },
                {
                    "title": "DBS Expands Digital Banking Services Across ASEAN",
                    "summary": "DBS continues its digital transformation with new mobile banking features and expanded services across Southeast Asian markets.",
                    "sentiment": 0.6,
                    "source": "Business Times",
                    "categories": ["digital", "expansion"]
                }
            ],
            "RELIANCE.NS": [
                {
                    "title": "Reliance Industries Announces Major Green Energy Investment",
                    "summary": "Reliance Industries plans massive investment in renewable energy projects, targeting carbon neutrality by 2035.",
                    "sentiment": 0.7,
                    "source": "Economic Times",
                    "categories": ["energy", "sustainability", "investment"]
                },
                {
                    "title": "Jio 5G Network Rollout Accelerates Across India",
                    "summary": "Reliance Jio's 5G network expansion continues at rapid pace, covering major cities and driving subscriber growth.",
                    "sentiment": 0.5,
                    "source": "Hindu Business Line",
                    "categories": ["telecom", "technology", "expansion"]
                }
            ],
            "TSLA": [
                {
                    "title": "Tesla Deliveries Exceed Expectations for Q4",
                    "summary": "Tesla delivered more vehicles than expected in Q4, driven by strong Model Y demand and improved production efficiency.",
                    "sentiment": 0.6,
                    "source": "CNBC",
                    "categories": ["deliveries", "automotive"]
                }
            ]
        }
    
    def get_stock_news(self, symbol: str, days: int = 7) -> List[NewsItem]:
        """Get recent news for a specific stock"""
        symbol_news = self.mock_news.get(symbol, [])
        news_items = []
        
        for i, news_data in enumerate(symbol_news):
            # Generate recent dates
            published_at = datetime.now() - timedelta(days=random.randint(0, days))
            
            news_item = NewsItem(
                title=news_data["title"],
                summary=news_data["summary"],
                source=news_data["source"],
                published_at=published_at,
                sentiment_score=news_data["sentiment"],
                relevance_score=random.uniform(0.7, 1.0),
                categories=news_data.get("categories", []),
                url=f"https://example.com/news/{symbol.lower()}-{i+1}"
            )
            news_items.append(news_item)
        
        return sorted(news_items, key=lambda x: x.published_at, reverse=True)
    
    def get_market_news(self, market: str = "global", days: int = 7) -> List[NewsItem]:
        """Get general market news"""
        market_news = [
            {
                "title": "Global Markets Show Mixed Signals Amid Economic Data",
                "summary": "International markets react to latest economic indicators with cautious optimism despite inflation concerns.",
                "sentiment": 0.2,
                "source": "Reuters",
                "categories": ["markets", "global"]
            },
            {
                "title": "Central Banks Signal Potential Policy Changes",
                "summary": "Major central banks hint at possible monetary policy adjustments in response to evolving economic conditions.",
                "sentiment": -0.1,
                "source": "Bloomberg",
                "categories": ["monetary_policy", "central_banks"]
            },
            {
                "title": "Tech Sector Resilience Continues Despite Headwinds",
                "summary": "Technology companies demonstrate strong fundamentals and adaptability in challenging market conditions.",
                "sentiment": 0.4,
                "source": "Financial Times",
                "categories": ["technology", "sectors"]
            }
        ]
        
        news_items = []
        for i, news_data in enumerate(market_news):
            published_at = datetime.now() - timedelta(days=random.randint(0, days))
            
            news_item = NewsItem(
                title=news_data["title"],
                summary=news_data["summary"],
                source=news_data["source"],
                published_at=published_at,
                sentiment_score=news_data["sentiment"],
                relevance_score=random.uniform(0.6, 0.9),
                categories=news_data.get("categories", [])
            )
            news_items.append(news_item)
        
        return sorted(news_items, key=lambda x: x.published_at, reverse=True)


class SentimentAnalyzer:
    """Sentiment analysis engine for news content"""
    
    def __init__(self):
        self.positive_keywords = [
            "strong", "growth", "beat", "exceeds", "record", "profit", "gain", 
            "positive", "optimistic", "bullish", "upgrade", "expansion", "success",
            "robust", "solid", "impressive", "outperform", "momentum"
        ]
        
        self.negative_keywords = [
            "decline", "loss", "weak", "miss", "falls", "drops", "concern",
            "negative", "bearish", "downgrade", "risk", "challenge", "pressure",
            "struggles", "disappoints", "uncertainty", "volatility", "warns"
        ]
    
    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text content (-1 to 1)"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        # Calculate sentiment score
        sentiment_raw = (positive_count - negative_count) / max(total_words / 10, 1)
        
        # Normalize to -1 to 1 range
        return max(-1.0, min(1.0, sentiment_raw))
    
    def extract_key_themes(self, news_items: List[NewsItem]) -> List[str]:
        """Extract key themes from multiple news items"""
        all_categories = []
        for item in news_items:
            if item.categories:
                all_categories.extend(item.categories)
        
        # Count category frequency
        category_counts = {}
        for category in all_categories:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        # Return most common themes
        sorted_themes = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        return [theme[0] for theme in sorted_themes[:5]]


class NewsIntelligenceEngine:
    """Main news intelligence engine"""
    
    def __init__(self):
        self.news_provider = MockNewsProvider()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def analyze_stock_news(self, symbol: str, days: int = 7) -> StockNewsAnalysis:
        """Comprehensive news analysis for a stock"""
        news_items = self.news_provider.get_stock_news(symbol, days)
        
        if not news_items:
            return self._create_default_analysis(symbol)
        
        # Calculate sentiment metrics
        sentiments = [item.sentiment_score for item in news_items]
        overall_sentiment = sum(sentiments) / len(sentiments)
        
        positive_count = sum(1 for s in sentiments if s > 0.1)
        negative_count = sum(1 for s in sentiments if s < -0.1)
        
        # Extract recent headlines
        recent_headlines = [item.title for item in news_items[:5]]
        
        # Extract key themes
        key_themes = self.sentiment_analyzer.extract_key_themes(news_items)
        
        # Determine sentiment trend
        sentiment_trend = self._calculate_sentiment_trend(news_items)
        
        # Calculate impact score
        impact_score = self._calculate_impact_score(news_items, overall_sentiment)
        
        return StockNewsAnalysis(
            symbol=symbol,
            overall_sentiment=round(overall_sentiment, 3),
            news_count=len(news_items),
            positive_news_count=positive_count,
            negative_news_count=negative_count,
            recent_headlines=recent_headlines,
            key_themes=key_themes,
            sentiment_trend=sentiment_trend,
            impact_score=round(impact_score, 1)
        )
    
    def _create_default_analysis(self, symbol: str) -> StockNewsAnalysis:
        """Create default analysis when no news is available"""
        return StockNewsAnalysis(
            symbol=symbol,
            overall_sentiment=0.0,
            news_count=0,
            positive_news_count=0,
            negative_news_count=0,
            recent_headlines=["No recent news available"],
            key_themes=["general"],
            sentiment_trend="stable",
            impact_score=50.0
        )
    
    def _calculate_sentiment_trend(self, news_items: List[NewsItem]) -> str:
        """Calculate sentiment trend over time"""
        if len(news_items) < 2:
            return "stable"
        
        # Sort by date and compare recent vs older sentiment
        sorted_news = sorted(news_items, key=lambda x: x.published_at)
        
        recent_sentiment = sum(item.sentiment_score for item in sorted_news[-3:]) / min(3, len(sorted_news))
        older_sentiment = sum(item.sentiment_score for item in sorted_news[:-3]) / max(1, len(sorted_news) - 3)
        
        diff = recent_sentiment - older_sentiment
        
        if diff > 0.1:
            return "improving"
        elif diff < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_impact_score(self, news_items: List[NewsItem], overall_sentiment: float) -> float:
        """Calculate potential market impact score"""
        if not news_items:
            return 50.0
        
        # Base score from sentiment magnitude
        sentiment_impact = abs(overall_sentiment) * 30
        
        # Volume of news impact
        volume_impact = min(len(news_items) * 5, 25)
        
        # Recency impact
        recent_news_count = sum(1 for item in news_items 
                               if (datetime.now() - item.published_at).days <= 2)
        recency_impact = recent_news_count * 10
        
        # Source credibility (mock implementation)
        credibility_impact = 15
        
        total_impact = 50 + sentiment_impact + volume_impact + recency_impact + credibility_impact
        
        return min(100, max(0, total_impact))
    
    def get_portfolio_news_summary(self, symbols: List[str]) -> Dict[str, Any]:
        """Get news summary for entire portfolio"""
        portfolio_analysis = {}
        overall_sentiment = 0.0
        total_impact = 0.0
        
        for symbol in symbols:
            analysis = self.analyze_stock_news(symbol)
            portfolio_analysis[symbol] = {
                "sentiment": analysis.overall_sentiment,
                "news_count": analysis.news_count,
                "sentiment_trend": analysis.sentiment_trend,
                "impact_score": analysis.impact_score,
                "top_headline": analysis.recent_headlines[0] if analysis.recent_headlines else None
            }
            
            overall_sentiment += analysis.overall_sentiment
            total_impact += analysis.impact_score
        
        # Calculate portfolio-level metrics
        avg_sentiment = overall_sentiment / len(symbols) if symbols else 0.0
        avg_impact = total_impact / len(symbols) if symbols else 0.0
        
        return {
            "portfolio_sentiment": round(avg_sentiment, 3),
            "average_impact_score": round(avg_impact, 1),
            "stocks_with_positive_news": sum(1 for s in symbols 
                                           if portfolio_analysis[s]["sentiment"] > 0.1),
            "stocks_with_negative_news": sum(1 for s in symbols 
                                           if portfolio_analysis[s]["sentiment"] < -0.1),
            "individual_stocks": portfolio_analysis,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_market_sentiment(self, market: str = "global") -> Dict[str, Any]:
        """Get overall market sentiment from news"""
        market_news = self.news_provider.get_market_news(market)
        
        if not market_news:
            return {"sentiment": 0.0, "news_count": 0, "key_themes": ["general"]}
        
        overall_sentiment = sum(item.sentiment_score for item in market_news) / len(market_news)
        key_themes = self.sentiment_analyzer.extract_key_themes(market_news)
        
        return {
            "market": market,
            "overall_sentiment": round(overall_sentiment, 3),
            "news_count": len(market_news),
            "key_themes": key_themes,
            "recent_headlines": [item.title for item in market_news[:3]],
            "last_updated": datetime.now().isoformat()
        }


# Global news intelligence engine instance
news_engine = NewsIntelligenceEngine()