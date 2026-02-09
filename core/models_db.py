"""
Sarasai - Database Models
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User accounts and profiles"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100))
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    timezone = Column(String(50), default="UTC")
    currency = Column(String(10), default="USD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class Portfolio(Base):
    """User portfolios - users can have multiple portfolios"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)  # e.g., "Main Portfolio", "Retirement"
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    total_invested = Column(Float, default=0.0)
    current_value = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio")


class Position(Base):
    """Stock positions within portfolios"""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(20), nullable=False)  # e.g., "AAPL", "GOOGL"
    shares = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    current_price = Column(Float)
    market_value = Column(Float)
    gain_loss = Column(Float)
    gain_loss_percent = Column(Float)
    sector = Column(String(50))
    market = Column(String(50))  # e.g., "NASDAQ", "NSE"
    currency = Column(String(10))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")


class Transaction(Base):
    """Trade transactions history"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    symbol = Column(String(20), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # BUY, SELL
    shares = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    fees = Column(Float, default=0.0)
    notes = Column(Text)
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="transactions")


class Watchlist(Base):
    """User watchlists for tracking stocks"""
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    symbols = Column(Text)  # JSON array of symbols: ["AAPL", "GOOGL", "MSFT"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="watchlists")


class StockCache(Base):
    """Cache for stock data to reduce API calls"""
    __tablename__ = "stock_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(200))
    current_price = Column(Float)
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)
    sector = Column(String(50))
    market = Column(String(50))
    currency = Column(String(10))
    volume = Column(Integer)
    day_high = Column(Float)
    day_low = Column(Float)
    data_source = Column(String(50))  # "alpha_vantage", "yfinance", etc.
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NewsCache(Base):
    """Cache for news and sentiment data"""
    __tablename__ = "news_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    headline = Column(String(500))
    summary = Column(Text)
    sentiment_score = Column(Float)  # -1.0 to 1.0
    source = Column(String(100))
    published_at = Column(DateTime(timezone=True))
    impact_score = Column(Float)  # 0.0 to 1.0
    url = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())