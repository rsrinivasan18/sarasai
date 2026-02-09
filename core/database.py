"""
Sarasai - Database Configuration
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Database URL from environment or default to SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./data/sarasai.db"  # SQLite fallback for local development
)

# For PostgreSQL in production:
# DATABASE_URL = "postgresql://username:password@localhost/sarasai"

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration
    engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Generator:
    """
    Database dependency for FastAPI
    
    Usage:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    # Import all models to register them with Base
    from . import models_db
    
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {DATABASE_URL}")


def get_db_info():
    """Get database connection information"""
    return {
        "url": DATABASE_URL,
        "driver": engine.driver,
        "connected": True if engine else False
    }