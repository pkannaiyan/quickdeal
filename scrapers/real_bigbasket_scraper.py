"""
Real BigBasket Scraper.

Scrapes actual product data from BigBasket.
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


class RealBigBasketScraper(BaseScraper):
    """
    Real scraper for BigBasket.
    """
    
    PLATFORM_ID = "bigbasket"
    PLATFORM_NAME = "BigBasket"
    BASE_URL = "https://www.bigbasket.com"
    LOGO = "🟢"
    DELIVERY_TIME = "Same day"
    
    # BigBasket API
    SEARCH_API = "https://www.bigbasket.com/listing-svc/v2/products"
    
    def __init__(self, pincode: str = "400001"):
        super().__init__(pincode=pincode)
        self._member_id = None
        self._session_cookies = {}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get BigBasket-specific headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/",
            "x-channel": "web",
            "x-request-id": f"bb_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        }
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """Search for products on BigBasket."""
        self._log("search_start", {"query": query})
        
        await self._rate_limit()
        products = []
        
        try:
            params = {
                "slug": query.lower().replace(" ", "-"),
                "query": query,
                "page": 1,
                "tab_type": '["product"]',
                "sorted_on": "relevance",
                "listtype": 1
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
                    
                    tabs = data.get("tabs", [])
                    for tab in tabs:
                        if tab.get("type") == "product":
                            items = tab.get("product_info", {}).get("products", [])
                            for item in items[:limit]:
                                product = self._parse_product(item)
                                if product:
                                    products.append(product)
                            break
                else:
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
            url = f"{self.BASE_URL}/ps/?q={quote(query)}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Find product cards
                    cards = soup.find_all('div', {'class': re.compile(r'PaginateItems')})
                    if not cards:
                        cards = soup.find_all('li', {'class': re.compile(r'product')})
                    
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
            product_id = str(item.get("sku", item.get("id", "")))
            name = item.get("desc", item.get("name", ""))
            
            if not name:
                return None
            
            # Pricing
            pricing = item.get("pricing", {})
            price = float(pricing.get("discount", {}).get("mrp", pricing.get("mrp", 0)))
            mrp = float(pricing.get("mrp", price))
            
            # Sometimes discount price is separate
            if pricing.get("discount", {}).get("mrp"):
                price = float(pricing.get("discount", {}).get("mrp"))
            
            # Brand
            brand = item.get("brand", {}).get("name") if isinstance(item.get("brand"), dict) else item.get("brand")
            
            # Quantity
            quantity = item.get("w", item.get("pack_desc", "1 unit"))
            
            # Image
            images = item.get("images", [])
            image_url = None
            if images:
                if isinstance(images[0], dict):
                    image_url = images[0].get("s", images[0].get("m"))
                else:
                    image_url = images[0]
            
            # Availability
            availability = item.get("availability", {})
            is_available = availability.get("is_available", True)
            
            discount = ((mrp - price) / mrp * 100) if mrp > price else 0
            
            quantity_text, unit, unit_value = self._parse_quantity(quantity)
            category = self._categorize_product(name, item.get("tlc_n", ""))
            
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
                url=f"{self.BASE_URL}/pd/{product_id}",
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
            name_elem = card.find('a', {'class': re.compile(r'ProductName')})
            if not name_elem:
                name_elem = card.find('h3') or card.find('a', href=re.compile(r'/pd/'))
            
            name = name_elem.get_text(strip=True) if name_elem else None
            if not name:
                return None
            
            # Price
            price_elem = card.find('span', {'class': re.compile(r'discnt-price|Price')})
            price = float(re.sub(r'[^\d.]', '', price_elem.get_text()) if price_elem else 0)
            
            # MRP
            mrp_elem = card.find('span', {'class': re.compile(r'MRPStrikeText|mrp')})
            mrp = float(re.sub(r'[^\d.]', '', mrp_elem.get_text()) if mrp_elem else price)
            
            # Product ID from URL
            link = card.find('a', href=re.compile(r'/pd/'))
            product_id = ""
            if link:
                match = re.search(r'/pd/([^/?\s]+)', link.get('href', ''))
                if match:
                    product_id = match.group(1)
            
            if not product_id:
                product_id = f"html_{hash(name)}"
            
            # Image
            img = card.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None
            
            # Quantity
            qty_elem = card.find('span', {'class': re.compile(r'Label|pack')})
            quantity = qty_elem.get_text(strip=True) if qty_elem else "1 unit"
            
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
                url=f"{self.BASE_URL}/pd/{product_id}",
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
            url = f"{self.BASE_URL}/pd/{product_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Extract JSON-LD
                    script = soup.find('script', {'type': 'application/ld+json'})
                    if script:
                        data = json.loads(script.string)
                        if isinstance(data, list):
                            data = data[0]
                        
                        return self._parse_jsonld(data, product_id)
                        
        except Exception as e:
            self._log("get_product_error", {"error": str(e)}, level="ERROR")
        
        return None
    
    def _parse_jsonld(self, data: Dict, product_id: str) -> Optional[Product]:
        """Parse from JSON-LD schema."""
        try:
            name = data.get("name", "")
            offers = data.get("offers", {})
            price = float(offers.get("price", 0))
            
            return Product(
                id=self._generate_product_id(product_id),
                name=name,
                brand=data.get("brand", {}).get("name"),
                category=self._categorize_product(name),
                quantity="",
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/pd/{product_id}",
                current_price=price,
                mrp=price,
                discount_percent=0,
                is_available=True,
                stock_status="in_stock",
                image_url=data.get("image"),
                scraped_at=datetime.now(),
                location_pincode=self.pincode
            )
        except:
            return None
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        """Get products from category."""
        return await self.search(category, limit=limit)

