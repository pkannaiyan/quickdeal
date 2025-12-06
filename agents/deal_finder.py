"""
Deal Finder Agent - Finds the best deals across platforms.

Analyzes price data to identify:
- Best overall deals
- Category-specific deals
- Price drops
- Platform-specific offers
"""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.price import PriceComparison, PriceEntry
from api.config import PLATFORMS, LOGS_DIR


class DealFinderAgent:
    """
    AI Agent for finding the best deals across platforms.
    
    Analyzes price comparisons to surface the best opportunities
    for savings.
    """
    
    def __init__(self):
        """Initialize the deal finder."""
        self._stats = {
            "deals_found": 0,
            "searches_performed": 0
        }
    
    def find_best_deals(
        self,
        comparisons: List[PriceComparison],
        min_savings_percent: float = 5.0,
        min_platforms: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Find the best deals from price comparisons.
        
        Args:
            comparisons: List of price comparisons
            min_savings_percent: Minimum savings % to consider a deal
            min_platforms: Minimum platforms for valid comparison
        
        Returns:
            List of deal objects, sorted by savings
        """
        import random
        
        self._log("finding_deals", {
            "comparisons_count": len(comparisons),
            "min_savings_percent": min_savings_percent
        })
        
        # Shuffle comparisons to get different deals each time
        shuffled_comparisons = list(comparisons)
        random.shuffle(shuffled_comparisons)
        
        deals = []
        
        for comparison in shuffled_comparisons:
            # Skip if not enough platforms
            if comparison.available_on < min_platforms:
                continue
            
            # Skip if savings too low
            if comparison.savings_percent < min_savings_percent:
                continue
            
            # Create deal object
            deal = {
                "product_id": comparison.product_id,
                "product_name": comparison.product_name,
                "brand": comparison.brand,
                "category": comparison.category,
                "quantity": comparison.quantity,
                "image_url": comparison.image_url,
                
                # Best price info
                "best_price": comparison.best_price,
                "best_platform": comparison.best_platform,
                "best_platform_name": comparison.best_platform_name,
                "best_platform_logo": comparison.best_platform_logo,
                "best_delivery_time": comparison.best_delivery_time,
                
                # Comparison stats
                "highest_price": comparison.highest_price,
                "average_price": comparison.average_price,
                "savings_amount": comparison.savings_potential,
                "savings_percent": round(comparison.savings_percent, 1),
                
                # Availability
                "available_on": comparison.available_on,
                "total_platforms": comparison.total_platforms,
                
                # All prices for reference
                "all_prices": [
                    {
                        "platform": p.platform,
                        "platform_name": p.platform_name,
                        "platform_logo": p.platform_logo,
                        "price": p.price,
                        "mrp": p.mrp,
                        "discount_percent": p.discount_percent,
                        "is_available": p.is_available,
                        "delivery_time": p.delivery_time,
                        "url": p.product_url
                    }
                    for p in comparison.prices
                ],
                
                # Deal quality score (0-100)
                "deal_score": self._calculate_deal_score(comparison),
                
                # Timestamp
                "found_at": datetime.now().isoformat()
            }
            
            deals.append(deal)
        
        # Sort by deal score (best first)
        deals.sort(key=lambda d: d["deal_score"], reverse=True)
        
        self._stats["deals_found"] += len(deals)
        self._stats["searches_performed"] += 1
        
        self._log("deals_found", {
            "count": len(deals),
            "top_deal": deals[0]["product_name"] if deals else None
        })
        
        return deals
    
    def _calculate_deal_score(self, comparison: PriceComparison) -> float:
        """
        Calculate a deal quality score (0-100).
        
        Factors:
        - Savings percentage (higher = better)
        - Number of platforms (more = more reliable)
        - Price consistency (lower variance = more reliable)
        - Random factor for variety
        """
        import random
        
        score = 0.0
        
        # Savings contribution (up to 50 points)
        # 20% savings = 50 points
        savings_score = min(50, comparison.savings_percent * 2.5)
        score += savings_score
        
        # Platform coverage (up to 30 points)
        # All 5 platforms = 30 points
        platform_score = (comparison.available_on / 5) * 30
        score += platform_score
        
        # Absolute savings bonus (up to 20 points)
        # ₹100 savings = 20 points
        absolute_score = min(20, comparison.savings_potential / 5)
        score += absolute_score
        
        # Add random variation (±10 points) to mix up the order
        random_factor = random.uniform(-10, 10)
        score += random_factor
        
        return max(0, min(100, round(score, 1)))
    
    def find_category_deals(
        self,
        comparisons: List[PriceComparison],
        category: str
    ) -> List[Dict[str, Any]]:
        """Find best deals in a specific category."""
        category_comparisons = [
            c for c in comparisons 
            if c.category == category
        ]
        return self.find_best_deals(category_comparisons)
    
    def find_platform_exclusive_deals(
        self,
        comparisons: List[PriceComparison],
        platform: str
    ) -> List[Dict[str, Any]]:
        """
        Find products where a specific platform has the best price.
        """
        platform_deals = []
        
        for comparison in comparisons:
            if comparison.best_platform == platform:
                # Check if it's significantly cheaper
                if comparison.savings_percent >= 5.0:
                    platform_deals.append(comparison)
        
        return self.find_best_deals(platform_deals, min_savings_percent=0)
    
    def get_price_alerts_worthy(
        self,
        comparisons: List[PriceComparison],
        threshold_percent: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Find products worth setting price alerts for.
        
        These are products with high price variance across platforms,
        suggesting prices fluctuate and alerts could catch good deals.
        """
        alert_worthy = []
        
        for comparison in comparisons:
            if comparison.available_on < 2:
                continue
            
            # Check price variance
            price_range_percent = comparison.savings_percent
            
            if price_range_percent >= threshold_percent:
                alert_worthy.append({
                    "product_id": comparison.product_id,
                    "product_name": comparison.product_name,
                    "brand": comparison.brand,
                    "current_best_price": comparison.best_price,
                    "current_highest_price": comparison.highest_price,
                    "price_variance_percent": round(price_range_percent, 1),
                    "suggested_alert_price": round(comparison.best_price * 0.95, 2),
                    "best_platform": comparison.best_platform
                })
        
        # Sort by variance (highest first)
        alert_worthy.sort(key=lambda x: x["price_variance_percent"], reverse=True)
        
        return alert_worthy
    
    def get_summary(
        self,
        comparisons: List[PriceComparison]
    ) -> Dict[str, Any]:
        """
        Get a summary of deals across all comparisons.
        """
        if not comparisons:
            return {
                "total_products": 0,
                "avg_savings_percent": 0,
                "platform_winners": {},
                "category_breakdown": {}
            }
        
        total_savings_percent = 0
        platform_wins = {}
        category_counts = {}
        
        for comparison in comparisons:
            total_savings_percent += comparison.savings_percent
            
            # Count platform wins
            if comparison.best_platform:
                platform_wins[comparison.best_platform] = platform_wins.get(
                    comparison.best_platform, 0
                ) + 1
            
            # Count by category
            category_counts[comparison.category] = category_counts.get(
                comparison.category, 0
            ) + 1
        
        # Calculate platform win percentages
        total_products = len(comparisons)
        platform_winners = {
            platform: {
                "wins": wins,
                "percent": round((wins / total_products) * 100, 1)
            }
            for platform, wins in sorted(
                platform_wins.items(),
                key=lambda x: x[1],
                reverse=True
            )
        }
        
        return {
            "total_products": total_products,
            "avg_savings_percent": round(total_savings_percent / total_products, 1),
            "platform_winners": platform_winners,
            "category_breakdown": category_counts,
            "best_platform_overall": max(platform_wins.keys(), key=lambda k: platform_wins[k]) if platform_wins else None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return self._stats
    
    def _log(self, event_type: str, data: Dict = None, level: str = "INFO") -> None:
        """Log an event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "agent": "deal_finder",
            "event_type": event_type,
            "data": data or {}
        }
        
        log_file = LOGS_DIR / f"agent-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass


# Singleton instance
_deal_finder: Optional[DealFinderAgent] = None


def get_deal_finder() -> DealFinderAgent:
    """Get the singleton deal finder instance."""
    global _deal_finder
    if _deal_finder is None:
        _deal_finder = DealFinderAgent()
    return _deal_finder

