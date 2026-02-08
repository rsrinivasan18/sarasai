"""
Debug the metrics formatting issue
"""

import sys
sys.path.append('.')

from core.metrics_service import metrics_service

def test_metrics():
    print("Testing metrics service...")
    
    try:
        # Test AAPL metrics
        print("Getting metrics for AAPL...")
        metrics = metrics_service.get_stock_metrics("AAPL")
        
        if metrics:
            print(f"Success! Got metrics for AAPL")
            print(f"RSI: {metrics.rsi}")
            print(f"PE Ratio: {metrics.pe_ratio}")
            print(f"ROE: {metrics.roe}")
            print(f"Price Change 1M: {metrics.price_change_1m}")
            
            # Test formatting
            print("\nTesting formatting...")
            try:
                rsi_str = f"{metrics.rsi:.1f}" if metrics.rsi is not None else "N/A"
                print(f"RSI formatted: {rsi_str}")
                
                pe_str = f"{metrics.pe_ratio:.1f}" if metrics.pe_ratio is not None else "N/A"
                print(f"PE formatted: {pe_str}")
                
                roe_str = f"{metrics.roe:.1%}" if metrics.roe is not None else "N/A"
                print(f"ROE formatted: {roe_str}")
                
                print("All formatting successful!")
                
            except Exception as format_error:
                print(f"Formatting error: {format_error}")
        
        else:
            print("Failed to get metrics")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metrics()