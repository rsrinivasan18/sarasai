"""
Expert Advisor Aggregation System
Aggregates insights from multiple expert sources and financial advisors
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import random

from .config_service import config_service


class ExpertType(Enum):
    FUNDAMENTAL_ANALYST = "fundamental_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    QUANTITATIVE_ANALYST = "quantitative_analyst"
    MARKET_STRATEGIST = "market_strategist"
    SECTOR_SPECIALIST = "sector_specialist"


class RecommendationAction(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


@dataclass
class ExpertRecommendation:
    """Individual expert recommendation"""
    expert_name: str
    expert_type: ExpertType
    symbol: str
    action: RecommendationAction
    confidence: float  # 0-100
    target_price: Optional[float]
    reasoning: str
    time_horizon: str  # "short", "medium", "long"
    last_updated: datetime
    track_record_score: float  # 0-100, historical accuracy


@dataclass
class ConsensusRecommendation:
    """Aggregated consensus from multiple experts"""
    symbol: str
    consensus_action: RecommendationAction
    consensus_confidence: float
    consensus_target_price: Optional[float]
    expert_count: int
    agreement_level: float  # 0-100, how much experts agree
    bullish_experts: int
    bearish_experts: int
    neutral_experts: int
    weighted_score: float
    key_arguments: List[str]
    dissenting_views: List[str]


class ExpertDatabase:
    """Database of expert opinions and track records"""
    
    def __init__(self):
        self.config = config_service.load_config("experts")
        self._load_expert_data()
    
    def _load_expert_data(self):
        """Load expert recommendations and track records"""
        self.experts = {
            # Fundamental Analysts
            "Warren Buffett": {
                "type": ExpertType.FUNDAMENTAL_ANALYST,
                "track_record": 92.5,
                "specialty": ["value_investing", "large_cap", "consumer"],
                "bias": "conservative"
            },
            "Peter Lynch": {
                "type": ExpertType.FUNDAMENTAL_ANALYST,
                "track_record": 89.3,
                "specialty": ["growth_investing", "consumer", "technology"],
                "bias": "growth_oriented"
            },
            "Benjamin Graham": {
                "type": ExpertType.FUNDAMENTAL_ANALYST,
                "track_record": 87.8,
                "specialty": ["value_investing", "deep_value", "margin_safety"],
                "bias": "conservative"
            },
            
            # Technical Analysts
            "John Murphy": {
                "type": ExpertType.TECHNICAL_ANALYST,
                "track_record": 78.5,
                "specialty": ["chart_patterns", "momentum", "trends"],
                "bias": "momentum"
            },
            "Ralph Nelson Elliott": {
                "type": ExpertType.TECHNICAL_ANALYST,
                "track_record": 75.2,
                "specialty": ["elliott_wave", "market_cycles", "fibonacci"],
                "bias": "cyclical"
            },
            
            # Quantitative Analysts
            "James Simons": {
                "type": ExpertType.QUANTITATIVE_ANALYST,
                "track_record": 94.1,
                "specialty": ["mathematical_models", "statistical_arbitrage", "algorithms"],
                "bias": "data_driven"
            },
            "Ray Dalio": {
                "type": ExpertType.MARKET_STRATEGIST,
                "track_record": 85.7,
                "specialty": ["macro_economics", "risk_parity", "diversification"],
                "bias": "macro_focused"
            },
            
            # Sector Specialists
            "Cathie Wood": {
                "type": ExpertType.SECTOR_SPECIALIST,
                "track_record": 72.4,
                "specialty": ["technology", "innovation", "disruptive_tech"],
                "bias": "innovation_focused"
            },
            "Mary Meeker": {
                "type": ExpertType.SECTOR_SPECIALIST,
                "track_record": 81.2,
                "specialty": ["technology", "internet", "digital_trends"],
                "bias": "tech_bullish"
            }
        }
        
        # Mock recommendations for different stocks
        self.mock_recommendations = {
            "AAPL": [
                {
                    "expert": "Warren Buffett",
                    "action": RecommendationAction.BUY,
                    "confidence": 85.0,
                    "target_price": 200.0,
                    "reasoning": "Strong brand moat, consistent cash flows, and reasonable valuation make Apple attractive for long-term investors.",
                    "time_horizon": "long"
                },
                {
                    "expert": "Cathie Wood",
                    "action": RecommendationAction.STRONG_BUY,
                    "confidence": 92.0,
                    "target_price": 220.0,
                    "reasoning": "Apple's AI integration and services growth create significant upside potential in innovation-driven markets.",
                    "time_horizon": "medium"
                },
                {
                    "expert": "John Murphy",
                    "action": RecommendationAction.HOLD,
                    "confidence": 68.0,
                    "target_price": 190.0,
                    "reasoning": "Technical indicators show mixed signals with resistance at current levels, suggesting sideways movement.",
                    "time_horizon": "short"
                }
            ],
            "DBS.SI": [
                {
                    "expert": "Peter Lynch",
                    "action": RecommendationAction.BUY,
                    "confidence": 78.0,
                    "target_price": 32.0,
                    "reasoning": "DBS benefits from rising interest rates and strong Southeast Asian economic growth prospects.",
                    "time_horizon": "medium"
                },
                {
                    "expert": "Ray Dalio",
                    "action": RecommendationAction.BUY,
                    "confidence": 82.0,
                    "target_price": 31.5,
                    "reasoning": "Singapore's strategic position and DBS's regional dominance provide defensive characteristics in uncertain times.",
                    "time_horizon": "long"
                }
            ],
            "RELIANCE.NS": [
                {
                    "expert": "Benjamin Graham",
                    "action": RecommendationAction.HOLD,
                    "confidence": 72.0,
                    "target_price": 2500.0,
                    "reasoning": "Trading at fair value with debt concerns offsetting strong business fundamentals.",
                    "time_horizon": "medium"
                },
                {
                    "expert": "Mary Meeker",
                    "action": RecommendationAction.BUY,
                    "confidence": 86.0,
                    "target_price": 2800.0,
                    "reasoning": "Jio's digital ecosystem and renewable energy transition position Reliance for future growth.",
                    "time_horizon": "long"
                }
            ],
            "TSLA": [
                {
                    "expert": "Cathie Wood",
                    "action": RecommendationAction.STRONG_BUY,
                    "confidence": 95.0,
                    "target_price": 300.0,
                    "reasoning": "Tesla leads in EV technology, autonomous driving, and energy storage with massive addressable market.",
                    "time_horizon": "long"
                },
                {
                    "expert": "Warren Buffett",
                    "action": RecommendationAction.SELL,
                    "confidence": 79.0,
                    "target_price": 180.0,
                    "reasoning": "Valuation remains excessive relative to traditional automotive metrics and competitive pressures are increasing.",
                    "time_horizon": "medium"
                }
            ]
        }
    
    def get_expert_recommendations(self, symbol: str) -> List[ExpertRecommendation]:
        """Get all expert recommendations for a symbol"""
        recommendations = []
        symbol_recs = self.mock_recommendations.get(symbol, [])
        
        for rec_data in symbol_recs:
            expert_name = rec_data["expert"]
            expert_info = self.experts.get(expert_name, {})
            
            recommendation = ExpertRecommendation(
                expert_name=expert_name,
                expert_type=expert_info.get("type", ExpertType.FUNDAMENTAL_ANALYST),
                symbol=symbol,
                action=rec_data["action"],
                confidence=rec_data["confidence"],
                target_price=rec_data.get("target_price"),
                reasoning=rec_data["reasoning"],
                time_horizon=rec_data["time_horizon"],
                last_updated=datetime.now() - timedelta(days=random.randint(0, 7)),
                track_record_score=expert_info.get("track_record", 75.0)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_expert_info(self, expert_name: str) -> Dict[str, Any]:
        """Get detailed information about an expert"""
        return self.experts.get(expert_name, {})


class ConsensusEngine:
    """Engine for aggregating expert opinions into consensus recommendations"""
    
    def __init__(self):
        self.expert_db = ExpertDatabase()
        
        # Weights for different expert types
        self.expert_weights = {
            ExpertType.FUNDAMENTAL_ANALYST: 1.0,
            ExpertType.TECHNICAL_ANALYST: 0.8,
            ExpertType.QUANTITATIVE_ANALYST: 1.2,
            ExpertType.MARKET_STRATEGIST: 0.9,
            ExpertType.SECTOR_SPECIALIST: 1.1
        }
    
    def calculate_consensus(self, symbol: str) -> ConsensusRecommendation:
        """Calculate consensus recommendation from all experts"""
        recommendations = self.expert_db.get_expert_recommendations(symbol)
        
        if not recommendations:
            return self._create_default_consensus(symbol)
        
        # Calculate weighted scores
        weighted_scores = []
        target_prices = []
        key_arguments = []
        dissenting_views = []
        
        action_counts = {action: 0 for action in RecommendationAction}
        
        for rec in recommendations:
            # Get expert weight
            expert_weight = self.expert_weights.get(rec.expert_type, 1.0)
            track_record_weight = rec.track_record_score / 100.0
            
            # Calculate weighted contribution
            total_weight = expert_weight * track_record_weight
            
            # Convert action to numeric score
            action_score = self._action_to_score(rec.action)
            weighted_score = action_score * total_weight * (rec.confidence / 100.0)
            weighted_scores.append(weighted_score)
            
            # Count actions
            action_counts[rec.action] += 1
            
            # Collect target prices
            if rec.target_price:
                target_prices.append(rec.target_price)
            
            # Collect arguments
            if rec.action in [RecommendationAction.BUY, RecommendationAction.STRONG_BUY]:
                key_arguments.append(f"{rec.expert_name}: {rec.reasoning}")
            elif rec.action in [RecommendationAction.SELL, RecommendationAction.STRONG_SELL]:
                dissenting_views.append(f"{rec.expert_name}: {rec.reasoning}")
        
        # Calculate consensus metrics
        avg_weighted_score = sum(weighted_scores) / len(weighted_scores)
        consensus_action = self._score_to_action(avg_weighted_score)
        
        # Calculate agreement level
        max_action_count = max(action_counts.values())
        agreement_level = (max_action_count / len(recommendations)) * 100
        
        # Calculate consensus confidence
        confidence_scores = [rec.confidence for rec in recommendations]
        consensus_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # Calculate consensus target price
        consensus_target_price = sum(target_prices) / len(target_prices) if target_prices else None
        
        # Count expert sentiment
        bullish_count = action_counts[RecommendationAction.STRONG_BUY] + action_counts[RecommendationAction.BUY]
        bearish_count = action_counts[RecommendationAction.STRONG_SELL] + action_counts[RecommendationAction.SELL]
        neutral_count = action_counts[RecommendationAction.HOLD]
        
        return ConsensusRecommendation(
            symbol=symbol,
            consensus_action=consensus_action,
            consensus_confidence=round(consensus_confidence, 1),
            consensus_target_price=round(consensus_target_price, 2) if consensus_target_price else None,
            expert_count=len(recommendations),
            agreement_level=round(agreement_level, 1),
            bullish_experts=bullish_count,
            bearish_experts=bearish_count,
            neutral_experts=neutral_count,
            weighted_score=round(avg_weighted_score, 2),
            key_arguments=key_arguments[:3],  # Top 3 arguments
            dissenting_views=dissenting_views[:2]  # Top 2 dissenting views
        )
    
    def _action_to_score(self, action: RecommendationAction) -> float:
        """Convert recommendation action to numeric score"""
        action_scores = {
            RecommendationAction.STRONG_SELL: 1.0,
            RecommendationAction.SELL: 2.0,
            RecommendationAction.HOLD: 3.0,
            RecommendationAction.BUY: 4.0,
            RecommendationAction.STRONG_BUY: 5.0
        }
        return action_scores.get(action, 3.0)
    
    def _score_to_action(self, score: float) -> RecommendationAction:
        """Convert numeric score to recommendation action"""
        if score >= 4.5:
            return RecommendationAction.STRONG_BUY
        elif score >= 3.5:
            return RecommendationAction.BUY
        elif score >= 2.5:
            return RecommendationAction.HOLD
        elif score >= 1.5:
            return RecommendationAction.SELL
        else:
            return RecommendationAction.STRONG_SELL
    
    def _create_default_consensus(self, symbol: str) -> ConsensusRecommendation:
        """Create default consensus when no expert recommendations available"""
        return ConsensusRecommendation(
            symbol=symbol,
            consensus_action=RecommendationAction.HOLD,
            consensus_confidence=50.0,
            consensus_target_price=None,
            expert_count=0,
            agreement_level=0.0,
            bullish_experts=0,
            bearish_experts=0,
            neutral_experts=0,
            weighted_score=3.0,
            key_arguments=["No expert recommendations available"],
            dissenting_views=[]
        )
    
    def get_portfolio_expert_analysis(self, symbols: List[str]) -> Dict[str, Any]:
        """Get expert consensus analysis for entire portfolio"""
        if not symbols:
            return {"message": "No symbols provided", "recommendations": {}}
        
        portfolio_recommendations = {}
        total_weighted_score = 0.0
        total_experts = 0
        bullish_stocks = 0
        bearish_stocks = 0
        
        for symbol in symbols:
            consensus = self.calculate_consensus(symbol)
            portfolio_recommendations[symbol] = {
                "consensus_action": consensus.consensus_action.value,
                "consensus_confidence": consensus.consensus_confidence,
                "expert_count": consensus.expert_count,
                "agreement_level": consensus.agreement_level,
                "weighted_score": consensus.weighted_score,
                "target_price": consensus.consensus_target_price
            }
            
            total_weighted_score += consensus.weighted_score
            total_experts += consensus.expert_count
            
            if consensus.weighted_score > 3.5:
                bullish_stocks += 1
            elif consensus.weighted_score < 2.5:
                bearish_stocks += 1
        
        avg_portfolio_score = total_weighted_score / len(symbols) if symbols else 3.0
        portfolio_sentiment = self._score_to_action(avg_portfolio_score)
        
        return {
            "portfolio_sentiment": portfolio_sentiment.value,
            "average_expert_score": round(avg_portfolio_score, 2),
            "total_experts_consulted": total_experts,
            "bullish_recommendations": bullish_stocks,
            "bearish_recommendations": bearish_stocks,
            "neutral_recommendations": len(symbols) - bullish_stocks - bearish_stocks,
            "individual_stocks": portfolio_recommendations,
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_expert_track_records(self) -> List[Dict[str, Any]]:
        """Get track record information for all experts"""
        track_records = []
        
        for expert_name, expert_info in self.expert_db.experts.items():
            track_records.append({
                "name": expert_name,
                "type": expert_info["type"].value,
                "track_record_score": expert_info["track_record"],
                "specialty": expert_info.get("specialty", []),
                "bias": expert_info.get("bias", "balanced"),
                "weight_in_consensus": self.expert_weights.get(expert_info["type"], 1.0)
            })
        
        # Sort by track record
        track_records.sort(key=lambda x: x["track_record_score"], reverse=True)
        return track_records


# Global expert advisor engine instance
expert_engine = ConsensusEngine()