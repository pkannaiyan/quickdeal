"""
Blinkit Scraper.

Scrapes product data from Blinkit (formerly Grofers).
Note: This uses simulated data for demonstration. In production,
you would need to implement actual API calls or web scraping.
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base_scraper import BaseScraper

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product, ProductCategory


class BlinkitScraper(BaseScraper):
    """
    Scraper for Blinkit quick commerce platform.
    """
    
    PLATFORM_ID = "blinkit"
    PLATFORM_NAME = "Blinkit"
    BASE_URL = "https://blinkit.com"
    LOGO = "🟢"
    DELIVERY_TIME = "10-20 min"
    
    # API endpoints (for reference - actual implementation would use these)
    SEARCH_API = "https://blinkit.com/v2/search"
    PRODUCT_API = "https://blinkit.com/v2/product"
    
    def __init__(self, pincode: str = None):
        super().__init__(pincode=pincode)
        
        # Load product database (prices will be generated dynamically)
        self._product_database = self._load_product_database()
        
        # Platform-specific price variation range
        self._price_range = (0.97, 1.05)  # Blinkit tends to be slightly higher
    
    def _load_product_database(self) -> List[Dict]:
        """Load the product database."""
        try:
            from data.product_database import PRODUCT_DATABASE, get_product_image
            return PRODUCT_DATABASE
        except ImportError:
            return []
    
    @property
    def _sample_products(self) -> List[Dict]:
        """Generate products with dynamic pricing (called on each access)."""
        import random
        from data.product_database import get_product_image
        
        if not self._product_database:
            return self._get_fallback_products()
        
        products = []
        for i, p in enumerate(self._product_database):
            # Apply platform-specific pricing with slight variation
            price_variation = random.uniform(*self._price_range)
            base_price = p["base_price"] * price_variation
            products.append({
                "id": f"BL{1001 + i}",
                "name": p["name"],
                "brand": p.get("brand"),
                "category": p["category"],
                "quantity": p["quantity"],
                "price": round(base_price, 0),
                "mrp": p["mrp"],
                "image": get_product_image(p["name"], p.get("category")),
                "available": random.random() > 0.05  # 95% availability
            })
        return products
    
    def _get_fallback_products(self) -> List[Dict]:
        """Fallback product list if database not available."""
        return [
            {"id": "1001", "name": "Amul Taaza Toned Fresh Milk", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "price": 66, "mrp": 68, "available": True},
            {"id": "1002", "name": "Amul Gold Full Cream Milk", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "price": 72, "mrp": 74, "available": True},
            {"id": "1003", "name": "Mother Dairy Milk", "brand": "Mother Dairy", "category": "dairy_bread", "quantity": "1 L", "price": 64, "mrp": 66, "available": True},
            {"id": "1004", "name": "Britannia Brown Bread", "brand": "Britannia", "category": "dairy_bread", "quantity": "400 g", "price": 45, "mrp": 48, "available": True},
            {"id": "1005", "name": "Parle-G Gold Biscuits", "brand": "Parle", "category": "snacks_beverages", "quantity": "1 kg", "price": 99, "mrp": 110, "available": True},
            {"id": "1006", "name": "Lays Classic Salted Chips", "brand": "Lays", "category": "snacks_beverages", "quantity": "177 g", "price": 40, "mrp": 40, "available": True},
            {"id": "1007", "name": "Coca-Cola Soft Drink", "brand": "Coca-Cola", "category": "snacks_beverages", "quantity": "2.25 L", "price": 98, "mrp": 100, "available": True},
            {"id": "1008", "name": "Aashirvaad Atta", "brand": "Aashirvaad", "category": "staples", "quantity": "5 kg", "price": 289, "mrp": 305, "available": True},
            {"id": "1009", "name": "Fortune Rice Bran Oil", "brand": "Fortune", "category": "staples", "quantity": "5 L", "price": 789, "mrp": 845, "available": True},
            {"id": "1010", "name": "Tata Salt", "brand": "Tata", "category": "staples", "quantity": "1 kg", "price": 28, "mrp": 28, "available": True},
            {"id": "1011", "name": "Surf Excel Easy Wash", "brand": "Surf Excel", "category": "household", "quantity": "1.5 kg", "price": 229, "mrp": 260, "available": True},
            {"id": "1012", "name": "Dettol Antiseptic Liquid", "brand": "Dettol", "category": "personal_care", "quantity": "550 ml", "price": 179, "mrp": 199, "available": True},
            {"id": "1013", "name": "Fresh Onion", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "price": 35, "mrp": 40, "available": True},
            {"id": "1014", "name": "Fresh Tomato", "brand": None, "category": "fruits_vegetables", "quantity": "1 kg", "price": 40, "mrp": 45, "available": True},
            {"id": "1015", "name": "Maggi 2-Minute Noodles", "brand": "Maggi", "category": "snacks_beverages", "quantity": "560 g (Pack of 8)", "price": 96, "mrp": 104, "available": True},
        ]
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """
        Search for products on Blinkit.
        
        In production, this would call the actual API.
        For demonstration, we search the sample data.
        """
        self._log(f"Searching for: {query}")
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        query_lower = query.lower()
        results = []
        
        for item in self._sample_products:
            # Simple text matching
            name_match = query_lower in item["name"].lower()
            brand_match = item.get("brand") and query_lower in item["brand"].lower()
            
            if name_match or brand_match:
                product = self._convert_to_product(item)
                results.append(product)
                
                if len(results) >= limit:
                    break
        
        self._stats["products_scraped"] += len(results)
        self._log(f"Found {len(results)} products for '{query}'")
        
        return results
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get a specific product by ID."""
        self._log(f"Getting product: {product_id}")
        
        await asyncio.sleep(0.05)
        
        for item in self._sample_products:
            if item["id"] == product_id:
                return self._convert_to_product(item)
        
        return None
    
    async def get_category_products(
        self,
        category: str,
        limit: int = 50
    ) -> List[Product]:
        """Get products from a category."""
        self._log(f"Getting category: {category}")
        
        await asyncio.sleep(0.1)
        
        results = []
        for item in self._sample_products:
            if item.get("category") == category:
                product = self._convert_to_product(item)
                results.append(product)
                
                if len(results) >= limit:
                    break
        
        self._stats["products_scraped"] += len(results)
        return results
    
    def _convert_to_product(self, item: Dict) -> Product:
        """Convert raw data to Product model."""
        quantity_text, unit, unit_value = self._parse_quantity(item.get("quantity", ""))
        
        mrp = item.get("mrp", item["price"])
        discount = ((mrp - item["price"]) / mrp * 100) if mrp > item["price"] else 0
        
        # Generate proper Blinkit search URL
        search_term = item["name"].replace(" ", "%20")
        product_url = f"https://blinkit.com/s/?q={search_term}"
        
        return Product(
            id=self._generate_product_id(item["id"]),
            name=item["name"],
            brand=item.get("brand"),
            category=ProductCategory(item.get("category", "other")),
            quantity=quantity_text,
            unit=unit,
            unit_value=unit_value,
            platform=self.PLATFORM_ID,
            platform_product_id=item["id"],
            url=product_url,
            current_price=float(item["price"]),
            mrp=float(mrp),
            discount_percent=round(discount, 2),
            is_available=item.get("available", True),
            stock_status="in_stock" if item.get("available", True) else "out_of_stock",
            image_url=item.get("image") or get_product_image(item["name"], item.get("category")),
            thumbnail_url=item.get("image") or get_product_image(item["name"], item.get("category")),
            scraped_at=datetime.now(),
            location_pincode=self.pincode
        )
    
    async def get_all_products(self) -> List[Product]:
        """Get all sample products (for demo purposes)."""
        return [self._convert_to_product(item) for item in self._sample_products]

