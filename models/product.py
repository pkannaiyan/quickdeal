"""
Product data models.
"""
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ProductCategory(str, Enum):
    """Product categories."""
    FRUITS_VEGETABLES = "fruits_vegetables"
    DAIRY_BREAD = "dairy_bread"
    SNACKS_BEVERAGES = "snacks_beverages"
    STAPLES = "staples"
    PERSONAL_CARE = "personal_care"
    HOUSEHOLD = "household"
    BABY_CARE = "baby_care"
    PET_CARE = "pet_care"
    MEAT_SEAFOOD = "meat_seafood"
    FROZEN = "frozen"
    OTHER = "other"


class Product(BaseModel):
    """
    Product model representing a scraped item.
    """
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    brand: Optional[str] = Field(None, description="Brand name")
    
    # Product details
    category: ProductCategory = Field(ProductCategory.OTHER)
    subcategory: Optional[str] = None
    description: Optional[str] = None
    
    # Quantity/Size
    quantity: str = Field(..., description="e.g., '1 kg', '500 ml', '6 pack'")
    unit: Optional[str] = Field(None, description="kg, g, ml, L, pack, piece")
    unit_value: Optional[float] = Field(None, description="Numeric value of quantity")
    
    # Platform info
    platform: str = Field(..., description="Source platform")
    platform_product_id: str = Field(..., description="ID on the platform")
    url: Optional[str] = Field(None, description="Product URL")
    
    # Pricing
    current_price: float = Field(..., ge=0)
    mrp: Optional[float] = Field(None, ge=0, description="Maximum Retail Price")
    discount_percent: float = Field(0, ge=0, le=100)
    
    # Availability
    is_available: bool = Field(True)
    stock_status: str = Field("in_stock", description="in_stock, low_stock, out_of_stock")
    
    # Images
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now)
    location_pincode: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "prod-blinkit-123",
                "name": "Amul Taaza Toned Fresh Milk",
                "brand": "Amul",
                "category": "dairy_bread",
                "quantity": "1 L",
                "unit": "L",
                "unit_value": 1.0,
                "platform": "blinkit",
                "platform_product_id": "123456",
                "current_price": 66.0,
                "mrp": 68.0,
                "discount_percent": 2.94,
                "is_available": True,
                "stock_status": "in_stock"
            }
        }
    
    @property
    def price_per_unit(self) -> Optional[float]:
        """Calculate price per unit."""
        if self.unit_value and self.unit_value > 0:
            return self.current_price / self.unit_value
        return None


class ProductMatch(BaseModel):
    """
    Represents matched products across platforms.
    
    Groups similar products from different platforms for comparison.
    """
    id: str = Field(..., description="Unique match group ID")
    canonical_name: str = Field(..., description="Normalized product name")
    brand: Optional[str] = None
    category: ProductCategory = Field(ProductCategory.OTHER)
    
    # Matched products
    products: List[Product] = Field(default_factory=list)
    
    # Match quality
    match_confidence: float = Field(1.0, ge=0, le=1, description="How confident we are in the match")
    match_method: str = Field("exact", description="exact, fuzzy, ai")
    
    # Aggregated info
    lowest_price: float = Field(0)
    highest_price: float = Field(0)
    price_range_percent: float = Field(0, description="% difference between highest and lowest")
    best_platform: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "match-milk-amul-1l",
                "canonical_name": "Amul Taaza Toned Milk 1L",
                "brand": "Amul",
                "category": "dairy_bread",
                "products": [],
                "match_confidence": 0.95,
                "lowest_price": 64.0,
                "highest_price": 72.0,
                "price_range_percent": 12.5,
                "best_platform": "dmart"
            }
        }
    
    def calculate_stats(self) -> None:
        """Calculate aggregated statistics."""
        if not self.products:
            return
        
        available_products = [p for p in self.products if p.is_available]
        if not available_products:
            return
        
        prices = [p.current_price for p in available_products]
        self.lowest_price = min(prices)
        self.highest_price = max(prices)
        
        if self.lowest_price > 0:
            self.price_range_percent = ((self.highest_price - self.lowest_price) / self.lowest_price) * 100
        
        # Find best platform (lowest price + available)
        best_product = min(available_products, key=lambda p: p.current_price)
        self.best_platform = best_product.platform
        
        self.updated_at = datetime.now()


class SearchQuery(BaseModel):
    """Search query model."""
    query: str = Field(..., min_length=2, max_length=200)
    category: Optional[ProductCategory] = None
    brand: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    platforms: List[str] = Field(default_factory=list, description="Filter by platforms")
    pincode: Optional[str] = None
    sort_by: str = Field("price_low", description="price_low, price_high, discount, relevance")
    limit: int = Field(50, ge=1, le=200)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "amul milk 1 litre",
                "category": "dairy_bread",
                "min_price": 50,
                "max_price": 100,
                "platforms": ["blinkit", "zepto", "instamart"],
                "sort_by": "price_low",
                "limit": 20
            }
        }

