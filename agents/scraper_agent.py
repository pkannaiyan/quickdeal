"""
Scraper Agent - Orchestrates scraping across all platforms.

This agent manages the scraping process, coordinating multiple
platform scrapers and aggregating results.
"""
import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product, ProductCategory
from api.config import PLATFORMS, LOGS_DIR

# Check if real scrapers should be used
USE_REAL_SCRAPERS = os.getenv("USE_REAL_SCRAPERS", "false").lower() == "true"

# Import both real and demo scrapers for hybrid mode
from scrapers import (
    BlinkitScraper as DemoBlinkitScraper,
    ZeptoScraper as DemoZeptoScraper,
    InstamartScraper as DemoInstamartScraper,
    BigBasketScraper as DemoBigBasketScraper,
    JioMartScraper as DemoJioMartScraper
)

if USE_REAL_SCRAPERS:
    from scrapers.real_blinkit_scraper import RealBlinkitScraper
    from scrapers.real_zepto_scraper import RealZeptoScraper
    from scrapers.real_bigbasket_scraper import RealBigBasketScraper
    from scrapers.real_instamart_scraper import RealInstamartScraper
    from scrapers.real_jiomart_scraper import RealJioMartScraper
    print("🔴 REAL-TIME SCRAPING ENABLED - Fetching live prices from platforms")
else:
    print("🟡 DEMO MODE - Using sample product data")

# Alias for compatibility
BlinkitScraper = DemoBlinkitScraper
ZeptoScraper = DemoZeptoScraper
InstamartScraper = DemoInstamartScraper
BigBasketScraper = DemoBigBasketScraper
JioMartScraper = DemoJioMartScraper


class ScraperAgent:
    """
    Orchestrates scraping across multiple quick commerce platforms.
    
    Features:
    - Parallel scraping across platforms
    - Intelligent rate limiting
    - Error handling and retry logic
    - Result aggregation
    """
    
    def __init__(self, pincode: str = "400001"):
        """
        Initialize the scraper agent.
        
        Args:
            pincode: Location pincode for accurate pricing
        """
        self.pincode = pincode
        
        # Initialize all scrapers
        self.scrapers = {
            "blinkit": BlinkitScraper(pincode=pincode),
            "zepto": ZeptoScraper(pincode=pincode),
            "instamart": InstamartScraper(pincode=pincode),
            "bigbasket": BigBasketScraper(pincode=pincode),
            "jiomart": JioMartScraper(pincode=pincode),
        }
        
        # Statistics
        self._stats = {
            "total_searches": 0,
            "total_products_found": 0,
            "search_times": [],
            "errors": []
        }
    
    async def search_all_platforms(
        self,
        query: str,
        platforms: List[str] = None,
        limit_per_platform: int = 20
    ) -> Dict[str, List[Product]]:
        """
        Search for products across all platforms in parallel.
        
        Args:
            query: Search query
            platforms: List of platform IDs to search (None = all)
            limit_per_platform: Max results per platform
        
        Returns:
            Dict mapping platform ID to list of products
        """
        start_time = datetime.now()
        self._log("search_start", {"query": query, "platforms": platforms})
        
        # Determine which platforms to search
        platform_ids = platforms or list(self.scrapers.keys())
        
        # Create search tasks for each platform
        tasks = {}
        for platform_id in platform_ids:
            if platform_id in self.scrapers:
                tasks[platform_id] = self.scrapers[platform_id].search(
                    query, limit=limit_per_platform
                )
        
        # Execute all searches in parallel
        results = {}
        platform_results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        for platform_id, result in zip(tasks.keys(), platform_results):
            if isinstance(result, Exception):
                self._log("search_error", {
                    "platform": platform_id,
                    "error": str(result)
                }, level="ERROR")
                self._stats["errors"].append({
                    "platform": platform_id,
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
                results[platform_id] = []
            else:
                results[platform_id] = result
        
        # Update stats
        search_time = (datetime.now() - start_time).total_seconds()
        self._stats["total_searches"] += 1
        self._stats["total_products_found"] += sum(len(p) for p in results.values())
        self._stats["search_times"].append(search_time)
        
        self._log("search_complete", {
            "query": query,
            "results_count": {k: len(v) for k, v in results.items()},
            "search_time_seconds": search_time
        })
        
        return results
    
    async def get_product_from_all(
        self,
        product_name: str,
        platforms: List[str] = None
    ) -> Dict[str, Optional[Product]]:
        """
        Get a specific product from all platforms.
        
        Useful for comparing a known product across platforms.
        
        Args:
            product_name: Product name to search for
            platforms: Platforms to search
        
        Returns:
            Dict mapping platform ID to product (or None if not found)
        """
        # Search with tight limit
        results = await self.search_all_platforms(
            query=product_name,
            platforms=platforms,
            limit_per_platform=5
        )
        
        # Get best match from each platform
        best_matches = {}
        for platform_id, products in results.items():
            if products:
                # Take first result (most relevant)
                best_matches[platform_id] = products[0]
            else:
                best_matches[platform_id] = None
        
        return best_matches
    
    async def get_category_from_all(
        self,
        category: str,
        platforms: List[str] = None,
        limit_per_platform: int = 50
    ) -> Dict[str, List[Product]]:
        """
        Get products from a category across all platforms.
        
        Args:
            category: Category ID
            platforms: Platforms to search
            limit_per_platform: Max results per platform
        
        Returns:
            Dict mapping platform ID to products
        """
        platform_ids = platforms or list(self.scrapers.keys())
        
        tasks = {}
        for platform_id in platform_ids:
            if platform_id in self.scrapers:
                tasks[platform_id] = self.scrapers[platform_id].get_category_products(
                    category, limit=limit_per_platform
                )
        
        results = {}
        platform_results = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True
        )
        
        for platform_id, result in zip(tasks.keys(), platform_results):
            if isinstance(result, Exception):
                results[platform_id] = []
            else:
                results[platform_id] = result
        
        return results
    
    async def get_all_products(self, sample_size: int = None) -> Dict[str, List[Product]]:
        """
        Get products from all platforms with random sampling for variety.
        
        Args:
            sample_size: If provided, randomly sample this many products per platform
        
        Returns:
            Dict mapping platform ID to products
        """
        import random
        
        results = {}
        
        for platform_id, scraper in self.scrapers.items():
            try:
                if hasattr(scraper, 'get_all_products'):
                    products = await scraper.get_all_products()
                    
                    # Randomly sample products for variety on each call
                    if sample_size and len(products) > sample_size:
                        products = random.sample(products, sample_size)
                    else:
                        # Shuffle to get different order each time
                        random.shuffle(products)
                    
                    results[platform_id] = products
            except Exception as e:
                self._log("get_all_error", {
                    "platform": platform_id,
                    "error": str(e)
                }, level="ERROR")
                results[platform_id] = []
        
        return results
    
    def get_platform_info(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Get platform configuration and status."""
        if platform_id not in PLATFORMS:
            return None
        
        info = PLATFORMS[platform_id].copy()
        
        # Add scraper stats if available
        if platform_id in self.scrapers:
            info["scraper_stats"] = self.scrapers[platform_id].get_stats()
        
        return info
    
    def get_all_platforms(self) -> List[Dict[str, Any]]:
        """Get info about all supported platforms."""
        platforms = []
        for platform_id, config in PLATFORMS.items():
            info = config.copy()
            info["id"] = platform_id
            info["is_active"] = platform_id in self.scrapers
            
            if platform_id in self.scrapers:
                stats = self.scrapers[platform_id].get_stats()
                info["products_scraped"] = stats.get("products_scraped", 0)
                info["last_request"] = stats.get("last_request")
            
            platforms.append(info)
        
        return platforms
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        avg_search_time = (
            sum(self._stats["search_times"]) / len(self._stats["search_times"])
            if self._stats["search_times"] else 0
        )
        
        return {
            "total_searches": self._stats["total_searches"],
            "total_products_found": self._stats["total_products_found"],
            "average_search_time_seconds": round(avg_search_time, 3),
            "error_count": len(self._stats["errors"]),
            "recent_errors": self._stats["errors"][-5:],
            "scraper_stats": {
                pid: scraper.get_stats()
                for pid, scraper in self.scrapers.items()
            }
        }
    
    def _log(self, event_type: str, data: Dict = None, level: str = "INFO") -> None:
        """Log an event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "agent": "scraper_agent",
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
_scraper_agent: Optional[ScraperAgent] = None


def get_scraper_agent(pincode: str = "400001") -> ScraperAgent:
    """Get the singleton scraper agent instance."""
    global _scraper_agent
    if _scraper_agent is None:
        _scraper_agent = ScraperAgent(pincode=pincode)
    return _scraper_agent

