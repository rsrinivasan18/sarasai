"""
Sarasai - Database-backed Data Providers
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import json

from .data_providers import UserDataProvider, PortfolioDataProvider
from .database import SessionLocal
from .models_db import User, Portfolio, Position, Transaction, Watchlist


class DatabaseUserDataProvider(UserDataProvider):
    """Database-backed user data provider"""
    
    def get_user(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get user from database"""
        db = SessionLocal()
        try:
            if user_id:
                user = db.query(User).filter(User.username == user_id).first()
                if user:
                    return {
                        "id": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "is_active": user.is_active,
                        "is_premium": user.is_premium,
                        "timezone": user.timezone,
                        "currency": user.currency,
                        "created_at": user.created_at.isoformat() if user.created_at else None
                    }
            
            # Return default user for development
            return {
                "id": "default_user",
                "email": "rsrinivasan18@gmail.com",
                "full_name": "Srinivasan Ramarao",
                "is_active": True,
                "is_premium": True,
                "timezone": "Asia/Singapore",
                "currency": "SGD"
            }
        finally:
            db.close()
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Update user in database"""
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == user_id).first()
            if user:
                for key, value in data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating user: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        """Get user settings"""
        user_data = self.get_user(user_id)
        return {
            "timezone": user_data.get("timezone", "UTC"),
            "currency": user_data.get("currency", "USD"),
            "theme": "light",
            "auto_refresh": True
        }


class DatabasePortfolioDataProvider(PortfolioDataProvider):
    """Database-backed portfolio data provider"""
    
    def get_positions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get portfolio positions from database"""
        db = SessionLocal()
        try:
            # Get user's default portfolio
            user = db.query(User).filter(User.username == user_id).first()
            if not user:
                return self._get_sample_positions()  # Fallback to sample data
            
            portfolio = db.query(Portfolio).filter(
                Portfolio.user_id == user.id,
                Portfolio.is_default == True
            ).first()
            
            if not portfolio:
                return self._get_sample_positions()  # Fallback to sample data
            
            positions = db.query(Position).filter(Position.portfolio_id == portfolio.id).all()
            
            return [
                {
                    "id": str(position.id),
                    "symbol": position.symbol,
                    "shares": position.shares,
                    "avg_price": position.avg_price,
                    "current_price": position.current_price,
                    "market_value": position.market_value,
                    "gain_loss": position.gain_loss,
                    "gain_loss_percent": position.gain_loss_percent,
                    "sector": position.sector,
                    "market": position.market,
                    "currency": position.currency,
                    "last_updated": position.updated_at.isoformat() if position.updated_at else None
                }
                for position in positions
            ]
        except Exception as e:
            print(f"Error getting positions: {e}")
            return self._get_sample_positions()  # Fallback to sample data
        finally:
            db.close()
    
    def _get_sample_positions(self) -> List[Dict[str, Any]]:
        """Fallback sample positions"""
        return [
            {
                "id": "sample_1",
                "symbol": "AAPL",
                "shares": 10,
                "avg_price": 180.00,
                "current_price": 278.12,
                "market_value": 2781.20,
                "gain_loss": 981.20,
                "gain_loss_percent": 54.51,
                "sector": "Technology",
                "market": "NASDAQ",
                "currency": "USD",
                "last_updated": datetime.now().isoformat()
            },
            {
                "id": "sample_2", 
                "symbol": "GOOGL",
                "shares": 5,
                "avg_price": 130.00,
                "current_price": 322.86,
                "market_value": 1614.30,
                "gain_loss": 964.30,
                "gain_loss_percent": 148.35,
                "sector": "Technology",
                "market": "NASDAQ",
                "currency": "USD",
                "last_updated": datetime.now().isoformat()
            }
        ]
    
    def add_position(self, user_id: str, position: Dict[str, Any]) -> str:
        """Add new position to database"""
        db = SessionLocal()
        try:
            # Get or create user
            user = db.query(User).filter(User.username == user_id).first()
            if not user:
                user = User(
                    username=user_id,
                    email=f"{user_id}@example.com",
                    full_name=user_id.title()
                )
                db.add(user)
                db.flush()  # Get user.id
            
            # Get or create default portfolio
            portfolio = db.query(Portfolio).filter(
                Portfolio.user_id == user.id,
                Portfolio.is_default == True
            ).first()
            
            if not portfolio:
                portfolio = Portfolio(
                    user_id=user.id,
                    name="Main Portfolio",
                    is_default=True
                )
                db.add(portfolio)
                db.flush()  # Get portfolio.id
            
            # Add position
            new_position = Position(
                portfolio_id=portfolio.id,
                symbol=position.get("symbol"),
                shares=position.get("shares"),
                avg_price=position.get("avg_price"),
                current_price=position.get("current_price"),
                sector=position.get("sector"),
                market=position.get("market"),
                currency=position.get("currency", "USD")
            )
            
            db.add(new_position)
            db.commit()
            
            return str(new_position.id)
            
        except Exception as e:
            print(f"Error adding position: {e}")
            db.rollback()
            return str(hash(str(position)))  # Fallback ID
        finally:
            db.close()
    
    def update_position(self, position_id: str, data: Dict[str, Any]) -> bool:
        """Update position in database"""
        db = SessionLocal()
        try:
            position = db.query(Position).filter(Position.id == int(position_id)).first()
            if position:
                for key, value in data.items():
                    if hasattr(position, key):
                        setattr(position, key, value)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error updating position: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def delete_position(self, position_id: str) -> bool:
        """Delete position from database"""
        db = SessionLocal()
        try:
            position = db.query(Position).filter(Position.id == int(position_id)).first()
            if position:
                db.delete(position)
                db.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting position: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_portfolio_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive portfolio summary"""
        positions = self.get_positions(user_id)
        
        total_invested = sum(pos["shares"] * pos["avg_price"] for pos in positions)
        total_value = sum(pos["market_value"] or 0 for pos in positions)
        total_gain_loss = total_value - total_invested
        total_gain_loss_percent = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        # Sector allocation
        sector_allocation = {}
        for pos in positions:
            sector = pos.get("sector", "Unknown")
            sector_allocation[sector] = sector_allocation.get(sector, 0) + (pos["market_value"] or 0)
        
        return {
            "total_positions": len(positions),
            "total_invested": total_invested,
            "total_value": total_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "sector_allocation": sector_allocation,
            "positions": positions
        }