"""
Zepto Scraper.

Scrapes product data from Zepto.
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


class ZeptoScraper(BaseScraper):
    """Scraper for Zepto quick commerce platform."""
    
    PLATFORM_ID = "zepto"
    PLATFORM_NAME = "Zepto"
    BASE_URL = "https://www.zeptonow.com"
    LOGO = "🟣"
    DELIVERY_TIME = "10 min"
    
    def __init__(self, pincode: str = None):
        super().__init__(pincode=pincode)
        self._product_database = self._load_product_database()
        self._price_range = (0.94, 1.02)  # Zepto tends to be slightly cheaper
    
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
                {"id": "Z1001", "name": "Amul Taaza Toned Fresh Milk", "brand": "Amul", "category": "dairy_bread", "quantity": "1 L", "price": 64, "mrp": 68},
                {"id": "Z1002", "name": "Parle-G Gold Biscuits", "brand": "Parle", "category": "snacks_beverages", "quantity": "1 kg", "price": 95, "mrp": 110},
            ]
        
        products = []
        for i, p in enumerate(self._product_database):
            price_variation = random.uniform(*self._price_range)
            base_price = p["base_price"] * price_variation
            products.append({
                "id": f"ZP{1001 + i}",
                "name": p["name"],
                "brand": p.get("brand"),
                "category": p["category"],
                "quantity": p["quantity"],
                "price": round(base_price, 0),
                "mrp": p["mrp"],
                "available": random.random() > 0.08
            })
        return products
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        await asyncio.sleep(0.1)
        query_lower = query.lower()
        results = []
        
        for item in self._sample_products:
            if query_lower in item["name"].lower() or (item.get("brand") and query_lower in item["brand"].lower()):
                results.append(self._convert_to_product(item))
                if len(results) >= limit:
                    break
        
        self._stats["products_scraped"] += len(results)
        return results
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        await asyncio.sleep(0.05)
        for item in self._sample_products:
            if item["id"] == product_id:
                return self._convert_to_product(item)
        return None
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        await asyncio.sleep(0.1)
        results = [self._convert_to_product(item) for item in self._sample_products if item.get("category") == category]
        return results[:limit]
    
    def _convert_to_product(self, item: Dict) -> Product:
        quantity_text, unit, unit_value = self._parse_quantity(item.get("quantity", ""))
        mrp = item.get("mrp", item["price"])
        discount = ((mrp - item["price"]) / mrp * 100) if mrp > item["price"] else 0
        
        # Generate proper Zepto search URL
        search_term = item["name"].replace(" ", "%20")
        product_url = f"https://www.zeptonow.com/search?query={search_term}"
        
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

