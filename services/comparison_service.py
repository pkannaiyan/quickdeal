"""
Comparison Service - Orchestrates the complete comparison flow.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.price import PriceComparison
from agents.scraper_agent import get_scraper_agent
from agents.product_matcher import get_product_matcher
from agents.deal_finder import get_deal_finder


class ComparisonService:
    """
    High-level service for price comparison operations.
    
    Coordinates between scrapers, matchers, and deal finders.
    """
    
    def __init__(self, pincode: str = "400001"):
        """Initialize the comparison service."""
        self.pincode = pincode
        self.scraper = get_scraper_agent(pincode=pincode)
        self.matcher = get_product_matcher()
        self.deal_finder = get_deal_finder()
    
    async def search_and_compare(
        self,
        query: str,
        platforms: List[str] = None,
        limit: int = 20
    ) -> List[PriceComparison]:
        """
        Search and compare products across platforms.
        
        This is the main entry point for comparisons.
        """
        # Step 1: Search across platforms
        products_by_platform = await self.scraper.search_all_platforms(
            query=query,
            platforms=platforms,
            limit_per_platform=limit
        )
        
        # Step 2: Match products
        matches = self.matcher.match_products(products_by_platform)
        
        # Step 3: Create comparisons
        comparisons = [
            self.matcher.create_price_comparison(match)
            for match in matches
        ]
        
        # Sort by lowest price
        comparisons.sort(key=lambda c: c.lowest_price)
        
        return comparisons
    
    async def get_best_deals(
        self,
        min_savings_percent: float = 5.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get the best deals currently available."""
        # Get all products
        all_products = await self.scraper.get_all_products()
        
        # Match products
        matches = self.matcher.match_products(all_products)
        
        # Create comparisons
        comparisons = [
            self.matcher.create_price_comparison(match)
            for match in matches
        ]
        
        # Find deals
        deals = self.deal_finder.find_best_deals(
            comparisons,
            min_savings_percent=min_savings_percent
        )
        
        return deals[:limit]
    
    async def compare_single_product(
        self,
        product_name: str,
        platforms: List[str] = None
    ) -> Optional[PriceComparison]:
        """Compare a single product across platforms."""
        products_by_platform = await self.scraper.search_all_platforms(
            query=product_name,
            platforms=platforms,
            limit_per_platform=5
        )
        
        matches = self.matcher.match_products(products_by_platform)
        
        if not matches:
            return None
        
        # Get best match
        best_match = max(matches, key=lambda m: len(m.products))
        return self.matcher.create_price_comparison(best_match)
    
    async def compare_basket(
        self,
        products: List[str],
        platforms: List[str] = None
    ) -> Dict[str, Any]:
        """Compare a basket of products."""
        results = []
        platform_totals: Dict[str, Dict] = {}
        
        for product_name in products:
            comparison = await self.compare_single_product(
                product_name,
                platforms=platforms
            )
            
            if comparison:
                results.append({
                    "query": product_name,
                    "product_name": comparison.product_name,
                    "found": True,
                    "lowest_price": comparison.lowest_price,
                    "best_platform": comparison.best_platform
                })
                
                # Track totals per platform
                for price in comparison.prices:
                    if price.is_available:
                        if price.platform not in platform_totals:
                            platform_totals[price.platform] = {
                                "name": price.platform_name,
                                "logo": price.platform_logo,
                                "total": 0,
                                "items": 0
                            }
                        platform_totals[price.platform]["total"] += price.price
                        platform_totals[price.platform]["items"] += 1
            else:
                results.append({
                    "query": product_name,
                    "found": False
                })
        
        # Find best platform for complete basket
        found_count = len([r for r in results if r["found"]])
        complete_baskets = [
            (pid, data) for pid, data in platform_totals.items()
            if data["items"] == found_count
        ]
        
        best_platform = None
        if complete_baskets:
            best_platform = min(complete_baskets, key=lambda x: x[1]["total"])
        
        return {
            "products_searched": len(products),
            "products_found": found_count,
            "basket_items": results,
            "platform_totals": sorted(
                [{"platform": pid, **data} for pid, data in platform_totals.items()],
                key=lambda x: x["total"]
            ),
            "best_platform": {
                "platform": best_platform[0],
                "name": best_platform[1]["name"],
                "total": best_platform[1]["total"]
            } if best_platform else None,
            "compared_at": datetime.now().isoformat()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get service summary and statistics."""
        return {
            "scraper_stats": self.scraper.get_stats(),
            "matcher_stats": self.matcher.get_stats(),
            "deal_finder_stats": self.deal_finder.get_stats(),
            "pincode": self.pincode
        }


# Singleton
_comparison_service: Optional[ComparisonService] = None


def get_comparison_service(pincode: str = "400001") -> ComparisonService:
    """Get the singleton comparison service."""
    global _comparison_service
    if _comparison_service is None:
        _comparison_service = ComparisonService(pincode=pincode)
    return _comparison_service

