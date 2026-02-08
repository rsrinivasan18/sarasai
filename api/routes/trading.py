"""
Professional Trading API Routes
Real trading operations, orders, and portfolio management
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/trading", tags=["Professional Trading"])

# Data Models
class Position(BaseModel):
    id: str
    symbol: str
    name: str
    shares: float
    avg_price: float
    current_price: float
    market_value: float
    gain_loss: float
    gain_loss_percent: float
    recommendation: str
    last_updated: datetime

class Order(BaseModel):
    id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    order_type: str  # "MARKET", "LIMIT", "STOP"
    price: Optional[float] = None
    status: str  # "PENDING", "FILLED", "CANCELLED"
    created_at: datetime
    filled_at: Optional[datetime] = None

class WatchlistItem(BaseModel):
    id: str
    symbol: str
    name: str
    price: float
    change_percent: float
    added_at: datetime
    alerts: List[dict] = []

class PortfolioMetrics(BaseModel):
    total_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    day_gain_loss: float
    day_gain_loss_percent: float
    cash_balance: float
    buying_power: float
    positions_count: int

class CreateOrderRequest(BaseModel):
    symbol: str
    side: str
    quantity: float
    order_type: str = "MARKET"
    price: Optional[float] = None

class AddToWatchlistRequest(BaseModel):
    symbol: str
    price_alert: Optional[float] = None

# In-memory storage (in production, use database)
positions_db = {}
orders_db = {}
watchlist_db = {}
user_cash_balance = 10000.00

# Mock data initialization
def init_mock_data():
    global positions_db, orders_db, watchlist_db
    
    # Sample positions
    positions_db = {
        "pos_1": Position(
            id="pos_1",
            symbol="AAPL",
            name="Apple Inc.",
            shares=100,
            avg_price=150.00,
            current_price=185.92,
            market_value=18592.00,
            gain_loss=3592.00,
            gain_loss_percent=23.95,
            recommendation="BUY",
            last_updated=datetime.now()
        ),
        "pos_2": Position(
            id="pos_2",
            symbol="GOOGL",
            name="Alphabet Inc.",
            shares=50,
            avg_price=120.00,
            current_price=141.80,
            market_value=7090.00,
            gain_loss=1090.00,
            gain_loss_percent=18.17,
            recommendation="HOLD",
            last_updated=datetime.now()
        ),
        "pos_3": Position(
            id="pos_3",
            symbol="MSFT",
            name="Microsoft Corporation",
            shares=75,
            avg_price=300.00,
            current_price=378.91,
            market_value=28418.25,
            gain_loss=5918.25,
            gain_loss_percent=26.30,
            recommendation="BUY",
            last_updated=datetime.now()
        )
    }

    # Sample watchlist
    watchlist_db = {
        "watch_1": WatchlistItem(
            id="watch_1",
            symbol="TSLA",
            name="Tesla, Inc.",
            price=242.84,
            change_percent=2.45,
            added_at=datetime.now() - timedelta(days=2)
        ),
        "watch_2": WatchlistItem(
            id="watch_2",
            symbol="NVDA",
            name="NVIDIA Corporation",
            price=875.50,
            change_percent=-1.23,
            added_at=datetime.now() - timedelta(days=5)
        )
    }

# Initialize mock data on startup
init_mock_data()

# Portfolio Endpoints
@router.get("/portfolio/positions", response_model=List[Position])
async def get_positions():
    """Get all portfolio positions"""
    return list(positions_db.values())

@router.get("/portfolio/metrics", response_model=PortfolioMetrics)
async def get_portfolio_metrics():
    """Get portfolio summary metrics"""
    positions = list(positions_db.values())
    
    total_value = sum(p.market_value for p in positions)
    total_gain_loss = sum(p.gain_loss for p in positions)
    total_cost = total_value - total_gain_loss
    total_gain_loss_percent = (total_gain_loss / total_cost * 100) if total_cost > 0 else 0
    
    # Simulate day's change (10% of total change)
    day_gain_loss = total_gain_loss * 0.1
    day_gain_loss_percent = total_gain_loss_percent * 0.1
    
    return PortfolioMetrics(
        total_value=total_value,
        total_gain_loss=total_gain_loss,
        total_gain_loss_percent=total_gain_loss_percent,
        day_gain_loss=day_gain_loss,
        day_gain_loss_percent=day_gain_loss_percent,
        cash_balance=user_cash_balance,
        buying_power=user_cash_balance * 2,  # 2x leverage
        positions_count=len(positions)
    )

@router.post("/portfolio/positions")
async def add_position(symbol: str, shares: float, price: float):
    """Add a new position to portfolio"""
    position_id = f"pos_{len(positions_db) + 1}"
    
    # Simulate getting current price and company name
    current_price = price * (1 + (0.05 * (1 if shares > 0 else -1)))  # 5% change simulation
    
    position = Position(
        id=position_id,
        symbol=symbol.upper(),
        name=f"{symbol.upper()} Company",  # In real app, fetch from API
        shares=shares,
        avg_price=price,
        current_price=current_price,
        market_value=shares * current_price,
        gain_loss=shares * (current_price - price),
        gain_loss_percent=((current_price - price) / price * 100),
        recommendation="HOLD",
        last_updated=datetime.now()
    )
    
    positions_db[position_id] = position
    
    # Update cash balance
    global user_cash_balance
    user_cash_balance -= (shares * price)
    
    return {"message": f"Added position for {symbol}", "position": position}

# Order Management
@router.get("/orders", response_model=List[Order])
async def get_orders(status: Optional[str] = None):
    """Get orders, optionally filtered by status"""
    orders = list(orders_db.values())
    
    if status:
        orders = [o for o in orders if o.status.upper() == status.upper()]
    
    return orders

@router.post("/orders")
async def create_order(order_request: CreateOrderRequest):
    """Create a new trading order"""
    order_id = str(uuid.uuid4())
    
    order = Order(
        id=order_id,
        symbol=order_request.symbol.upper(),
        side=order_request.side.upper(),
        quantity=order_request.quantity,
        order_type=order_request.order_type.upper(),
        price=order_request.price,
        status="PENDING",
        created_at=datetime.now()
    )
    
    orders_db[order_id] = order
    
    # Simulate order processing (in real app, send to broker)
    if order.order_type == "MARKET":
        # Market orders fill immediately
        order.status = "FILLED"
        order.filled_at = datetime.now()
        
        # Update portfolio if it's a buy/sell of existing position
        if order.side == "BUY":
            # Add to existing position or create new one
            await add_position(order.symbol, order.quantity, order.price or 100.0)
        
    return {"message": f"Order created for {order.symbol}", "order": order}

@router.put("/orders/{order_id}/cancel")
async def cancel_order(order_id: str):
    """Cancel a pending order"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    if order.status != "PENDING":
        raise HTTPException(status_code=400, detail="Can only cancel pending orders")
    
    order.status = "CANCELLED"
    
    return {"message": f"Order {order_id} cancelled", "order": order}

# Watchlist Management
@router.get("/watchlist", response_model=List[WatchlistItem])
async def get_watchlist():
    """Get user's watchlist"""
    return list(watchlist_db.values())

@router.post("/watchlist")
async def add_to_watchlist(request: AddToWatchlistRequest):
    """Add stock to watchlist"""
    watch_id = f"watch_{len(watchlist_db) + 1}"
    
    # Simulate getting current price and company name
    current_price = 100.0 + (len(watchlist_db) * 10)  # Mock price
    
    watchlist_item = WatchlistItem(
        id=watch_id,
        symbol=request.symbol.upper(),
        name=f"{request.symbol.upper()} Company",
        price=current_price,
        change_percent=0.0,
        added_at=datetime.now(),
        alerts=[]
    )
    
    if request.price_alert:
        watchlist_item.alerts.append({
            "type": "price",
            "value": request.price_alert,
            "condition": "above" if request.price_alert > current_price else "below"
        })
    
    watchlist_db[watch_id] = watchlist_item
    
    return {"message": f"Added {request.symbol} to watchlist", "item": watchlist_item}

@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(item_id: str):
    """Remove stock from watchlist"""
    if item_id not in watchlist_db:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    item = watchlist_db.pop(item_id)
    
    return {"message": f"Removed {item.symbol} from watchlist"}

# Market Data & Analysis
@router.get("/market/indices")
async def get_market_indices():
    """Get major market indices"""
    return [
        {"name": "S&P 500", "symbol": "SPY", "value": 4150.25, "change": 0.62},
        {"name": "NASDAQ 100", "symbol": "QQQ", "value": 12850.80, "change": -0.34},
        {"name": "Dow Jones", "symbol": "DIA", "value": 34195.40, "change": 0.38},
        {"name": "Russell 2000", "symbol": "IWM", "value": 1895.40, "change": 1.23}
    ]

@router.get("/market/movers")
async def get_market_movers():
    """Get top market movers (gainers and losers)"""
    return {
        "gainers": [
            {"symbol": "NVDA", "name": "NVIDIA Corp", "price": 875.50, "change": 12.45},
            {"symbol": "AMD", "name": "AMD Inc", "price": 165.20, "change": 8.90},
            {"symbol": "TSLA", "name": "Tesla Inc", "price": 242.84, "change": 7.35},
            {"symbol": "AAPL", "name": "Apple Inc", "price": 185.92, "change": 5.20}
        ],
        "losers": [
            {"symbol": "NFLX", "name": "Netflix Inc", "price": 425.30, "change": -6.80},
            {"symbol": "META", "name": "Meta Platforms", "price": 315.60, "change": -4.25},
            {"symbol": "GOOGL", "name": "Alphabet Inc", "price": 141.80, "change": -3.15},
            {"symbol": "AMZN", "name": "Amazon Inc", "price": 145.20, "change": -2.90}
        ]
    }

@router.get("/analytics/performance")
async def get_portfolio_performance(period: str = "1M"):
    """Get portfolio performance data for charts"""
    import random
    from datetime import datetime, timedelta
    
    # Generate mock performance data
    periods = {
        "1D": 24,    # 24 hours
        "1W": 7,     # 7 days  
        "1M": 30,    # 30 days
        "3M": 90,    # 90 days
        "1Y": 365    # 365 days
    }
    
    days = periods.get(period, 30)
    base_value = sum(p.market_value for p in positions_db.values())
    
    data = []
    current_value = base_value
    
    for i in range(days, 0, -1):
        date = datetime.now() - timedelta(days=i)
        
        # Simulate price movement
        change = (random.random() - 0.5) * 0.02  # ±1% daily change
        current_value *= (1 + change)
        
        data.append({
            "date": date.isoformat(),
            "value": round(current_value, 2)
        })
    
    return {"period": period, "data": data}

@router.get("/analytics/risk")
async def get_risk_metrics():
    """Get portfolio risk analysis"""
    positions = list(positions_db.values())
    
    if not positions:
        return {"error": "No positions for risk analysis"}
    
    total_value = sum(p.market_value for p in positions)
    
    # Calculate concentration risk
    largest_position = max(p.market_value for p in positions)
    concentration_risk = (largest_position / total_value) * 100
    
    # Mock risk metrics
    return {
        "portfolio_beta": 1.25,
        "sharpe_ratio": 1.8,
        "max_drawdown": -8.5,
        "var_95": -2450.00,  # Value at Risk 95%
        "concentration_risk": round(concentration_risk, 2),
        "diversification_score": 7.2,
        "risk_rating": "MODERATE"
    }

# Real-time Updates
@router.get("/realtime/updates")
async def get_realtime_updates():
    """Get real-time portfolio updates"""
    import random
    
    # Simulate price updates for positions
    updates = []
    
    for position in positions_db.values():
        # Simulate small price changes
        price_change = (random.random() - 0.5) * 0.01  # ±0.5% change
        new_price = position.current_price * (1 + price_change)
        
        position.current_price = new_price
        position.market_value = position.shares * new_price
        position.gain_loss = position.shares * (new_price - position.avg_price)
        position.gain_loss_percent = ((new_price - position.avg_price) / position.avg_price) * 100
        position.last_updated = datetime.now()
        
        updates.append({
            "symbol": position.symbol,
            "price": new_price,
            "change": price_change * 100,
            "timestamp": position.last_updated.isoformat()
        })
    
    return {"updates": updates, "timestamp": datetime.now().isoformat()}

# Advanced Features
@router.post("/analytics/backtest")
async def run_backtest(strategy: dict):
    """Run portfolio backtesting (placeholder)"""
    return {
        "strategy": strategy,
        "results": {
            "total_return": 15.5,
            "sharpe_ratio": 1.2,
            "max_drawdown": -12.3,
            "win_rate": 65.0,
            "total_trades": 45
        }
    }

@router.get("/research/recommendations/{symbol}")
async def get_stock_recommendations(symbol: str):
    """Get detailed stock analysis and recommendations"""
    return {
        "symbol": symbol.upper(),
        "recommendation": "BUY",
        "target_price": 200.00,
        "confidence": 8.5,
        "analyst_ratings": {
            "strong_buy": 8,
            "buy": 5,
            "hold": 2,
            "sell": 1,
            "strong_sell": 0
        },
        "key_metrics": {
            "pe_ratio": 25.4,
            "peg_ratio": 1.2,
            "price_to_book": 3.8,
            "debt_to_equity": 0.85
        },
        "technical_indicators": {
            "rsi": 65.2,
            "macd": "bullish",
            "moving_avg_50": 175.30,
            "moving_avg_200": 165.80
        }
    }