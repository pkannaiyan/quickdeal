"""
Real JioMart Scraper.

Scrapes actual product data from JioMart.
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


class RealJioMartScraper(BaseScraper):
    """
    Real scraper for JioMart.
    """
    
    PLATFORM_ID = "jiomart"
    PLATFORM_NAME = "JioMart"
    BASE_URL = "https://www.jiomart.com"
    LOGO = "🔵"
    DELIVERY_TIME = "Same day"
    
    # JioMart API endpoints
    SEARCH_API = "https://www.jiomart.com/search"
    
    def __init__(self, pincode: str = "400001", lat: float = 19.0760, lng: float = 72.8777):
        super().__init__(pincode=pincode)
        self.lat = lat
        self.lng = lng
    
    def _get_headers(self) -> Dict[str, str]:
        """Get JioMart-specific headers."""
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
    
    async def search(self, query: str, limit: int = 20) -> List[Product]:
        """Search for products on JioMart."""
        self._log("search_start", {"query": query, "limit": limit})
        
        await self._rate_limit()
        
        products = []
        
        try:
            url = f"{self.BASE_URL}/search?q={quote(query)}"
            
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url, headers=self._get_headers())
                
                self._stats["requests_made"] += 1
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Try to find JSON data embedded in the page
                    script_tags = soup.find_all('script', {'type': 'application/json'})
                    for script in script_tags:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, dict):
                                # Look for product data
                                items = self._extract_products_from_json(data)
                                for item in items[:limit]:
                                    product = self._parse_product(item)
                                    if product:
                                        products.append(product)
                        except (json.JSONDecodeError, TypeError):
                            continue
                    
                    # If no JSON products found, try HTML parsing
                    if not products:
                        products = self._parse_html_products(soup, limit)
                        
        except Exception as e:
            self._log("search_error", {"error": str(e)}, level="ERROR")
        
        self._stats["products_scraped"] += len(products)
        return products
    
    def _extract_products_from_json(self, data: Dict, products: List = None) -> List[Dict]:
        """Recursively extract product data from JSON."""
        if products is None:
            products = []
        
        if isinstance(data, dict):
            # Check if this looks like a product
            if "name" in data and ("price" in data or "sellingPrice" in data):
                products.append(data)
            
            # Check common product array keys
            for key in ["products", "items", "results", "productList", "data"]:
                if key in data:
                    value = data[key]
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict) and "name" in item:
                                products.append(item)
                    elif isinstance(value, dict):
                        self._extract_products_from_json(value, products)
            
            # Recurse into nested objects
            for value in data.values():
                if isinstance(value, (dict, list)):
                    self._extract_products_from_json(value, products)
                    
        elif isinstance(data, list):
            for item in data:
                self._extract_products_from_json(item, products)
        
        return products
    
    def _parse_html_products(self, soup, limit: int) -> List[Product]:
        """Parse products from HTML."""
        products = []
        
        # Try various selectors for product cards
        selectors = [
            'div[data-testid="plp-product-card"]',
            '.product-card',
            '.product-item',
            'div[class*="ProductCard"]',
            'article[class*="product"]',
            '.plp-card',
        ]
        
        cards = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                break
        
        # Fallback to finding product-like elements
        if not cards:
            cards = soup.find_all('div', {'class': re.compile(r'product|card|item', re.I)})
        
        for card in cards[:limit]:
            try:
                # Find name
                name_elem = (
                    card.find('h3') or 
                    card.find('h4') or 
                    card.find('a', {'class': re.compile(r'title|name')}) or
                    card.find('div', {'class': re.compile(r'title|name')}) or
                    card.find('span', {'class': re.compile(r'title|name')})
                )
                if not name_elem:
                    continue
                    
                name = name_elem.get_text(strip=True)
                if not name or len(name) < 3:
                    continue
                
                # Find price
                price_elem = card.find(['span', 'div'], {'class': re.compile(r'price|amount|rupee', re.I)})
                if not price_elem:
                    continue
                    
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                if not price_match:
                    continue
                price = float(price_match.group())
                
                # Find MRP
                mrp_elem = card.find(['span', 'div'], {'class': re.compile(r'mrp|strike|original', re.I)})
                mrp = price
                if mrp_elem:
                    mrp_text = mrp_elem.get_text(strip=True)
                    mrp_match = re.search(r'[\d,]+\.?\d*', mrp_text.replace(',', ''))
                    if mrp_match:
                        mrp = float(mrp_match.group())
                
                # Find product ID from link
                link = card.find('a', href=True)
                product_id = f"jio_{hash(name) % 100000}"
                product_url = f"{self.BASE_URL}/search?q={quote(name)}"
                
                if link:
                    href = link.get('href', '')
                    if href.startswith('/'):
                        product_url = f"{self.BASE_URL}{href}"
                    elif href.startswith('http'):
                        product_url = href
                    
                    # Try to extract ID from URL
                    id_match = re.search(r'/(\d{6,})', href)
                    if id_match:
                        product_id = id_match.group(1)
                
                # Find image
                img = card.find('img')
                image_url = None
                if img:
                    image_url = img.get('src') or img.get('data-src') or img.get('data-lazy')
                
                # Find quantity
                qty_elem = card.find(['span', 'div'], {'class': re.compile(r'qty|quantity|weight|size|pack', re.I)})
                quantity = qty_elem.get_text(strip=True) if qty_elem else "1 unit"
                
                discount = ((mrp - price) / mrp * 100) if mrp > price else 0
                quantity_text, unit, unit_value = self._parse_quantity(quantity)
                
                product = Product(
                    id=self._generate_product_id(product_id),
                    name=name,
                    brand=None,
                    category=self._categorize_product(name),
                    quantity=quantity_text or quantity,
                    unit=unit,
                    unit_value=unit_value,
                    platform=self.PLATFORM_ID,
                    platform_product_id=product_id,
                    url=product_url,
                    current_price=price,
                    mrp=mrp,
                    discount_percent=round(discount, 2),
                    is_available=True,
                    stock_status="in_stock",
                    image_url=image_url,
                    scraped_at=datetime.now(),
                    location_pincode=self.pincode
                )
                products.append(product)
                
            except Exception as e:
                self._log("html_parse_error", {"error": str(e)}, level="WARNING")
                continue
        
        return products
    
    def _parse_product(self, item: Dict) -> Optional[Product]:
        """Parse product from JSON data."""
        try:
            product_id = str(item.get("id", item.get("productId", item.get("sku", ""))))
            name = item.get("name", item.get("productName", item.get("title", "")))
            
            if not name:
                return None
            
            # Pricing
            price = float(item.get("sellingPrice", item.get("price", item.get("salePrice", 0))))
            mrp = float(item.get("mrp", item.get("maxPrice", item.get("regularPrice", price))))
            
            # Brand
            brand = item.get("brand", item.get("brandName"))
            
            # Quantity
            quantity = item.get("packSize", item.get("quantity", item.get("weight", "1 unit")))
            
            # Image
            image_url = item.get("image", item.get("imageUrl", item.get("thumbnail")))
            images = item.get("images", [])
            if not image_url and images:
                image_url = images[0] if isinstance(images[0], str) else images[0].get("url")
            
            # Availability
            is_available = item.get("inStock", item.get("available", True))
            
            discount = ((mrp - price) / mrp * 100) if mrp > price else 0
            
            quantity_text, unit, unit_value = self._parse_quantity(str(quantity))
            category = self._categorize_product(name, item.get("category", ""))
            
            return Product(
                id=self._generate_product_id(product_id or f"jio_{hash(name)}"),
                name=name,
                brand=brand,
                category=category,
                quantity=quantity_text or str(quantity),
                unit=unit,
                unit_value=unit_value,
                platform=self.PLATFORM_ID,
                platform_product_id=product_id,
                url=f"{self.BASE_URL}/search?q={quote(name)}",
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
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Get specific product."""
        return None  # Would need product page scraping
    
    async def get_category_products(self, category: str, limit: int = 50) -> List[Product]:
        """Get products from category."""
        return await self.search(category, limit=limit)

