"""
Price-related data models.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PriceEntry(BaseModel):
    """
    A single price entry for a product on a platform.
    """
    id: str = Field(default_factory=lambda: f"price-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    
    # Identifiers
    product_id: str
    platform: str
    platform_product_id: str
    
    # Product info (denormalized for quick access)
    product_name: str
    brand: Optional[str] = None
    quantity: str
    image_url: Optional[str] = None
    
    # Pricing
    price: float = Field(..., ge=0)
    mrp: Optional[float] = Field(None, ge=0)
    discount_percent: float = Field(0)
    price_per_unit: Optional[float] = None
    
    # Availability
    is_available: bool = True
    stock_status: str = "in_stock"
    delivery_time: Optional[str] = None
    
    # Platform info
    platform_name: str
    platform_logo: str = "🛒"
    product_url: Optional[str] = None
    
    # Metadata
    scraped_at: datetime = Field(default_factory=datetime.now)
    pincode: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "milk-amul-1l",
                "platform": "blinkit",
                "platform_product_id": "123456",
                "product_name": "Amul Taaza Toned Milk",
                "brand": "Amul",
                "quantity": "1 L",
                "price": 66.0,
                "mrp": 68.0,
                "discount_percent": 2.94,
                "is_available": True,
                "platform_name": "Blinkit",
                "platform_logo": "🟢",
                "delivery_time": "10-20 min"
            }
        }


class PriceComparison(BaseModel):
    """
    Price comparison result for a product across platforms.
    """
    product_id: str
    product_name: str
    brand: Optional[str] = None
    category: str
    quantity: str
    image_url: Optional[str] = None
    
    # Price entries from different platforms
    prices: List[PriceEntry] = Field(default_factory=list)
    
    # Summary statistics
    lowest_price: float = 0
    highest_price: float = 0
    average_price: float = 0
    savings_potential: float = Field(0, description="Amount saved by choosing cheapest")
    savings_percent: float = Field(0, description="% saved vs average")
    
    # Best option
    best_platform: Optional[str] = None
    best_platform_name: Optional[str] = None
    best_platform_logo: Optional[str] = None
    best_price: float = 0
    best_delivery_time: Optional[str] = None
    
    # Availability summary
    available_on: int = Field(0, description="Number of platforms where available")
    total_platforms: int = Field(0, description="Total platforms checked")
    
    # Metadata
    compared_at: datetime = Field(default_factory=datetime.now)
    pincode: Optional[str] = None
    
    def calculate_stats(self) -> None:
        """Calculate comparison statistics."""
        available_prices = [p for p in self.prices if p.is_available]
        
        self.total_platforms = len(self.prices)
        self.available_on = len(available_prices)
        
        if not available_prices:
            return
        
        price_values = [p.price for p in available_prices]
        self.lowest_price = min(price_values)
        self.highest_price = max(price_values)
        self.average_price = sum(price_values) / len(price_values)
        
        self.savings_potential = self.highest_price - self.lowest_price
        if self.average_price > 0:
            self.savings_percent = ((self.average_price - self.lowest_price) / self.average_price) * 100
        
        # Find best option
        best = min(available_prices, key=lambda p: p.price)
        self.best_platform = best.platform
        self.best_platform_name = best.platform_name
        self.best_platform_logo = best.platform_logo
        self.best_price = best.price
        self.best_delivery_time = best.delivery_time
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "milk-amul-1l",
                "product_name": "Amul Taaza Toned Fresh Milk",
                "brand": "Amul",
                "category": "dairy_bread",
                "quantity": "1 L",
                "lowest_price": 64.0,
                "highest_price": 72.0,
                "average_price": 67.5,
                "savings_potential": 8.0,
                "savings_percent": 5.2,
                "best_platform": "dmart",
                "best_platform_name": "DMart Ready",
                "best_price": 64.0,
                "available_on": 6,
                "total_platforms": 8
            }
        }


class PriceHistory(BaseModel):
    """
    Price history for a product on a platform.
    """
    product_id: str
    platform: str
    product_name: str
    
    # History entries
    history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Summary
    current_price: float = 0
    lowest_ever: float = 0
    highest_ever: float = 0
    average_price: float = 0
    
    # Trend
    price_trend: str = Field("stable", description="up, down, stable")
    trend_percent: float = Field(0, description="% change in trend period")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "milk-amul-1l",
                "platform": "blinkit",
                "product_name": "Amul Taaza Milk 1L",
                "current_price": 66.0,
                "lowest_ever": 62.0,
                "highest_ever": 72.0,
                "average_price": 66.5,
                "price_trend": "stable",
                "trend_percent": 0.0
            }
        }


class PriceAlert(BaseModel):
    """
    Price alert configuration.
    """
    id: str = Field(default_factory=lambda: f"alert-{datetime.now().strftime('%Y%m%d%H%M%S%f')}")
    
    # Alert target
    product_id: str
    product_name: str
    platforms: List[str] = Field(default_factory=list, description="Empty = all platforms")
    
    # Alert conditions
    target_price: float = Field(..., ge=0, description="Alert when price drops to/below this")
    current_lowest: float = Field(0)
    
    # User info
    email: Optional[str] = None
    
    # Status
    is_active: bool = True
    triggered: bool = False
    triggered_at: Optional[datetime] = None
    triggered_platform: Optional[str] = None
    triggered_price: Optional[float] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "milk-amul-1l",
                "product_name": "Amul Taaza Milk 1L",
                "platforms": ["blinkit", "zepto"],
                "target_price": 60.0,
                "current_lowest": 66.0,
                "is_active": True
            }
        }

