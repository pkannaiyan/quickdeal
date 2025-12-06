"""
Real Swiggy Instamart Scraper.

Scrapes actual product data from Swiggy Instamart.
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


class RealInstamartScraper(BaseScraper):
    """
    Real scraper for Swiggy Instamart.
    """
    
    PLATFORM_ID = "instamart"
    PLATFORM_NAME = "Swiggy Instamart"
    BASE_URL = "https://www.swiggy.com"
    LOGO = "🟠"
    DELIVERY_TIME = "15-30 min"
    
    # Instamart API endpoints
    API_BASE = "https://www.swiggy.com/api/instamart"
    SEARCH_API = "https://www.swiggy.com/api/instamart/search"
    
    def __init__(self, pincode: str = "400001", lat: float = 19.0760, lng: float = 72.8777):
        super().__init__(pincode=pincode)
        self.lat = lat
        self.lng = lng
        self._store_id = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get Instamart-specific headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/instamart",
            "Content-Type": "application/json",
        }
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """Search for products on Swiggy Instamart."""
        self._log("search_start", {"query": query, "limit": limit})
        
        await self._rate_limit()
        
        products = []
        
        try:
            # Try the search API first
            params = {
                "query": query,
                "lat": self.lat,
                "lng": self.lng,
                "pageSize": min(limit, 50),
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.SEARCH_API,
                    params=params,
                    headers=self._get_headers()
                )
                
                self._stats["requests_made"] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response structure
                    items = data.get("data", {}).get("products", [])
                    if not items:
                        items = data.get("widgets", [])
                        for widget in items:
                            if "products" in widget:
                                items = widget["products"]
                                break
                    
                    for item in items[:limit]:
                        product = self._parse_product(item)
                        if product:
                            products.append(product)
                else:
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
            url = f"{self.BASE_URL}/instamart/search?custom_back=true&query={quote(query)}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    # Try to find JSON data in the page
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Look for __NEXT_DATA__ or similar
                    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
                    if script_tag:
                        try:
                            data = json.loads(script_tag.string)
                            page_props = data.get("props", {}).get("pageProps", {})
                            items = page_props.get("products", [])
                            
                            for item in items[:limit]:
                                product = self._parse_product(item)
                                if product:
                                    products.append(product)
                        except json.JSONDecodeError:
                            pass
                    
                    # If no JSON, try HTML parsing
                    if not products:
                        cards = soup.find_all('div', {'class': re.compile(r'ProductCard|product-card')})
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
            product_id = str(item.get("id", item.get("product_id", item.get("variations", [{}])[0].get("id", ""))))
            name = item.get("name", item.get("product_name", ""))
            
            if not name:
                return None
            
            # Get variation data if available
            variations = item.get("variations", [{}])
            variation = variations[0] if variations else item
            
            # Pricing
            price = float(variation.get("price", item.get("price", 0))) / 100  # Usually in paise
            if price > 10000:  # If price seems to be in paise
                price = price / 100
            mrp = float(variation.get("mrp", item.get("mrp", price * 100))) / 100
            if mrp > 10000:
                mrp = mrp / 100
            
            # Ensure price is reasonable
            if price < 1:
                price = float(item.get("price", variation.get("price", 0)))
                mrp = float(item.get("mrp", variation.get("mrp", price)))
            
            # Brand
            brand = item.get("brand", item.get("brand_name"))
            
            # Quantity
            quantity = variation.get("quantity", item.get("quantity", "1 unit"))
            
            # Image
            image_url = item.get("image", item.get("image_url"))
            images = item.get("images", [])
            if not image_url and images:
                image_url = images[0] if isinstance(images[0], str) else images[0].get("url")
            
            # Availability
            is_available = item.get("in_stock", variation.get("in_stock", True))
            inventory = variation.get("inventory", item.get("inventory", 1))
            if inventory == 0:
                is_available = False
            
            discount = ((mrp - price) / mrp * 100) if mrp > price else 0
            
            quantity_text, unit, unit_value = self._parse_quantity(str(quantity))
            category = self._categorize_product(name, item.get("category", ""))
            
            return Product(
                id=self._generate_product_id(product_id),
                name=name,
                brand=brand,
                category=category,
                quantity=quantity_text or str(quantity),
                unit=unit,
                unit_value=unit_value,
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/instamart/item/{product_id}",
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
            name_elem = card.find('h3') or card.find('div', {'class': re.compile(r'name|title')})
            name = name_elem.get_text(strip=True) if name_elem else None
            if not name:
                return None
            
            # Price
            price_elem = card.find('span', {'class': re.compile(r'price|amount')})
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = float(re.sub(r'[^\d.]', '', price_text) or 0)
            
            # MRP
            mrp_elem = card.find('span', {'class': re.compile(r'mrp|strike')})
            mrp = float(re.sub(r'[^\d.]', '', mrp_elem.get_text()) if mrp_elem else price)
            
            # Product ID
            link = card.find('a', href=True)
            product_id = f"html_{hash(name)}"
            if link:
                href = link.get('href', '')
                match = re.search(r'/item/([^/?\s]+)', href)
                if match:
                    product_id = match.group(1)
            
            # Quantity
            qty_elem = card.find('span', {'class': re.compile(r'quantity|weight')})
            quantity = qty_elem.get_text(strip=True) if qty_elem else "1 unit"
            
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
                url=f"{self.BASE_URL}/instamart/item/{product_id}",
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
        return await self.search(product_id, limit=1)
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        """Get products from category."""
        return await self.search(category, limit=limit)

