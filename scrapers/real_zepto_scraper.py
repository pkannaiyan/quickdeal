"""
Real Zepto Scraper.

Scrapes actual product data from Zepto using their API.
"""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from urllib.parse import quote

import httpx
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product, ProductCategory


class RealZeptoScraper(BaseScraper):
    """
    Real scraper for Zepto using their API.
    """
    
    PLATFORM_ID = "zepto"
    PLATFORM_NAME = "Zepto"
    BASE_URL = "https://www.zeptonow.com"
    LOGO = "🟣"
    DELIVERY_TIME = "10 min"
    
    # Zepto API endpoints
    API_BASE = "https://api.zeptonow.com"
    SEARCH_API = "https://api.zeptonow.com/api/v3/search"
    
    def __init__(self, pincode: str = "400001", lat: float = 19.0760, lng: float = 72.8777):
        super().__init__(pincode=pincode)
        self.lat = lat
        self.lng = lng
        self._store_id = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get Zepto-specific headers."""
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/",
            "x-platform": "web",
            "x-app-version": "1.0.0",
        }
        
        if self._store_id:
            headers["x-store-id"] = self._store_id
            
        return headers
    
    async def _get_store_id(self) -> Optional[str]:
        """Get store ID based on location."""
        if self._store_id:
            return self._store_id
            
        try:
            # API to get nearby store
            url = f"{self.API_BASE}/api/v1/config/store"
            params = {
                "lat": self.lat,
                "lng": self.lng
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, params=params, headers=self._get_headers())
                
                if response.status_code == 200:
                    data = response.json()
                    self._store_id = data.get("store_id") or data.get("data", {}).get("store_id")
                    return self._store_id
                    
        except Exception as e:
            self._log("store_id_error", {"error": str(e)}, level="WARNING")
        
        return None
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """Search for products on Zepto."""
        self._log("search_start", {"query": query, "limit": limit})
        
        await self._rate_limit()
        await self._get_store_id()
        
        products = []
        
        try:
            params = {
                "query": query,
                "page": 1,
                "pageSize": min(limit, 50),
            }
            
            if self._store_id:
                params["storeId"] = self._store_id
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.SEARCH_API,
                    params=params,
                    headers=self._get_headers()
                )
                
                self._stats["requests_made"] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse products from response
                    items = data.get("products", [])
                    if not items:
                        items = data.get("data", {}).get("products", [])
                    if not items:
                        items = data.get("results", [])
                    
                    for item in items[:limit]:
                        product = self._parse_product(item)
                        if product:
                            products.append(product)
                else:
                    self._log("api_error", {"status": response.status_code}, level="WARNING")
                    # Fallback to web scraping
                    products = await self._scrape_web_search(query, limit)
                    
        except Exception as e:
            self._log("search_error", {"error": str(e)}, level="ERROR")
            products = await self._scrape_web_search(query, limit)
        
        self._stats["products_scraped"] += len(products)
        return products
    
    async def _scrape_web_search(self, query: str, limit: int) -> List[Product]:
        """Fallback: Scrape from web."""
        products = []
        
        try:
            url = f"{self.BASE_URL}/search?query={quote(query)}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Find product cards
                    cards = soup.find_all('div', {'data-testid': re.compile(r'product-card')})
                    if not cards:
                        cards = soup.find_all('div', {'class': re.compile(r'ProductCard')})
                    
                    for card in cards[:limit]:
                        product = self._parse_html_product(card)
                        if product:
                            products.append(product)
                            
        except Exception as e:
            self._log("web_scrape_error", {"error": str(e)}, level="ERROR")
        
        return products
    
    def _parse_product(self, item: Dict) -> Optional[Product]:
        """Parse product from API response."""
        try:
            product_id = str(item.get("id", item.get("productId", "")))
            name = item.get("name", item.get("productName", ""))
            
            if not name:
                return None
            
            # Pricing
            price = float(item.get("sellingPrice", item.get("price", 0)))
            mrp = float(item.get("mrp", item.get("markedPrice", price)))
            
            # Brand
            brand = item.get("brand", item.get("brandName"))
            
            # Quantity
            quantity = item.get("packSize", item.get("quantity", "1 unit"))
            
            # Image
            image_url = item.get("image", item.get("imageUrl"))
            images = item.get("images", [])
            if not image_url and images:
                image_url = images[0] if isinstance(images[0], str) else images[0].get("url")
            
            # Availability
            is_available = item.get("inStock", True)
            if item.get("outOfStock"):
                is_available = False
            
            discount = ((mrp - price) / mrp * 100) if mrp > price else 0
            
            quantity_text, unit, unit_value = self._parse_quantity(quantity)
            category = self._categorize_product(name, item.get("category", ""))
            
            return Product(
                id=self._generate_product_id(product_id),
                name=name,
                brand=brand,
                category=category,
                quantity=quantity_text or quantity,
                unit=unit,
                unit_value=unit_value,
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/product/{product_id}",
                current_price=price,
                mrp=mrp,
                discount_percent=round(discount, 2),
                is_available=is_available,
                stock_status="in_stock" if is_available else "out_of_stock",
                image_url=image_url,
                scraped_at=datetime.now(),
                location_pincode=self.pincode
            )
            
        except Exception as e:
            self._log("parse_error", {"error": str(e)}, level="WARNING")
            return None
    
    def _parse_html_product(self, card) -> Optional[Product]:
        """Parse product from HTML."""
        try:
            name_elem = card.find('h4') or card.find('p', {'class': re.compile(r'name|title')})
            name = name_elem.get_text(strip=True) if name_elem else None
            if not name:
                return None
            
            # Price
            price_elem = card.find('span', {'class': re.compile(r'price|amount')})
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = float(re.sub(r'[^\d.]', '', price_text) or 0)
            
            # MRP
            mrp_elem = card.find('span', {'class': re.compile(r'mrp|strike|original')})
            mrp = float(re.sub(r'[^\d.]', '', mrp_elem.get_text()) if mrp_elem else price)
            
            # Quantity
            qty_elem = card.find('span', {'class': re.compile(r'quantity|weight|size')})
            quantity = qty_elem.get_text(strip=True) if qty_elem else "1 unit"
            
            # Product ID
            link = card.find('a', href=True)
            product_id = ""
            if link:
                href = link.get('href', '')
                match = re.search(r'/product/([^/?\s]+)', href)
                if match:
                    product_id = match.group(1)
            
            if not product_id:
                product_id = f"html_{hash(name)}"
            
            # Image
            img = card.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None
            
            discount = ((mrp - price) / mrp * 100) if mrp > price else 0
            quantity_text, unit, unit_value = self._parse_quantity(quantity)
            
            return Product(
                id=self._generate_product_id(product_id),
                name=name,
                brand=None,
                category=self._categorize_product(name),
                quantity=quantity_text or quantity,
                unit=unit,
                unit_value=unit_value,
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/product/{product_id}",
                current_price=price,
                mrp=mrp,
                discount_percent=round(discount, 2),
                is_available=True,
                stock_status="in_stock",
                image_url=image_url,
                scraped_at=datetime.now(),
                location_pincode=self.pincode
            )
            
        except Exception as e:
            self._log("html_parse_error", {"error": str(e)}, level="WARNING")
            return None
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get specific product."""
        await self._rate_limit()
        
        try:
            url = f"{self.API_BASE}/api/v1/products/{product_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    data = response.json()
                    return self._parse_product(data.get("product", data))
                    
        except Exception as e:
            self._log("get_product_error", {"error": str(e)}, level="ERROR")
        
        return None
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        """Get products from category."""
        return await self.search(category, limit=limit)

