"""
Authentication API Routes.

Endpoints for user registration, login, and token management.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from models.user import (
    UserCreate, UserLogin, UserUpdate, UserResponse,
    Token, PasswordChange
)
from services.auth_service import get_auth_service, AuthService

router = APIRouter()
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    """
    auth_service = get_auth_service()
    
    token = credentials.credentials
    payload, error = auth_service.verify_token(token)
    
    if error:
        raise HTTPException(
            status_code=401,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = auth_service.get_user(payload.sub)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "user_id": payload.sub,
        "email": payload.email,
        "username": payload.username,
        "role": payload.role,
        "user": user
    }


def get_optional_user(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Dependency to optionally get current user (for endpoints that work with or without auth).
    """
    if not authorization:
        return None
    
    if not authorization.startswith("Bearer "):
        return None
    
    token = authorization.replace("Bearer ", "")
    
    auth_service = get_auth_service()
    payload, error = auth_service.verify_token(token)
    
    if error:
        return None
    
    user = auth_service.get_user(payload.sub)
    if not user:
        return None
    
    return {
        "user_id": payload.sub,
        "email": payload.email,
        "username": payload.username,
        "role": payload.role,
        "user": user
    }


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """
    Register a new user account.
    
    **Example:**
    ```json
    {
        "email": "user@example.com",
        "username": "priceHunter",
        "password": "securePassword123",
        "full_name": "Price Hunter"
    }
    ```
    """
    auth_service = get_auth_service()
    
    user, error = auth_service.register(user_data)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Auto-login after registration
    login_data = UserLogin(email=user_data.email, password=user_data.password)
    token, _ = auth_service.login(login_data)
    
    return {
        "message": "Registration successful",
        "user": user.model_dump(),
        "token": token.model_dump() if token else None
    }


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login and get access token.
    
    **Example:**
    ```json
    {
        "email": "user@example.com",
        "password": "securePassword123"
    }
    ```
    """
    auth_service = get_auth_service()
    
    token, error = auth_service.login(login_data)
    
    if error:
        raise HTTPException(status_code=401, detail=error)
    
    return token


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token.
    """
    auth_service = get_auth_service()
    
    token, error = auth_service.refresh_tokens(refresh_token)
    
    if error:
        raise HTTPException(status_code=401, detail=error)
    
    return token


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user (invalidate token).
    """
    # In production, you'd blacklist the token
    return {
        "message": "Logged out successfully",
        "user_id": current_user["user_id"]
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current user's profile.
    """
    user = current_user["user"]
    return UserResponse(**user.model_dump(exclude={"hashed_password"}))


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's profile.
    """
    auth_service = get_auth_service()
    
    user, error = auth_service.update_user(current_user["user_id"], update_data)
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change password for current user.
    """
    auth_service = get_auth_service()
    
    success, error = auth_service.change_password(
        current_user["user_id"],
        password_data.current_password,
        password_data.new_password
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=error)
    
    return {"message": "Password changed successfully"}


@router.get("/verify")
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Verify if token is valid.
    """
    return {
        "valid": True,
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "role": current_user["role"]
    }

