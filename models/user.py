"""
User data models for authentication.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    USER = "user"
    BUYER = "buyer"
    SELLER = "seller"
    PREMIUM = "premium"
    ADMIN = "admin"


class User(BaseModel):
    """User model."""
    id: str = Field(..., description="Unique user ID")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    hashed_password: str = Field(..., description="Hashed password")
    
    # Profile
    full_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Location preferences
    default_pincode: str = Field("400001")
    default_city: str = Field("Mumbai")
    
    # Role and permissions
    role: UserRole = Field(UserRole.USER)
    is_active: bool = Field(True)
    is_verified: bool = Field(False)
    
    # Preferences
    favorite_platforms: List[str] = Field(default_factory=list)
    notification_enabled: bool = Field(True)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "usr_123abc",
                "email": "user@example.com",
                "username": "priceHunter",
                "full_name": "Price Hunter",
                "default_pincode": "400001",
                "default_city": "Mumbai",
                "role": "user",
                "is_active": True
            }
        }


class UserCreate(BaseModel):
    """Request model for user registration."""
    email: str = Field(..., description="Email address")
    username: str = Field(..., min_length=3, max_length=30, description="Username")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    full_name: Optional[str] = None
    phone: Optional[str] = None
    default_pincode: Optional[str] = "400001"
    role: Optional[str] = Field("buyer", description="User role: buyer or seller")
    
    # Seller specific fields
    business_name: Optional[str] = None
    platform: Optional[str] = None  # For sellers: which platform they represent
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "priceHunter",
                "password": "securePassword123",
                "full_name": "Price Hunter",
                "default_pincode": "400001",
                "role": "buyer"
            }
        }


class UserLogin(BaseModel):
    """Request model for login."""
    email: str = Field(..., description="Email or username")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securePassword123"
            }
        }


class UserUpdate(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    default_pincode: Optional[str] = None
    default_city: Optional[str] = None
    favorite_platforms: Optional[List[str]] = None
    notification_enabled: Optional[bool] = None


class UserResponse(BaseModel):
    """Response model for user data (excludes sensitive info)."""
    id: str
    email: str
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    default_pincode: str
    default_city: str
    role: UserRole
    is_active: bool
    is_verified: bool
    favorite_platforms: List[str]
    notification_enabled: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """JWT Token response."""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Seconds until expiration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenPayload(BaseModel):
    """JWT Token payload."""
    sub: str  # User ID
    email: str
    username: str
    role: str
    exp: datetime
    iat: datetime
    type: str = "access"  # "access" or "refresh"


class PasswordReset(BaseModel):
    """Password reset request."""
    email: str


class PasswordResetConfirm(BaseModel):
    """Confirm password reset."""
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChange(BaseModel):
    """Change password (when logged in)."""
    current_password: str
    new_password: str = Field(..., min_length=8)

