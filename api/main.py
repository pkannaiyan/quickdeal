"""
QuickDeal API.

FastAPI application for comparing prices and negotiating deals across Indian quick commerce platforms.
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.config import API_HOST, API_PORT, DEBUG, PLATFORMS, CATEGORIES, get_config
from api.routes import search, compare, alerts, auth, analytics, chat, jiomart, negotiation

# Create FastAPI app
app = FastAPI(
    title="QuickDeal API",
    description="Compare prices & negotiate deals across Blinkit, Zepto, Instamart, BigBasket & JioMart",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(compare.router, prefix="/api/compare", tags=["Compare"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(chat.router, tags=["Chatbot"])
app.include_router(jiomart.router, prefix="/api/jiomart", tags=["JioMart Integration"])
app.include_router(negotiation.router, prefix="/api/negotiate", tags=["Negotiation Marketplace"])


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "QuickDeal API",
        "version": "2.0.0",
        "description": "Compare prices & negotiate deals across quick commerce platforms",
        "docs": "/docs",
        "platforms_supported": len(PLATFORMS),
        "endpoints": {
            "search": "/api/search?q={query}",
            "compare": "/api/compare/{product_id}",
            "deals": "/api/search/deals",
            "platforms": "/api/platforms",
            "categories": "/api/categories",
            "analytics_dashboard": "/api/analytics/dashboard",
            "analytics_live": "/api/analytics/live",
            "chat": "/api/chat",
            "jiomart_login": "/api/jiomart/login",
            "jiomart_cart": "/api/jiomart/add-to-cart",
            "jiomart_one_click": "/api/jiomart/one-click-order"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/platforms")
async def get_platforms():
    """Get list of all supported platforms."""
    platforms = []
    for platform_id, config in PLATFORMS.items():
        platforms.append({
            "id": platform_id,
            "name": config["name"],
            "logo": config["logo"],
            "base_url": config["base_url"],
            "delivery_time": config["delivery_time"],
            "cities": config["cities"]
        })
    
    return {
        "platforms": platforms,
        "count": len(platforms)
    }


@app.get("/api/categories")
async def get_categories():
    """Get list of product categories."""
    return {
        "categories": CATEGORIES,
        "count": len(CATEGORIES)
    }


@app.get("/api/config")
async def get_configuration():
    """Get current configuration (non-sensitive)."""
    config = get_config()
    return {
        "scraping": config["scraping"],
        "location": config["location"],
        "platforms_count": len(config["platforms"]),
        "categories_count": len(config["categories"])
    }


@app.get("/api/stats")
async def get_stats():
    """Get system statistics."""
    from agents.scraper_agent import get_scraper_agent
    from agents.product_matcher import get_product_matcher
    from agents.deal_finder import get_deal_finder
    
    return {
        "scraper": get_scraper_agent().get_stats(),
        "matcher": get_product_matcher().get_stats(),
        "deal_finder": get_deal_finder().get_stats(),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG
    )

