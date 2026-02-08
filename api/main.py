"""
Sarasai - Stock Analysis API
Author: Srinivasan Ramarao <rsrinivasan18@gmail.com>
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import stocks, portfolio, auth, trading
from core.models import RootResponse, HealthResponse
from core.services import stock_service
from config.settings import settings
from core.data_providers import ui_provider, user_provider
from core.enhanced_data_providers import register_enhanced_providers

# Register enhanced providers on startup
register_enhanced_providers()

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

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Serve frontend files directly (for relative paths)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend_files")

# Include routers
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(portfolio.router)
app.include_router(trading.router)


@app.get("/app")
def frontend_app():
    """Serve the frontend application"""
    return FileResponse("frontend/index.html")

@app.get("/pro")
def professional_app():
    """Serve the professional trading platform"""
    return FileResponse("frontend/professional_index.html")

@app.get("/test-trading")
def test_trading():
    """Test trading functionality"""
    return {"message": "Trading routes working", "status": "ok"}

@app.get("/demo")
def demo_page():
    """Serve the professional platform demo page"""
    return FileResponse("professional_demo.html")

@app.get("/test")
def test_page():
    """Serve the functionality testing page"""
    return FileResponse("test_functionality.html")

@app.get("/test-app")
def test_app_page():
    """Run system diagnostics"""
    return {
        "system_status": "operational",
        "message": "All intelligence engines are working",
        "endpoints_available": [
            "/api/portfolio/recommendations",
            "/api/portfolio/health", 
            "/api/news/portfolio",
            "/api/experts/portfolio/analysis",
            "/api/stocks/{symbol}/analysis"
        ],
        "main_app": "/pro",
        "basic_app": "/app"
    }


@app.get("/api", response_model=RootResponse)
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


@app.get("/", response_model=RootResponse)  
def home():
    """Home endpoint - redirect to API info for now"""
    branding = ui_provider.get_branding()
    app_info = branding.get("application", {})
    
    return RootResponse(
        message=f"🦢 {app_info.get('name', 'Sarasai')} - {app_info.get('tagline', 'Where Wisdom Flows')}",
        status="flowing",
        version=app_info.get('version', '1.0.0'),
        data_mode=f"{settings.DATA_SOURCE} (CSV)",
        available_stocks=stock_service.get_stock_count(),
        note="Frontend app available at /app - Full dashboard with portfolio analysis"
    )


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        data_source=f"{settings.DATA_SOURCE} (CSV)",
        stocks_available=stock_service.get_available_symbols()
    )


@app.get("/api/stocks/search")
def search_stocks_api(q: str):
    """Search for stocks by symbol or name (API endpoint for frontend)"""
    query = q.lower()
    symbols = stock_service.get_available_symbols()
    
    # Filter stocks based on query
    results = []
    for symbol in symbols[:50]:  # Limit to 50 for performance
        try:
            stock_data = stock_service.get_stock(symbol)
            if stock_data:
                if (query in symbol.lower() or 
                    (hasattr(stock_data, 'name') and query in stock_data.name.lower())):
                    results.append({
                        "symbol": symbol,
                        "name": getattr(stock_data, 'name', f"{symbol} Inc."),
                        "current_price": stock_data.current_price,
                        "change_percent": getattr(stock_data, 'change_percent', 0.0)
                    })
        except Exception as e:
            # Skip stocks that cause errors
            continue
    
    return results[:10]  # Return top 10 matches


@app.get("/api/config/branding")
def get_branding_config():
    """Get branding configuration for frontend"""
    return ui_provider.get_branding()


@app.get("/api/config/user")  
def get_user_config():
    """Get current user configuration"""
    return user_provider.get_user()


@app.get("/api/config/ui")
def get_ui_config(section: str = None):
    """Get UI text configuration"""
    return ui_provider.get_ui_text(section)


@app.get("/api/config/navigation")
def get_navigation_config():
    """Get navigation menu configuration"""  
    return ui_provider.get_navigation_items()


# Enhanced Multi-Market API Endpoints
@app.get("/api/markets")
def get_markets():
    """Get all supported markets"""
    from core.data_providers import data_registry
    market_provider = data_registry.get_provider("market")
    return market_provider.get_markets()


@app.get("/api/markets/{market_code}/stocks")
def get_market_stocks(market_code: str):
    """Get all stocks for a specific market"""
    from core.data_providers import data_registry
    market_provider = data_registry.get_provider("market")
    return market_provider.get_stocks_by_market(market_code)


@app.get("/api/stocks/search/enhanced")
def enhanced_stock_search(q: str, market: str = None):
    """Enhanced stock search across markets"""
    from core.data_providers import data_registry
    market_provider = data_registry.get_provider("market")
    return market_provider.search_stocks(q, market)


@app.get("/api/portfolio/summary")
def get_portfolio_summary():
    """Get comprehensive portfolio summary"""
    from core.data_providers import data_registry
    portfolio_provider = data_registry.get_provider("portfolio")
    return portfolio_provider.get_portfolio_summary("default_user")


@app.post("/api/portfolio/positions/add")
def add_portfolio_position(position: dict):
    """Add new position to portfolio"""
    from core.data_providers import data_registry
    portfolio_provider = data_registry.get_provider("portfolio")
    position_id = portfolio_provider.add_position("default_user", position)
    return {"success": True, "position_id": position_id}


@app.delete("/api/portfolio/positions/{position_id}")
def delete_portfolio_position(position_id: str):
    """Delete position from portfolio"""
    from core.data_providers import data_registry
    portfolio_provider = data_registry.get_provider("portfolio")
    success = portfolio_provider.delete_position(position_id)
    return {"success": success}


@app.get("/api/markets/indices/all")
def get_all_market_indices():
    """Get indices from all markets"""
    from core.data_providers import data_registry
    market_provider = data_registry.get_provider("market")
    return market_provider.get_market_indices()


# Portfolio Intelligence API Endpoints
@app.get("/api/portfolio/recommendations")
def get_portfolio_recommendations(user_id: str = "default_user"):
    """Get AI-powered portfolio recommendations"""
    from core.portfolio_intelligence import intelligence_engine
    recommendations = intelligence_engine.generate_recommendations(user_id)
    
    # Convert to serializable format
    return [
        {
            "symbol": rec.symbol,
            "name": rec.name,
            "action": rec.action.value,
            "confidence": float(rec.confidence),
            "target_price": float(rec.target_price) if rec.target_price is not None else None,
            "reasoning": rec.reasoning,
            "position_size": float(rec.position_size) if rec.position_size is not None else None,
            "current_price": float(rec.metrics.current_price),
            "sector": rec.metrics.sector,
            "market": rec.metrics.market,
            "pe_ratio": float(rec.metrics.pe_ratio),
            "dividend_yield": float(rec.metrics.dividend_yield)
        }
        for rec in recommendations
    ]


@app.get("/api/portfolio/health")
def get_portfolio_health(user_id: str = "default_user"):
    """Get comprehensive portfolio health analysis"""
    from core.portfolio_intelligence import intelligence_engine
    return intelligence_engine.get_portfolio_health_score(user_id)


@app.get("/api/stocks/{symbol}/analysis")
def get_stock_analysis(symbol: str):
    """Get detailed stock analysis and metrics"""
    from core.portfolio_intelligence import intelligence_engine
    metrics = intelligence_engine.analyze_stock(symbol.upper())
    
    if not metrics:
        return {"error": "Stock not found or analysis unavailable"}
    
    return {
        "symbol": metrics.symbol,
        "current_price": float(metrics.current_price),
        "market": metrics.market,
        "sector": metrics.sector,
        "currency": metrics.currency,
        "fundamentals": {
            "pe_ratio": float(metrics.pe_ratio),
            "dividend_yield": float(metrics.dividend_yield),
            "market_cap_millions": float(metrics.market_cap),
            "value_score": float(metrics.value_score),
            "growth_score": float(metrics.growth_score),
            "quality_score": float(metrics.quality_score)
        },
        "technical": {
            "rsi": float(metrics.rsi),
            "price_momentum": float(metrics.price_momentum),
            "volatility": float(metrics.volatility)
        },
        "sentiment": {
            "analyst_rating": float(metrics.analyst_rating),
            "news_sentiment": float(metrics.news_sentiment)
        }
    }


# News Intelligence API Endpoints
@app.get("/api/news/stock/{symbol}")
def get_stock_news_analysis(symbol: str, days: int = 7):
    """Get comprehensive news analysis for a stock"""
    from core.news_sentiment_engine import news_engine
    analysis = news_engine.analyze_stock_news(symbol.upper(), days)
    
    return {
        "symbol": analysis.symbol,
        "overall_sentiment": analysis.overall_sentiment,
        "sentiment_trend": analysis.sentiment_trend,
        "news_count": analysis.news_count,
        "positive_news_count": analysis.positive_news_count,
        "negative_news_count": analysis.negative_news_count,
        "impact_score": analysis.impact_score,
        "recent_headlines": analysis.recent_headlines,
        "key_themes": analysis.key_themes,
        "analysis_period_days": days
    }


@app.get("/api/news/portfolio")
def get_portfolio_news_summary(user_id: str = "default_user"):
    """Get news summary for entire portfolio"""
    from core.data_providers import data_registry
    from core.news_sentiment_engine import news_engine
    
    portfolio_provider = data_registry.get_provider("portfolio")
    positions = portfolio_provider.get_positions(user_id)
    
    symbols = [position["symbol"] for position in positions]
    
    if not symbols:
        return {"message": "No positions in portfolio", "symbols": []}
    
    return news_engine.get_portfolio_news_summary(symbols)


@app.get("/api/news/market/{market}")
def get_market_news_sentiment(market: str = "global"):
    """Get market-wide news sentiment"""
    from core.news_sentiment_engine import news_engine
    return news_engine.get_market_sentiment(market)


# Expert Advisor API Endpoints
@app.get("/api/experts/consensus/{symbol}")
def get_expert_consensus(symbol: str):
    """Get expert consensus recommendation for a stock"""
    from core.expert_advisor_engine import expert_engine
    consensus = expert_engine.calculate_consensus(symbol.upper())
    
    return {
        "symbol": consensus.symbol,
        "consensus_action": consensus.consensus_action.value,
        "consensus_confidence": consensus.consensus_confidence,
        "consensus_target_price": consensus.consensus_target_price,
        "expert_count": consensus.expert_count,
        "agreement_level": consensus.agreement_level,
        "bullish_experts": consensus.bullish_experts,
        "bearish_experts": consensus.bearish_experts,
        "neutral_experts": consensus.neutral_experts,
        "weighted_score": consensus.weighted_score,
        "key_arguments": consensus.key_arguments,
        "dissenting_views": consensus.dissenting_views
    }


@app.get("/api/experts/recommendations/{symbol}")
def get_individual_expert_recommendations(symbol: str):
    """Get individual recommendations from all experts for a stock"""
    from core.expert_advisor_engine import expert_engine
    recommendations = expert_engine.expert_db.get_expert_recommendations(symbol.upper())
    
    return [
        {
            "expert_name": rec.expert_name,
            "expert_type": rec.expert_type.value,
            "action": rec.action.value,
            "confidence": rec.confidence,
            "target_price": rec.target_price,
            "reasoning": rec.reasoning,
            "time_horizon": rec.time_horizon,
            "track_record_score": rec.track_record_score,
            "last_updated": rec.last_updated.isoformat()
        }
        for rec in recommendations
    ]


@app.get("/api/experts/portfolio/analysis")
def get_portfolio_expert_analysis(user_id: str = "default_user"):
    """Get expert analysis for entire portfolio"""
    from core.data_providers import data_registry
    from core.expert_advisor_engine import expert_engine
    
    portfolio_provider = data_registry.get_provider("portfolio")
    positions = portfolio_provider.get_positions(user_id)
    
    symbols = [position["symbol"] for position in positions]
    
    if not symbols:
        return {"message": "No positions in portfolio", "symbols": []}
    
    return expert_engine.get_portfolio_expert_analysis(symbols)


@app.get("/api/experts/track-records")
def get_expert_track_records():
    """Get track record information for all experts"""
    from core.expert_advisor_engine import expert_engine
    return expert_engine.get_expert_track_records()