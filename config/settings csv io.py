"""
Sarasai - Where Wisdom Flows
Stock Portfolio Analysis Platform

Author: Srinivasan Ramarao
Email: rsrinivasan18@gmail.com
GitHub: github.com/rsrinivasan18
"""

from pathlib import Path

class Settings:
    """Application settings"""
    
    # Author information
    AUTHOR_NAME = "Srinivasan Ramarao"
    AUTHOR_EMAIL = "rsrinivasan18@gmail.com"
    
    # Project paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # API settings
    APP_NAME = "Sarasai"
    APP_VERSION = "0.4.0"
    APP_DESCRIPTION = "Where Wisdom Flows - Stock Analysis API"
    
    # Data settings
    MOCK_DATA_FILE = DATA_DIR / "mock_stocks.csv"
    DATA_SOURCE = "mock"  # Will change to "live" later
    
    # Future: API keys (when we add real data)
    ALPHA_VANTAGE_API_KEY = None
    

settings = Settings()