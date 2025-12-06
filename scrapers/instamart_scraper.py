"""
Swiggy Instamart Scraper.
"""
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

from .base_scraper import BaseScraper

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product, ProductCategory
from data.product_database import get_product_image


class InstamartScraper(BaseScraper):
    """Scraper for Swiggy Instamart."""
    
    PLATFORM_ID = "instamart"
    PLATFORM_NAME = "Swiggy Instamart"
    BASE_URL = "https://www.swiggy.com/instamart"
    LOGO = "🟠"
    DELIVERY_TIME = "15-30 min"
    
    def __init__(self, pincode: str = None):
        super().__init__(pincode=pincode)
        self._product_database = self._load_product_database()
        self._price_range = (0.96, 1.04)  # Instamart mid-range pricing
    
    def _load_product_database(self) -> List[Dict]:
        try:
            from data.product_database import PRODUCT_DATABASE, get_product_image
            return PRODUCT_DATABASE
        except ImportError:
            return []
    
    @property
    def _sample_products(self) -> List[Dict]:
        """Generate products with dynamic pricing."""
        import random
        
        if not self._product_database:
            return [
                {"id": "SM1001", "name": "Amul Taaza Toned Fresh Milk", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "price": 65, "mrp": 68},
            ]
        
        products = []
        for i, p in enumerate(self._product_database):
            price_variation = random.uniform(*self._price_range)
            base_price = p["base_price"] * price_variation
            products.append({
                "id": f"SM{1001 + i}",
                "name": p["name"],
                "brand": p.get("brand"),
                "category": p["category"],
                "quantity": p["quantity"],
                "price": round(base_price, 0),
                "mrp": p["mrp"],
                "available": random.random() > 0.1
            })
        return products
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        await asyncio.sleep(0.1)
        query_lower = query.lower()
        results = [self._convert_to_product(item) for item in self._sample_products 
                   if query_lower in item["name"].lower() or (item.get("brand") and query_lower in item["brand"].lower())]
        return results[:limit]
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        for item in self._sample_products:
            if item["id"] == product_id:
                return self._convert_to_product(item)
        return None
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        results = [self._convert_to_product(item) for item in self._sample_products if item.get("category") == category]
        return results[:limit]
    
    def _convert_to_product(self, item: Dict) -> Product:
        quantity_text, unit, unit_value = self._parse_quantity(item.get("quantity", ""))
        mrp = item.get("mrp", item["price"])
        discount = ((mrp - item["price"]) / mrp * 100) if mrp > item["price"] else 0
        
        # Generate proper Swiggy Instamart search URL
        search_term = item["name"].replace(" ", "%20")
        product_url = f"https://www.swiggy.com/instamart/search?custom_back=true&query={search_term}"
        
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
            is_available=True,
            stock_status="in_stock",
            image_url=get_product_image(item["name"], item.get("category")),
            thumbnail_url=get_product_image(item["name"], item.get("category")),
            scraped_at=datetime.now(),
            location_pincode=self.pincode
        )
    
    async def get_all_products(self) -> List[Product]:
        return [self._convert_to_product(item) for item in self._sample_products]

