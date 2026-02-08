"""
Sarasai - Where Wisdom Flows
Stock Portfolio Analysis Platform (Legacy Settings - migrating to config/)

Author: Srinivasan Ramarao  
Email: rsrinivasan18@gmail.com
GitHub: github.com/rsrinivasan18
"""

import os
from pathlib import Path
from core.config_service import config_service


class Settings:
    """Application settings - transitioning to new config system"""

    def __init__(self):
        # Load from new config system
        self._app_config = config_service.get_app_config()
        self._branding = config_service.get_branding()
        
    # Author information (from config)
    @property 
    def AUTHOR_NAME(self):
        return self._branding.get("company", {}).get("founder", "Srinivasan Ramarao")
    
    @property
    def AUTHOR_EMAIL(self):
        return self._branding.get("company", {}).get("contact_email", "rsrinivasan18@gmail.com")

    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    # API settings (from config)
    @property
    def APP_NAME(self):
        return self._branding.get("application", {}).get("name", "Sarasai")
    
    @property 
    def APP_VERSION(self):
        return self._branding.get("application", {}).get("version", "1.0.0")
        
    @property
    def APP_DESCRIPTION(self):
        return self._branding.get("application", {}).get("description", "Where Wisdom Flows")

    # Data settings
    MOCK_DATA_FILE = DATA_DIR / "mock_stocks.csv"
    DATA_SOURCE = "live"

    # External API (from environment + config)
    @property
    def ALPHA_VANTAGE_API_KEY(self):
        return os.getenv('ALPHA_VANTAGE_API_KEY', "AI0J92EXAQ12E0RY")
    
    @property    
    def ALPHA_VANTAGE_BASE_URL(self):
        return self._app_config.get("external_apis", {}).get("alpha_vantage", {}).get("base_url", "https://www.alphavantage.co/query")


settings = Settings()
