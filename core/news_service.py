"""
Sarasai - News Sentiment Analysis Service
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from typing import List, Optional
from datetime import datetime, timedelta
import yfinance as yf

from core.models import NewsItem


class NewsService:
    """Service for fetching and analyzing stock-related news sentiment"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=2)  # Cache news for 2 hours
    
    def get_stock_news(self, symbol: str, limit: int = 5) -> List[NewsItem]:
        """Get recent news for a stock with sentiment analysis"""
        
        # Check cache first
        cache_key = f"{symbol}_news"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data[:limit]
        
        try:
            # Try to get news from yfinance first
            news_items = self._get_yfinance_news(symbol)
            
            # If no news from yfinance, try alternative sources
            if not news_items:
                news_items = self._get_alternative_news(symbol)
            
            # Cache the results
            if news_items:
                self.cache[cache_key] = (news_items, datetime.now())
            
            return news_items[:limit]
            
        except Exception as e:
            print(f"Error fetching news for {symbol}: {str(e)}")
            return []
    
    def _get_yfinance_news(self, symbol: str) -> List[NewsItem]:
        """Fetch news from yfinance"""
        try:
            stock = yf.Ticker(symbol)
            news = stock.news
            
            news_items = []
            for article in news:
                # Analyze sentiment
                title = article.get('title', '')
                summary = article.get('summary', article.get('description', ''))
                
                sentiment_score, sentiment_label = self._analyze_sentiment(f"{title} {summary}")
                
                # Convert timestamp
                published_timestamp = article.get('providerPublishTime', 0)
                published_date = datetime.fromtimestamp(published_timestamp) if published_timestamp else datetime.now()
                
                news_item = NewsItem(
                    title=title,
                    summary=summary,
                    url=article.get('link', ''),
                    published_date=published_date,
                    sentiment_score=sentiment_score,
                    sentiment_label=sentiment_label,
                    source=article.get('publisher', 'Unknown')
                )
                news_items.append(news_item)
            
            return news_items
            
        except Exception as e:
            print(f"Error fetching yfinance news: {str(e)}")
            return []
    
    def _get_alternative_news(self, symbol: str) -> List[NewsItem]:
        """Fetch news from alternative sources (mock data for now)"""
        # In a real implementation, you would integrate with news APIs like:
        # - Alpha Vantage News API
        # - Financial Modeling Prep
        # - NewsAPI
        # - Google News RSS
        
        # For now, return mock news data
        mock_news = [
            {
                "title": f"{symbol} Shows Strong Performance in Latest Quarter",
                "summary": f"Recent financial results show {symbol} maintaining steady growth with positive outlook for next quarter.",
                "url": f"https://example.com/news/{symbol.lower()}-performance",
                "published_date": datetime.now() - timedelta(hours=2),
                "source": "Financial Times"
            },
            {
                "title": f"Analysts Upgrade {symbol} Rating",
                "summary": f"Leading analysts have upgraded their rating for {symbol} citing strong fundamentals and market position.",
                "url": f"https://example.com/news/{symbol.lower()}-upgrade",
                "published_date": datetime.now() - timedelta(hours=6),
                "source": "MarketWatch"
            },
            {
                "title": f"Market Volatility Impact on {symbol}",
                "summary": f"Analysis of how current market conditions are affecting {symbol} and similar stocks in the sector.",
                "url": f"https://example.com/news/{symbol.lower()}-volatility",
                "published_date": datetime.now() - timedelta(days=1),
                "source": "Bloomberg"
            }
        ]
        
        news_items = []
        for article in mock_news:
            sentiment_score, sentiment_label = self._analyze_sentiment(f"{article['title']} {article['summary']}")
            
            news_item = NewsItem(
                title=article['title'],
                summary=article['summary'],
                url=article['url'],
                published_date=article['published_date'],
                sentiment_score=sentiment_score,
                sentiment_label=sentiment_label,
                source=article['source']
            )
            news_items.append(news_item)
        
        return news_items
    
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity  # Returns -1 to 1
            
            # Categorize sentiment
            if sentiment_score > 0.1:
                sentiment_label = "positive"
            elif sentiment_score < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            return round(sentiment_score, 3), sentiment_label
            
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return 0.0, "neutral"
    
    def get_overall_sentiment(self, news_items: List[NewsItem]) -> tuple[float, str]:
        """Calculate overall sentiment from multiple news items"""
        if not news_items:
            return 0.0, "neutral"
        
        # Calculate weighted average (more recent news has higher weight)
        total_score = 0.0
        total_weight = 0.0
        now = datetime.now()
        
        for news in news_items:
            # Weight based on recency (newer = higher weight)
            hours_ago = (now - news.published_date).total_seconds() / 3600
            weight = max(1.0, 24.0 - hours_ago)  # News from last 24h gets higher weight
            
            total_score += news.sentiment_score * weight
            total_weight += weight
        
        avg_sentiment = total_score / total_weight if total_weight > 0 else 0.0
        
        # Categorize overall sentiment
        if avg_sentiment > 0.2:
            sentiment_label = "positive"
        elif avg_sentiment < -0.2:
            sentiment_label = "negative"
        else:
            sentiment_label = "neutral"
        
        return round(avg_sentiment, 3), sentiment_label


# Singleton instance
news_service = NewsService()