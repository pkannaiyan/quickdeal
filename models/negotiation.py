"""
Negotiation Models for Price Negotiation Marketplace.

Supports buyer offers, seller responses, and deal tracking.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    """User roles in the marketplace."""
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"


class OfferStatus(str, Enum):
    """Status of a negotiation offer."""
    PENDING = "pending"           # Waiting for seller response
    ACCEPTED = "accepted"         # Seller accepted the offer
    REJECTED = "rejected"         # Seller rejected the offer
    COUNTERED = "countered"       # Seller made a counter offer
    EXPIRED = "expired"           # Offer expired (no response)
    CANCELLED = "cancelled"       # Buyer cancelled
    COMPLETED = "completed"       # Deal completed (paid)


class DealStatus(str, Enum):
    """Status of a completed deal."""
    PENDING_PAYMENT = "pending_payment"
    ORDERED = "ordered"  # Order placed at deal price
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class NegotiationOffer(BaseModel):
    """A negotiation offer from buyer to seller."""
    offer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Product info
    product_id: str
    product_name: str
    product_brand: Optional[str] = None
    product_quantity: str  # e.g., "1 kg", "500ml"
    product_image: Optional[str] = None
    
    # Platform/Seller info
    platform: str  # blinkit, zepto, jiomart, etc.
    platform_name: str
    seller_id: Optional[str] = None
    seller_name: Optional[str] = None
    
    # Pricing
    original_price: float  # Listed price
    offered_price: float   # Buyer's offer
    discount_percent: float  # Calculated discount %
    
    # Quantity
    quantity: int = 1
    total_original: float = 0  # original_price * quantity
    total_offered: float = 0   # offered_price * quantity
    
    # Buyer info
    buyer_id: str
    buyer_name: str
    buyer_phone: Optional[str] = None
    
    # Negotiation state
    status: OfferStatus = OfferStatus.PENDING
    message: Optional[str] = None  # Buyer's message
    
    # Counter offer (if seller counters)
    counter_price: Optional[float] = None
    counter_message: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None  # Offer expiry (24 hours)
    manual_review_deadline: Optional[datetime] = None  # Deadline for manual review before auto-process
    responded_at: Optional[datetime] = None
    auto_processed: bool = False  # True if processed by auto-accept/reject
    
    # Location
    pincode: Optional[str] = None
    city: Optional[str] = None
    
    def calculate_totals(self):
        """Calculate total amounts."""
        self.total_original = self.original_price * self.quantity
        self.total_offered = self.offered_price * self.quantity
        self.discount_percent = round(
            ((self.original_price - self.offered_price) / self.original_price) * 100, 2
        )


class CounterOffer(BaseModel):
    """A counter offer from seller."""
    counter_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    offer_id: str  # Original offer ID
    
    counter_price: float
    message: Optional[str] = None
    valid_until: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.now)


class Deal(BaseModel):
    """A completed deal after negotiation."""
    deal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    offer_id: str  # Original offer ID
    
    # Product
    product_id: str
    product_name: str
    platform: str
    platform_name: str = ""  # e.g., "Blinkit", "Zepto"
    
    # Parties
    buyer_id: str
    buyer_name: str
    seller_id: Optional[str] = None
    seller_name: Optional[str] = None
    
    # Pricing
    original_price: float
    final_price: float  # Agreed price
    quantity: int
    total_amount: float
    savings: float  # original - final
    savings_percent: float
    
    # Status
    status: DealStatus = DealStatus.PENDING_PAYMENT
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    
    # Delivery
    delivery_address: Optional[str] = None
    delivery_pincode: Optional[str] = None
    estimated_delivery: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    ordered_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class SellerProfile(BaseModel):
    """Seller profile for the marketplace."""
    seller_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Link to user account
    
    # Business info
    business_name: str
    platform: str  # Which platform they represent
    platform_name: str
    
    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Settings
    manual_review_only: bool = False  # If True, NEVER auto-accept (manual only forever)
    manual_review_timeout_mins: int = 5  # Minutes to wait for manual review before auto-processing
    auto_accept_discount: float = 10  # Auto-accept offers with <= this % discount
    auto_reject_discount: float = 30  # Auto-reject offers with > this % discount
    max_discount: float = 30  # Maximum discount they'll consider
    min_order_value: float = 0  # Minimum order value
    
    # Stats
    total_offers_received: int = 0
    offers_accepted: int = 0
    offers_rejected: int = 0
    offers_countered: int = 0
    total_deals: int = 0
    total_revenue: float = 0
    avg_discount_given: float = 0
    
    # Rating
    rating: float = 5.0
    review_count: int = 0
    
    # Status
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Service areas
    pincodes: List[str] = []
    cities: List[str] = []


class BuyerStats(BaseModel):
    """Buyer statistics for dashboard."""
    buyer_id: str
    
    # Offer stats
    total_offers_made: int = 0
    offers_accepted: int = 0
    offers_rejected: int = 0
    offers_pending: int = 0
    offers_countered: int = 0
    
    # Deal stats
    total_deals: int = 0
    total_spent: float = 0
    total_savings: float = 0
    avg_discount: float = 0
    
    # Success rate
    success_rate: float = 0  # accepted / total
    
    # Recent activity
    last_offer_at: Optional[datetime] = None
    last_deal_at: Optional[datetime] = None


class SellerStats(BaseModel):
    """Seller statistics for dashboard."""
    seller_id: str
    platform: str
    
    # Offer stats
    total_offers_received: int = 0
    offers_accepted: int = 0
    offers_rejected: int = 0
    offers_pending: int = 0
    offers_countered: int = 0
    
    # Deal stats
    total_deals: int = 0
    total_revenue: float = 0
    avg_deal_value: float = 0
    avg_discount_given: float = 0
    
    # Performance
    response_rate: float = 0  # responded / total
    acceptance_rate: float = 0  # accepted / total
    avg_response_time_mins: float = 0
    
    # Top products
    top_products: List[dict] = []
    
    # Recent activity
    last_offer_at: Optional[datetime] = None
    last_deal_at: Optional[datetime] = None


# Request/Response Models for API

class CreateOfferRequest(BaseModel):
    """Request to create a new offer."""
    product_id: str
    product_name: str
    product_brand: Optional[str] = None
    product_quantity: str
    platform: str
    platform_name: str
    original_price: float
    offered_price: float
    quantity: int = 1
    message: Optional[str] = None
    pincode: Optional[str] = None
    city: Optional[str] = None


class RespondOfferRequest(BaseModel):
    """Seller response to an offer."""
    action: Literal["accept", "reject", "counter"]
    counter_price: Optional[float] = None
    message: Optional[str] = None


class CompleteDealRequest(BaseModel):
    """Request to complete a deal after acceptance."""
    offer_id: str
    payment_method: str
    delivery_address: str
    delivery_pincode: str

