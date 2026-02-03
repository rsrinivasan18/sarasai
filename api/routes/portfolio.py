"""
Sarasai - Portfolio Routes
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import json

from core.models import (
    PortfolioAnalysis, PortfolioInput, StockRecommendation, 
    StockMetrics, PortfolioHolding
)
from core.portfolio_service import portfolio_service
from core.metrics_service import metrics_service
from core.news_service import news_service
from core.guru_service import guru_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.post("/analyze", response_model=PortfolioAnalysis)
def analyze_portfolio(portfolio_input: PortfolioInput):
    """
    Analyze portfolio and get comprehensive recommendations
    
    Example request body:
    {
        "holdings": [
            {"symbol": "AAPL", "quantity": 10, "avg_price": 150.0},
            {"symbol": "GOOGL", "quantity": 5, "avg_price": 140.0},
            {"symbol": "RELIANCE.NS", "quantity": 100, "avg_price": 2400.0}
        ]
    }
    """
    try:
        analysis = portfolio_service.analyze_portfolio(portfolio_input)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {str(e)}")


@router.get("/recommendation/{symbol}", response_model=StockRecommendation)
def get_stock_recommendation(symbol: str):
    """
    Get detailed recommendation for a specific stock
    
    Available symbols: AAPL, GOOGL, MSFT, TSLA, RELIANCE.NS, TCS.NS, INFY.NS, etc.
    """
    try:
        recommendation = portfolio_service._generate_stock_recommendation(symbol)
        if not recommendation:
            raise HTTPException(status_code=404, detail=f"Could not generate recommendation for {symbol}")
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")


@router.get("/metrics/{symbol}", response_model=StockMetrics)
def get_stock_metrics(symbol: str):
    """
    Get technical and fundamental metrics for a stock
    """
    try:
        metrics = metrics_service.get_stock_metrics(symbol)
        if not metrics:
            # Return default metrics when data is not available
            from core.models import StockMetrics
            metrics = StockMetrics(
                symbol=symbol,
                rsi=None, moving_avg_50=None, moving_avg_200=None,
                bollinger_upper=None, bollinger_lower=None, macd=None,
                pe_ratio=None, pb_ratio=None, debt_to_equity=None,
                roe=None, dividend_yield=None,
                price_change_1d=None, price_change_1w=None,
                price_change_1m=None, price_change_3m=None
            )
        return metrics
    except Exception as e:
        # Return default metrics with error info
        from core.models import StockMetrics
        return StockMetrics(
            symbol=symbol,
            rsi=None, moving_avg_50=None, moving_avg_200=None,
            bollinger_upper=None, bollinger_lower=None, macd=None,
            pe_ratio=None, pb_ratio=None, debt_to_equity=None,
            roe=None, dividend_yield=None,
            price_change_1d=None, price_change_1w=None,
            price_change_1m=None, price_change_3m=None
        )


@router.get("/news/{symbol}")
def get_stock_news(symbol: str, limit: int = 5):
    """
    Get recent news and sentiment analysis for a stock
    """
    try:
        news_items = news_service.get_stock_news(symbol, limit)
        overall_sentiment = news_service.get_overall_sentiment(news_items)
        
        return {
            "symbol": symbol,
            "news_count": len(news_items),
            "overall_sentiment": {
                "score": overall_sentiment[0],
                "label": overall_sentiment[1]
            },
            "news_items": [news.model_dump() for news in news_items]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"News fetch failed: {str(e)}")


@router.get("/gurus/{symbol}")
def get_guru_recommendations(symbol: str, limit: int = 5):
    """
    Get analyst and guru recommendations for a stock
    """
    try:
        recommendations = guru_service.get_guru_recommendations(symbol, limit)
        consensus = guru_service.get_consensus_recommendation(recommendations)
        
        return {
            "symbol": symbol,
            "recommendation_count": len(recommendations),
            "consensus": {
                "action": consensus[0].value,
                "confidence": consensus[1],
                "explanation": consensus[2]
            },
            "recommendations": [rec.model_dump() for rec in recommendations]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Guru recommendations fetch failed: {str(e)}")


@router.get("/dashboard/{symbol}", response_class=HTMLResponse)
def stock_dashboard(symbol: str):
    """
    Interactive HTML dashboard for a specific stock with all analysis
    """
    try:
        # Get all data for the stock
        recommendation = portfolio_service._generate_stock_recommendation(symbol)
        if not recommendation:
            return f"<h1>Error: Could not generate analysis for {symbol}</h1>"
        
        # Create simple HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sarasai - {symbol} Analysis Dashboard</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background: #f5f5f5;
                }}
                .container {{ 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 20px; 
                    border-radius: 10px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .recommendation {{ 
                    background: #667eea; 
                    color: white; 
                    padding: 20px; 
                    border-radius: 8px; 
                    margin: 20px 0;
                    text-align: center;
                }}
                .section {{ 
                    background: #f8f9ff; 
                    padding: 15px; 
                    margin: 15px 0; 
                    border-radius: 8px; 
                    border-left: 4px solid #667eea;
                }}
                .metric {{ 
                    display: flex; 
                    justify-content: space-between; 
                    padding: 5px 0; 
                    border-bottom: 1px solid #eee;
                }}
                h1, h2, h3 {{ color: #333; }}
                .price {{ font-size: 24px; font-weight: bold; color: #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{recommendation.name} ({symbol})</h1>
                    <div class="price">${recommendation.current_price:.2f}</div>
                </div>
                
                <div class="recommendation">
                    <h2>Recommendation: {recommendation.recommendation.value.upper()}</h2>
                    <p><strong>Confidence:</strong> {recommendation.confidence_score}/10</p>
                    <p>{recommendation.reasoning_summary}</p>
                </div>
                
                <div class="section">
                    <h3>Technical Analysis</h3>
                    <p>{recommendation.technical_analysis}</p>
                    <div class="metric">
                        <span>RSI:</span> 
                        <strong>{'N/A' if recommendation.metrics.rsi is None else f'{recommendation.metrics.rsi:.1f}'}</strong>
                    </div>
                    <div class="metric">
                        <span>P/E Ratio:</span> 
                        <strong>{'N/A' if recommendation.metrics.pe_ratio is None else f'{recommendation.metrics.pe_ratio:.1f}'}</strong>
                    </div>
                </div>
                
                <div class="section">
                    <h3>News Sentiment</h3>
                    <p>{recommendation.news_sentiment}</p>
                    <p><strong>Recent News:</strong> {len(recommendation.recent_news)} articles analyzed</p>
                </div>
                
                <div class="section">
                    <h3>Expert Consensus</h3>
                    <p>{recommendation.guru_consensus}</p>
                    <p><strong>Analyst Recommendations:</strong> {len(recommendation.guru_recommendations)} opinions</p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
                    Analysis generated at {recommendation.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                    <br>Powered by Sarasai - Where Wisdom Flows
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>Error generating dashboard for {symbol}: {str(e)}</h1>"


@router.post("/dashboard", response_class=HTMLResponse)
def portfolio_dashboard(portfolio_input: PortfolioInput):
    """
    Interactive HTML dashboard for complete portfolio analysis
    """
    try:
        analysis = portfolio_service.analyze_portfolio(portfolio_input)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sarasai - Portfolio Analysis Dashboard</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }}
                .container {{ 
                    max-width: 1400px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 15px 50px rgba(0,0,0,0.3);
                    color: #333;
                }}
                .header {{ text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #eee; }}
                .summary {{ 
                    background: linear-gradient(45deg, #667eea, #764ba2); 
                    color: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    margin-bottom: 30px; 
                    text-align: center;
                }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
                .metric-box {{ 
                    background: #f8f9ff; 
                    padding: 20px; 
                    border-radius: 10px; 
                    text-align: center; 
                    border-left: 4px solid #667eea;
                }}
                .holdings-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .holdings-table th {{ 
                    background: #667eea; 
                    color: white; 
                    padding: 12px; 
                    text-align: left; 
                }}
                .holdings-table td {{ 
                    padding: 12px; 
                    border-bottom: 1px solid #eee; 
                }}
                .profit {{ color: #10b981; font-weight: bold; }}
                .loss {{ color: #ef4444; font-weight: bold; }}
                .recommendation {{ 
                    background: white; 
                    padding: 20px; 
                    margin: 15px 0; 
                    border-radius: 10px; 
                    border-left: 4px solid #667eea;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                }}
                .action-buy {{ border-left-color: #10b981; }}
                .action-sell {{ border-left-color: #ef4444; }}
                .action-hold {{ border-left-color: #f59e0b; }}
                h1, h2, h3 {{ color: #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🦢 Portfolio Analysis Dashboard</h1>
                    <p>Comprehensive analysis of your investment portfolio</p>
                </div>
                
                <div class="summary">
                    <h2>Portfolio Summary</h2>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 20px; text-align: center;">
                        <div>
                            <h3>Total Invested</h3>
                            <div style="font-size: 24px; font-weight: bold;">${analysis.total_invested:,.2f}</div>
                        </div>
                        <div>
                            <h3>Current Value</h3>
                            <div style="font-size: 24px; font-weight: bold;">${analysis.current_value:,.2f}</div>
                        </div>
                        <div>
                            <h3>Total P&L</h3>
                            <div style="font-size: 24px; font-weight: bold; color: {'#10b981' if analysis.total_profit_loss >= 0 else '#ef4444'};">
                                ${analysis.total_profit_loss:,.2f} ({analysis.total_profit_loss_percent:+.2f}%)
                            </div>
                        </div>
                        <div>
                            <h3>Overall Sentiment</h3>
                            <div style="font-size: 20px; font-weight: bold;">{analysis.overall_sentiment.upper()}</div>
                        </div>
                    </div>
                </div>
                
                <div class="grid">
                    <div class="metric-box">
                        <h3>Risk Score</h3>
                        <div style="font-size: 32px; font-weight: bold; color: #667eea;">{analysis.portfolio_risk_score}/10</div>
                        <p>Portfolio Risk Level</p>
                    </div>
                    <div class="metric-box">
                        <h3>Diversification</h3>
                        <div style="font-size: 32px; font-weight: bold; color: #667eea;">{analysis.diversification_score}/10</div>
                        <p>Diversification Score</p>
                    </div>
                    <div class="metric-box">
                        <h3>Holdings</h3>
                        <div style="font-size: 32px; font-weight: bold; color: #667eea;">{len(analysis.holdings)}</div>
                        <p>Number of Stocks</p>
                    </div>
                </div>
                
                <div style="background: #f8f9ff; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
                    <h3>📈 Portfolio Holdings</h3>
                    <table class="holdings-table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Name</th>
                                <th>Quantity</th>
                                <th>Avg Price</th>
                                <th>Current Price</th>
                                <th>Invested</th>
                                <th>Current Value</th>
                                <th>P&L</th>
                                <th>P&L %</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # Add holdings rows
        for holding in analysis.holdings:
            profit_loss_class = "profit" if holding.profit_loss >= 0 else "loss"
            html_content += f"""
                            <tr>
                                <td><strong>{holding.symbol}</strong></td>
                                <td>{holding.name}</td>
                                <td>{holding.quantity}</td>
                                <td>${holding.avg_purchase_price:.2f}</td>
                                <td>${holding.current_price:.2f}</td>
                                <td>${holding.total_invested:,.2f}</td>
                                <td>${holding.current_value:,.2f}</td>
                                <td class="{profit_loss_class}">${holding.profit_loss:+.2f}</td>
                                <td class="{profit_loss_class}">{holding.profit_loss_percent:+.2f}%</td>
                            </tr>
            """
        
        html_content += """
                        </tbody>
                    </table>
                </div>
                
                <div style="background: #f8f9ff; padding: 20px; border-radius: 10px;">
                    <h3>🎯 Stock Recommendations</h3>
        """
        
        # Add recommendation cards
        for rec in analysis.recommendations:
            html_content += f"""
                    <div class="recommendation action-{rec.recommendation.value}">
                        <h4>{rec.name} ({rec.symbol}) - {rec.recommendation.value.upper()}</h4>
                        <p><strong>Current Price:</strong> ${rec.current_price:.2f} | 
                           <strong>Confidence:</strong> {rec.confidence_score}/10</p>
                        <p>{rec.reasoning_summary[:200]}...</p>
                        <small>Technical: {rec.technical_analysis[:100]}...</small>
                    </div>
            """
        
        html_content += f"""
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #999; font-size: 12px;">
                    Analysis generated at {analysis.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                    <br>🦢 Powered by Sarasai - Where Wisdom Flows
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        return f"<h1>Error generating portfolio dashboard: {str(e)}</h1>"