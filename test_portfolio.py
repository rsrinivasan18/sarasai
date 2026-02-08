"""
Test script for portfolio analysis functionality
"""

import sys
import asyncio
from datetime import datetime

# Add the project directory to the path
sys.path.append('.')

from core.portfolio_service import portfolio_service
from core.models import PortfolioInput

def test_portfolio_analysis():
    """Test the portfolio analysis with sample data"""
    
    # Sample portfolio with different stocks
    sample_portfolio = {
        "holdings": [
            {"symbol": "AAPL", "quantity": 10, "avg_price": 180.0},
            {"symbol": "GOOGL", "quantity": 5, "avg_price": 130.0},
            {"symbol": "RELIANCE.NS", "quantity": 100, "avg_price": 2300.0},
            {"symbol": "TCS.NS", "quantity": 20, "avg_price": 3700.0}
        ]
    }
    
    print("Sarasai Portfolio Analysis Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        # Create portfolio input
        portfolio_input = PortfolioInput(**sample_portfolio)
        print("Portfolio input created successfully")
        
        # Analyze portfolio
        print("Analyzing portfolio...")
        analysis = portfolio_service.analyze_portfolio(portfolio_input)
        print("Portfolio analysis completed")
        print()
        
        # Display results
        print("PORTFOLIO SUMMARY")
        print("-" * 30)
        print(f"Total Invested: ${analysis.total_invested:,.2f}")
        print(f"Current Value: ${analysis.current_value:,.2f}")
        print(f"Total P&L: ${analysis.total_profit_loss:+,.2f} ({analysis.total_profit_loss_percent:+.2f}%)")
        print(f"Portfolio Risk Score: {analysis.portfolio_risk_score}/10")
        print(f"Diversification Score: {analysis.diversification_score}/10")
        print(f"Overall Sentiment: {analysis.overall_sentiment.upper()}")
        print()
        
        print("HOLDINGS BREAKDOWN")
        print("-" * 50)
        for holding in analysis.holdings:
            print(f"{holding.symbol} ({holding.name})")
            print(f"  Quantity: {holding.quantity}")
            print(f"  Avg Price: ${holding.avg_purchase_price:.2f} -> Current: ${holding.current_price:.2f}")
            print(f"  P&L: ${holding.profit_loss:+,.2f} ({holding.profit_loss_percent:+.2f}%)")
            print()
        
        print("STOCK RECOMMENDATIONS")
        print("-" * 50)
        for rec in analysis.recommendations:
            print(f"{rec.symbol} ({rec.name})")
            print(f"  Recommendation: {rec.recommendation.value.upper()}")
            print(f"  Confidence: {rec.confidence_score}/10")
            print(f"  Reasoning: {rec.reasoning_summary[:100]}...")
            print()
        
        print("Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_single_stock_recommendation():
    """Test single stock recommendation"""
    
    print("\nTesting Single Stock Recommendation")
    print("=" * 50)
    
    try:
        symbol = "AAPL"
        print(f"Getting recommendation for {symbol}...")
        
        recommendation = portfolio_service._generate_stock_recommendation(symbol)
        
        if recommendation:
            print("Recommendation generated successfully")
            print()
            print(f"Stock: {recommendation.name} ({recommendation.symbol})")
            print(f"Current Price: ${recommendation.current_price:.2f}")
            print(f"Recommendation: {recommendation.recommendation.value.upper()}")
            print(f"Confidence: {recommendation.confidence_score}/10")
            print(f"Technical Analysis: {recommendation.technical_analysis}")
            print(f"News Sentiment: {recommendation.news_sentiment}")
            print(f"Recent News Count: {len(recommendation.recent_news)}")
            print(f"Guru Recommendations: {len(recommendation.guru_recommendations)}")
            print()
            return True
        else:
            print("Failed to generate recommendation")
            return False
            
    except Exception as e:
        print(f"Single stock test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Portfolio Analysis Tests...")
    print()
    
    # Test single stock first
    single_test = test_single_stock_recommendation()
    
    # Test full portfolio analysis
    portfolio_test = test_portfolio_analysis()
    
    print("\n" + "="*50)
    print("TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Single Stock Test: {'PASS' if single_test else 'FAIL'}")
    print(f"Portfolio Test: {'PASS' if portfolio_test else 'FAIL'}")
    
    if single_test and portfolio_test:
        print("\nAll tests passed! Portfolio analysis system is working!")
    else:
        print("\nSome tests failed. Please check the error messages above.")