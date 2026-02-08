"""
Sarasai Data Providers
Abstract interfaces for data sources - easily swap between config, API, DB, MCP
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path

from .config_service import config_service


class UserDataProvider(ABC):
    """Abstract interface for user data - future: DB, Auth API, MCP"""
    
    @abstractmethod
    def get_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user profile data"""
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user profile"""
        pass
    
    @abstractmethod
    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences and settings"""
        pass


class MarketDataProvider(ABC):
    """Abstract interface for market data - future: Real-time API, MCP"""
    
    @abstractmethod
    def get_market_indices(self) -> List[Dict[str, Any]]:
        """Get market indices data"""
        pass
    
    @abstractmethod
    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current stock price"""
        pass
    
    @abstractmethod
    def get_market_status(self) -> Dict[str, str]:
        """Get current market status"""
        pass


class PortfolioDataProvider(ABC):
    """Abstract interface for portfolio data - future: DB, Trading API"""
    
    @abstractmethod
    def get_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's portfolio positions"""
        pass
    
    @abstractmethod
    def add_position(self, user_id: str, position: Dict[str, Any]) -> str:
        """Add new position, return position ID"""
        pass
    
    @abstractmethod
    def update_position(self, position_id: str, data: Dict[str, Any]) -> bool:
        """Update existing position"""
        pass
    
    @abstractmethod
    def delete_position(self, position_id: str) -> bool:
        """Delete position"""
        pass


class UIDataProvider(ABC):
    """Abstract interface for UI data - future: CMS, i18n API"""
    
    @abstractmethod
    def get_branding(self) -> Dict[str, Any]:
        """Get branding information"""
        pass
    
    @abstractmethod
    def get_ui_text(self, section: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """Get UI text/labels"""
        pass
    
    @abstractmethod
    def get_navigation_items(self) -> List[Dict[str, Any]]:
        """Get navigation menu items"""
        pass


# ===== CURRENT IMPLEMENTATIONS (CONFIG-BASED) =====

class ConfigUserDataProvider(UserDataProvider):
    """Config-based user data provider - current implementation"""
    
    def get_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user from config"""
        user_config = config_service.get_user_config()
        
        if user_id and user_id in user_config.get("demo_users", {}):
            user_data = user_config["demo_users"][user_id].copy()
            user_data["id"] = user_id
            return user_data
        
        # Return default user (you!)
        default_user = user_config.get("default_user", {}).copy()
        default_user["id"] = "default"
        return default_user
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user - currently just logs, future: DB update"""
        print(f"[ConfigUserDataProvider] Update user {user_id}: {data}")
        # TODO: When moving to DB, implement actual update
        return True
    
    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user settings"""
        user_config = config_service.get_user_config()
        defaults = user_config.get("user_defaults", {})
        
        # Future: merge with user-specific overrides from DB
        return {
            "timezone": defaults.get("default_timezone", "Asia/Singapore"),
            "currency": defaults.get("default_currency", "SGD"),
            "theme": "light",
            "auto_refresh": True
        }


class ConfigMarketDataProvider(MarketDataProvider):
    """Config-based market data provider - will be enhanced with APIs"""
    
    def get_market_indices(self) -> List[Dict[str, Any]]:
        """Get market indices from config"""
        market_config = config_service.get_market_config()
        indices = market_config.get("market_indices", [])
        
        # Add mock real-time data
        import random
        for index in indices:
            # Simulate price movement
            base_value = index.get("default_value", 1000)
            change_percent = random.uniform(-2.0, 2.0)
            current_value = base_value * (1 + change_percent / 100)
            
            index.update({
                "value": round(current_value, 2),
                "change": round(change_percent, 2),
                "last_updated": datetime.now().isoformat()
            })
        
        return indices
    
    def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock price - future: real API call"""
        # Mock implementation - future: call external API
        import random
        base_prices = {
            "DBS.SI": 28.50, "O39.SI": 12.80, "U11.SI": 26.90,
            "AAPL": 185.00, "GOOGL": 141.00, "MSFT": 380.00
        }
        
        if symbol in base_prices:
            base_price = base_prices[symbol]
            change_percent = random.uniform(-3.0, 3.0)
            current_price = base_price * (1 + change_percent / 100)
            
            return {
                "symbol": symbol,
                "price": round(current_price, 2),
                "change_percent": round(change_percent, 2),
                "last_updated": datetime.now().isoformat(),
                "source": "mock"  # Future: "yahoo", "alpha_vantage", "mcp"
            }
        
        return None
    
    def get_market_status(self) -> Dict[str, str]:
        """Get market status"""
        # Future: check actual market hours
        now = datetime.now()
        if 9 <= now.hour <= 17:
            return {
                "status": "open",
                "message": "Market Open",
                "timezone": "SGT"
            }
        else:
            return {
                "status": "closed", 
                "message": "Market Closed",
                "timezone": "SGT"
            }


class ConfigPortfolioDataProvider(PortfolioDataProvider):
    """Config-based portfolio provider - future: database"""
    
    def __init__(self):
        self.data_file = Path(__file__).parent.parent / "data" / "sample_portfolio.json"
        self._load_sample_data()
    
    def _load_sample_data(self):
        """Load sample portfolio data"""
        try:
            with open(self.data_file, 'r') as f:
                self.sample_data = json.load(f)
        except Exception:
            self.sample_data = {"sample_positions": [], "sample_watchlist": []}
    
    def get_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get portfolio positions"""
        positions = self.sample_data.get("sample_positions", [])
        
        # Add real-time prices
        for pos in positions:
            price_data = market_provider.get_stock_price(pos["symbol"])
            if price_data:
                pos.update({
                    "current_price": price_data["price"],
                    "market_value": pos["shares"] * price_data["price"],
                    "gain_loss": (price_data["price"] - pos["avg_price"]) * pos["shares"],
                    "gain_loss_percent": ((price_data["price"] - pos["avg_price"]) / pos["avg_price"]) * 100,
                    "last_updated": price_data["last_updated"]
                })
        
        return positions
    
    def add_position(self, user_id: str, position: Dict[str, Any]) -> str:
        """Add new position"""
        import uuid
        position_id = str(uuid.uuid4())
        position["id"] = position_id
        position["created_at"] = datetime.now().isoformat()
        
        # Future: save to database
        print(f"[ConfigPortfolioDataProvider] Added position: {position}")
        return position_id
    
    def update_position(self, position_id: str, data: Dict[str, Any]) -> bool:
        """Update position"""
        print(f"[ConfigPortfolioDataProvider] Update position {position_id}: {data}")
        return True
    
    def delete_position(self, position_id: str) -> bool:
        """Delete position"""
        print(f"[ConfigPortfolioDataProvider] Delete position {position_id}")
        return True


class ConfigUIDataProvider(UIDataProvider):
    """Config-based UI provider - future: CMS, i18n"""
    
    def get_branding(self) -> Dict[str, Any]:
        """Get branding from config"""
        return config_service.get_branding()
    
    def get_ui_text(self, section: Optional[str] = None, language: str = "en") -> Dict[str, Any]:
        """Get UI text - future: support multiple languages"""
        # Future: check language parameter and load appropriate config
        return config_service.get_ui_text(section)
    
    def get_navigation_items(self) -> List[Dict[str, Any]]:
        """Get navigation items"""
        ui_text = config_service.get_ui_text()
        navigation = ui_text.get("navigation", {})
        sections = ui_text.get("sections", {})
        
        # Build structured navigation
        nav_items = [
            {
                "section": sections.get("trading", "Trading"),
                "items": [
                    {"key": "dashboard", "label": navigation.get("dashboard", "Dashboard"), "icon": "fas fa-tachometer-alt"},
                    {"key": "portfolio", "label": navigation.get("portfolio", "Portfolio"), "icon": "fas fa-briefcase"},
                    {"key": "watchlist", "label": navigation.get("watchlist", "Watchlist"), "icon": "fas fa-eye"},
                    {"key": "orders", "label": navigation.get("orders", "Orders"), "icon": "fas fa-list"}
                ]
            },
            {
                "section": sections.get("research", "Research"),
                "items": [
                    {"key": "discover", "label": navigation.get("discover", "Discover"), "icon": "fas fa-search"},
                    {"key": "screener", "label": navigation.get("screener", "Stock Screener"), "icon": "fas fa-filter"},
                    {"key": "market", "label": navigation.get("market", "Market News"), "icon": "fas fa-globe"}
                ]
            }
        ]
        
        return nav_items


# ===== SERVICE REGISTRY - EASY TO SWAP IMPLEMENTATIONS =====

class DataProviderRegistry:
    """Registry for data providers - easy to swap implementations"""
    
    def __init__(self):
        self.providers = {}
        self._setup_default_providers()
    
    def _setup_default_providers(self):
        """Setup default config-based providers"""
        self.providers = {
            "user": ConfigUserDataProvider(),
            "market": ConfigMarketDataProvider(), 
            "portfolio": ConfigPortfolioDataProvider(),
            "ui": ConfigUIDataProvider()
        }
    
    def get_provider(self, provider_type: str):
        """Get provider by type"""
        return self.providers.get(provider_type)
    
    def register_provider(self, provider_type: str, provider):
        """Register new provider implementation"""
        self.providers[provider_type] = provider
        print(f"[DataProviderRegistry] Registered {provider_type} provider: {provider.__class__.__name__}")


# Global registry
data_registry = DataProviderRegistry()

# Convenience accessors
user_provider = data_registry.get_provider("user")
market_provider = data_registry.get_provider("market")
portfolio_provider = data_registry.get_provider("portfolio") 
ui_provider = data_registry.get_provider("ui")


# ===== FUTURE IMPLEMENTATIONS (EXAMPLES) =====
"""
# Example: Database-based user provider
class DatabaseUserDataProvider(UserDataProvider):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_user(self, user_id: str) -> Dict[str, Any]:
        return self.db.query("SELECT * FROM users WHERE id = ?", user_id)

# Example: External API market provider  
class ExternalAPIMarketDataProvider(MarketDataProvider):
    def __init__(self, api_client):
        self.api = api_client
        
    def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        return self.api.get_quote(symbol)

# Example: MCP-based provider
class MCPDataProvider(MarketDataProvider):
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        
    def get_market_indices(self) -> List[Dict[str, Any]]:
        return self.mcp.call_tool("get_market_data", {"type": "indices"})

# Usage: Easy to swap providers
# data_registry.register_provider("user", DatabaseUserDataProvider(db_conn))
# data_registry.register_provider("market", MCPDataProvider(mcp_client))
"""