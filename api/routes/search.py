"""
Search API Routes.

Endpoints for searching products across platforms.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.scraper_agent import get_scraper_agent
from agents.product_matcher import get_product_matcher
from agents.deal_finder import get_deal_finder
from services.analytics_service import get_analytics_service

router = APIRouter()


@router.get("")
async def search_products(
    q: str = Query(..., min_length=2, max_length=200, description="Search query"),
    platforms: Optional[str] = Query(None, description="Comma-separated platform IDs"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort: str = Query("price", description="Sort by: price, discount, platform"),
    limit: int = Query(20, ge=1, le=100, description="Results per platform"),
    pincode: Optional[str] = Query(None, description="Location pincode")
):
    """
    Search for products across all platforms.
    
    Returns matched products grouped for comparison.
    
    **Example:**
    - `/api/search?q=amul milk` - Search for Amul milk
    - `/api/search?q=chips&platforms=blinkit,zepto` - Search specific platforms
    """
    try:
        # Parse platforms
        platform_list = None
        if platforms:
            platform_list = [p.strip() for p in platforms.split(",")]
        
        # Search across platforms
        scraper = get_scraper_agent(pincode=pincode or "400001")
        results = await scraper.search_all_platforms(
            query=q,
            platforms=platform_list,
            limit_per_platform=limit
        )
        
        # Match products across platforms
        matcher = get_product_matcher()
        matches = matcher.match_products(results)
        
        # Filter by category if specified
        if category:
            matches = [m for m in matches if m.category.value == category]
        
        # Convert to comparisons
        comparisons = [matcher.create_price_comparison(m) for m in matches]
        
        # Sort results
        if sort == "price":
            comparisons.sort(key=lambda c: c.lowest_price)
        elif sort == "discount":
            comparisons.sort(key=lambda c: c.savings_percent, reverse=True)
        elif sort == "platform":
            comparisons.sort(key=lambda c: c.available_on, reverse=True)
        
        # Track search analytics
        try:
            analytics = get_analytics_service()
            best_platform = comparisons[0].best_platform if comparisons else None
            best_price = comparisons[0].lowest_price if comparisons else None
            detected_category = matches[0].category.value if matches else None
            
            analytics.track_search(
                query=q,
                results_count=len(comparisons),
                platforms_searched=list(results.keys()),
                best_platform=best_platform,
                best_price=best_price,
                category=detected_category,
                location={"pincode": pincode} if pincode else None
            )
        except Exception:
            pass  # Don't fail search if analytics tracking fails
        
        # Format response
        return {
            "query": q,
            "total_results": len(comparisons),
            "platforms_searched": list(results.keys()),
            "results": [
                {
                    "product_id": c.product_id,
                    "product_name": c.product_name,
                    "brand": c.brand,
                    "category": c.category,
                    "quantity": c.quantity,
                    "image_url": c.image_url,
                    "lowest_price": c.lowest_price,
                    "highest_price": c.highest_price,
                    "savings_percent": round(c.savings_percent, 1),
                    "best_platform": c.best_platform_name,
                    "best_platform_logo": c.best_platform_logo,
                    "best_delivery_time": c.best_delivery_time,
                    "available_on": c.available_on,
                    "prices": [
                        {
                            "platform": p.platform,
                            "platform_name": p.platform_name,
                            "platform_logo": p.platform_logo,
                            "price": p.price,
                            "mrp": p.mrp,
                            "discount_percent": round(p.discount_percent, 1),
                            "is_available": p.is_available,
                            "delivery_time": p.delivery_time,
                            "url": p.product_url
                        }
                        for p in c.prices
                    ]
                }
                for c in comparisons
            ],
            "searched_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/deals")
async def get_best_deals(
    min_savings: float = Query(5.0, description="Minimum savings percentage"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=50, description="Number of deals to return")
):
    """
    Get the best deals across all platforms.
    
    Returns products with highest price differences.
    Each refresh returns different deals for variety.
    """
    import random
    
    try:
        # Get all products
        scraper = get_scraper_agent()
        all_products = await scraper.get_all_products()
        
        # Match products
        matcher = get_product_matcher()
        matches = matcher.match_products(all_products)
        
        # Filter by category if specified
        if category:
            matches = [m for m in matches if m.category.value == category]
        
        # Shuffle matches to get different products each time
        random.shuffle(matches)
        
        # Take a random subset for variety (3x the limit to ensure enough deals)
        sample_size = min(len(matches), limit * 3)
        sampled_matches = random.sample(matches, sample_size) if len(matches) > sample_size else matches
        
        # Convert to comparisons
        comparisons = [matcher.create_price_comparison(m) for m in sampled_matches]
        
        # Find deals
        deal_finder = get_deal_finder()
        deals = deal_finder.find_best_deals(
            comparisons,
            min_savings_percent=min_savings
        )
        
        # Shuffle final deals again for extra randomness
        random.shuffle(deals)
        
        return {
            "total_deals": len(deals),
            "min_savings_threshold": min_savings,
            "deals": deals[:limit],
            "found_at": datetime.now().isoformat(),
            "refresh_id": random.randint(1000, 9999)  # Unique ID for each refresh
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to find deals: {str(e)}")


@router.get("/category/{category_id}")
async def get_category_products(
    category_id: str,
    platforms: Optional[str] = Query(None, description="Comma-separated platform IDs"),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get products from a specific category.
    """
    try:
        platform_list = None
        if platforms:
            platform_list = [p.strip() for p in platforms.split(",")]
        
        scraper = get_scraper_agent()
        results = await scraper.get_category_from_all(
            category=category_id,
            platforms=platform_list,
            limit_per_platform=limit
        )
        
        # Match products
        matcher = get_product_matcher()
        matches = matcher.match_products(results)
        comparisons = [matcher.create_price_comparison(m) for m in matches]
        
        # Sort by price
        comparisons.sort(key=lambda c: c.lowest_price)
        
        return {
            "category": category_id,
            "total_products": len(comparisons),
            "products": [
                {
                    "product_id": c.product_id,
                    "product_name": c.product_name,
                    "brand": c.brand,
                    "lowest_price": c.lowest_price,
                    "highest_price": c.highest_price,
                    "best_platform": c.best_platform_name,
                    "available_on": c.available_on
                }
                for c in comparisons
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get category: {str(e)}")


@router.get("/summary")
async def get_search_summary():
    """
    Get a summary of pricing across all platforms.
    """
    try:
        # Get all products
        scraper = get_scraper_agent()
        all_products = await scraper.get_all_products()
        
        # Match and compare
        matcher = get_product_matcher()
        matches = matcher.match_products(all_products)
        comparisons = [matcher.create_price_comparison(m) for m in matches]
        
        # Get summary
        deal_finder = get_deal_finder()
        summary = deal_finder.get_summary(comparisons)
        
        return {
            **summary,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

