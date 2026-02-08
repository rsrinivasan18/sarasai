"""
Advanced Portfolio Intelligence Engine
Provides buy/hold/sell recommendations based on multiple metrics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .enhanced_data_providers import MultiMarketDataProvider, PersistentPortfolioProvider
from .news_sentiment_engine import news_engine
from .expert_advisor_engine import expert_engine


def safe_float_convert(value, default=0.0):
    """Safely convert any numeric value to Python float"""
    if pd.isna(value):
        return default
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_str_convert(value, default="Unknown"):
    """Safely convert any value to Python string"""
    if pd.isna(value):
        return default
    return str(value)


class RecommendationType(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class StockMetrics:
    """Comprehensive stock metrics for analysis"""
    symbol: str
    current_price: float
    pe_ratio: float
    dividend_yield: float
    market_cap: float
    sector: str
    market: str
    currency: str
    
    # Technical indicators
    rsi: float = 50.0
    price_momentum: float = 0.0
    volatility: float = 0.0
    
    # Fundamental scores
    value_score: float = 50.0
    growth_score: float = 50.0
    quality_score: float = 50.0
    
    # Market sentiment
    analyst_rating: float = 3.0  # 1-5 scale
    news_sentiment: float = 0.0  # -1 to 1
    
    # Portfolio context
    current_allocation: float = 0.0
    recommended_allocation: float = 0.0


@dataclass
class PortfolioRecommendation:
    """Portfolio-level recommendation"""
    symbol: str
    name: str
    action: RecommendationType
    confidence: float
    target_price: Optional[float]
    reasoning: List[str]
    metrics: StockMetrics
    position_size: Optional[float] = None


class PortfolioIntelligenceEngine:
    """Advanced portfolio analytics and recommendation engine"""
    
    def __init__(self):
        self.market_provider = MultiMarketDataProvider()
        self.portfolio_provider = PersistentPortfolioProvider()
        
        # Scoring weights
        self.weights = {
            'technical': 0.25,
            'fundamental': 0.35,
            'sentiment': 0.20,
            'portfolio_fit': 0.20
        }
    
    def analyze_stock(self, symbol: str) -> StockMetrics:
        """Comprehensive stock analysis"""
        stock_data = self.market_provider.get_stock_price(symbol)
        if not stock_data:
            return None
            
        # Get stock universe data
        stock_universe = self.market_provider.stock_universe
        stock_row = stock_universe[stock_universe['symbol'] == symbol]
        
        if stock_row.empty:
            return None
            
        stock_info = stock_row.iloc[0]
        
        # Calculate technical indicators
        rsi = self._calculate_rsi(symbol)
        momentum = self._calculate_momentum(symbol)
        volatility = self._calculate_volatility(symbol)
        
        # Calculate fundamental scores
        value_score = self._calculate_value_score(stock_info)
        growth_score = self._calculate_growth_score(stock_info)
        quality_score = self._calculate_quality_score(stock_info)
        
        # Market sentiment
        analyst_rating = self._get_analyst_rating(stock_info)
        news_sentiment = self._get_news_sentiment(symbol)
        
        return StockMetrics(
            symbol=symbol,
            current_price=safe_float_convert(stock_data['price']),
            pe_ratio=safe_float_convert(stock_info.get('pe_ratio'), 20.0),
            dividend_yield=safe_float_convert(stock_info.get('dividend_yield'), 0.0),
            market_cap=safe_float_convert(stock_info.get('market_cap_millions'), 1000.0),
            sector=safe_str_convert(stock_info.get('sector'), 'Unknown'),
            market=safe_str_convert(stock_info.get('market'), 'Unknown'),
            currency=safe_str_convert(stock_info.get('currency'), 'USD'),
            rsi=safe_float_convert(rsi),
            price_momentum=safe_float_convert(momentum),
            volatility=safe_float_convert(volatility),
            value_score=safe_float_convert(value_score),
            growth_score=safe_float_convert(growth_score),
            quality_score=safe_float_convert(quality_score),
            analyst_rating=safe_float_convert(analyst_rating),
            news_sentiment=safe_float_convert(news_sentiment)
        )
    
    def _calculate_rsi(self, symbol: str) -> float:
        """Calculate RSI (mock implementation)"""
        # Mock RSI calculation - in real implementation, use price history
        import random
        return random.uniform(20, 80)
    
    def _calculate_momentum(self, symbol: str) -> float:
        """Calculate price momentum (mock implementation)"""
        import random
        return random.uniform(-15, 15)
    
    def _calculate_volatility(self, symbol: str) -> float:
        """Calculate volatility (mock implementation)"""
        import random
        return random.uniform(10, 40)
    
    def _calculate_value_score(self, stock_info) -> float:
        """Calculate value investment score (0-100)"""
        pe_ratio = safe_float_convert(stock_info.get('pe_ratio'), 20.0)
        dividend_yield = safe_float_convert(stock_info.get('dividend_yield'), 0.0)
        
        # Lower P/E and higher dividend yield = higher value score
        pe_score = max(0.0, 100.0 - (pe_ratio - 10.0) * 3.0)  # Optimal PE around 10-15
        dividend_score = min(100.0, dividend_yield * 20.0)  # Max at 5% dividend
        
        return (pe_score + dividend_score) / 2.0
    
    def _calculate_growth_score(self, stock_info) -> float:
        """Calculate growth investment score (0-100)"""
        sector = safe_str_convert(stock_info.get('sector'), '')
        market_cap = safe_float_convert(stock_info.get('market_cap_millions'), 1000.0)
        
        # Technology and healthcare sectors get growth bonus
        sector_bonus = 20.0 if sector in ['Technology', 'Healthcare'] else 0.0
        
        # Mid-cap stocks get growth bonus
        cap_bonus = 15.0 if 1000.0 <= market_cap <= 10000.0 else 0.0
        
        base_score = 50.0
        return min(100.0, base_score + sector_bonus + cap_bonus)
    
    def _calculate_quality_score(self, stock_info) -> float:
        """Calculate quality investment score (0-100)"""
        market_cap = safe_float_convert(stock_info.get('market_cap_millions'), 1000.0)
        dividend_yield = safe_float_convert(stock_info.get('dividend_yield'), 0.0)
        
        # Large cap stocks are typically higher quality
        cap_score = min(50.0, market_cap / 1000.0)  # Max 50 points
        
        # Consistent dividend payers are higher quality
        dividend_score = min(30.0, dividend_yield * 10.0)  # Max 30 points
        
        # Base quality score
        base_score = 20.0
        
        return cap_score + dividend_score + base_score
    
    def _get_analyst_rating(self, stock_info) -> float:
        """Get analyst rating using expert consensus"""
        try:
            symbol = safe_str_convert(stock_info.get('symbol'), '')
            if symbol:
                consensus = expert_engine.calculate_consensus(symbol)
                # Convert consensus action to 1-5 rating
                action_to_rating = {
                    'STRONG_SELL': 1.0,
                    'SELL': 2.0,
                    'HOLD': 3.0,
                    'BUY': 4.0,
                    'STRONG_BUY': 5.0
                }
                return action_to_rating.get(consensus.consensus_action.value, 3.0)
        except Exception as e:
            print(f"Error getting expert consensus for {stock_info.get('symbol', 'unknown')}: {e}")
            
        # Fallback to mock implementation
        sector = safe_str_convert(stock_info.get('sector'), '')
        market_cap = safe_float_convert(stock_info.get('market_cap_millions'), 1000.0)
        
        base_rating = 3.0
        
        # Tech stocks get slight bonus
        if sector == 'Technology':
            base_rating += 0.3
        
        # Large caps get stability bonus
        if market_cap > 10000.0:
            base_rating += 0.2
            
        return min(5.0, max(1.0, base_rating))
    
    def _get_news_sentiment(self, symbol: str) -> float:
        """Get news sentiment using real news analysis"""
        try:
            news_analysis = news_engine.analyze_stock_news(symbol, days=7)
            return news_analysis.overall_sentiment
        except Exception as e:
            print(f"Error getting news sentiment for {symbol}: {e}")
            return 0.0
    
    def generate_recommendations(self, user_id: str = "default_user") -> List[PortfolioRecommendation]:
        """Generate portfolio recommendations"""
        recommendations = []
        
        # Get current portfolio
        positions = self.portfolio_provider.get_positions(user_id)
        portfolio_summary = self.portfolio_provider.get_portfolio_summary(user_id)
        
        # Analyze current positions
        for position in positions:
            symbol = position['symbol']
            metrics = self.analyze_stock(symbol)
            
            if metrics:
                metrics.current_allocation = float(position['market_value']) / float(portfolio_summary['total_value_sgd']) * 100.0
                
                recommendation = self._generate_position_recommendation(position, metrics)
                recommendations.append(recommendation)
        
        # Find new opportunities
        new_opportunities = self._find_new_opportunities(portfolio_summary)
        recommendations.extend(new_opportunities)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x.confidence, reverse=True)
        
        return recommendations
    
    def _generate_position_recommendation(self, position: Dict, metrics: StockMetrics) -> PortfolioRecommendation:
        """Generate recommendation for existing position"""
        symbol = position['symbol']
        name = position.get('name', symbol)
        
        # Calculate composite score
        technical_score = self._calculate_technical_score(metrics)
        fundamental_score = self._calculate_fundamental_score(metrics)
        sentiment_score = self._calculate_sentiment_score(metrics)
        portfolio_score = self._calculate_portfolio_fit_score(metrics, position)
        
        composite_score = (
            technical_score * self.weights['technical'] +
            fundamental_score * self.weights['fundamental'] +
            sentiment_score * self.weights['sentiment'] +
            portfolio_score * self.weights['portfolio_fit']
        )
        
        # Determine action and reasoning
        action, reasoning, confidence = self._determine_action(composite_score, metrics, position)
        
        # Calculate target price
        target_price = self._calculate_target_price(metrics, action)
        
        return PortfolioRecommendation(
            symbol=symbol,
            name=name,
            action=action,
            confidence=confidence,
            target_price=target_price,
            reasoning=reasoning,
            metrics=metrics
        )
    
    def _calculate_technical_score(self, metrics: StockMetrics) -> float:
        """Calculate technical analysis score (0-100)"""
        rsi_score = 100.0 - abs(float(metrics.rsi) - 50.0) * 2.0  # Optimal RSI around 50
        momentum_score = max(0.0, 50.0 + float(metrics.price_momentum) * 2.0)
        volatility_score = max(0.0, 100.0 - float(metrics.volatility) * 2.0)
        
        return float((rsi_score + momentum_score + volatility_score) / 3.0)
    
    def _calculate_fundamental_score(self, metrics: StockMetrics) -> float:
        """Calculate fundamental analysis score (0-100)"""
        return float((float(metrics.value_score) + float(metrics.growth_score) + float(metrics.quality_score)) / 3.0)
    
    def _calculate_sentiment_score(self, metrics: StockMetrics) -> float:
        """Calculate sentiment score (0-100)"""
        analyst_score = float(metrics.analyst_rating) * 20.0  # Convert 1-5 to 0-100
        news_score = (float(metrics.news_sentiment) + 1.0) * 50.0  # Convert -1,1 to 0-100
        
        return float((analyst_score + news_score) / 2.0)
    
    def _calculate_portfolio_fit_score(self, metrics: StockMetrics, position: Dict) -> float:
        """Calculate how well stock fits in portfolio"""
        # Diversification score - penalize over-concentration
        concentration_penalty = max(0.0, float(metrics.current_allocation) - 20.0) * 2.0
        
        # Sector diversification
        sector_bonus = 10.0 if metrics.sector not in ['Financials'] else 0.0
        
        base_score = 70.0
        return float(max(0.0, base_score + sector_bonus - concentration_penalty))
    
    def _determine_action(self, composite_score: float, metrics: StockMetrics, 
                         position: Dict) -> Tuple[RecommendationType, List[str], float]:
        """Determine recommended action based on scores"""
        reasoning = []
        
        # Score-based action
        if composite_score >= 80:
            action = RecommendationType.STRONG_BUY
            reasoning.append(f"Excellent overall score ({composite_score:.1f}/100)")
        elif composite_score >= 65:
            action = RecommendationType.BUY
            reasoning.append(f"Good overall score ({composite_score:.1f}/100)")
        elif composite_score >= 45:
            action = RecommendationType.HOLD
            reasoning.append(f"Moderate score ({composite_score:.1f}/100)")
        elif composite_score >= 30:
            action = RecommendationType.SELL
            reasoning.append(f"Below average score ({composite_score:.1f}/100)")
        else:
            action = RecommendationType.STRONG_SELL
            reasoning.append(f"Poor overall score ({composite_score:.1f}/100)")
        
        # Add specific reasoning
        if metrics.pe_ratio > 30:
            reasoning.append(f"High P/E ratio ({metrics.pe_ratio:.1f}) indicates overvaluation")
        elif metrics.pe_ratio < 15:
            reasoning.append(f"Attractive P/E ratio ({metrics.pe_ratio:.1f})")
            
        if metrics.dividend_yield > 4:
            reasoning.append(f"Strong dividend yield ({metrics.dividend_yield:.1f}%)")
            
        if metrics.current_allocation > 25:
            reasoning.append(f"Over-concentrated position ({metrics.current_allocation:.1f}% of portfolio)")
        
        # Gain/loss consideration
        gain_loss_percent = position.get('gain_loss_percent', 0)
        if gain_loss_percent < -20:
            reasoning.append(f"Significant loss ({gain_loss_percent:.1f}%) - consider tax harvesting")
        elif gain_loss_percent > 30:
            reasoning.append(f"Strong gains ({gain_loss_percent:.1f}%) - consider profit taking")
        
        confidence = float(min(95.0, max(50.0, float(composite_score))))
        
        return action, reasoning, confidence
    
    def _calculate_target_price(self, metrics: StockMetrics, action: RecommendationType) -> Optional[float]:
        """Calculate target price based on analysis"""
        current_price = float(metrics.current_price)
        
        # Simple target price calculation
        if action in [RecommendationType.STRONG_BUY, RecommendationType.BUY]:
            return float(round(current_price * 1.15, 2))  # 15% upside
        elif action == RecommendationType.HOLD:
            return float(round(current_price * 1.05, 2))  # 5% upside
        elif action in [RecommendationType.SELL, RecommendationType.STRONG_SELL]:
            return float(round(current_price * 0.95, 2))  # 5% downside
            
        return None
    
    def _find_new_opportunities(self, portfolio_summary: Dict) -> List[PortfolioRecommendation]:
        """Find new investment opportunities"""
        opportunities = []
        
        # Get top stocks from each market for diversification
        markets = ['SGX', 'NASDAQ', 'NYSE', 'NSE']
        
        for market in markets:
            market_stocks = self.market_provider.get_stocks_by_market(market)
            
            # Analyze top 3 stocks from each market
            for stock in market_stocks[:3]:
                symbol = stock['symbol']
                metrics = self.analyze_stock(symbol)
                
                if metrics:
                    # Only recommend if score is high enough
                    fundamental_score = self._calculate_fundamental_score(metrics)
                    technical_score = self._calculate_technical_score(metrics)
                    
                    if fundamental_score > 70 and technical_score > 60:
                        reasoning = [
                            f"Strong fundamental score ({fundamental_score:.1f}/100)",
                            f"Good technical indicators ({technical_score:.1f}/100)",
                            f"Diversification opportunity in {metrics.market} market"
                        ]
                        
                        # Recommend 5-10% allocation for new positions
                        position_size = float(min(10.0, max(5.0, 100.0 / len(market_stocks))))
                        
                        opportunity = PortfolioRecommendation(
                            symbol=symbol,
                            name=stock.get('name', symbol),
                            action=RecommendationType.BUY,
                            confidence=float(min(85.0, (fundamental_score + technical_score) / 2.0)),
                            target_price=self._calculate_target_price(metrics, RecommendationType.BUY),
                            reasoning=reasoning,
                            metrics=metrics,
                            position_size=position_size
                        )
                        
                        opportunities.append(opportunity)
        
        # Return top 5 opportunities
        opportunities.sort(key=lambda x: x.confidence, reverse=True)
        return opportunities[:5]
    
    def get_portfolio_health_score(self, user_id: str = "default_user") -> Dict[str, Any]:
        """Calculate overall portfolio health metrics"""
        positions = self.portfolio_provider.get_positions(user_id)
        portfolio_summary = self.portfolio_provider.get_portfolio_summary(user_id)
        
        if not positions:
            return {"health_score": 0, "message": "No positions in portfolio"}
        
        # Diversification analysis
        sector_allocation = {}
        market_allocation = {}
        
        for position in positions:
            sector = position.get('sector', 'Unknown')
            market = position.get('market', 'Unknown')
            allocation = float(position['market_value']) / float(portfolio_summary['total_value_sgd']) * 100.0
            
            sector_allocation[sector] = float(sector_allocation.get(sector, 0.0)) + float(allocation)
            market_allocation[market] = float(market_allocation.get(market, 0.0)) + float(allocation)
        
        # Calculate diversification score
        diversification_score = self._calculate_diversification_score(sector_allocation, market_allocation)
        
        # Calculate performance score
        performance_score = min(100.0, max(0.0, 50.0 + float(portfolio_summary['total_gain_loss_percent']) * 2.0))
        
        # Calculate risk score
        risk_score = self._calculate_portfolio_risk_score(positions)
        
        # Overall health score
        health_score = float(diversification_score * 0.4 + performance_score * 0.4 + risk_score * 0.2)
        
        # Ensure all allocation values are Python floats
        sector_allocation_clean = {k: float(v) for k, v in sector_allocation.items()}
        market_allocation_clean = {k: float(v) for k, v in market_allocation.items()}
        
        return {
            "health_score": float(round(health_score, 1)),
            "performance_score": float(round(performance_score, 1)),
            "diversification_score": float(round(diversification_score, 1)),
            "risk_score": float(round(risk_score, 1)),
            "sector_allocation": sector_allocation_clean,
            "market_allocation": market_allocation_clean,
            "total_positions": int(len(positions)),
            "total_value": float(portfolio_summary['total_value_sgd']),
            "total_gain_loss_percent": float(portfolio_summary['total_gain_loss_percent'])
        }
    
    def _calculate_diversification_score(self, sector_allocation: Dict, market_allocation: Dict) -> float:
        """Calculate portfolio diversification score"""
        # Penalize concentration
        max_sector_allocation = max(sector_allocation.values()) if sector_allocation else 100.0
        max_market_allocation = max(market_allocation.values()) if market_allocation else 100.0
        
        sector_score = max(0.0, 100.0 - (float(max_sector_allocation) - 30.0) * 2.0)
        market_score = max(0.0, 100.0 - (float(max_market_allocation) - 40.0) * 2.0)
        
        return float((sector_score + market_score) / 2.0)
    
    def _calculate_portfolio_risk_score(self, positions: List[Dict]) -> float:
        """Calculate portfolio risk score"""
        # Simple risk calculation based on volatility and concentration
        if not positions:
            return 0.0
            
        total_risk = 0.0
        for position in positions:
            # Mock volatility calculation
            import random
            symbol_risk = random.uniform(15, 35)  # Mock volatility - using Python random
            total_value = sum(float(p.get('market_value', 0)) for p in positions)
            weight = float(position.get('market_value', 0)) / total_value if total_value > 0 else 0
            total_risk += symbol_risk * weight
        
        # Convert to 0-100 score (lower risk = higher score)
        risk_score = max(0.0, 100.0 - total_risk * 2.0)
        return float(risk_score)


# Global intelligence engine instance
intelligence_engine = PortfolioIntelligenceEngine()