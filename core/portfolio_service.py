"""
Sarasai - Portfolio Management and Recommendation Service
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import yfinance as yf

from core.models import (
    PortfolioHolding, PortfolioAnalysis, StockRecommendation, 
    RecommendationAction, PortfolioInput, StockMetrics
)
from core.services import stock_service
from core.metrics_service import metrics_service
from core.news_service import news_service
from core.guru_service import guru_service


class PortfolioService:
    """Main service for portfolio analysis and recommendations"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)  # Cache analysis for 30 minutes
    
    def analyze_portfolio(self, portfolio_input: PortfolioInput) -> PortfolioAnalysis:
        """Perform complete portfolio analysis with recommendations"""
        
        # Calculate portfolio holdings
        holdings = self._calculate_holdings(portfolio_input.holdings)
        
        # Generate recommendations for each stock
        recommendations = []
        for holding in holdings:
            recommendation = self._generate_stock_recommendation(holding.symbol)
            if recommendation:
                recommendations.append(recommendation)
        
        # Calculate portfolio-level metrics
        total_invested = sum(holding.total_invested for holding in holdings)
        current_value = sum(holding.current_value for holding in holdings)
        total_profit_loss = current_value - total_invested
        total_profit_loss_percent = (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Calculate portfolio risk and diversification scores
        portfolio_risk_score = self._calculate_portfolio_risk(holdings, recommendations)
        diversification_score = self._calculate_diversification_score(holdings)
        overall_sentiment = self._calculate_overall_sentiment(recommendations)
        
        return PortfolioAnalysis(
            total_invested=total_invested,
            current_value=current_value,
            total_profit_loss=total_profit_loss,
            total_profit_loss_percent=round(total_profit_loss_percent, 2),
            holdings=holdings,
            recommendations=recommendations,
            portfolio_risk_score=portfolio_risk_score,
            diversification_score=diversification_score,
            overall_sentiment=overall_sentiment,
            analysis_timestamp=datetime.now()
        )
    
    def _calculate_holdings(self, holdings_input: List[Dict]) -> List[PortfolioHolding]:
        """Calculate current portfolio holdings with profit/loss"""
        
        holdings = []
        for holding_data in holdings_input:
            try:
                symbol = holding_data["symbol"]
                quantity = holding_data["quantity"]
                avg_purchase_price = holding_data["avg_price"]
                
                # Get current stock data
                stock_data = stock_service.get_stock(symbol)
                current_price = stock_data.current_price
                
                # Calculate values
                total_invested = quantity * avg_purchase_price
                current_value = quantity * current_price
                profit_loss = current_value - total_invested
                profit_loss_percent = (profit_loss / total_invested * 100) if total_invested > 0 else 0
                
                holding = PortfolioHolding(
                    symbol=symbol,
                    name=stock_data.name,
                    quantity=quantity,
                    avg_purchase_price=avg_purchase_price,
                    current_price=current_price,
                    total_invested=total_invested,
                    current_value=current_value,
                    profit_loss=profit_loss,
                    profit_loss_percent=round(profit_loss_percent, 2),
                    currency=stock_data.currency
                )
                holdings.append(holding)
                
            except Exception as e:
                print(f"Error calculating holding for {holding_data}: {str(e)}")
                continue
        
        return holdings
    
    def _generate_stock_recommendation(self, symbol: str) -> Optional[StockRecommendation]:
        """Generate comprehensive recommendation for a single stock"""
        
        try:
            # Get current stock data
            stock_data = stock_service.get_stock(symbol)
            
            # Get technical and fundamental metrics
            metrics = metrics_service.get_stock_metrics(symbol)
            if not metrics:
                # Create empty metrics if none available
                metrics = StockMetrics(
                    symbol=symbol,
                    rsi=None, moving_avg_50=None, moving_avg_200=None,
                    bollinger_upper=None, bollinger_lower=None, macd=None,
                    pe_ratio=stock_data.pe_ratio, pb_ratio=None, debt_to_equity=None,
                    roe=None, dividend_yield=None,
                    price_change_1d=None, price_change_1w=None,
                    price_change_1m=None, price_change_3m=None
                )
            
            # Get news sentiment
            recent_news = news_service.get_stock_news(symbol, limit=5)
            news_sentiment_score, news_sentiment_label = news_service.get_overall_sentiment(recent_news)
            
            # Get guru recommendations
            guru_recommendations = guru_service.get_guru_recommendations(symbol, limit=5)
            guru_consensus, guru_confidence, guru_explanation = guru_service.get_consensus_recommendation(guru_recommendations)
            
            # Generate overall recommendation
            recommendation, confidence_score = self._calculate_recommendation(
                metrics, news_sentiment_score, guru_consensus, guru_confidence
            )
            
            # Generate detailed analyses
            technical_analysis = self._generate_technical_analysis(metrics)
            fundamental_analysis = self._generate_fundamental_analysis(metrics, stock_data)
            reasoning_summary = self._generate_reasoning_summary(
                recommendation, technical_analysis, fundamental_analysis, 
                news_sentiment_label, guru_explanation
            )
            
            # Generate chart data
            chart_data = self._generate_chart_data(symbol)
            
            return StockRecommendation(
                symbol=symbol,
                name=stock_data.name,
                current_price=stock_data.current_price,
                recommendation=recommendation,
                confidence_score=confidence_score,
                reasoning_summary=reasoning_summary,
                technical_analysis=technical_analysis,
                fundamental_analysis=fundamental_analysis,
                news_sentiment=f"Overall sentiment: {news_sentiment_label} (score: {news_sentiment_score})",
                guru_consensus=guru_explanation,
                metrics=metrics,
                recent_news=recent_news,
                guru_recommendations=guru_recommendations,
                chart_data=chart_data,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"Error generating recommendation for {symbol}: {str(e)}")
            return None
    
    def _calculate_recommendation(self, metrics: StockMetrics, news_sentiment: float, 
                                guru_consensus: RecommendationAction, guru_confidence: float) -> tuple[RecommendationAction, float]:
        """Calculate overall recommendation based on all factors"""
        
        # Initialize scores for each action
        buy_score = 0.0
        hold_score = 0.0
        sell_score = 0.0
        
        # Technical analysis scoring
        if metrics.rsi:
            if metrics.rsi < 30:  # Oversold - good buy signal
                buy_score += 2.0
            elif metrics.rsi > 70:  # Overbought - potential sell signal
                sell_score += 1.5
            else:
                hold_score += 1.0
        
        # Moving average analysis
        if metrics.moving_avg_50 and metrics.moving_avg_200:
            if metrics.moving_avg_50 > metrics.moving_avg_200:  # Golden cross
                buy_score += 1.5
            else:  # Death cross
                sell_score += 1.0
        
        # Price momentum
        if metrics.price_change_1m:
            if metrics.price_change_1m > 10:  # Strong positive momentum
                buy_score += 1.0
            elif metrics.price_change_1m < -10:  # Strong negative momentum
                sell_score += 1.0
            else:
                hold_score += 0.5
        
        # News sentiment scoring
        if news_sentiment > 0.3:  # Very positive news
            buy_score += 2.0
        elif news_sentiment > 0.1:  # Positive news
            buy_score += 1.0
        elif news_sentiment < -0.3:  # Very negative news
            sell_score += 2.0
        elif news_sentiment < -0.1:  # Negative news
            sell_score += 1.0
        else:  # Neutral news
            hold_score += 0.5
        
        # Guru consensus scoring (weighted by confidence)
        guru_weight = guru_confidence / 10.0  # Convert to 0-1 scale
        if guru_consensus == RecommendationAction.BUY:
            buy_score += 3.0 * guru_weight
        elif guru_consensus == RecommendationAction.SELL:
            sell_score += 3.0 * guru_weight
        else:
            hold_score += 2.0 * guru_weight
        
        # Fundamental analysis scoring
        if metrics.pe_ratio:
            if metrics.pe_ratio < 15:  # Undervalued
                buy_score += 1.0
            elif metrics.pe_ratio > 30:  # Overvalued
                sell_score += 0.5
        
        # Determine final recommendation
        max_score = max(buy_score, hold_score, sell_score)
        total_score = buy_score + hold_score + sell_score
        
        if buy_score == max_score:
            recommendation = RecommendationAction.BUY
        elif sell_score == max_score:
            recommendation = RecommendationAction.SELL
        else:
            recommendation = RecommendationAction.HOLD
        
        # Calculate confidence (0-10 scale)
        confidence = min(10.0, (max_score / total_score * 10)) if total_score > 0 else 5.0
        
        return recommendation, round(confidence, 1)
    
    def _generate_technical_analysis(self, metrics: StockMetrics) -> str:
        """Generate technical analysis summary"""
        
        analysis = []
        
        if metrics.rsi:
            if metrics.rsi < 30:
                analysis.append(f"RSI ({metrics.rsi}) indicates oversold conditions - potential buying opportunity.")
            elif metrics.rsi > 70:
                analysis.append(f"RSI ({metrics.rsi}) shows overbought levels - caution advised.")
            else:
                analysis.append(f"RSI ({metrics.rsi}) is in neutral territory.")
        
        if metrics.moving_avg_50 and metrics.moving_avg_200:
            if metrics.moving_avg_50 > metrics.moving_avg_200:
                analysis.append("50-day MA above 200-day MA indicates bullish trend.")
            else:
                analysis.append("50-day MA below 200-day MA suggests bearish trend.")
        
        if metrics.price_change_1m:
            if metrics.price_change_1m > 5:
                analysis.append(f"Strong 1-month momentum (+{metrics.price_change_1m}%).")
            elif metrics.price_change_1m < -5:
                analysis.append(f"Negative 1-month momentum ({metrics.price_change_1m}%).")
        
        return " ".join(analysis) if analysis else "Limited technical data available."
    
    def _generate_fundamental_analysis(self, metrics: StockMetrics, stock_data) -> str:
        """Generate fundamental analysis summary"""
        
        analysis = []
        
        if metrics.pe_ratio:
            if metrics.pe_ratio < 15:
                analysis.append(f"P/E ratio ({metrics.pe_ratio}) suggests undervaluation.")
            elif metrics.pe_ratio > 25:
                analysis.append(f"P/E ratio ({metrics.pe_ratio}) indicates premium valuation.")
            else:
                analysis.append(f"P/E ratio ({metrics.pe_ratio}) is reasonable.")
        
        if metrics.dividend_yield and metrics.dividend_yield > 0.02:
            analysis.append(f"Dividend yield of {metrics.dividend_yield:.1%} provides income.")
        
        if metrics.debt_to_equity:
            if metrics.debt_to_equity > 1.0:
                analysis.append("High debt-to-equity ratio raises financial risk concerns.")
            else:
                analysis.append("Manageable debt levels.")
        
        return " ".join(analysis) if analysis else "Limited fundamental data available."
    
    def _generate_reasoning_summary(self, recommendation: RecommendationAction, 
                                  technical: str, fundamental: str, 
                                  news_sentiment: str, guru_consensus: str) -> str:
        """Generate overall reasoning summary"""
        
        action_text = recommendation.value.upper()
        
        summary = f"Recommendation: {action_text}. "
        summary += f"Technical indicators {technical.lower()} "
        summary += f"Fundamentals show {fundamental.lower()} "
        summary += f"News sentiment is {news_sentiment}. "
        summary += f"Analyst consensus: {guru_consensus}"
        
        return summary
    
    def _generate_chart_data(self, symbol: str) -> Optional[Dict]:
        """Generate chart data for visualization"""
        
        try:
            # Get 6 months of price data
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")
            
            if hist.empty:
                return None
            
            # Create candlestick chart data
            chart_data = {
                "dates": hist.index.strftime('%Y-%m-%d').tolist(),
                "open": hist['Open'].round(2).tolist(),
                "high": hist['High'].round(2).tolist(),
                "low": hist['Low'].round(2).tolist(),
                "close": hist['Close'].round(2).tolist(),
                "volume": hist['Volume'].tolist()
            }
            
            return chart_data
            
        except Exception as e:
            print(f"Error generating chart data for {symbol}: {str(e)}")
            return None
    
    def _calculate_portfolio_risk(self, holdings: List[PortfolioHolding], 
                                recommendations: List[StockRecommendation]) -> float:
        """Calculate overall portfolio risk score (1-10)"""
        
        if not holdings:
            return 5.0
        
        risk_scores = []
        
        for holding in holdings:
            # Find corresponding recommendation
            rec = next((r for r in recommendations if r.symbol == holding.symbol), None)
            
            # Base risk on volatility and recommendation confidence
            base_risk = 5.0  # Default medium risk
            
            if rec:
                # Lower confidence = higher risk
                confidence_risk = 10 - rec.confidence_score
                
                # Selling recommendations increase risk
                if rec.recommendation == RecommendationAction.SELL:
                    action_risk = 8.0
                elif rec.recommendation == RecommendationAction.BUY:
                    action_risk = 4.0
                else:
                    action_risk = 6.0
                
                stock_risk = (confidence_risk + action_risk) / 2
            else:
                stock_risk = base_risk
            
            # Weight by portfolio allocation
            weight = holding.current_value / sum(h.current_value for h in holdings)
            risk_scores.append(stock_risk * weight)
        
        portfolio_risk = sum(risk_scores)
        return round(min(10.0, max(1.0, portfolio_risk)), 1)
    
    def _calculate_diversification_score(self, holdings: List[PortfolioHolding]) -> float:
        """Calculate portfolio diversification score (1-10)"""
        
        if len(holdings) <= 1:
            return 1.0  # No diversification
        
        # Base score on number of holdings
        num_holdings = len(holdings)
        if num_holdings >= 10:
            base_score = 9.0
        elif num_holdings >= 5:
            base_score = 7.0
        elif num_holdings >= 3:
            base_score = 5.0
        else:
            base_score = 3.0
        
        # Check concentration risk
        total_value = sum(h.current_value for h in holdings)
        max_allocation = max(h.current_value / total_value for h in holdings)
        
        if max_allocation > 0.5:  # More than 50% in one stock
            concentration_penalty = 3.0
        elif max_allocation > 0.3:  # More than 30% in one stock
            concentration_penalty = 1.5
        else:
            concentration_penalty = 0.0
        
        final_score = base_score - concentration_penalty
        return round(max(1.0, min(10.0, final_score)), 1)
    
    def _calculate_overall_sentiment(self, recommendations: List[StockRecommendation]) -> str:
        """Calculate overall portfolio sentiment"""
        
        if not recommendations:
            return "neutral"
        
        buy_count = sum(1 for r in recommendations if r.recommendation == RecommendationAction.BUY)
        sell_count = sum(1 for r in recommendations if r.recommendation == RecommendationAction.SELL)
        hold_count = len(recommendations) - buy_count - sell_count
        
        if buy_count > sell_count and buy_count > hold_count:
            return "bullish"
        elif sell_count > buy_count and sell_count > hold_count:
            return "bearish"
        else:
            return "neutral"


# Singleton instance
portfolio_service = PortfolioService()