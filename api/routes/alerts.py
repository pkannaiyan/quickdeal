"""
Alerts API Routes.

Endpoints for managing price alerts.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.price import PriceAlert
from agents.scraper_agent import get_scraper_agent
from agents.product_matcher import get_product_matcher
from agents.deal_finder import get_deal_finder

router = APIRouter()

# In-memory alert storage (use database in production)
_alerts: List[PriceAlert] = []


class CreateAlertRequest(BaseModel):
    """Request model for creating a price alert."""
    product_name: str = Field(..., description="Product to track")
    target_price: float = Field(..., gt=0, description="Alert when price drops to/below this")
    platforms: List[str] = Field(default_factory=list, description="Platforms to monitor (empty = all)")
    email: Optional[str] = Field(None, description="Email for notifications")


@router.post("")
async def create_alert(request: CreateAlertRequest):
    """
    Create a price alert for a product.
    
    You'll be notified when the price drops to or below your target.
    """
    try:
        # Search to get current price
        scraper = get_scraper_agent()
        results = await scraper.search_all_platforms(
            query=request.product_name,
            platforms=request.platforms or None,
            limit_per_platform=5
        )
        
        matcher = get_product_matcher()
        matches = matcher.match_products(results)
        
        if not matches:
            raise HTTPException(
                status_code=404,
                detail=f"Product '{request.product_name}' not found"
            )
        
        best_match = max(matches, key=lambda m: len(m.products))
        comparison = matcher.create_price_comparison(best_match)
        
        # Create alert
        alert = PriceAlert(
            product_id=comparison.product_id,
            product_name=comparison.product_name,
            platforms=request.platforms,
            target_price=request.target_price,
            current_lowest=comparison.lowest_price,
            email=request.email
        )
        
        _alerts.append(alert)
        
        # Check if already at target
        is_triggered = comparison.lowest_price <= request.target_price
        if is_triggered:
            alert.triggered = True
            alert.triggered_at = datetime.now()
            alert.triggered_platform = comparison.best_platform
            alert.triggered_price = comparison.lowest_price
        
        return {
            "alert_id": alert.id,
            "product_name": alert.product_name,
            "target_price": alert.target_price,
            "current_lowest": alert.current_lowest,
            "is_active": alert.is_active,
            "already_triggered": is_triggered,
            "message": (
                f"Great news! {comparison.product_name} is already at ₹{comparison.lowest_price} on {comparison.best_platform_name}!"
                if is_triggered
                else f"Alert created! We'll notify you when {comparison.product_name} drops to ₹{request.target_price}"
            ),
            "created_at": alert.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create alert: {str(e)}")


@router.get("")
async def list_alerts(
    active_only: bool = Query(True, description="Show only active alerts")
):
    """
    List all price alerts.
    """
    alerts = _alerts
    
    if active_only:
        alerts = [a for a in alerts if a.is_active]
    
    return {
        "total_alerts": len(alerts),
        "alerts": [
            {
                "alert_id": a.id,
                "product_name": a.product_name,
                "target_price": a.target_price,
                "current_lowest": a.current_lowest,
                "platforms": a.platforms,
                "is_active": a.is_active,
                "triggered": a.triggered,
                "triggered_at": a.triggered_at.isoformat() if a.triggered_at else None,
                "triggered_platform": a.triggered_platform,
                "triggered_price": a.triggered_price,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]
    }


@router.get("/{alert_id}")
async def get_alert(alert_id: str):
    """
    Get a specific alert by ID.
    """
    for alert in _alerts:
        if alert.id == alert_id:
            return {
                "alert_id": alert.id,
                "product_name": alert.product_name,
                "target_price": alert.target_price,
                "current_lowest": alert.current_lowest,
                "platforms": alert.platforms,
                "is_active": alert.is_active,
                "triggered": alert.triggered,
                "triggered_at": alert.triggered_at.isoformat() if alert.triggered_at else None,
                "created_at": alert.created_at.isoformat()
            }
    
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@router.delete("/{alert_id}")
async def delete_alert(alert_id: str):
    """
    Delete a price alert.
    """
    for i, alert in enumerate(_alerts):
        if alert.id == alert_id:
            _alerts.pop(i)
            return {"message": f"Alert {alert_id} deleted", "success": True}
    
    raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")


@router.post("/check")
async def check_alerts():
    """
    Check all active alerts against current prices.
    
    Returns alerts that have been triggered.
    """
    try:
        triggered_alerts = []
        scraper = get_scraper_agent()
        matcher = get_product_matcher()
        
        active_alerts = [a for a in _alerts if a.is_active and not a.triggered]
        
        for alert in active_alerts:
            # Get current prices
            results = await scraper.search_all_platforms(
                query=alert.product_name,
                platforms=alert.platforms or None,
                limit_per_platform=5
            )
            
            matches = matcher.match_products(results)
            if not matches:
                continue
            
            best_match = max(matches, key=lambda m: len(m.products))
            comparison = matcher.create_price_comparison(best_match)
            
            # Update current lowest
            alert.current_lowest = comparison.lowest_price
            
            # Check if triggered
            if comparison.lowest_price <= alert.target_price:
                alert.triggered = True
                alert.triggered_at = datetime.now()
                alert.triggered_platform = comparison.best_platform
                alert.triggered_price = comparison.lowest_price
                
                triggered_alerts.append({
                    "alert_id": alert.id,
                    "product_name": alert.product_name,
                    "target_price": alert.target_price,
                    "current_price": comparison.lowest_price,
                    "platform": comparison.best_platform_name,
                    "savings": round(alert.target_price - comparison.lowest_price, 2)
                })
        
        return {
            "alerts_checked": len(active_alerts),
            "alerts_triggered": len(triggered_alerts),
            "triggered": triggered_alerts,
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check alerts: {str(e)}")


@router.get("/suggestions")
async def get_alert_suggestions():
    """
    Get suggestions for products worth setting alerts on.
    
    Returns products with high price variance.
    """
    try:
        scraper = get_scraper_agent()
        all_products = await scraper.get_all_products()
        
        matcher = get_product_matcher()
        matches = matcher.match_products(all_products)
        comparisons = [matcher.create_price_comparison(m) for m in matches]
        
        deal_finder = get_deal_finder()
        suggestions = deal_finder.get_price_alerts_worthy(comparisons)
        
        return {
            "suggestions_count": len(suggestions),
            "suggestions": suggestions[:10],  # Top 10
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

