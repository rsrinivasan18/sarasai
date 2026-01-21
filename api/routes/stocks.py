"""
Sarasai - Stock Routes
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from typing import List

from core.models import StockData, StockListItem
from core.services import stock_service

router = APIRouter(prefix="/stocks", tags=["stocks"])


# IMPORTANT: Specific routes BEFORE dynamic routes!


@router.get("/table", response_class=HTMLResponse)
def stocks_table():
    """
    Display all stocks in a nice HTML table
    """
    stocks = stock_service.list_stocks()

    # Build HTML table
    html = (
        """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sarasai - Stock List</title>
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
                max-width: 1200px;
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
            .header-title {
                color: #333;
                margin-bottom: 20px;
            }
            .stats {
                text-align: center;
                margin-bottom: 20px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header-title">🦢 Sarasai - Stock Portfolio</h1>
            <div class="stats">
                <strong>Total Stocks:</strong> """
        + str(len(stocks))
        + """ | 
                <strong>Data Source:</strong> Mock CSV
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Currency</th>
                        <th>Exchange</th>
                    </tr>
                </thead>
                <tbody>
    """
    )

    for stock in stocks:
        html += f"""
                    <tr>
                        <td class="symbol">{stock.symbol}</td>
                        <td>{stock.name}</td>
                        <td class="price">{stock.price:,.2f}</td>
                        <td>{stock.currency}</td>
                        <td><span class="exchange">{stock.exchange}</span></td>
                    </tr>
        """

    html += """
                </tbody>
            </table>
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
