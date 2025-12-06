"""
Negotiation API Routes.

Endpoints for:
- Buyers: Create offers, view offers, accept/reject counters
- Sellers: View offers, respond (accept/reject/counter)
- Stats: Buyer and seller dashboards
"""
from fastapi import APIRouter, HTTPException, Header, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

from models.negotiation import (
    NegotiationOffer, Deal, OfferStatus,
    CreateOfferRequest, RespondOfferRequest, CompleteDealRequest,
    BuyerStats, SellerStats
)
from services.negotiation_service import get_negotiation_service


router = APIRouter()


# ==================== BUYER ENDPOINTS ====================

@router.post("/offers", response_model=Dict[str, Any])
async def create_offer(
    request: CreateOfferRequest,
    x_user_id: str = Header(..., alias="X-User-Id"),
    x_user_name: str = Header("Guest", alias="X-User-Name")
):
    """
    Create a new negotiation offer.
    
    Buyer proposes a discounted price to the seller.
    """
    service = get_negotiation_service()
    
    # Validate discount
    if request.offered_price >= request.original_price:
        raise HTTPException(
            status_code=400,
            detail="Offered price must be less than original price"
        )
    
    discount_percent = ((request.original_price - request.offered_price) / request.original_price) * 100
    if discount_percent > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum discount allowed is 50%"
        )
    
    offer = service.create_offer(
        buyer_id=x_user_id,
        buyer_name=x_user_name,
        request=request
    )
    
    return {
        "success": True,
        "message": "Offer submitted successfully" if offer.status == OfferStatus.PENDING else "Offer auto-accepted!",
        "offer": {
            "offer_id": offer.offer_id,
            "status": offer.status.value,
            "product_name": offer.product_name,
            "original_price": offer.original_price,
            "offered_price": offer.offered_price,
            "discount_percent": offer.discount_percent,
            "platform": offer.platform,
            "platform_name": offer.platform_name,
            "expires_at": offer.expires_at.isoformat() if offer.expires_at else None
        }
    }


@router.get("/offers/my", response_model=Dict[str, Any])
async def get_my_offers(
    status: Optional[str] = None,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Get all offers made by the current buyer."""
    service = get_negotiation_service()
    
    status_filter = None
    if status:
        try:
            status_filter = OfferStatus(status)
        except ValueError:
            pass
    
    offers = service.get_buyer_offers(x_user_id, status_filter)
    
    return {
        "offers": [
            {
                "offer_id": o.offer_id,
                "product_name": o.product_name,
                "product_quantity": o.product_quantity,
                "platform": o.platform,
                "platform_name": o.platform_name,
                "original_price": o.original_price,
                "offered_price": o.offered_price,
                "discount_percent": o.discount_percent,
                "quantity": o.quantity,
                "total_offered": o.total_offered,
                "status": o.status.value,
                "counter_price": o.counter_price,
                "counter_message": o.counter_message,
                "message": o.message,
                "created_at": o.created_at.isoformat(),
                "expires_at": o.expires_at.isoformat() if o.expires_at else None
            }
            for o in offers
        ],
        "count": len(offers)
    }


@router.get("/offers/{offer_id}", response_model=Dict[str, Any])
async def get_offer(offer_id: str):
    """Get details of a specific offer."""
    service = get_negotiation_service()
    offer = service.get_offer(offer_id)
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    return {
        "offer": {
            "offer_id": offer.offer_id,
            "product_id": offer.product_id,
            "product_name": offer.product_name,
            "product_brand": offer.product_brand,
            "product_quantity": offer.product_quantity,
            "platform": offer.platform,
            "platform_name": offer.platform_name,
            "seller_name": offer.seller_name,
            "original_price": offer.original_price,
            "offered_price": offer.offered_price,
            "discount_percent": offer.discount_percent,
            "quantity": offer.quantity,
            "total_original": offer.total_original,
            "total_offered": offer.total_offered,
            "buyer_name": offer.buyer_name,
            "status": offer.status.value,
            "message": offer.message,
            "counter_price": offer.counter_price,
            "counter_message": offer.counter_message,
            "created_at": offer.created_at.isoformat(),
            "expires_at": offer.expires_at.isoformat() if offer.expires_at else None,
            "responded_at": offer.responded_at.isoformat() if offer.responded_at else None
        }
    }


@router.post("/offers/{offer_id}/cancel")
async def cancel_offer(
    offer_id: str,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Cancel a pending offer."""
    service = get_negotiation_service()
    success = service.cancel_offer(offer_id, x_user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel this offer")
    
    return {"success": True, "message": "Offer cancelled"}


@router.post("/offers/{offer_id}/accept-counter")
async def accept_counter_offer(
    offer_id: str,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Accept a counter offer from seller."""
    service = get_negotiation_service()
    success, message, deal = service.accept_counter_offer(offer_id, x_user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": message,
        "deal": {
            "deal_id": deal.deal_id,
            "product_name": deal.product_name,
            "final_price": deal.final_price,
            "total_amount": deal.total_amount,
            "savings": deal.savings,
            "savings_percent": deal.savings_percent
        } if deal else None
    }


@router.post("/offers/{offer_id}/reject-counter")
async def reject_counter_offer(
    offer_id: str,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Reject a counter offer from seller."""
    service = get_negotiation_service()
    success, message = service.reject_counter_offer(offer_id, x_user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@router.get("/buyer/stats", response_model=Dict[str, Any])
async def get_buyer_stats(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get buyer dashboard statistics."""
    service = get_negotiation_service()
    stats = service.get_buyer_stats(x_user_id)
    
    return {
        "stats": {
            "total_offers_made": stats.total_offers_made,
            "offers_accepted": stats.offers_accepted,
            "offers_rejected": stats.offers_rejected,
            "offers_pending": stats.offers_pending,
            "offers_countered": stats.offers_countered,
            "total_deals": stats.total_deals,
            "total_spent": stats.total_spent,
            "total_savings": stats.total_savings,
            "avg_discount": round(stats.avg_discount, 1),
            "success_rate": round(stats.success_rate, 1),
            "last_offer_at": stats.last_offer_at.isoformat() if stats.last_offer_at else None,
            "last_deal_at": stats.last_deal_at.isoformat() if stats.last_deal_at else None
        }
    }


@router.get("/buyer/deals", response_model=Dict[str, Any])
async def get_buyer_deals(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get all deals for the buyer."""
    service = get_negotiation_service()
    deals = service.get_buyer_deals(x_user_id)
    
    return {
        "deals": [
            {
                "deal_id": d.deal_id,
                "product_name": d.product_name,
                "platform": d.platform,
                "platform_name": d.platform_name or d.platform.title(),
                "original_price": d.original_price,
                "final_price": d.final_price,
                "quantity": d.quantity,
                "total_amount": d.total_amount,
                "savings": d.savings,
                "savings_percent": d.savings_percent,
                "status": d.status.value,
                "created_at": d.created_at.isoformat()
            }
            for d in deals
        ],
        "count": len(deals)
    }


@router.post("/deals/{deal_id}/order", response_model=Dict[str, Any])
async def place_order_at_deal_price(
    deal_id: str,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """
    Place an order at the negotiated deal price.
    
    This confirms the purchase at the previously agreed negotiated price.
    """
    service = get_negotiation_service()
    
    # Find the deal
    deals = service.get_buyer_deals(x_user_id)
    deal = next((d for d in deals if d.deal_id == deal_id), None)
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Update deal status to "ordered"
    order_result = service.complete_deal_order(
        deal_id=deal_id,
        buyer_id=x_user_id,
        order_price=deal.final_price  # Use the negotiated price
    )
    
    return {
        "success": True,
        "message": f"Order placed successfully at negotiated price ₹{deal.final_price}",
        "order": {
            "deal_id": deal_id,
            "product_name": deal.product_name,
            "platform": deal.platform,
            "order_price": deal.final_price,  # Negotiated price used
            "original_price": deal.original_price,
            "quantity": deal.quantity,
            "total_amount": deal.final_price * deal.quantity,
            "savings": deal.savings,
            "order_status": "confirmed",
            "ordered_at": datetime.now().isoformat()
        }
    }


# ==================== SELLER ENDPOINTS ====================

@router.get("/seller/offers", response_model=Dict[str, Any])
async def get_seller_offers(
    status: Optional[str] = None,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Get all offers for the seller."""
    service = get_negotiation_service()
    
    # Get seller by user ID
    seller = service.get_seller_by_user_id(x_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    status_filter = None
    if status:
        try:
            status_filter = OfferStatus(status)
        except ValueError:
            pass
    
    offers = service.get_seller_offers(seller.seller_id, status_filter)
    
    return {
        "seller_id": seller.seller_id,
        "platform": seller.platform,
        "offers": [
            {
                "offer_id": o.offer_id,
                "product_name": o.product_name,
                "product_quantity": o.product_quantity,
                "buyer_name": o.buyer_name,
                "original_price": o.original_price,
                "offered_price": o.offered_price,
                "discount_percent": o.discount_percent,
                "quantity": o.quantity,
                "total_offered": o.total_offered,
                "status": o.status.value,
                "message": o.message,
                "pincode": o.pincode,
                "city": o.city,
                "created_at": o.created_at.isoformat()
            }
            for o in offers
        ],
        "count": len(offers)
    }


@router.get("/seller/pending", response_model=Dict[str, Any])
async def get_seller_pending_offers(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get pending offers for seller to respond."""
    service = get_negotiation_service()
    
    seller = service.get_seller_by_user_id(x_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    offers = service.get_seller_pending_offers(seller.seller_id)
    
    # Process any expired manual reviews first
    service.process_expired_manual_reviews()
    
    # Re-fetch pending offers after processing
    offers = service.get_seller_pending_offers(seller.seller_id)
    
    return {
        "pending_offers": [
            {
                "offer_id": o.offer_id,
                "product_name": o.product_name,
                "product_quantity": o.product_quantity,
                "buyer_name": o.buyer_name,
                "platform": o.platform,
                "platform_name": o.platform_name,
                "original_price": o.original_price,
                "offered_price": o.offered_price,
                "discount_percent": o.discount_percent,
                "quantity": o.quantity,
                "total_offered": o.total_offered,
                "message": o.message,
                "pincode": o.pincode,
                "city": o.city,
                "created_at": o.created_at.isoformat(),
                "expires_at": o.expires_at.isoformat() if o.expires_at else None,
                "manual_review_deadline": o.manual_review_deadline.isoformat() if o.manual_review_deadline else None,
                "time_remaining_secs": service.get_offer_time_remaining(o.offer_id)
            }
            for o in offers
        ],
        "count": len(offers),
        "seller_settings": {
            "manual_review_only": seller.manual_review_only,
            "manual_review_timeout_mins": seller.manual_review_timeout_mins,
            "auto_accept_discount": seller.auto_accept_discount,
            "auto_reject_discount": seller.auto_reject_discount
        }
    }


@router.post("/seller/offers/{offer_id}/respond")
async def respond_to_offer(
    offer_id: str,
    response: RespondOfferRequest,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Seller responds to an offer (accept/reject/counter)."""
    service = get_negotiation_service()
    
    seller = service.get_seller_by_user_id(x_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    success, message, offer = service.respond_to_offer(
        offer_id=offer_id,
        seller_id=seller.seller_id,
        response=response
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "success": True,
        "message": message,
        "offer_status": offer.status.value if offer else None
    }


@router.get("/seller/stats", response_model=Dict[str, Any])
async def get_seller_stats(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get seller dashboard statistics."""
    service = get_negotiation_service()
    
    seller = service.get_seller_by_user_id(x_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    stats = service.get_seller_stats(seller.seller_id)
    
    return {
        "seller": {
            "seller_id": seller.seller_id,
            "business_name": seller.business_name,
            "platform": seller.platform,
            "platform_name": seller.platform_name,
            "manual_review_only": seller.manual_review_only,
            "manual_review_timeout_mins": seller.manual_review_timeout_mins,
            "auto_accept_discount": seller.auto_accept_discount,
            "auto_reject_discount": seller.auto_reject_discount,
            "max_discount": seller.max_discount
        },
        "stats": {
            "total_offers_received": stats.total_offers_received,
            "offers_accepted": stats.offers_accepted,
            "offers_rejected": stats.offers_rejected,
            "offers_pending": stats.offers_pending,
            "offers_countered": stats.offers_countered,
            "total_deals": stats.total_deals,
            "total_revenue": stats.total_revenue,
            "avg_deal_value": round(stats.avg_deal_value, 2),
            "avg_discount_given": round(stats.avg_discount_given, 1),
            "response_rate": round(stats.response_rate, 1),
            "acceptance_rate": round(stats.acceptance_rate, 1),
            "top_products": stats.top_products,
            "last_offer_at": stats.last_offer_at.isoformat() if stats.last_offer_at else None,
            "last_deal_at": stats.last_deal_at.isoformat() if stats.last_deal_at else None
        }
    }


@router.get("/seller/deals", response_model=Dict[str, Any])
async def get_seller_deals(x_user_id: str = Header(..., alias="X-User-Id")):
    """Get all deals for the seller."""
    service = get_negotiation_service()
    
    seller = service.get_seller_by_user_id(x_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    deals = service.get_seller_deals(seller.seller_id)
    
    return {
        "deals": [
            {
                "deal_id": d.deal_id,
                "product_name": d.product_name,
                "buyer_name": d.buyer_name,
                "platform": d.platform,
                "platform_name": d.platform_name,
                "original_price": d.original_price,
                "final_price": d.final_price,
                "quantity": d.quantity,
                "total_amount": d.total_amount,
                "savings_percent": d.savings_percent,
                "status": d.status.value,
                "created_at": d.created_at.isoformat()
            }
            for d in deals
        ],
        "count": len(deals),
        "total_revenue": sum(d.total_amount for d in deals)
    }


class UpdateSellerSettingsRequest(BaseModel):
    manual_review_only: Optional[bool] = None
    manual_review_timeout_mins: Optional[int] = None
    auto_accept_discount: Optional[float] = None
    auto_reject_discount: Optional[float] = None
    max_discount: Optional[float] = None


@router.put("/seller/settings")
async def update_seller_settings(
    settings: UpdateSellerSettingsRequest,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Update seller settings."""
    service = get_negotiation_service()
    
    seller = service.get_seller_by_user_id(x_user_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller profile not found")
    
    if settings.manual_review_only is not None:
        seller.manual_review_only = settings.manual_review_only
    if settings.manual_review_timeout_mins is not None:
        seller.manual_review_timeout_mins = settings.manual_review_timeout_mins
    if settings.auto_accept_discount is not None:
        seller.auto_accept_discount = settings.auto_accept_discount
    if settings.auto_reject_discount is not None:
        seller.auto_reject_discount = settings.auto_reject_discount
    if settings.max_discount is not None:
        seller.max_discount = settings.max_discount
    
    service._save_sellers()
    
    return {"success": True, "message": "Settings updated"}


# ==================== PUBLIC/ADMIN ENDPOINTS ====================

@router.get("/platforms/stats", response_model=Dict[str, Any])
async def get_platform_stats():
    """Get negotiation stats for all platforms."""
    service = get_negotiation_service()
    stats = service.get_platform_stats()
    
    return {
        "platforms": list(stats.values()),
        "total_platforms": len(stats)
    }


@router.get("/deals/recent", response_model=Dict[str, Any])
async def get_recent_deals(limit: int = 10):
    """Get recent deals across all platforms."""
    service = get_negotiation_service()
    deals = service.get_recent_deals(limit)
    
    return {
        "deals": [
            {
                "deal_id": d.deal_id,
                "product_name": d.product_name,
                "platform": d.platform,
                "buyer_name": d.buyer_name,
                "final_price": d.final_price,
                "savings_percent": d.savings_percent,
                "status": d.status,
                "created_at": d.created_at.isoformat()
            }
            for d in deals
        ],
        "count": len(deals)
    }


@router.get("/admin/all-offers", response_model=Dict[str, Any])
async def get_all_offers_admin(limit: int = Query(default=100, le=500)):
    """Admin endpoint to get all offers across all sellers."""
    service = get_negotiation_service()
    all_offers = service.get_all_offers(limit)
    
    return {
        "offers": [
            {
                "offer_id": o.offer_id,
                "product_name": o.product_name,
                "buyer_name": o.buyer_name,
                "buyer_id": o.buyer_id,
                "platform": o.platform,
                "platform_name": o.platform_name,
                "original_price": o.original_price,
                "offered_price": o.offered_price,
                "discount_percent": round((o.original_price - o.offered_price) / o.original_price * 100, 2),
                "status": o.status.value,
                "created_at": o.created_at.isoformat()
            }
            for o in all_offers
        ],
        "count": len(all_offers)
    }


class RegisterSellerRequest(BaseModel):
    platform: str
    business_name: str
    platform_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    auto_accept_discount: float = 5
    max_discount: float = 25
    cities: List[str] = []


@router.post("/process-expired")
async def process_expired_offers():
    """
    Process offers where manual review deadline has passed.
    Applies auto-accept/reject rules based on seller settings.
    """
    service = get_negotiation_service()
    processed = service.process_expired_manual_reviews()
    
    return {
        "processed_count": len(processed),
        "results": processed
    }


@router.post("/seller/register")
async def register_seller(
    request: RegisterSellerRequest,
    x_user_id: str = Header(..., alias="X-User-Id")
):
    """Register as a seller for a platform."""
    service = get_negotiation_service()
    
    # Check if already registered
    existing = service.get_seller_by_user_id(x_user_id)
    if existing:
        return {
            "success": True,
            "message": "Already registered as seller",
            "seller_id": existing.seller_id,
            "platform": existing.platform
        }
    
    seller = service.register_seller(
        user_id=x_user_id,
        platform=request.platform,
        business_name=request.business_name,
        platform_name=request.platform_name,
        email=request.email,
        phone=request.phone,
        auto_accept_discount=request.auto_accept_discount,
        max_discount=request.max_discount,
        cities=request.cities
    )
    
    return {
        "success": True,
        "message": "Registered as seller",
        "seller_id": seller.seller_id,
        "platform": seller.platform
    }

