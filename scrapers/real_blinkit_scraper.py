"""
Real Blinkit Scraper.

Scrapes actual product data from Blinkit using their internal API.
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


class RealBlinkitScraper(BaseScraper):
    """
    Real scraper for Blinkit using their GraphQL API.
    """
    
    PLATFORM_ID = "blinkit"
    PLATFORM_NAME = "Blinkit"
    BASE_URL = "https://blinkit.com"
    LOGO = "🟢"
    DELIVERY_TIME = "10-20 min"
    
    # Blinkit uses GraphQL API
    GRAPHQL_ENDPOINT = "https://blinkit.com/v2/graphql"
    SEARCH_API = "https://blinkit.com/v6/search/products"
    
    def __init__(self, pincode: str = "400001", lat: float = 19.0760, lng: float = 72.8777):
        super().__init__(pincode=pincode)
        self.lat = lat
        self.lng = lng
        self._session_token = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get Blinkit-specific headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://blinkit.com",
            "Referer": "https://blinkit.com/",
            "lat": str(self.lat),
            "lon": str(self.lng),
            "app_client": "consumer_web",
            "app_version": "41011000",
            "web_app_version": "1.0.0",
            "device_id": "web_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "session_uuid": "web_session_" + datetime.now().strftime("%Y%m%d%H%M%S"),
        }
    
    async def _initialize_session(self) -> None:
        """Initialize session and get necessary tokens."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # Get main page to establish session
                response = await client.get(
                    self.BASE_URL,
                    headers=self._get_headers(),
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    # Extract any tokens from cookies
                    self._session_token = response.cookies.get("session_id")
                    self._log("session_initialized", {"status": "success"})
                    
        except Exception as e:
            self._log("session_init_error", {"error": str(e)}, level="ERROR")
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """
        Search for products on Blinkit.
        """
        self._log("search_start", {"query": query, "limit": limit})
        
        await self._rate_limit()
        
        products = []
        
        try:
            params = {
                "q": query,
                "page": 0,
                "size": min(limit, 50),
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.SEARCH_API,
                    params=params,
                    headers=self._get_headers(),
                    follow_redirects=True
                )
                
                self._stats["requests_made"] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse response based on Blinkit's API structure
                    product_list = data.get("products", [])
                    if not product_list:
                        product_list = data.get("data", {}).get("products", [])
                    
                    for item in product_list[:limit]:
                        product = self._parse_product(item)
                        if product:
                            products.append(product)
                else:
                    self._log("search_error", {
                        "status": response.status_code,
                        "query": query
                    }, level="WARNING")
                    
                    # Fallback to web scraping
                    products = await self._scrape_web_search(query, limit)
                    
        except Exception as e:
            self._log("search_exception", {"error": str(e), "query": query}, level="ERROR")
            # Fallback to web scraping
            products = await self._scrape_web_search(query, limit)
        
        self._stats["products_scraped"] += len(products)
        self._log("search_complete", {"query": query, "results": len(products)})
        
        return products
    
    async def _scrape_web_search(self, query: str, limit: int) -> List[Product]:
        """Fallback: Scrape search results from web page."""
        products = []
        
        try:
            url = f"{self.BASE_URL}/s/?q={quote(query)}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Find product cards (structure may vary)
                    product_cards = soup.find_all('div', {'class': re.compile(r'Product__UpdatedPlpProductContainer')})
                    
                    if not product_cards:
                        # Alternative selectors
                        product_cards = soup.find_all('a', {'class': re.compile(r'plp-product')})
                    
                    for card in product_cards[:limit]:
                        product = self._parse_html_product(card)
                        if product:
                            products.append(product)
                            
        except Exception as e:
            self._log("web_scrape_error", {"error": str(e)}, level="ERROR")
        
        return products
    
    def _parse_product(self, item: Dict) -> Optional[Product]:
        """Parse product from API response."""
        try:
            product_id = str(item.get("product_id", item.get("id", "")))
            name = item.get("name", item.get("product_name", ""))
            
            if not product_id or not name:
                return None
            
            # Extract pricing
            price = float(item.get("price", item.get("offer_price", 0)))
            mrp = float(item.get("mrp", item.get("marked_price", price)))
            
            # Extract brand
            brand = item.get("brand", item.get("brand_name"))
            
            # Extract quantity
            quantity = item.get("unit", item.get("quantity", "1 unit"))
            
            # Extract image
            image_url = item.get("image_url", item.get("product_image"))
            if image_url and not image_url.startswith("http"):
                image_url = f"https://cdn.grofers.com/cdn-cgi/image/{image_url}"
            
            # Determine availability
            is_available = item.get("in_stock", True)
            inventory = item.get("inventory", 0)
            if inventory == 0:
                is_available = False
            
            # Calculate discount
            discount = 0
            if mrp > price:
                discount = ((mrp - price) / mrp) * 100
            
            # Parse quantity
            quantity_text, unit, unit_value = self._parse_quantity(quantity)
            
            # Categorize
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
                url=f"{self.BASE_URL}/prn/{product_id}",
                current_price=price,
                mrp=mrp,
                discount_percent=round(discount, 2),
                is_available=is_available,
                stock_status="in_stock" if is_available else "out_of_stock",
                image_url=image_url,
                thumbnail_url=image_url,
                scraped_at=datetime.now(),
                location_pincode=self.pincode
            )
            
        except Exception as e:
            self._log("parse_error", {"error": str(e), "item": str(item)[:200]}, level="WARNING")
            return None
    
    def _parse_html_product(self, card) -> Optional[Product]:
        """Parse product from HTML element."""
        try:
            # Extract product details from HTML
            name_elem = card.find('div', {'class': re.compile(r'Product__UpdatedTitle')})
            if not name_elem:
                name_elem = card.find('h3') or card.find('div', {'class': re.compile(r'title')})
            
            name = name_elem.get_text(strip=True) if name_elem else None
            if not name:
                return None
            
            # Extract price
            price_elem = card.find('div', {'class': re.compile(r'Product__UpdatedPriceAndAtc498')})
            if not price_elem:
                price_elem = card.find('span', {'class': re.compile(r'price|amount')})
            
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price = float(re.sub(r'[^\d.]', '', price_text) or 0)
            
            # Extract MRP
            mrp_elem = card.find('div', {'class': re.compile(r'mrp|original')})
            mrp_text = mrp_elem.get_text(strip=True) if mrp_elem else str(price)
            mrp = float(re.sub(r'[^\d.]', '', mrp_text) or price)
            
            # Extract quantity
            qty_elem = card.find('span', {'class': re.compile(r'variant|quantity|unit')})
            quantity = qty_elem.get_text(strip=True) if qty_elem else "1 unit"
            
            # Extract product ID from URL
            link = card.get('href', '') if card.name == 'a' else card.find('a', href=True)
            product_id = ""
            if link:
                href = link if isinstance(link, str) else link.get('href', '')
                match = re.search(r'/prn/([^/]+)', href)
                if match:
                    product_id = match.group(1)
            
            if not product_id:
                product_id = f"html_{hash(name)}"
            
            # Extract image
            img_elem = card.find('img')
            image_url = None
            if img_elem:
                image_url = img_elem.get('src') or img_elem.get('data-src')
            
            # Calculate discount
            discount = ((mrp - price) / mrp * 100) if mrp > price else 0
            
            quantity_text, unit, unit_value = self._parse_quantity(quantity)
            category = self._categorize_product(name)
            
            return Product(
                id=self._generate_product_id(product_id),
                name=name,
                brand=None,  # Extract if available
                category=category,
                quantity=quantity_text or quantity,
                unit=unit,
                unit_value=unit_value,
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/prn/{product_id}",
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
        """Get a specific product by ID."""
        await self._rate_limit()
        
        try:
            url = f"{self.BASE_URL}/prn/{product_id}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    # Parse product page
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Extract product data from page
                    # Look for JSON-LD data
                    script = soup.find('script', {'type': 'application/ld+json'})
                    if script:
                        try:
                            data = json.loads(script.string)
                            return self._parse_jsonld_product(data, product_id)
                        except json.JSONDecodeError:
                            pass
                    
        except Exception as e:
            self._log("get_product_error", {"error": str(e), "product_id": product_id}, level="ERROR")
        
        return None
    
    def _parse_jsonld_product(self, data: Dict, product_id: str) -> Optional[Product]:
        """Parse product from JSON-LD schema."""
        try:
            name = data.get("name", "")
            
            offers = data.get("offers", {})
            price = float(offers.get("price", 0))
            
            image = data.get("image", "")
            if isinstance(image, list):
                image = image[0] if image else ""
            
            return Product(
                id=self._generate_product_id(product_id),
                name=name,
                brand=data.get("brand", {}).get("name"),
                category=self._categorize_product(name),
                quantity="",
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/prn/{product_id}",
                current_price=price,
                mrp=price,
                discount_percent=0,
                is_available=offers.get("availability", "").endswith("InStock"),
                stock_status="in_stock",
                image_url=image,
                scraped_at=datetime.now(),
                location_pincode=self.pincode
            )
        except Exception:
            return None
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        """Get products from a category."""
        # Map category to Blinkit's category URL
        category_urls = {
            "dairy_bread": "/cn/dairy-and-bread",
            "fruits_vegetables": "/cn/fruits-and-vegetables",
            "snacks_beverages": "/cn/munchies",
            "staples": "/cn/atta-rice-oil-and-dals",
            "household": "/cn/cleaning-essentials",
            "personal_care": "/cn/pharma-and-wellness",
        }
        
        url_path = category_urls.get(category, f"/cn/{category}")
        return await self._scrape_category_page(url_path, limit)
    
    async def _scrape_category_page(self, path: str, limit: int) -> List[Product]:
        """Scrape products from a category page."""
        products = []
        
        try:
            url = f"{self.BASE_URL}{path}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self._get_headers())
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    product_cards = soup.find_all('div', {'class': re.compile(r'Product')})
                    
                    for card in product_cards[:limit]:
                        product = self._parse_html_product(card)
                        if product:
                            products.append(product)
                            
        except Exception as e:
            self._log("category_scrape_error", {"error": str(e), "path": path}, level="ERROR")
        
        return products

