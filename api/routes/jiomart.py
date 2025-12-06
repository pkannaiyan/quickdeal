"""
JioMart Integration API Routes.

Provides endpoints for:
- Login with OTP
- Add to cart
- One-click checkout
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from services.jiomart_integration import get_jiomart_integration


router = APIRouter()


class SendOTPRequest(BaseModel):
    phone: str


class LoginRequest(BaseModel):
    phone: str
    otp: str
    session_id: Optional[str] = None


class CredentialLoginRequest(BaseModel):
    phone: str
    password: str


class AddToCartRequest(BaseModel):
    product_id: str
    product_name: Optional[str] = None
    quantity: int = 1


class OneClickOrderRequest(BaseModel):
    product_id: str
    product_name: str
    quantity: int = 1
    address_id: Optional[str] = None
    payment_method: str = "cod"


class CheckoutRequest(BaseModel):
    address_id: str
    payment_method: str = "cod"
    delivery_slot: Optional[str] = None


@router.post("/send-otp")
async def send_otp(request: SendOTPRequest) -> Dict[str, Any]:
    """
    Send OTP to phone number for login.
    
    Returns session_id to use in login.
    """
    integration = get_jiomart_integration()
    result = await integration.send_otp(request.phone)
    return result


@router.post("/login")
async def login(request: LoginRequest) -> Dict[str, Any]:
    """
    Login with phone and OTP.
    
    Returns user profile and session token.
    """
    integration = get_jiomart_integration()
    user = await integration.login(
        phone=request.phone,
        otp=request.otp,
        session_id=request.session_id
    )
    
    if user:
        return {
            "success": True,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "phone": user.phone
            },
            "message": "Login successful"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid OTP or login failed")


@router.post("/login-password")
async def login_with_password(request: CredentialLoginRequest) -> Dict[str, Any]:
    """
    Login with phone and password.
    """
    integration = get_jiomart_integration()
    user = await integration.login_with_credentials(
        phone=request.phone,
        password=request.password
    )
    
    if user:
        return {
            "success": True,
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "phone": user.phone
            },
            "message": "Login successful"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/addresses")
async def get_addresses() -> Dict[str, Any]:
    """Get saved delivery addresses."""
    integration = get_jiomart_integration()
    addresses = await integration.get_addresses()
    return {"addresses": addresses}


@router.post("/add-to-cart")
async def add_to_cart(request: AddToCartRequest) -> Dict[str, Any]:
    """
    Add product to JioMart cart.
    """
    integration = get_jiomart_integration()
    
    if not integration.session_token:
        raise HTTPException(status_code=401, detail="Please login first")
    
    result = await integration.add_to_cart(
        product_id=request.product_id,
        quantity=request.quantity,
        product_name=request.product_name
    )
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to add to cart"))


@router.get("/cart")
async def get_cart() -> Dict[str, Any]:
    """Get current cart contents."""
    integration = get_jiomart_integration()
    
    if not integration.session_token:
        raise HTTPException(status_code=401, detail="Please login first")
    
    return await integration.get_cart()


@router.get("/payment-options")
async def get_payment_options() -> Dict[str, Any]:
    """Get available payment methods."""
    integration = get_jiomart_integration()
    options = await integration.get_payment_options()
    return {"options": options}


@router.post("/checkout")
async def checkout(request: CheckoutRequest) -> Dict[str, Any]:
    """
    Initiate checkout and place order.
    """
    integration = get_jiomart_integration()
    
    if not integration.session_token:
        raise HTTPException(status_code=401, detail="Please login first")
    
    # Initiate checkout
    checkout_result = await integration.initiate_checkout(request.address_id)
    if not checkout_result.get("success"):
        raise HTTPException(status_code=400, detail="Failed to initiate checkout")
    
    # Place order
    order = await integration.place_order(
        checkout_id=checkout_result["checkout_id"],
        payment_method=request.payment_method,
        delivery_slot=request.delivery_slot
    )
    
    if order:
        return {
            "success": True,
            "order_id": order.order_id,
            "status": order.status,
            "total": order.total_amount,
            "estimated_delivery": order.estimated_delivery
        }
    else:
        raise HTTPException(status_code=400, detail="Failed to place order")


@router.post("/one-click-order")
async def one_click_order(request: OneClickOrderRequest) -> Dict[str, Any]:
    """
    Complete one-click order flow.
    
    Adds to cart, uses default address, and places order with specified payment method.
    """
    integration = get_jiomart_integration()
    
    if not integration.session_token:
        raise HTTPException(status_code=401, detail="Please login to JioMart first")
    
    result = await integration.one_click_order(
        product_id=request.product_id,
        product_name=request.product_name,
        quantity=request.quantity,
        address_id=request.address_id,
        payment_method=request.payment_method
    )
    
    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Order failed"))


@router.get("/order/{order_id}")
async def get_order_status(order_id: str) -> Dict[str, Any]:
    """Get status of an order."""
    integration = get_jiomart_integration()
    return await integration.get_order_status(order_id)


@router.get("/status")
async def get_integration_status() -> Dict[str, Any]:
    """Check if JioMart integration is configured and logged in."""
    integration = get_jiomart_integration()
    
    return {
        "configured": bool(integration.api_key or integration.client_id),
        "logged_in": integration.session_token is not None,
        "user": {
            "name": integration.current_user.name if integration.current_user else None,
            "phone": integration.current_user.phone if integration.current_user else None
        } if integration.current_user else None
    }

