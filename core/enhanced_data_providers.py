"""
Enhanced Data Providers for Multi-Market Support
Supports SGX, NYSE, NASDAQ, NSE markets with real portfolio persistence
"""

import json
import csv
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid
import random

from .data_providers import PortfolioDataProvider, MarketDataProvider
from .config_service import config_service


class MultiMarketDataProvider(MarketDataProvider):
    """Enhanced market data provider with multi-market support"""
    
    def __init__(self):
        self.markets_config = config_service.load_config("markets")
        self.stock_universe = self._load_stock_universe()
        
    def _load_stock_universe(self) -> pd.DataFrame:
        """Load comprehensive stock universe from CSV"""
        try:
            csv_path = Path(__file__).parent.parent / "data" / "stock_universe.csv"
            df = pd.read_csv(csv_path)
            
            # Explicitly convert numeric columns to Python float
            numeric_columns = ['market_cap_millions', 'pe_ratio', 'dividend_yield']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].astype('float64')
            
            # Convert string columns to ensure they're Python strings
            string_columns = ['symbol', 'name', 'sector', 'market', 'currency', 'description']
            for col in string_columns:
                if col in df.columns:
                    df[col] = df[col].astype('str')
            
            print(f"Loaded {len(df)} stocks from {len(df['market'].unique())} markets")
            return df
        except Exception as e:
            print(f"Error loading stock universe: {e}")
            return pd.DataFrame()
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """Get all supported markets"""
        markets = []
        for market_code, market_info in self.markets_config.get("markets", {}).items():
            markets.append({
                "code": market_code,
                "name": market_info.get("name"),
                "currency": market_info.get("currency"),
                "timezone": market_info.get("timezone"),
                "market_hours": market_info.get("market_hours"),
                "status": self._get_market_status(market_code)
            })
        return markets
    
    def _get_market_status(self, market_code: str) -> str:
        """Get current market status (open/closed)"""
        # Simplified - in real implementation, check actual market hours
        import datetime
        now = datetime.datetime.now()
        if 9 <= now.hour <= 17:
            return "open"
        else:
            return "closed"
    
    def get_stocks_by_market(self, market_code: str) -> List[Dict[str, Any]]:
        """Get all stocks for a specific market"""
        if self.stock_universe.empty:
            return []
            
        market_stocks = self.stock_universe[self.stock_universe['market'] == market_code]
        return market_stocks.to_dict('records')
    
    def search_stocks(self, query: str, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search stocks across markets or within specific market"""
        if self.stock_universe.empty:
            return []
            
        df = self.stock_universe
        if market:
            df = df[df['market'] == market]
            
        # Search in symbol and name
        mask = (df['symbol'].str.contains(query, case=False, na=False) | 
                df['name'].str.contains(query, case=False, na=False))
        
        results = df[mask].head(10).to_dict('records')
        
        # Add mock current prices
        for stock in results:
            stock['current_price'] = self._generate_mock_price(stock['symbol'])
            stock['change_percent'] = random.uniform(-3.0, 3.0)
            
        return results
    
    def _generate_mock_price(self, symbol: str) -> float:
        """Generate realistic mock prices based on symbol"""
        # Base prices for realistic simulation
        base_prices = {
            # Singapore stocks (SGD)
            "DBS.SI": 28.50, "O39.SI": 12.80, "U11.SI": 26.90,
            "C6L.SI": 5.20, "S68.SI": 7.45,
            
            # US stocks (USD)  
            "AAPL": 185.00, "GOOGL": 141.00, "MSFT": 380.00,
            "TSLA": 220.00, "NVDA": 450.00, "AMZN": 145.00,
            
            # Indian stocks (INR)
            "RELIANCE.NS": 2450.00, "TCS.NS": 3520.00, "HDFCBANK.NS": 1680.00,
            "INFY.NS": 1450.00, "ITC.NS": 415.00
        }
        
        if symbol in base_prices:
            base_price = base_prices[symbol]
        else:
            # Generate based on market
            if ".SI" in symbol:
                base_price = random.uniform(1.0, 50.0)  # SGD range
            elif ".NS" in symbol:
                base_price = random.uniform(100.0, 5000.0)  # INR range
            else:
                base_price = random.uniform(10.0, 500.0)  # USD range
        
        # Add some randomness
        variance = random.uniform(-0.05, 0.05)  # ±5%
        return round(base_price * (1 + variance), 2)
    
    def get_market_indices(self) -> List[Dict[str, Any]]:
        """Get indices for all markets"""
        indices = []
        for market_code, market_info in self.markets_config.get("markets", {}).items():
            market_indices = market_info.get("major_indices", [])
            for index in market_indices:
                indices.append({
                    "symbol": index["symbol"],
                    "name": index["name"],
                    "market": market_code,
                    "currency": market_info.get("currency"),
                    "value": self._generate_mock_price(index["symbol"]),
                    "change_percent": random.uniform(-2.0, 2.0),
                    "last_updated": datetime.now().isoformat()
                })
        return indices
    
    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current stock price with market context"""
        # Find stock in universe
        if not self.stock_universe.empty:
            stock_row = self.stock_universe[self.stock_universe['symbol'] == symbol]
            if not stock_row.empty:
                stock_info = stock_row.iloc[0]
                return {
                    "symbol": symbol,
                    "name": str(stock_info["name"]),
                    "market": str(stock_info["market"]),
                    "currency": str(stock_info["currency"]),
                    "sector": str(stock_info["sector"]),
                    "price": float(self._generate_mock_price(symbol)),
                    "change_percent": float(random.uniform(-5.0, 5.0)),
                    "last_updated": datetime.now().isoformat(),
                    "source": "mock"
                }
        
        # Fallback for unknown symbols
        return {
            "symbol": symbol,
            "price": float(self._generate_mock_price(symbol)),
            "change_percent": float(random.uniform(-3.0, 3.0)),
            "last_updated": datetime.now().isoformat(),
            "source": "mock"
        }

    def get_market_status(self) -> Dict[str, str]:
        """Get comprehensive market status"""
        statuses = {}
        for market_code in self.markets_config.get("markets", {}):
            statuses[market_code] = self._get_market_status(market_code)
        
        return {
            "markets": statuses,
            "timezone": "Asia/Singapore",
            "last_updated": datetime.now().isoformat()
        }


class PersistentPortfolioProvider(PortfolioDataProvider):
    """Enhanced portfolio provider with real persistence"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.portfolio_file = self.data_dir / "user_portfolio.json"
        self.transactions_file = self.data_dir / "transactions_history.json"
        self.market_provider = MultiMarketDataProvider()
        
        # Initialize files if they don't exist
        self._initialize_data_files()
        
    def _initialize_data_files(self):
        """Initialize portfolio and transaction files"""
        self.data_dir.mkdir(exist_ok=True)
        
        if not self.portfolio_file.exists():
            initial_portfolio = {
                "positions": [],
                "cash_balances": {
                    "SGD": 10000.00,
                    "USD": 0.00,
                    "INR": 0.00
                },
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            self._save_portfolio(initial_portfolio)
            print(f"Created new portfolio file: {self.portfolio_file}")
        
        if not self.transactions_file.exists():
            initial_transactions = {
                "transactions": [],
                "created_at": datetime.now().isoformat()
            }
            with open(self.transactions_file, 'w') as f:
                json.dump(initial_transactions, f, indent=2)
            print(f"Created new transactions file: {self.transactions_file}")
    
    def _load_portfolio(self) -> Dict[str, Any]:
        """Load portfolio from file"""
        try:
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return {"positions": [], "cash_balances": {"SGD": 10000.00}}
    
    def _save_portfolio(self, portfolio_data: Dict[str, Any]):
        """Save portfolio to file"""
        portfolio_data["last_updated"] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w') as f:
            json.dump(portfolio_data, f, indent=2)
    
    def get_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's portfolio positions with real-time prices"""
        portfolio = self._load_portfolio()
        positions = portfolio.get("positions", [])
        
        # Enhance with current market data
        enhanced_positions = []
        for position in positions:
            # Get current price
            price_data = self.market_provider.get_stock_price(position["symbol"])
            
            if price_data:
                current_price = price_data["price"]
                market_value = position["shares"] * current_price
                total_cost = position["shares"] * position["avg_price"]
                gain_loss = market_value - total_cost
                gain_loss_percent = (gain_loss / total_cost) * 100 if total_cost > 0 else 0
                
                enhanced_position = {
                    **position,
                    "current_price": current_price,
                    "market_value": round(market_value, 2),
                    "gain_loss": round(gain_loss, 2),
                    "gain_loss_percent": round(gain_loss_percent, 2),
                    "market": price_data.get("market", "Unknown"),
                    "currency": price_data.get("currency", "USD"),
                    "sector": price_data.get("sector", "Unknown"),
                    "last_updated": price_data["last_updated"]
                }
                enhanced_positions.append(enhanced_position)
        
        return enhanced_positions
    
    def add_position(self, user_id: str, position: Dict[str, Any]) -> str:
        """Add new position to portfolio"""
        portfolio = self._load_portfolio()
        
        position_id = str(uuid.uuid4())
        new_position = {
            "id": position_id,
            "symbol": position["symbol"].upper(),
            "shares": float(position["shares"]),
            "avg_price": float(position.get("price", position.get("avg_price", 0))),
            "purchase_date": position.get("date", datetime.now().strftime("%Y-%m-%d")),
            "created_at": datetime.now().isoformat()
        }
        
        # Add stock info from universe
        price_data = self.market_provider.get_stock_price(position["symbol"])
        if price_data:
            new_position["name"] = price_data.get("name", position["symbol"])
            new_position["market"] = price_data.get("market", "Unknown")
            new_position["currency"] = price_data.get("currency", "USD")
        
        portfolio["positions"].append(new_position)
        self._save_portfolio(portfolio)
        
        # Log transaction
        self._log_transaction("BUY", new_position)
        
        print(f"Added position: {new_position['symbol']} x {new_position['shares']}")
        return position_id
    
    def _log_transaction(self, action: str, position: Dict[str, Any]):
        """Log transaction to history file"""
        try:
            with open(self.transactions_file, 'r') as f:
                transactions_data = json.load(f)
        except:
            transactions_data = {"transactions": []}
        
        transaction = {
            "id": str(uuid.uuid4()),
            "action": action,
            "symbol": position["symbol"],
            "shares": position["shares"],
            "price": position["avg_price"],
            "total_amount": position["shares"] * position["avg_price"],
            "currency": position.get("currency", "USD"),
            "timestamp": datetime.now().isoformat(),
            "position_id": position.get("id")
        }
        
        transactions_data["transactions"].append(transaction)
        
        with open(self.transactions_file, 'w') as f:
            json.dump(transactions_data, f, indent=2)
    
    def update_position(self, position_id: str, data: Dict[str, Any]) -> bool:
        """Update existing position"""
        portfolio = self._load_portfolio()
        
        for position in portfolio["positions"]:
            if position["id"] == position_id:
                position.update(data)
                position["updated_at"] = datetime.now().isoformat()
                self._save_portfolio(portfolio)
                return True
        
        return False
    
    def delete_position(self, position_id: str) -> bool:
        """Delete position"""
        portfolio = self._load_portfolio()
        
        for i, position in enumerate(portfolio["positions"]):
            if position["id"] == position_id:
                deleted_position = portfolio["positions"].pop(i)
                self._save_portfolio(portfolio)
                
                # Log sale transaction
                self._log_transaction("SELL", deleted_position)
                print(f"Deleted position: {deleted_position['symbol']}")
                return True
        
        return False
    
    def get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        positions = self.get_positions(user_id)
        portfolio = self._load_portfolio()
        
        # Calculate totals by currency
        currency_totals = {}
        total_value_sgd = 0
        total_cost_sgd = 0
        
        for position in positions:
            currency = position.get("currency", "USD")
            market_value = position["market_value"]
            cost = position["shares"] * position["avg_price"]
            
            if currency not in currency_totals:
                currency_totals[currency] = {
                    "market_value": 0,
                    "cost": 0,
                    "gain_loss": 0
                }
            
            currency_totals[currency]["market_value"] += market_value
            currency_totals[currency]["cost"] += cost
            currency_totals[currency]["gain_loss"] += position["gain_loss"]
            
            # Convert to SGD for total (simplified conversion)
            conversion_rate = {"SGD": 1.0, "USD": 1.35, "INR": 0.016}.get(currency, 1.0)
            total_value_sgd += market_value * conversion_rate
            total_cost_sgd += cost * conversion_rate
        
        total_gain_loss_sgd = total_value_sgd - total_cost_sgd
        total_gain_loss_percent = (total_gain_loss_sgd / total_cost_sgd * 100) if total_cost_sgd > 0 else 0
        
        return {
            "total_value_sgd": round(total_value_sgd, 2),
            "total_cost_sgd": round(total_cost_sgd, 2),
            "total_gain_loss_sgd": round(total_gain_loss_sgd, 2),
            "total_gain_loss_percent": round(total_gain_loss_percent, 2),
            "positions_count": len(positions),
            "currency_breakdown": currency_totals,
            "cash_balances": portfolio.get("cash_balances", {}),
            "last_updated": datetime.now().isoformat()
        }


# Update the registry with enhanced providers
def register_enhanced_providers():
    """Register enhanced providers in the global registry"""
    from .data_providers import data_registry
    
    # Register enhanced providers
    data_registry.register_provider("market", MultiMarketDataProvider())
    data_registry.register_provider("portfolio", PersistentPortfolioProvider())
    
    print("Enhanced multi-market providers registered!")


# Auto-register when module is imported
register_enhanced_providers()