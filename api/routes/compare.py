"""
Compare API Routes.

Endpoints for comparing specific products across platforms.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.scraper_agent import get_scraper_agent
from agents.product_matcher import get_product_matcher
from agents.deal_finder import get_deal_finder

router = APIRouter()


@router.get("/{product_name}")
async def compare_product(
    product_name: str,
    platforms: Optional[str] = Query(None, description="Comma-separated platform IDs"),
    pincode: Optional[str] = Query(None, description="Location pincode")
):
    """
    Compare prices for a specific product across platforms.
    
    **Example:**
    - `/api/compare/amul%20milk%201l` - Compare Amul milk 1L
    - `/api/compare/maggi%20noodles?platforms=blinkit,zepto` - Specific platforms
    """
    try:
        # Parse platforms
        platform_list = None
        if platforms:
            platform_list = [p.strip() for p in platforms.split(",")]
        
        # Search for the product
        scraper = get_scraper_agent(pincode=pincode or "400001")
        results = await scraper.search_all_platforms(
            query=product_name,
            platforms=platform_list,
            limit_per_platform=5  # Get top 5 matches from each
        )
        
        # Match products
        matcher = get_product_matcher()
        matches = matcher.match_products(results)
        
        if not matches:
            raise HTTPException(
                status_code=404,
                detail=f"No products found matching '{product_name}'"
            )
        
        # Get the best match (most platforms)
        best_match = max(matches, key=lambda m: len(m.products))
        comparison = matcher.create_price_comparison(best_match)
        
        return {
            "product_id": comparison.product_id,
            "product_name": comparison.product_name,
            "brand": comparison.brand,
            "category": comparison.category,
            "quantity": comparison.quantity,
            "image_url": comparison.image_url,
            
            # Price summary
            "lowest_price": comparison.lowest_price,
            "highest_price": comparison.highest_price,
            "average_price": round(comparison.average_price, 2),
            "savings_potential": comparison.savings_potential,
            "savings_percent": round(comparison.savings_percent, 1),
            
            # Best option
            "best_deal": {
                "platform": comparison.best_platform,
                "platform_name": comparison.best_platform_name,
                "platform_logo": comparison.best_platform_logo,
                "price": comparison.best_price,
                "delivery_time": comparison.best_delivery_time
            },
            
            # All prices
            "all_prices": [
                {
                    "platform": p.platform,
                    "platform_name": p.platform_name,
                    "platform_logo": p.platform_logo,
                    "price": p.price,
                    "mrp": p.mrp,
                    "discount_percent": round(p.discount_percent, 1),
                    "is_available": p.is_available,
                    "stock_status": p.stock_status,
                    "delivery_time": p.delivery_time,
                    "product_url": p.product_url,
                    "is_cheapest": p.price == comparison.lowest_price and p.is_available
                }
                for p in comparison.prices
            ],
            
            # Metadata
            "available_on": comparison.available_on,
            "total_platforms_checked": comparison.total_platforms,
            "compared_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/quick/{product_name}")
async def quick_compare(product_name: str):
    """
    Quick price comparison - returns just the essentials.
    
    Fast endpoint for simple price checks.
    """
    try:
        scraper = get_scraper_agent()
        results = await scraper.search_all_platforms(
            query=product_name,
            limit_per_platform=3
        )
        
        matcher = get_product_matcher()
        matches = matcher.match_products(results)
        
        if not matches:
            return {
                "product": product_name,
                "found": False,
                "message": "No matching products found"
            }
        
        best_match = max(matches, key=lambda m: len(m.products))
        comparison = matcher.create_price_comparison(best_match)
        
        return {
            "product": comparison.product_name,
            "found": True,
            "lowest_price": comparison.lowest_price,
            "highest_price": comparison.highest_price,
            "best_platform": comparison.best_platform_name,
            "savings": f"₹{comparison.savings_potential:.0f} ({comparison.savings_percent:.0f}%)",
            "platforms": comparison.available_on
        }
        
    except Exception as e:
        return {
            "product": product_name,
            "found": False,
            "error": str(e)
        }


@router.get("/basket")
async def compare_basket(
    products: str = Query(..., description="Comma-separated product names")
):
    """
    Compare multiple products at once - useful for basket comparison.
    
    **Example:**
    - `/api/compare/basket?products=milk,bread,eggs,butter`
    """
    try:
        product_list = [p.strip() for p in products.split(",")]
        
        if len(product_list) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 products per basket comparison"
            )
        
        scraper = get_scraper_agent()
        matcher = get_product_matcher()
        
        basket_results = []
        platform_totals = {}
        
        for product_name in product_list:
            # Search each product
            results = await scraper.search_all_platforms(
                query=product_name,
                limit_per_platform=5
            )
            
            matches = matcher.match_products(results)
            
            if matches:
                best_match = max(matches, key=lambda m: len(m.products))
                comparison = matcher.create_price_comparison(best_match)
                
                basket_results.append({
                    "query": product_name,
                    "product_name": comparison.product_name,
                    "found": True,
                    "lowest_price": comparison.lowest_price,
                    "best_platform": comparison.best_platform
                })
                
                # Track totals per platform
                for price_entry in comparison.prices:
                    if price_entry.is_available:
                        platform = price_entry.platform
                        if platform not in platform_totals:
                            platform_totals[platform] = {
                                "name": price_entry.platform_name,
                                "logo": price_entry.platform_logo,
                                "total": 0,
                                "items_found": 0
                            }
                        platform_totals[platform]["total"] += price_entry.price
                        platform_totals[platform]["items_found"] += 1
            else:
                basket_results.append({
                    "query": product_name,
                    "found": False
                })
        
        # Find cheapest platform for complete basket
        complete_baskets = [
            (pid, data) for pid, data in platform_totals.items()
            if data["items_found"] == len([r for r in basket_results if r["found"]])
        ]
        
        cheapest_platform = None
        if complete_baskets:
            cheapest_platform = min(complete_baskets, key=lambda x: x[1]["total"])
        
        return {
            "products_searched": len(product_list),
            "products_found": len([r for r in basket_results if r["found"]]),
            "basket_items": basket_results,
            "platform_totals": [
                {
                    "platform": pid,
                    "name": data["name"],
                    "logo": data["logo"],
                    "basket_total": round(data["total"], 2),
                    "items_found": data["items_found"],
                    "is_complete": data["items_found"] == len([r for r in basket_results if r["found"]])
                }
                for pid, data in sorted(platform_totals.items(), key=lambda x: x[1]["total"])
            ],
            "best_overall": {
                "platform": cheapest_platform[0] if cheapest_platform else None,
                "name": cheapest_platform[1]["name"] if cheapest_platform else None,
                "total": cheapest_platform[1]["total"] if cheapest_platform else None
            } if cheapest_platform else None,
            "compared_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Basket comparison failed: {str(e)}")

