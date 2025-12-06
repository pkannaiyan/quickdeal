"""
Platform data models.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class PlatformStatus(BaseModel):
    """
    Status of a platform scraper.
    """
    platform_id: str
    name: str
    logo: str
    
    # Status
    is_active: bool = True
    is_healthy: bool = True
    last_scrape: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Statistics
    total_products: int = 0
    products_scraped_today: int = 0
    avg_scrape_time_seconds: float = 0
    success_rate: float = 100.0
    
    # Rate limiting
    requests_today: int = 0
    rate_limit_remaining: int = 100
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "blinkit",
                "name": "Blinkit",
                "logo": "🟢",
                "is_active": True,
                "is_healthy": True,
                "total_products": 15000,
                "success_rate": 98.5
            }
        }


class Platform(BaseModel):
    """
    Platform configuration and metadata.
    """
    id: str = Field(..., description="Platform identifier")
    name: str = Field(..., description="Display name")
    
    # Branding
    logo: str = Field("🛒", description="Emoji or icon")
    color: str = Field("#000000", description="Brand color")
    
    # URLs
    base_url: str
    search_url_template: Optional[str] = None
    product_url_template: Optional[str] = None
    
    # Service info
    delivery_time: str = Field("Same day")
    min_order: float = Field(0, description="Minimum order value")
    delivery_fee: float = Field(0)
    free_delivery_above: Optional[float] = None
    
    # Coverage
    cities: List[str] = Field(default_factory=list)
    pincodes: List[str] = Field(default_factory=list)
    
    # Scraping config
    scraper_enabled: bool = True
    scrape_interval_minutes: int = 30
    rate_limit_rpm: int = 30
    requires_auth: bool = False
    
    # Status
    status: Optional[PlatformStatus] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "blinkit",
                "name": "Blinkit",
                "logo": "🟢",
                "color": "#0A7C42",
                "base_url": "https://blinkit.com",
                "delivery_time": "10-20 min",
                "min_order": 99,
                "delivery_fee": 25,
                "free_delivery_above": 199,
                "cities": ["Mumbai", "Delhi", "Bangalore"],
                "scraper_enabled": True
            }
        }


class PlatformComparison(BaseModel):
    """
    Comparison of platforms for a search/product.
    """
    search_query: Optional[str] = None
    product_id: Optional[str] = None
    
    platforms: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Summary
    cheapest_platform: Optional[str] = None
    fastest_delivery_platform: Optional[str] = None
    most_products_platform: Optional[str] = None
    
    compared_at: datetime = Field(default_factory=datetime.now)

