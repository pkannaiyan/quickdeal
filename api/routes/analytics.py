"""
Analytics API Routes - Dashboard endpoints for tracking and visualization.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from services.analytics_service import get_analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class SearchTrackingRequest(BaseModel):
    """Request model for tracking a search."""
    query: str
    results_count: int
    platforms_searched: List[str]
    best_platform: Optional[str] = None
    best_price: Optional[float] = None
    category: Optional[str] = None
    user_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None


class OrderTrackingRequest(BaseModel):
    """Request model for tracking an order intent."""
    product_id: str
    product_name: str
    selected_platform: str
    price: float
    quantity: int = 1
    user_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    all_prices: Optional[List[Dict[str, Any]]] = None


@router.get("/dashboard")
async def get_dashboard():
    """Get the complete analytics dashboard data."""
    analytics = get_analytics_service()
    return analytics.get_dashboard_summary()


@router.get("/searches")
async def get_search_analytics(hours: int = Query(default=24, ge=1, le=720)):
    """Get search analytics for specified time period."""
    analytics = get_analytics_service()
    return analytics.get_search_analytics(hours)


@router.get("/platforms")
async def get_platform_analytics():
    """Get platform performance analytics (best deals by platform)."""
    analytics = get_analytics_service()
    return analytics.get_platform_analytics()


@router.get("/orders")
async def get_order_analytics(hours: int = Query(default=24, ge=1, le=720)):
    """Get order/purchase intent analytics."""
    analytics = get_analytics_service()
    return analytics.get_order_analytics(hours)


@router.get("/categories")
async def get_category_analytics():
    """Get category-wise search analytics."""
    analytics = get_analytics_service()
    return analytics.get_category_analytics()


@router.post("/track/search")
async def track_search(request: SearchTrackingRequest):
    """Track a search query for analytics."""
    analytics = get_analytics_service()
    
    analytics.track_search(
        query=request.query,
        results_count=request.results_count,
        platforms_searched=request.platforms_searched,
        best_platform=request.best_platform,
        best_price=request.best_price,
        category=request.category,
        user_id=request.user_id,
        location=request.location
    )
    
    return {"status": "tracked", "query": request.query}


@router.post("/track/order")
async def track_order_intent(request: OrderTrackingRequest):
    """Track when a user selects a product to buy."""
    analytics = get_analytics_service()
    
    analytics.track_order_intent(
        product_id=request.product_id,
        product_name=request.product_name,
        selected_platform=request.selected_platform,
        price=request.price,
        quantity=request.quantity,
        user_id=request.user_id,
        location=request.location,
        all_prices=request.all_prices
    )
    
    return {
        "status": "tracked",
        "product": request.product_name,
        "platform": request.selected_platform,
        "amount": request.price * request.quantity
    }


@router.get("/live")
async def get_live_stats():
    """Get live/real-time statistics for the dashboard header."""
    analytics = get_analytics_service()
    
    # Get today's stats
    search_stats = analytics.get_search_analytics(24)
    order_stats = analytics.get_order_analytics(24)
    platform_stats = analytics.get_platform_analytics()
    
    return {
        "total_searches_today": search_stats["total_searches"],
        "total_orders_today": order_stats["total_order_intents"],
        "total_value_today": order_stats["total_value"],
        "best_platform": platform_stats["best_platform"],
        "total_comparisons": platform_stats["total_comparisons"]
    }


@router.get("/negotiations")
async def get_negotiation_analytics():
    """Get negotiation analytics - offers, success rates, discount patterns."""
    analytics = get_analytics_service()
    return analytics.get_negotiation_analytics()


@router.get("/savings")
async def get_savings_analytics():
    """Get savings analytics - total savings, platform-wise, trends."""
    analytics = get_analytics_service()
    return analytics.get_savings_analytics()


@router.get("/conversions")
async def get_conversion_analytics(hours: int = Query(default=24, ge=1, le=720)):
    """Get conversion funnel analytics."""
    analytics = get_analytics_service()
    return analytics.get_conversion_analytics(hours)


@router.get("/realtime")
async def get_realtime_metrics():
    """Get real-time metrics for live dashboard."""
    analytics = get_analytics_service()
    return analytics.get_realtime_metrics()


@router.get("/summary")
async def get_analytics_summary():
    """Get a compact summary of all analytics for overview cards."""
    analytics = get_analytics_service()
    
    negotiation = analytics.get_negotiation_analytics()
    savings = analytics.get_savings_analytics()
    search = analytics.get_search_analytics(24)
    orders = analytics.get_order_analytics(24)
    
    return {
        "quick_stats": {
            "total_searches": search["total_searches"],
            "total_orders": orders["total_order_intents"],
            "total_negotiations": negotiation["total_offers"],
            "total_deals": negotiation["total_deals"],
            "total_savings": savings["total_savings"],
            "avg_savings_percent": savings["avg_savings_percent"],
            "negotiation_success_rate": negotiation["success_rate"]
        },
        "top_platform": {
            "most_searches": analytics.get_platform_analytics().get("best_platform"),
            "best_negotiation": negotiation["platform_stats"][0] if negotiation["platform_stats"] else None
        },
        "trends": {
            "savings_trend": savings["daily_trend"],
            "top_products": savings["top_products"][:5]
        }
    }

