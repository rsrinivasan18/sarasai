"""
Sarasai - Guru Recommendations Aggregation Service
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import requests
from typing import List, Optional
from datetime import datetime, timedelta
import random

from core.models import GuruRecommendation, RecommendationAction


class GuruService:
    """Service for aggregating recommendations from financial experts and analysts"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(hours=4)  # Cache guru recommendations for 4 hours
        
        # Mock guru data - in real implementation, this would come from APIs
        self.mock_gurus = [
            {"name": "Warren Buffett", "source": "Berkshire Hathaway", "credibility": 9.5},
            {"name": "Peter Lynch", "source": "Fidelity", "credibility": 9.2},
            {"name": "Ray Dalio", "source": "Bridgewater", "credibility": 9.0},
            {"name": "Cathie Wood", "source": "ARK Invest", "credibility": 8.5},
            {"name": "Jim Cramer", "source": "Mad Money", "credibility": 7.8},
            {"name": "Motley Fool Analysts", "source": "Motley Fool", "credibility": 8.0},
            {"name": "Goldman Sachs Research", "source": "Goldman Sachs", "credibility": 8.7},
            {"name": "Morgan Stanley Analysts", "source": "Morgan Stanley", "credibility": 8.6},
            {"name": "JP Morgan Research", "source": "JP Morgan", "credibility": 8.5},
            {"name": "Bank of America Analysts", "source": "Bank of America", "credibility": 8.3}
        ]
    
    def get_guru_recommendations(self, symbol: str, limit: int = 5) -> List[GuruRecommendation]:
        """Get aggregated recommendations from financial gurus and analysts"""
        
        # Check cache first
        cache_key = f"{symbol}_gurus"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data[:limit]
        
        try:
            # In real implementation, you would fetch from:
            # - TipRanks API
            # - Yahoo Finance analyst recommendations
            # - Seeking Alpha
            # - Zacks Investment Research
            # - Financial news APIs
            
            recommendations = self._generate_mock_recommendations(symbol)
            
            # Cache the results
            if recommendations:
                self.cache[cache_key] = (recommendations, datetime.now())
            
            return recommendations[:limit]
            
        except Exception as e:
            print(f"Error fetching guru recommendations for {symbol}: {str(e)}")
            return []
    
    def _generate_mock_recommendations(self, symbol: str) -> List[GuruRecommendation]:
        """Generate mock recommendations for demonstration"""
        recommendations = []
        
        # Select random gurus for this stock
        selected_gurus = random.sample(self.mock_gurus, min(5, len(self.mock_gurus)))
        
        for guru in selected_gurus:
            # Generate realistic recommendation based on symbol characteristics
            recommendation = self._generate_realistic_recommendation(symbol, guru)
            recommendations.append(recommendation)
        
        # Sort by confidence score (highest first)
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return recommendations
    
    def _generate_realistic_recommendation(self, symbol: str, guru: dict) -> GuruRecommendation:
        """Generate a realistic recommendation based on stock and guru characteristics"""
        
        # Generate recommendation based on some logic
        # In real implementation, this would be actual analyst data
        
        # Mock current price (in real implementation, get from stock service)
        current_price = self._get_mock_current_price(symbol)
        
        # Generate recommendation action with some logic
        if guru["credibility"] > 9.0:
            # High credibility gurus tend to be more conservative
            actions = [RecommendationAction.HOLD, RecommendationAction.BUY, RecommendationAction.HOLD]
        else:
            # Lower credibility gurus might be more aggressive
            actions = [RecommendationAction.BUY, RecommendationAction.HOLD, RecommendationAction.SELL]
        
        action = random.choice(actions)
        
        # Generate target price based on action
        if action == RecommendationAction.BUY:
            target_price = current_price * random.uniform(1.05, 1.25)  # 5-25% upside
            reasoning = f"Strong fundamentals and growth potential make {symbol} attractive at current levels."
        elif action == RecommendationAction.SELL:
            target_price = current_price * random.uniform(0.80, 0.95)  # 5-20% downside
            reasoning = f"Overvaluation concerns and market headwinds suggest caution with {symbol}."
        else:  # HOLD
            target_price = current_price * random.uniform(0.95, 1.05)  # ±5%
            reasoning = f"Fair valuation for {symbol} with balanced risk-reward profile."
        
        # Confidence score based on guru credibility with some randomness
        base_confidence = guru["credibility"]
        confidence_score = min(10.0, base_confidence + random.uniform(-0.5, 0.5))
        
        # Generate publication date (within last 30 days)
        days_ago = random.randint(1, 30)
        publication_date = datetime.now() - timedelta(days=days_ago)
        
        return GuruRecommendation(
            source=guru["source"],
            analyst_name=guru["name"],
            recommendation=action,
            target_price=round(target_price, 2),
            confidence_score=round(confidence_score, 1),
            reasoning=reasoning,
            date_published=publication_date
        )
    
    def _get_mock_current_price(self, symbol: str) -> float:
        """Get mock current price for demonstration"""
        # This is a simplified mock - in real implementation, 
        # get actual price from stock service
        price_map = {
            "AAPL": 185.92,
            "GOOGL": 141.80,
            "MSFT": 378.91,
            "TSLA": 242.84,
            "RELIANCE.NS": 2456.30,
            "TCS.NS": 3842.75,
            "INFY.NS": 1456.80,
            "HDFCBANK.NS": 1678.50,
            "ITC.NS": 456.75,
            "SBIN.NS": 598.30
        }
        return price_map.get(symbol, 100.0)
    
    def get_consensus_recommendation(self, recommendations: List[GuruRecommendation]) -> tuple[RecommendationAction, float, str]:
        """Calculate consensus recommendation from multiple guru opinions"""
        
        if not recommendations:
            return RecommendationAction.HOLD, 5.0, "No analyst recommendations available."
        
        # Weight recommendations by confidence score
        action_scores = {
            RecommendationAction.BUY: 0.0,
            RecommendationAction.HOLD: 0.0,
            RecommendationAction.SELL: 0.0
        }
        
        total_weight = 0.0
        
        for rec in recommendations:
            weight = rec.confidence_score
            action_scores[rec.recommendation] += weight
            total_weight += weight
        
        # Normalize scores
        for action in action_scores:
            action_scores[action] = action_scores[action] / total_weight if total_weight > 0 else 0
        
        # Find consensus
        consensus_action = max(action_scores, key=action_scores.get)
        consensus_strength = action_scores[consensus_action]
        
        # Generate explanation
        buy_pct = round(action_scores[RecommendationAction.BUY] * 100, 1)
        hold_pct = round(action_scores[RecommendationAction.HOLD] * 100, 1)
        sell_pct = round(action_scores[RecommendationAction.SELL] * 100, 1)
        
        explanation = f"Analyst consensus: {buy_pct}% Buy, {hold_pct}% Hold, {sell_pct}% Sell. "
        explanation += f"Weighted consensus: {consensus_action.value.upper()} (strength: {consensus_strength:.1f})"
        
        return consensus_action, round(consensus_strength * 10, 1), explanation


# Singleton instance
guru_service = GuruService()