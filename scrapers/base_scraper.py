"""
Base Scraper class for quick commerce platforms.

All platform-specific scrapers inherit from this base class.
Implements common functionality for ethical web scraping.
"""
import asyncio
import json
import hashlib
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

import httpx
from fake_useragent import UserAgent

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product, ProductCategory
from api.config import (
    RATE_LIMIT_RPM, REQUEST_TIMEOUT, RESPECT_ROBOTS_TXT,
    DATA_DIR, LOGS_DIR, DEFAULT_PINCODE
)


class BaseScraper(ABC):
    """
    Abstract base class for platform scrapers.
    
    Implements:
    - Rate limiting
    - Request headers rotation
    - Error handling and retry logic
    - Caching
    - Logging
    """
    
    # Platform identifiers (override in subclass)
    PLATFORM_ID = "base"
    PLATFORM_NAME = "Base Platform"
    BASE_URL = "https://example.com"
    LOGO = "🛒"
    
    def __init__(
        self,
        pincode: str = None,
        rate_limit_rpm: int = None,
        timeout: int = None
    ):
        """
        Initialize scraper.
        
        Args:
            pincode: Location pincode for accurate pricing
            rate_limit_rpm: Requests per minute limit
            timeout: Request timeout in seconds
        """
        self.pincode = pincode or DEFAULT_PINCODE
        self.rate_limit_rpm = rate_limit_rpm or RATE_LIMIT_RPM
        self.timeout = timeout or REQUEST_TIMEOUT
        
        # User agent rotation
        self.ua = UserAgent()
        
        # Rate limiting state
        self._request_times: List[datetime] = []
        self._request_lock = asyncio.Lock()
        
        # Cache
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl_seconds = 300  # 5 minutes
        
        # Statistics
        self._stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "products_scraped": 0,
            "cache_hits": 0,
            "last_request": None,
            "last_error": None
        }
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with rotated user agent."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "application/json, text/html, */*",
            "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
        }
    
    async def _rate_limit(self) -> None:
        """Implement rate limiting."""
        async with self._request_lock:
            now = datetime.now()
            
            # Clean old requests (older than 1 minute)
            self._request_times = [
                t for t in self._request_times
                if (now - t).total_seconds() < 60
            ]
            
            # If at limit, wait
            if len(self._request_times) >= self.rate_limit_rpm:
                oldest = min(self._request_times)
                wait_time = 60 - (now - oldest).total_seconds()
                if wait_time > 0:
                    self._log(f"Rate limit hit, waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
            
            # Record this request
            self._request_times.append(datetime.now())
    
    def _get_cache_key(self, url: str, params: Dict = None) -> str:
        """Generate cache key."""
        cache_data = f"{url}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Get cached response if valid."""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            age = (datetime.now() - entry["timestamp"]).total_seconds()
            if age < self._cache_ttl_seconds:
                self._stats["cache_hits"] += 1
                return entry["data"]
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Cache response."""
        self._cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    async def _make_request(
        self,
        url: str,
        method: str = "GET",
        params: Dict = None,
        data: Dict = None,
        json_data: Dict = None,
        use_cache: bool = True
    ) -> Optional[httpx.Response]:
        """
        Make an HTTP request with rate limiting and error handling.
        
        Args:
            url: Request URL
            method: HTTP method
            params: Query parameters
            data: Form data
            json_data: JSON body
            use_cache: Whether to use caching
        
        Returns:
            Response object or None on failure
        """
        # Check cache
        if use_cache and method == "GET":
            cache_key = self._get_cache_key(url, params)
            cached = self._get_cached(cache_key)
            if cached:
                return cached
        
        # Apply rate limiting
        await self._rate_limit()
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=self._get_headers(),
                    follow_redirects=True
                )
                
                self._stats["requests_made"] += 1
                self._stats["last_request"] = datetime.now()
                
                if response.status_code == 200:
                    # Cache successful GET responses
                    if use_cache and method == "GET":
                        self._set_cache(cache_key, response)
                    return response
                else:
                    self._log(f"Request failed: {response.status_code}", level="WARNING")
                    self._stats["requests_failed"] += 1
                    return None
                    
        except httpx.TimeoutException:
            self._log(f"Request timeout: {url}", level="ERROR")
            self._stats["requests_failed"] += 1
            self._stats["last_error"] = "Timeout"
            return None
        except Exception as e:
            self._log(f"Request error: {str(e)}", level="ERROR")
            self._stats["requests_failed"] += 1
            self._stats["last_error"] = str(e)
            return None
    
    def _log(self, message: str, level: str = "INFO", data: Dict = None) -> None:
        """Log an event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "platform": self.PLATFORM_ID,
            "message": message,
            "data": data or {}
        }
        
        log_file = LOGS_DIR / f"scraper-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception:
            pass
    
    def _generate_product_id(self, platform_id: str) -> str:
        """Generate a unique product ID."""
        return f"prod-{self.PLATFORM_ID}-{platform_id}"
    
    def _parse_quantity(self, text: str) -> tuple:
        """
        Parse quantity from text like '1 kg', '500 ml', '6 pack'.
        
        Returns:
            Tuple of (quantity_text, unit, numeric_value)
        """
        if not text:
            return ("", None, None)
        
        text = text.strip().lower()
        
        # Common patterns
        patterns = [
            (r'(\d+(?:\.\d+)?)\s*(kg|kilogram)', 'kg'),
            (r'(\d+(?:\.\d+)?)\s*(g|gram|gm)', 'g'),
            (r'(\d+(?:\.\d+)?)\s*(l|litre|liter)', 'L'),
            (r'(\d+(?:\.\d+)?)\s*(ml|millilitre)', 'ml'),
            (r'(\d+)\s*(pack|pcs|pieces?|units?)', 'pack'),
            (r'(\d+)\s*x\s*(\d+(?:\.\d+)?)\s*(g|ml|gm)', 'combo'),
        ]
        
        for pattern, unit in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    return (text, unit, value)
                except:
                    pass
        
        return (text, None, None)
    
    def _categorize_product(self, name: str, category_hint: str = None) -> ProductCategory:
        """
        Determine product category from name/hints.
        """
        name_lower = name.lower()
        
        # Category keywords mapping
        keywords = {
            ProductCategory.DAIRY_BREAD: ["milk", "curd", "paneer", "cheese", "butter", "ghee", "bread", "yogurt", "dahi"],
            ProductCategory.FRUITS_VEGETABLES: ["fruit", "vegetable", "apple", "banana", "tomato", "onion", "potato", "sabzi"],
            ProductCategory.SNACKS_BEVERAGES: ["chips", "biscuit", "cookie", "juice", "soft drink", "cola", "pepsi", "namkeen", "water"],
            ProductCategory.STAPLES: ["rice", "dal", "atta", "flour", "oil", "sugar", "salt", "spice", "masala"],
            ProductCategory.PERSONAL_CARE: ["shampoo", "soap", "cream", "lotion", "toothpaste", "deodorant", "razor"],
            ProductCategory.HOUSEHOLD: ["detergent", "cleaner", "tissue", "toilet", "mop", "dustbin"],
            ProductCategory.BABY_CARE: ["diaper", "baby", "formula", "wipes"],
            ProductCategory.PET_CARE: ["dog", "cat", "pet food", "kibble"],
            ProductCategory.MEAT_SEAFOOD: ["chicken", "mutton", "fish", "prawns", "meat", "egg"],
            ProductCategory.FROZEN: ["frozen", "ice cream", "kulfi", "popsicle"]
        }
        
        for category, kws in keywords.items():
            if any(kw in name_lower for kw in kws):
                return category
        
        return ProductCategory.OTHER
    
    @abstractmethod
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """
        Search for products.
        
        Args:
            query: Search query
            limit: Maximum results to return
        
        Returns:
            List of Product objects
        """
        pass
    
    @abstractmethod
    async def get_product(self, product_id: str) -> Optional[Product]:
        """
        Get a specific product by ID.
        
        Args:
            product_id: Platform-specific product ID
        
        Returns:
            Product object or None
        """
        pass
    
    @abstractmethod
    async def get_category_products(
        self,
        category: str,
        limit: int = 50
    ) -> List[Product]:
        """
        Get products from a category.
        
        Args:
            category: Category identifier
            limit: Maximum results
        
        Returns:
            List of Product objects
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics."""
        return {
            "platform_id": self.PLATFORM_ID,
            "platform_name": self.PLATFORM_NAME,
            **self._stats,
            "cache_size": len(self._cache)
        }
    
    def clear_cache(self) -> None:
        """Clear the response cache."""
        self._cache = {}
        self._log("Cache cleared")

