"""
Real Scraper Agent - Uses actual web scrapers.

This agent uses real web scraping to get live prices from platforms.
Use with caution and respect rate limits.
"""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product
from scrapers.real_blinkit_scraper import RealBlinkitScraper
from scrapers.real_zepto_scraper import RealZeptoScraper
from scrapers.real_bigbasket_scraper import RealBigBasketScraper
from scrapers.instamart_scraper import InstamartScraper  # Fallback to demo
from scrapers.jiomart_scraper import JioMartScraper  # Fallback to demo
from api.config import PLATFORMS, LOGS_DIR

# Environment variable to enable real scrapers
USE_REAL_SCRAPERS = os.getenv("USE_REAL_SCRAPERS", "false").lower() == "true"


class RealScraperAgent:
    """
    Scraper agent that uses real web scrapers.
    
    Set USE_REAL_SCRAPERS=true to enable live scraping.
    """
    
    def __init__(self, pincode: str = "400001", use_real: bool = None):
        """
        Initialize the scraper agent.
        
        Args:
            pincode: Location pincode
            use_real: Override USE_REAL_SCRAPERS env variable
        """
        self.pincode = pincode
        self.use_real = use_real if use_real is not None else USE_REAL_SCRAPERS
        
        # Initialize scrapers based on mode
        if self.use_real:
            self.scrapers = {
                "blinkit": RealBlinkitScraper(pincode=pincode),
                "zepto": RealZeptoScraper(pincode=pincode),
                "bigbasket": RealBigBasketScraper(pincode=pincode),
                # Fallback to demo for others
                "instamart": InstamartScraper(pincode=pincode),
                "jiomart": JioMartScraper(pincode=pincode),
            }
        else:
            # Import demo scrapers
            from scrapers import (
                BlinkitScraper, ZeptoScraper, InstamartScraper,
                BigBasketScraper, JioMartScraper
            )
            self.scrapers = {
                "blinkit": BlinkitScraper(pincode=pincode),
                "zepto": ZeptoScraper(pincode=pincode),
                "instamart": InstamartScraper(pincode=pincode),
                "bigbasket": BigBasketScraper(pincode=pincode),
                "jiomart": JioMartScraper(pincode=pincode),
            }
        
        self._log("agent_initialized", {
            "mode": "real" if self.use_real else "demo",
            "scrapers": list(self.scrapers.keys())
        })
    
    async def search_all_platforms(
        self,
        query: str,
        platforms: List[str] = None,
        limit_per_platform: int = 20
    ) -> Dict[str, List[Product]]:
        """
        Search for products across all platforms in parallel.
        """
        platform_ids = platforms or list(self.scrapers.keys())
        
        tasks = {}
        for platform_id in platform_ids:
            if platform_id in self.scrapers:
                tasks[platform_id] = self.scrapers[platform_id].search(
                    query, limit=limit_per_platform
                )
        
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
                results[platform_id] = []
            else:
                results[platform_id] = result
        
        return results
    
    async def get_all_products(self) -> Dict[str, List[Product]]:
        """Get all available products."""
        results = {}
        
        for platform_id, scraper in self.scrapers.items():
            try:
                if hasattr(scraper, 'get_all_products'):
                    products = await scraper.get_all_products()
                    results[platform_id] = products
                else:
                    # Search for common items
                    products = await scraper.search("", limit=50)
                    results[platform_id] = products
            except Exception as e:
                self._log("get_all_error", {
                    "platform": platform_id,
                    "error": str(e)
                }, level="ERROR")
                results[platform_id] = []
        
        return results
    
    def get_all_platforms(self) -> List[Dict]:
        """Get info about all platforms."""
        platforms = []
        for platform_id, config in PLATFORMS.items():
            info = config.copy()
            info["id"] = platform_id
            info["is_active"] = platform_id in self.scrapers
            info["mode"] = "real" if self.use_real else "demo"
            platforms.append(info)
        return platforms
    
    def get_stats(self) -> Dict:
        """Get scraper statistics."""
        stats = {
            "mode": "real" if self.use_real else "demo",
            "scrapers": {}
        }
        
        for platform_id, scraper in self.scrapers.items():
            stats["scrapers"][platform_id] = scraper.get_stats()
        
        return stats
    
    def _log(self, event_type: str, data: Dict = None, level: str = "INFO"):
        """Log event."""
        import json
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "agent": "real_scraper_agent",
            "event_type": event_type,
            "data": data or {}
        }
        
        log_file = LOGS_DIR / f"agent-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass


# Factory function to get appropriate scraper agent
def get_scraper_agent(pincode: str = "400001", use_real: bool = None):
    """
    Get a scraper agent.
    
    Args:
        pincode: Location pincode
        use_real: Use real scrapers (default from env)
    
    Returns:
        ScraperAgent instance
    """
    should_use_real = use_real if use_real is not None else USE_REAL_SCRAPERS
    
    if should_use_real:
        return RealScraperAgent(pincode=pincode, use_real=True)
    else:
        # Use demo scraper agent
        from agents.scraper_agent import ScraperAgent
        return ScraperAgent(pincode=pincode)

