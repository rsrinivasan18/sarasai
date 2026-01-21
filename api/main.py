"""
Sarasai - Stock Analysis API
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from fastapi import FastAPI

from api.routes import stocks
from core.models import RootResponse, HealthResponse
from core.services import stock_service
from config.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    contact={
        "name": settings.AUTHOR_NAME,
        "email": settings.AUTHOR_EMAIL,
    },
    license_info={
        "name": "MIT",
    }
)

# Include routers
app.include_router(stocks.router)


@app.get("/", response_model=RootResponse)
def root():
    """Root endpoint - API information"""
    return RootResponse(
        message="🦢 Sarasai - Where Wisdom Flows",
        status="flowing",
        version=settings.APP_VERSION,
        data_mode=f"{settings.DATA_SOURCE} (CSV)",
        available_stocks=stock_service.get_stock_count(),
        note="Using CSV mock data. Real API integration coming soon."
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        data_source=f"{settings.DATA_SOURCE} (CSV)",
        stocks_available=stock_service.get_available_symbols()
    )