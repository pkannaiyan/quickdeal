"""
Negotiation Service for Price Negotiation Marketplace.

Handles:
- Creating offers from buyers
- Processing seller responses (accept/reject/counter)
- Converting accepted offers to deals
- Tracking statistics for both parties
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import uuid

from models.negotiation import (
    NegotiationOffer, CounterOffer, Deal,
    OfferStatus, DealStatus,
    SellerProfile, BuyerStats, SellerStats,
    CreateOfferRequest, RespondOfferRequest
)


class NegotiationService:
    """
    Service for managing price negotiations between buyers and sellers.
    """
    
    def __init__(self, data_dir: str = "data/negotiations"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # File paths
        self.offers_file = self.data_dir / "offers.jsonl"
        self.deals_file = self.data_dir / "deals.jsonl"
        self.sellers_file = self.data_dir / "sellers.json"
        self.counters_file = self.data_dir / "counters.jsonl"
        
        # In-memory cache
        self._offers: Dict[str, NegotiationOffer] = {}
        self._deals: Dict[str, Deal] = {}
        self._sellers: Dict[str, SellerProfile] = {}
        
        # Load existing data
        self._load_data()
    
    def _load_data(self):
        """Load existing data from files."""
        # Load offers
        if self.offers_file.exists():
            with open(self.offers_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        offer = NegotiationOffer(**data)
                        self._offers[offer.offer_id] = offer
                    except:
                        pass
        
        # Load deals
        if self.deals_file.exists():
            with open(self.deals_file, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        deal = Deal(**data)
                        self._deals[deal.deal_id] = deal
                    except:
                        pass
        
        # Load sellers
        if self.sellers_file.exists():
            with open(self.sellers_file, 'r') as f:
                try:
                    sellers_data = json.load(f)
                    for seller_data in sellers_data:
                        seller = SellerProfile(**seller_data)
                        self._sellers[seller.seller_id] = seller
                except:
                    pass
        
        # Create demo sellers if none exist
        if not self._sellers:
            self._create_demo_sellers()
    
    def _create_demo_sellers(self):
        """Create demo seller profiles for each platform."""
        platforms = [
            ("blinkit", "Blinkit"),
            ("zepto", "Zepto"),
            ("instamart", "Swiggy Instamart"),
            ("bigbasket", "BigBasket"),
            ("jiomart", "JioMart"),
        ]
        
        for platform_id, platform_name in platforms:
            seller = SellerProfile(
                seller_id=f"seller_{platform_id}",
                user_id=f"user_{platform_id}",
                business_name=f"{platform_name} Official",
                platform=platform_id,
                platform_name=platform_name,
                manual_review_only=False,  # Allow auto-processing after timeout
                manual_review_timeout_mins=5,  # 5 minute window for manual review
                auto_accept_discount=10,  # Auto-accept up to 10% discount
                auto_reject_discount=30,  # Auto-reject above 30% discount
                max_discount=30,  # Max 30% discount
                is_active=True,
                cities=["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad"]
            )
            self._sellers[seller.seller_id] = seller
        
        self._save_sellers()
    
    def _save_offer(self, offer: NegotiationOffer):
        """Save offer to file and update in-memory cache."""
        # Update in-memory cache
        self._offers[offer.offer_id] = offer
        
        # Append to file
        with open(self.offers_file, 'a') as f:
            # Convert datetime fields to ISO format
            data = offer.model_dump()
            for key in ['created_at', 'updated_at', 'expires_at', 'responded_at', 'manual_review_deadline']:
                if data.get(key):
                    if isinstance(data[key], datetime):
                        data[key] = data[key].isoformat()
                    elif hasattr(data[key], 'isoformat'):
                        data[key] = data[key].isoformat()
            # Handle OfferStatus enum
            if 'status' in data and hasattr(data['status'], 'value'):
                data['status'] = data['status'].value
            f.write(json.dumps(data, default=str) + '\n')
    
    def _save_deal(self, deal: Deal):
        """Save deal to file."""
        with open(self.deals_file, 'a') as f:
            data = deal.model_dump()
            for key in ['created_at', 'paid_at', 'delivered_at']:
                if data.get(key):
                    if isinstance(data[key], datetime):
                        data[key] = data[key].isoformat()
                    elif hasattr(data[key], 'isoformat'):
                        data[key] = data[key].isoformat()
            # Handle DealStatus enum
            if 'status' in data and hasattr(data['status'], 'value'):
                data['status'] = data['status'].value
            f.write(json.dumps(data, default=str) + '\n')
    
    def _save_sellers(self):
        """Save all sellers to file."""
        with open(self.sellers_file, 'w') as f:
            sellers_data = []
            for seller in self._sellers.values():
                data = seller.model_dump()
                if data.get('created_at'):
                    if isinstance(data['created_at'], datetime):
                        data['created_at'] = data['created_at'].isoformat()
                    elif hasattr(data['created_at'], 'isoformat'):
                        data['created_at'] = data['created_at'].isoformat()
                sellers_data.append(data)
            json.dump(sellers_data, f, indent=2, default=str)
    
    # ==================== BUYER OPERATIONS ====================
    
    def create_offer(
        self,
        buyer_id: str,
        buyer_name: str,
        request: CreateOfferRequest
    ) -> NegotiationOffer:
        """
        Create a new negotiation offer from a buyer.
        
        Args:
            buyer_id: ID of the buyer
            buyer_name: Name of the buyer
            request: Offer details
            
        Returns:
            The created offer
        """
        # Calculate discount
        discount_percent = round(
            ((request.original_price - request.offered_price) / request.original_price) * 100, 2
        )
        
        # Find seller for this platform
        seller = self.get_seller_by_platform(request.platform)
        
        # Set manual review deadline
        manual_review_deadline = None
        if seller:
            timeout_mins = seller.manual_review_timeout_mins or 5
            manual_review_deadline = datetime.now() + timedelta(minutes=timeout_mins)
        
        offer = NegotiationOffer(
            product_id=request.product_id,
            product_name=request.product_name,
            product_brand=request.product_brand,
            product_quantity=request.product_quantity,
            platform=request.platform,
            platform_name=request.platform_name,
            seller_id=seller.seller_id if seller else None,
            seller_name=seller.business_name if seller else request.platform_name,
            original_price=request.original_price,
            offered_price=request.offered_price,
            discount_percent=discount_percent,
            quantity=request.quantity,
            total_original=request.original_price * request.quantity,
            total_offered=request.offered_price * request.quantity,
            buyer_id=buyer_id,
            buyer_name=buyer_name,
            message=request.message,
            pincode=request.pincode,
            city=request.city,
            expires_at=datetime.now() + timedelta(hours=24),  # 24 hour expiry
            manual_review_deadline=manual_review_deadline  # Deadline for manual review
        )
        
        # Note: We don't auto-accept immediately anymore
        # All offers start as PENDING for manual review window
        
        self._offers[offer.offer_id] = offer
        self._save_offer(offer)
        
        # Update seller stats
        if seller:
            seller.total_offers_received += 1
            self._save_sellers()
        
        return offer
    
    def get_buyer_offers(
        self,
        buyer_id: str,
        status: Optional[OfferStatus] = None
    ) -> List[NegotiationOffer]:
        """Get all offers made by a buyer."""
        offers = [o for o in self._offers.values() if o.buyer_id == buyer_id]
        
        if status:
            offers = [o for o in offers if o.status == status]
        
        # Sort by created_at descending
        offers.sort(key=lambda x: x.created_at, reverse=True)
        return offers
    
    def get_buyer_deals(self, buyer_id: str) -> List[Deal]:
        """Get all deals for a buyer."""
        deals = [d for d in self._deals.values() if d.buyer_id == buyer_id]
        deals.sort(key=lambda x: x.created_at, reverse=True)
        return deals
    
    def complete_deal_order(self, deal_id: str, buyer_id: str, order_price: float) -> Dict[str, Any]:
        """
        Complete a deal by placing an order at the negotiated price.
        
        Args:
            deal_id: The deal ID
            buyer_id: The buyer's user ID
            order_price: The final order price (should match negotiated price)
        
        Returns:
            Order confirmation details
        """
        # Find the deal
        deal = self._deals.get(deal_id)
        if not deal:
            raise ValueError(f"Deal {deal_id} not found")
        
        if deal.buyer_id != buyer_id:
            raise ValueError("Unauthorized: This deal belongs to another buyer")
        
        # Verify the order price matches the deal price
        if order_price != deal.final_price:
            raise ValueError(f"Order price ₹{order_price} doesn't match deal price ₹{deal.final_price}")
        
        # Update deal status to ordered
        deal.status = DealStatus.ORDERED
        deal.ordered_at = datetime.now()
        
        # Save the updated deal
        self._save_deal(deal)
        
        return {
            "deal_id": deal_id,
            "product_name": deal.product_name,
            "platform": deal.platform,
            "order_price": order_price,
            "original_price": deal.original_price,
            "quantity": deal.quantity,
            "total_amount": order_price * deal.quantity,
            "savings": deal.savings,
            "status": "ordered",
            "ordered_at": deal.ordered_at.isoformat() if deal.ordered_at else datetime.now().isoformat()
        }
    
    def get_buyer_stats(self, buyer_id: str) -> BuyerStats:
        """Get statistics for a buyer."""
        offers = self.get_buyer_offers(buyer_id)
        deals = self.get_buyer_deals(buyer_id)
        
        stats = BuyerStats(buyer_id=buyer_id)
        stats.total_offers_made = len(offers)
        stats.offers_accepted = len([o for o in offers if o.status == OfferStatus.ACCEPTED])
        stats.offers_rejected = len([o for o in offers if o.status == OfferStatus.REJECTED])
        stats.offers_pending = len([o for o in offers if o.status == OfferStatus.PENDING])
        stats.offers_countered = len([o for o in offers if o.status == OfferStatus.COUNTERED])
        
        stats.total_deals = len(deals)
        stats.total_spent = sum(d.total_amount for d in deals)
        stats.total_savings = sum(d.savings for d in deals)
        
        if stats.total_spent > 0:
            stats.avg_discount = (stats.total_savings / (stats.total_spent + stats.total_savings)) * 100
        
        if stats.total_offers_made > 0:
            stats.success_rate = (stats.offers_accepted / stats.total_offers_made) * 100
        
        if offers:
            stats.last_offer_at = max(o.created_at for o in offers)
        if deals:
            stats.last_deal_at = max(d.created_at for d in deals)
        
        return stats
    
    def cancel_offer(self, offer_id: str, buyer_id: str) -> bool:
        """Cancel a pending offer."""
        offer = self._offers.get(offer_id)
        if not offer:
            return False
        
        if offer.buyer_id != buyer_id:
            return False
        
        if offer.status != OfferStatus.PENDING:
            return False
        
        offer.status = OfferStatus.CANCELLED
        offer.updated_at = datetime.now()
        self._save_offer(offer)
        return True
    
    # ==================== SELLER OPERATIONS ====================
    
    def get_seller_by_platform(self, platform: str) -> Optional[SellerProfile]:
        """Get seller profile for a platform."""
        for seller in self._sellers.values():
            if seller.platform == platform:
                return seller
        return None
    
    def get_seller_by_id(self, seller_id: str) -> Optional[SellerProfile]:
        """Get seller by ID."""
        return self._sellers.get(seller_id)
    
    def get_seller_by_user_id(self, user_id: str) -> Optional[SellerProfile]:
        """Get seller profile by user ID."""
        for seller in self._sellers.values():
            if seller.user_id == user_id:
                return seller
        return None
    
    def get_seller_offers(
        self,
        seller_id: str,
        status: Optional[OfferStatus] = None
    ) -> List[NegotiationOffer]:
        """Get all offers for a seller."""
        offers = [o for o in self._offers.values() if o.seller_id == seller_id]
        
        if status:
            offers = [o for o in offers if o.status == status]
        
        offers.sort(key=lambda x: x.created_at, reverse=True)
        return offers
    
    def get_seller_pending_offers(self, seller_id: str) -> List[NegotiationOffer]:
        """Get pending offers for seller."""
        return self.get_seller_offers(seller_id, OfferStatus.PENDING)
    
    def get_seller_deals(self, seller_id: str) -> List[Deal]:
        """Get all deals for a seller."""
        deals = [d for d in self._deals.values() if d.seller_id == seller_id]
        deals.sort(key=lambda x: x.created_at, reverse=True)
        return deals
    
    def respond_to_offer(
        self,
        offer_id: str,
        seller_id: str,
        response: RespondOfferRequest
    ) -> Tuple[bool, str, Optional[NegotiationOffer]]:
        """
        Seller responds to an offer.
        
        Returns:
            (success, message, updated_offer)
        """
        offer = self._offers.get(offer_id)
        if not offer:
            return False, "Offer not found", None
        
        if offer.seller_id != seller_id:
            return False, "Not authorized to respond to this offer", None
        
        if offer.status != OfferStatus.PENDING:
            return False, f"Offer is already {offer.status.value}", None
        
        seller = self._sellers.get(seller_id)
        
        offer.responded_at = datetime.now()
        offer.updated_at = datetime.now()
        
        if response.action == "accept":
            offer.status = OfferStatus.ACCEPTED
            self._save_offer(offer)  # Save the updated offer
            self._create_deal_from_offer(offer)
            
            if seller:
                seller.offers_accepted += 1
                self._save_sellers()
            
            return True, "Offer accepted! Deal created.", offer
        
        elif response.action == "reject":
            offer.status = OfferStatus.REJECTED
            self._save_offer(offer)  # Save the updated offer
            
            if seller:
                seller.offers_rejected += 1
                self._save_sellers()
            
            return True, "Offer rejected.", offer
        
        elif response.action == "counter":
            if not response.counter_price:
                return False, "Counter price is required", None
            
            if response.counter_price >= offer.original_price:
                return False, "Counter price must be less than original price", None
            
            if response.counter_price <= offer.offered_price:
                return False, "Counter price must be more than offered price", None
            
            offer.status = OfferStatus.COUNTERED
            offer.counter_price = response.counter_price
            offer.counter_message = response.message
            self._save_offer(offer)  # Save the updated offer
            
            if seller:
                seller.offers_countered += 1
                self._save_sellers()
            
            return True, f"Counter offer of ₹{response.counter_price} sent.", offer
        
        return False, "Invalid action", None
    
    def accept_counter_offer(
        self,
        offer_id: str,
        buyer_id: str
    ) -> Tuple[bool, str, Optional[Deal]]:
        """Buyer accepts a counter offer."""
        offer = self._offers.get(offer_id)
        if not offer:
            return False, "Offer not found", None
        
        if offer.buyer_id != buyer_id:
            return False, "Not authorized", None
        
        if offer.status != OfferStatus.COUNTERED:
            return False, "No counter offer to accept", None
        
        # Update offer with counter price
        offer.offered_price = offer.counter_price
        offer.total_offered = offer.counter_price * offer.quantity
        offer.discount_percent = round(
            ((offer.original_price - offer.counter_price) / offer.original_price) * 100, 2
        )
        offer.status = OfferStatus.ACCEPTED
        offer.updated_at = datetime.now()
        
        # Create deal
        deal = self._create_deal_from_offer(offer)
        
        return True, "Counter offer accepted! Deal created.", deal
    
    def reject_counter_offer(
        self,
        offer_id: str,
        buyer_id: str
    ) -> Tuple[bool, str]:
        """Buyer rejects a counter offer."""
        offer = self._offers.get(offer_id)
        if not offer:
            return False, "Offer not found"
        
        if offer.buyer_id != buyer_id:
            return False, "Not authorized"
        
        if offer.status != OfferStatus.COUNTERED:
            return False, "No counter offer to reject"
        
        offer.status = OfferStatus.CANCELLED
        offer.updated_at = datetime.now()
        
        return True, "Counter offer rejected. Negotiation ended."
    
    def get_seller_stats(self, seller_id: str) -> SellerStats:
        """Get statistics for a seller."""
        seller = self._sellers.get(seller_id)
        if not seller:
            return SellerStats(seller_id=seller_id, platform="unknown")
        
        offers = self.get_seller_offers(seller_id)
        deals = self.get_seller_deals(seller_id)
        
        stats = SellerStats(
            seller_id=seller_id,
            platform=seller.platform
        )
        
        stats.total_offers_received = len(offers)
        stats.offers_accepted = len([o for o in offers if o.status == OfferStatus.ACCEPTED])
        stats.offers_rejected = len([o for o in offers if o.status == OfferStatus.REJECTED])
        stats.offers_pending = len([o for o in offers if o.status == OfferStatus.PENDING])
        stats.offers_countered = len([o for o in offers if o.status == OfferStatus.COUNTERED])
        
        stats.total_deals = len(deals)
        stats.total_revenue = sum(d.total_amount for d in deals)
        
        if stats.total_deals > 0:
            stats.avg_deal_value = stats.total_revenue / stats.total_deals
            stats.avg_discount_given = sum(d.savings_percent for d in deals) / stats.total_deals
        
        if stats.total_offers_received > 0:
            responded = stats.offers_accepted + stats.offers_rejected + stats.offers_countered
            stats.response_rate = (responded / stats.total_offers_received) * 100
            stats.acceptance_rate = (stats.offers_accepted / stats.total_offers_received) * 100
        
        # Top products
        product_counts = {}
        for offer in offers:
            key = offer.product_name
            if key not in product_counts:
                product_counts[key] = {"name": key, "count": 0, "revenue": 0}
            product_counts[key]["count"] += 1
        
        for deal in deals:
            key = deal.product_name
            if key in product_counts:
                product_counts[key]["revenue"] += deal.total_amount
        
        stats.top_products = sorted(
            product_counts.values(),
            key=lambda x: x["count"],
            reverse=True
        )[:5]
        
        if offers:
            stats.last_offer_at = max(o.created_at for o in offers)
        if deals:
            stats.last_deal_at = max(d.created_at for d in deals)
        
        return stats
    
    # ==================== DEAL OPERATIONS ====================
    
    def _create_deal_from_offer(self, offer: NegotiationOffer) -> Deal:
        """Create a deal from an accepted offer."""
        deal = Deal(
            offer_id=offer.offer_id,
            product_id=offer.product_id,
            product_name=offer.product_name,
            platform=offer.platform,
            platform_name=offer.platform_name,
            buyer_id=offer.buyer_id,
            buyer_name=offer.buyer_name,
            seller_id=offer.seller_id,
            seller_name=offer.seller_name,
            original_price=offer.original_price,
            final_price=offer.offered_price,
            quantity=offer.quantity,
            total_amount=offer.total_offered,
            savings=(offer.original_price - offer.offered_price) * offer.quantity,
            savings_percent=offer.discount_percent,
            delivery_pincode=offer.pincode
        )
        
        self._deals[deal.deal_id] = deal
        self._save_deal(deal)
        
        # Update offer status to completed
        offer.status = OfferStatus.COMPLETED
        self._save_offer(offer)  # Save the completed status
        
        # Update seller stats
        seller = self._sellers.get(offer.seller_id)
        if seller:
            seller.total_deals += 1
            seller.total_revenue += deal.total_amount
            self._save_sellers()
        
        return deal
    
    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Get a deal by ID."""
        return self._deals.get(deal_id)
    
    def update_deal_status(
        self,
        deal_id: str,
        status: DealStatus,
        payment_id: Optional[str] = None
    ) -> bool:
        """Update deal status."""
        deal = self._deals.get(deal_id)
        if not deal:
            return False
        
        deal.status = status
        if payment_id:
            deal.payment_id = payment_id
        if status == DealStatus.PAID:
            deal.paid_at = datetime.now()
        if status == DealStatus.DELIVERED:
            deal.delivered_at = datetime.now()
        
        self._save_deal(deal)
        return True
    
    def get_offer(self, offer_id: str) -> Optional[NegotiationOffer]:
        """Get an offer by ID."""
        return self._offers.get(offer_id)
    
    # ==================== ADMIN/STATS ====================
    
    def get_platform_stats(self) -> Dict:
        """Get stats for all platforms."""
        stats = {}
        
        for seller in self._sellers.values():
            seller_stats = self.get_seller_stats(seller.seller_id)
            stats[seller.platform] = {
                "platform": seller.platform,
                "platform_name": seller.platform_name,
                "seller_name": seller.business_name,
                "total_offers": seller_stats.total_offers_received,
                "pending_offers": seller_stats.offers_pending,
                "acceptance_rate": seller_stats.acceptance_rate,
                "total_deals": seller_stats.total_deals,
                "total_revenue": seller_stats.total_revenue,
                "avg_discount": seller_stats.avg_discount_given
            }
        
        return stats
    
    def get_all_pending_offers(self) -> List[NegotiationOffer]:
        """Get all pending offers across all sellers."""
        return [o for o in self._offers.values() if o.status == OfferStatus.PENDING]
    
    def process_expired_manual_reviews(self) -> List[dict]:
        """
        Process offers where manual review deadline has passed.
        Apply auto-accept/reject rules based on seller settings.
        
        Returns list of processed offers with their new status.
        """
        processed = []
        now = datetime.now()
        
        for offer in list(self._offers.values()):
            # Only process pending offers with expired manual review deadline
            if offer.status != OfferStatus.PENDING:
                continue
            
            if not offer.manual_review_deadline:
                continue
            
            # Check if manual review deadline has passed
            if now < offer.manual_review_deadline:
                continue
            
            # Get seller settings
            seller = self._sellers.get(offer.seller_id)
            if not seller:
                continue
            
            # If manual_review_only is True, don't auto-process
            if seller.manual_review_only:
                continue
            
            # Apply auto-accept/reject rules
            discount = offer.discount_percent
            
            if discount <= seller.auto_accept_discount:
                # Auto-accept
                offer.status = OfferStatus.ACCEPTED
                offer.responded_at = now
                offer.auto_processed = True
                self._create_deal_from_offer(offer)
                processed.append({
                    "offer_id": offer.offer_id,
                    "action": "auto_accepted",
                    "discount": discount,
                    "threshold": seller.auto_accept_discount
                })
                
            elif discount > seller.auto_reject_discount:
                # Auto-reject (discount too high)
                offer.status = OfferStatus.REJECTED
                offer.responded_at = now
                offer.auto_processed = True
                processed.append({
                    "offer_id": offer.offer_id,
                    "action": "auto_rejected",
                    "discount": discount,
                    "threshold": seller.auto_reject_discount
                })
            else:
                # Discount is between auto-accept and auto-reject thresholds
                # Send a counter offer at a middle ground
                counter_price = offer.original_price * (1 - seller.auto_accept_discount / 100)
                offer.status = OfferStatus.COUNTERED
                offer.counter_price = round(counter_price, 2)
                offer.counter_message = "Auto-generated counter offer. This is our best price."
                offer.responded_at = now
                offer.auto_processed = True
                processed.append({
                    "offer_id": offer.offer_id,
                    "action": "auto_countered",
                    "discount": discount,
                    "counter_price": counter_price
                })
            
            # Save the updated offer
            offer.updated_at = now
            self._save_offer(offer)
        
        return processed
    
    def get_offer_time_remaining(self, offer_id: str) -> Optional[int]:
        """Get seconds remaining for manual review."""
        offer = self._offers.get(offer_id)
        if not offer or offer.status != OfferStatus.PENDING:
            return None
        
        if not offer.manual_review_deadline:
            return None
        
        remaining = (offer.manual_review_deadline - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def get_recent_deals(self, limit: int = 10) -> List[Deal]:
        """Get recent deals."""
        deals = list(self._deals.values())
        deals.sort(key=lambda x: x.created_at, reverse=True)
        return deals[:limit]
    
    def get_all_offers(self, limit: int = 100) -> List[NegotiationOffer]:
        """Get all offers across all sellers (for admin)."""
        all_offers = list(self._offers.values())
        all_offers.sort(key=lambda x: x.created_at, reverse=True)
        return all_offers[:limit]
    
    def register_seller(
        self,
        user_id: str,
        platform: str,
        business_name: str,
        **kwargs
    ) -> SellerProfile:
        """Register a new seller."""
        # Check if seller already exists for this platform
        existing = self.get_seller_by_platform(platform)
        if existing:
            return existing
        
        seller = SellerProfile(
            user_id=user_id,
            platform=platform,
            platform_name=kwargs.get("platform_name", platform.title()),
            business_name=business_name,
            email=kwargs.get("email"),
            phone=kwargs.get("phone"),
            auto_accept_discount=kwargs.get("auto_accept_discount", 5),
            max_discount=kwargs.get("max_discount", 25),
            cities=kwargs.get("cities", [])
        )
        
        self._sellers[seller.seller_id] = seller
        self._save_sellers()
        
        return seller


# Singleton instance
_negotiation_service: Optional[NegotiationService] = None


def get_negotiation_service() -> NegotiationService:
    """Get negotiation service instance."""
    global _negotiation_service
    if _negotiation_service is None:
        _negotiation_service = NegotiationService()
    return _negotiation_service

