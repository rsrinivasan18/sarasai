"""
Test the dashboard generation to find the formatting issue
"""

import sys
sys.path.append('.')

from core.portfolio_service import portfolio_service

def test_dashboard_generation():
    """Test dashboard generation for debugging"""
    
    try:
        symbol = "AAPL"
        print(f"Testing dashboard generation for {symbol}...")
        
        # Get recommendation
        recommendation = portfolio_service._generate_stock_recommendation(symbol)
        
        if recommendation:
            print("Recommendation generated successfully")
            print(f"Symbol: {recommendation.symbol}")
            print(f"Name: {recommendation.name}")
            print(f"Price: {recommendation.current_price}")
            print(f"Recommendation: {recommendation.recommendation}")
            print(f"Metrics RSI: {recommendation.metrics.rsi}")
            print(f"Metrics MA50: {recommendation.metrics.moving_avg_50}")
            print(f"Metrics PE: {recommendation.metrics.pe_ratio}")
            print(f"Metrics ROE: {recommendation.metrics.roe}")
            
            # Test formatting
            try:
                rsi_val = f"{recommendation.metrics.rsi:.1f}" if recommendation.metrics.rsi is not None else 'N/A'
                print(f"RSI formatted: {rsi_val}")
                
                ma_50_val = f"${recommendation.metrics.moving_avg_50:.2f}" if recommendation.metrics.moving_avg_50 is not None else 'N/A'
                print(f"MA50 formatted: {ma_50_val}")
                
                pe_ratio_val = f"{recommendation.metrics.pe_ratio:.1f}" if recommendation.metrics.pe_ratio is not None else 'N/A'
                print(f"PE formatted: {pe_ratio_val}")
                
                print("All formatting tests passed!")
                return True
                
            except Exception as format_error:
                print(f"Formatting error: {format_error}")
                return False
        else:
            print("Failed to generate recommendation")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_dashboard_generation()