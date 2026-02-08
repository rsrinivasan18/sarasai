"""
Sarasai Configuration Service
Centralized configuration management for all application settings
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigService:
    """Centralized configuration management service"""
    
    _instance = None
    _config_cache = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config_dir = Path(__file__).parent.parent / "config"
            self.initialized = True
            logger.info(f"ConfigService initialized with config dir: {self.config_dir}")
    
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load YAML configuration file with caching"""
        if config_name in self._config_cache:
            return self._config_cache[config_name]
            
        config_file = self.config_dir / f"{config_name}.yaml"
        
        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_file}")
            return {}
            
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                self._config_cache[config_name] = config
                logger.info(f"Loaded configuration: {config_name}")
                return config
        except Exception as e:
            logger.error(f"Error loading configuration {config_name}: {e}")
            return {}
    
    def get_branding(self) -> Dict[str, Any]:
        """Get branding configuration"""
        return self.load_config("branding")
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration"""
        return self.load_config("app_config")
    
    def get_user_config(self) -> Dict[str, Any]:
        """Get user configuration"""
        return self.load_config("users")
    
    def get_market_config(self) -> Dict[str, Any]:
        """Get market data configuration"""
        return self.load_config("market_data")
    
    def get_ui_text(self, section: Optional[str] = None) -> Dict[str, Any]:
        """Get UI text configuration"""
        config = self.load_config("ui_text")
        if section:
            return config.get(section, {})
        return config
    
    def get_time_config(self) -> Dict[str, Any]:
        """Get time periods and timezone configuration"""
        return self.load_config("time_periods")
    
    # Convenience methods for commonly used values
    def get_app_name(self) -> str:
        """Get application name"""
        branding = self.get_branding()
        return branding.get("application", {}).get("name", "Sarasai")
    
    def get_app_tagline(self) -> str:
        """Get application tagline"""
        branding = self.get_branding()
        return branding.get("application", {}).get("tagline", "Where Wisdom Flows")
    
    def get_default_user(self) -> Dict[str, Any]:
        """Get default user configuration"""
        user_config = self.get_user_config()
        return user_config.get("default_user", {})
    
    def get_timezone(self) -> str:
        """Get default timezone"""
        time_config = self.get_time_config()
        return time_config.get("timezone", {}).get("default", "Asia/Singapore")
    
    def get_api_base_url(self) -> str:
        """Get API base URL"""
        app_config = self.get_app_config()
        return app_config.get("api", {}).get("base_url", "http://localhost:8000")
    
    def get_market_indices(self) -> list:
        """Get configured market indices"""
        market_config = self.get_market_config()
        return market_config.get("market_indices", [])
    
    def reload_config(self, config_name: Optional[str] = None):
        """Reload configuration(s) from disk"""
        if config_name:
            if config_name in self._config_cache:
                del self._config_cache[config_name]
            logger.info(f"Reloaded configuration: {config_name}")
        else:
            self._config_cache.clear()
            logger.info("Reloaded all configurations")


# Global instance
config_service = ConfigService()


# Convenience functions for easy access
def get_branding() -> Dict[str, Any]:
    """Get branding configuration"""
    return config_service.get_branding()


def get_app_name() -> str:
    """Get application name"""
    return config_service.get_app_name()


def get_default_user() -> Dict[str, Any]:
    """Get default user configuration"""  
    return config_service.get_default_user()


def get_timezone() -> str:
    """Get default timezone"""
    return config_service.get_timezone()


def get_ui_text(section: Optional[str] = None) -> Dict[str, Any]:
    """Get UI text configuration"""
    return config_service.get_ui_text(section)