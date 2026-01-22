"""
Sarasai - Stock Routes
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import List

from core.models import StockData, StockListItem
from core.services import stock_service
from datetime import datetime


router = APIRouter(prefix="/stocks", tags=["stocks"])


# IMPORTANT: Specific routes BEFORE dynamic routes!


@router.get("/table", response_class=HTMLResponse)
def stocks_table():
    """
    Display all stocks in a nice HTML table with LIVE data
    """
    # Get list of symbols from CSV
    symbols = stock_service.get_available_symbols()

    # Fetch live data for each (this will use cache/fallback as needed)
    stocks_data = []
    for symbol in symbols:
        try:
            stock = stock_service.get_stock(symbol)
            stocks_data.append(
                {
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "price": stock.current_price,
                    "currency": stock.currency,
                    "exchange": stock.exchange,
                    "source": stock.data_source,
                }
            )
        except:
            # If fails, skip this stock
            continue

    # Build HTML table
    html = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sarasai - Live Stock Data</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            h1 {
                text-align: center;
                margin-bottom: 30px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background: white;
            }
            th {
                background: #667eea;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 1px;
            }
            td {
                padding: 12px 15px;
                border-bottom: 1px solid #f0f0f0;
                color: #333;
            }
            tr:hover {
                background: #f8f9ff;
            }
            .price {
                font-weight: bold;
                color: #667eea;
                font-size: 16px;
            }
            .symbol {
                font-weight: 600;
                color: #764ba2;
            }
            .exchange {
                background: #f0f0f0;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
                color: #666;
            }
            .live {
                background: #10b981;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
            }
            .csv {
                background: #f59e0b;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 10px;
                font-weight: 600;
            }
            .header-title {
                color: #333;
                margin-bottom: 20px;
            }
            .stats {
                text-align: center;
                margin-bottom: 20px;
                color: #666;
            }
            .refresh-note {
                text-align: center;
                margin-top: 20px;
                color: #999;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header-title">🦢 Sarasai - Live Stock Portfolio</h1>
            <div class="stats">
                <strong>Total Stocks:</strong> """
        + str(len(stocks_data))
        + """ | 
                <strong>Last Updated:</strong> """
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + """
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Currency</th>
                        <th>Exchange</th>
                        <th>Source</th>
                    </tr>
                </thead>
                <tbody>
    """
    )

    for stock in stocks_data:
        source_class = "live" if "live" in stock["source"].lower() else "csv"
        source_label = "LIVE" if "live" in stock["source"].lower() else "CSV"

        html += f"""
                    <tr>
                        <td class="symbol">{stock["symbol"]}</td>
                        <td>{stock["name"]}</td>
                        <td class="price">{stock["price"]:,.2f}</td>
                        <td>{stock["currency"]}</td>
                        <td><span class="exchange">{stock["exchange"]}</span></td>
                        <td><span class="{source_class}">{source_label}</span></td>
                    </tr>
        """

    html += """
                </tbody>
            </table>
            <div class="refresh-note">
                💡 Refresh page to update prices. Live data from Alpha Vantage API.
            </div>
        </div>
    </body>
    </html>
    """

    return html


@router.get("", response_model=dict)
def list_stocks():
    """
    List all available stocks from CSV
    """
    stocks = stock_service.list_stocks()

    return {
        "total": len(stocks),
        "source": "data/mock_stocks.csv",
        "stocks": [stock.model_dump() for stock in stocks],
    }


# Dynamic route MUST come LAST
@router.get("/{symbol}", response_model=StockData)
def get_stock(symbol: str):
    """
    Get stock data by symbol

    Available symbols:
    - US: AAPL, GOOGL, MSFT, TSLA
    - India: RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ITC.NS, SBIN.NS
    """
    return stock_service.get_stock(symbol)
