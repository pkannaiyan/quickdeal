"""
JioMart Direct Integration Service.

Provides true one-click checkout with:
- User authentication
- Add to cart
- Direct checkout

IMPORTANT: Store credentials securely in environment variables!
"""
import os
import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import hashlib


@dataclass
class JioMartUser:
    """Authenticated JioMart user."""
    user_id: str
    phone: str
    name: str
    token: str
    refresh_token: Optional[str]
    token_expiry: datetime
    default_address_id: Optional[str] = None


@dataclass
class CartItem:
    """Item in JioMart cart."""
    product_id: str
    product_name: str
    quantity: int
    price: float
    mrp: float


@dataclass
class JioMartOrder:
    """JioMart order details."""
    order_id: str
    status: str
    items: List[CartItem]
    total_amount: float
    delivery_address: Dict
    payment_status: str
    estimated_delivery: Optional[str]


class JioMartIntegration:
    """
    JioMart API Integration for direct cart and checkout.
    
    Usage:
        integration = JioMartIntegration()
        
        # Login
        user = await integration.login(phone="9876543210", otp="123456")
        
        # Add to cart
        await integration.add_to_cart(product_id="12345", quantity=2)
        
        # Checkout
        order = await integration.checkout(address_id="addr_123", payment_method="cod")
    """
    
    # JioMart API endpoints (these would need to be discovered/provided)
    BASE_URL = os.getenv("JIOMART_API_URL", "https://api.jiomart.com")
    
    # Endpoints (placeholder - need actual endpoints from JioMart)
    ENDPOINTS = {
        "send_otp": "/auth/v1/send-otp",
        "verify_otp": "/auth/v1/verify-otp",
        "refresh_token": "/auth/v1/refresh",
        "user_profile": "/user/v1/profile",
        "addresses": "/user/v1/addresses",
        "search": "/catalog/v1/search",
        "product": "/catalog/v1/product/{product_id}",
        "cart": "/cart/v1/cart",
        "add_to_cart": "/cart/v1/add",
        "update_cart": "/cart/v1/update",
        "remove_from_cart": "/cart/v1/remove",
        "checkout": "/checkout/v1/initiate",
        "place_order": "/order/v1/place",
        "order_status": "/order/v1/status/{order_id}",
        "payment_options": "/payment/v1/options",
    }
    
    def __init__(self):
        self.current_user: Optional[JioMartUser] = None
        self.session_token: Optional[str] = None
        self.cart_items: List[CartItem] = []
        
        # Load credentials from environment
        self.api_key = os.getenv("JIOMART_API_KEY", "")
        self.client_id = os.getenv("JIOMART_CLIENT_ID", "")
        self.client_secret = os.getenv("JIOMART_CLIENT_SECRET", "")
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "PriceCompare/1.0",
            "X-Client-Id": self.client_id,
            "X-Api-Key": self.api_key,
        }
        
        if include_auth and self.session_token:
            headers["Authorization"] = f"Bearer {self.session_token}"
        
        return headers
    
    async def send_otp(self, phone: str) -> Dict[str, Any]:
        """
        Send OTP to phone number for login.
        
        Args:
            phone: 10-digit Indian mobile number
            
        Returns:
            {"success": True, "message": "OTP sent", "session_id": "..."}
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}{self.ENDPOINTS['send_otp']}",
                    headers=self._get_headers(include_auth=False),
                    json={
                        "phone": phone,
                        "country_code": "+91"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "success": False,
                        "error": f"Failed to send OTP: {response.status_code}"
                    }
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def login(self, phone: str, otp: str, session_id: Optional[str] = None) -> Optional[JioMartUser]:
        """
        Login with phone and OTP.
        
        Args:
            phone: 10-digit mobile number
            otp: OTP received on phone
            session_id: Session ID from send_otp response
            
        Returns:
            JioMartUser object if successful, None otherwise
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}{self.ENDPOINTS['verify_otp']}",
                    headers=self._get_headers(include_auth=False),
                    json={
                        "phone": phone,
                        "otp": otp,
                        "session_id": session_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    self.session_token = data.get("access_token")
                    
                    self.current_user = JioMartUser(
                        user_id=data.get("user_id", ""),
                        phone=phone,
                        name=data.get("name", ""),
                        token=data.get("access_token", ""),
                        refresh_token=data.get("refresh_token"),
                        token_expiry=datetime.now() + timedelta(hours=24),
                        default_address_id=data.get("default_address_id")
                    )
                    
                    return self.current_user
                    
            except Exception as e:
                print(f"Login error: {e}")
                
        return None
    
    async def login_with_credentials(self, phone: str, password: str) -> Optional[JioMartUser]:
        """
        Login with phone and password (if supported).
        
        Args:
            phone: 10-digit mobile number
            password: Account password
            
        Returns:
            JioMartUser object if successful
        """
        # Hash password for security
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}/auth/v1/login",
                    headers=self._get_headers(include_auth=False),
                    json={
                        "phone": phone,
                        "password": password_hash,
                        "grant_type": "password"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.session_token = data.get("access_token")
                    
                    self.current_user = JioMartUser(
                        user_id=data.get("user_id", ""),
                        phone=phone,
                        name=data.get("name", ""),
                        token=data.get("access_token", ""),
                        refresh_token=data.get("refresh_token"),
                        token_expiry=datetime.now() + timedelta(hours=24)
                    )
                    
                    return self.current_user
                    
            except Exception as e:
                print(f"Login error: {e}")
                
        return None
    
    async def get_addresses(self) -> List[Dict]:
        """Get saved delivery addresses."""
        if not self.session_token:
            return []
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{self.ENDPOINTS['addresses']}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json().get("addresses", [])
                    
            except Exception as e:
                print(f"Get addresses error: {e}")
                
        return []
    
    async def search_product(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for products.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of products
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{self.ENDPOINTS['search']}",
                    headers=self._get_headers(),
                    params={
                        "q": query,
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    return response.json().get("products", [])
                    
            except Exception as e:
                print(f"Search error: {e}")
                
        return []
    
    async def add_to_cart(
        self, 
        product_id: str, 
        quantity: int = 1,
        product_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add product to cart.
        
        Args:
            product_id: JioMart product ID
            quantity: Number of items
            product_name: Optional product name for logging
            
        Returns:
            {"success": True, "cart_id": "...", "item_count": 5}
        """
        if not self.session_token:
            return {"success": False, "error": "Not logged in"}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}{self.ENDPOINTS['add_to_cart']}",
                    headers=self._get_headers(),
                    json={
                        "product_id": product_id,
                        "quantity": quantity
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "cart_id": data.get("cart_id"),
                        "item_count": data.get("total_items"),
                        "message": f"Added {quantity}x {product_name or product_id} to cart"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to add to cart: {response.status_code}"
                    }
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_cart(self) -> Dict[str, Any]:
        """Get current cart contents."""
        if not self.session_token:
            return {"items": [], "total": 0}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{self.ENDPOINTS['cart']}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                    
            except Exception as e:
                print(f"Get cart error: {e}")
                
        return {"items": [], "total": 0}
    
    async def update_cart_item(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """Update quantity of cart item."""
        if not self.session_token:
            return {"success": False, "error": "Not logged in"}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.put(
                    f"{self.BASE_URL}{self.ENDPOINTS['update_cart']}",
                    headers=self._get_headers(),
                    json={
                        "product_id": product_id,
                        "quantity": quantity
                    }
                )
                
                return {"success": response.status_code == 200}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def remove_from_cart(self, product_id: str) -> Dict[str, Any]:
        """Remove item from cart."""
        return await self.update_cart_item(product_id, 0)
    
    async def get_payment_options(self) -> List[Dict]:
        """Get available payment methods."""
        if not self.session_token:
            return []
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{self.ENDPOINTS['payment_options']}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json().get("options", [])
                    
            except Exception as e:
                print(f"Payment options error: {e}")
                
        return [
            {"id": "cod", "name": "Cash on Delivery", "enabled": True},
            {"id": "upi", "name": "UPI", "enabled": True},
            {"id": "card", "name": "Credit/Debit Card", "enabled": True},
            {"id": "netbanking", "name": "Net Banking", "enabled": True},
            {"id": "wallet", "name": "Wallets", "enabled": True},
        ]
    
    async def initiate_checkout(self, address_id: str) -> Dict[str, Any]:
        """
        Initiate checkout process.
        
        Args:
            address_id: Delivery address ID
            
        Returns:
            Checkout session details
        """
        if not self.session_token:
            return {"success": False, "error": "Not logged in"}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}{self.ENDPOINTS['checkout']}",
                    headers=self._get_headers(),
                    json={
                        "address_id": address_id
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "checkout_id": data.get("checkout_id"),
                        "summary": data.get("summary"),
                        "delivery_slots": data.get("delivery_slots", [])
                    }
                else:
                    return {"success": False, "error": "Checkout failed"}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def place_order(
        self,
        checkout_id: str,
        payment_method: str = "cod",
        delivery_slot: Optional[str] = None
    ) -> Optional[JioMartOrder]:
        """
        Place the final order.
        
        Args:
            checkout_id: Checkout session ID
            payment_method: Payment method (cod, upi, card, etc.)
            delivery_slot: Optional delivery slot ID
            
        Returns:
            JioMartOrder if successful
        """
        if not self.session_token:
            return None
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.BASE_URL}{self.ENDPOINTS['place_order']}",
                    headers=self._get_headers(),
                    json={
                        "checkout_id": checkout_id,
                        "payment_method": payment_method,
                        "delivery_slot": delivery_slot
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    return JioMartOrder(
                        order_id=data.get("order_id", ""),
                        status=data.get("status", "placed"),
                        items=[],
                        total_amount=data.get("total", 0),
                        delivery_address=data.get("address", {}),
                        payment_status=data.get("payment_status", "pending"),
                        estimated_delivery=data.get("estimated_delivery")
                    )
                    
            except Exception as e:
                print(f"Place order error: {e}")
                
        return None
    
    async def one_click_order(
        self,
        product_id: str,
        product_name: str,
        quantity: int = 1,
        address_id: Optional[str] = None,
        payment_method: str = "cod"
    ) -> Dict[str, Any]:
        """
        Complete one-click order flow.
        
        Args:
            product_id: Product to order
            product_name: Product name for display
            quantity: Number of items
            address_id: Delivery address (uses default if not provided)
            payment_method: Payment method
            
        Returns:
            {"success": True, "order_id": "...", "message": "Order placed!"}
        """
        # Step 1: Add to cart
        cart_result = await self.add_to_cart(product_id, quantity, product_name)
        if not cart_result.get("success"):
            return cart_result
        
        # Step 2: Get address
        if not address_id and self.current_user:
            address_id = self.current_user.default_address_id
            
        if not address_id:
            addresses = await self.get_addresses()
            if addresses:
                address_id = addresses[0].get("id")
            else:
                return {"success": False, "error": "No delivery address found"}
        
        # Step 3: Initiate checkout
        checkout_result = await self.initiate_checkout(address_id)
        if not checkout_result.get("success"):
            return checkout_result
        
        # Step 4: Place order
        order = await self.place_order(
            checkout_id=checkout_result["checkout_id"],
            payment_method=payment_method
        )
        
        if order:
            return {
                "success": True,
                "order_id": order.order_id,
                "status": order.status,
                "total": order.total_amount,
                "payment_status": order.payment_status,
                "estimated_delivery": order.estimated_delivery,
                "message": f"Order placed successfully! Order ID: {order.order_id}"
            }
        else:
            return {"success": False, "error": "Failed to place order"}
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """Get status of an order."""
        if not self.session_token:
            return {"error": "Not logged in"}
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}{self.ENDPOINTS['order_status'].format(order_id=order_id)}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                    
            except Exception as e:
                print(f"Order status error: {e}")
                
        return {"error": "Failed to get order status"}


# Singleton instance
_jiomart_integration: Optional[JioMartIntegration] = None


def get_jiomart_integration() -> JioMartIntegration:
    """Get JioMart integration instance."""
    global _jiomart_integration
    if _jiomart_integration is None:
        _jiomart_integration = JioMartIntegration()
    return _jiomart_integration

