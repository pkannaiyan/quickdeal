"""
Authentication Service - Handles user authentication with JWT.
"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import json

import jwt

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.user import (
    User, UserCreate, UserLogin, UserUpdate, UserResponse,
    Token, TokenPayload, UserRole
)
from api.config import DATA_DIR, LOGS_DIR


# Simple password hashing using SHA256 + salt (for demo purposes)
# In production, use bcrypt with proper backend installed
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "price-compare-salt-2024")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


class AuthService:
    """
    Authentication service for user management.
    
    Features:
    - User registration with password hashing
    - JWT token generation and validation
    - Password reset functionality
    - Session management
    """
    
    def __init__(self):
        """Initialize auth service."""
        self.users_file = DATA_DIR / "users.json"
        self.sessions_file = DATA_DIR / "sessions.json"
        
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Dict] = {}
        
        self._load_users()
        self._load_sessions()
    
    def _load_users(self) -> None:
        """Load users from storage."""
        if self.users_file.exists():
            try:
                with open(self.users_file) as f:
                    data = json.load(f)
                    for user_data in data.get("users", []):
                        user = User(**user_data)
                        self._users[user.id] = user
            except Exception as e:
                self._log("load_users_error", {"error": str(e)}, level="ERROR")
    
    def _save_users(self) -> None:
        """Save users to storage."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            data = {
                "users": [user.model_dump() for user in self._users.values()],
                "updated_at": datetime.now().isoformat()
            }
            with open(self.users_file, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self._log("save_users_error", {"error": str(e)}, level="ERROR")
    
    def _load_sessions(self) -> None:
        """Load active sessions."""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file) as f:
                    self._sessions = json.load(f)
            except:
                self._sessions = {}
    
    def _save_sessions(self) -> None:
        """Save sessions."""
        try:
            with open(self.sessions_file, "w") as f:
                json.dump(self._sessions, f, indent=2, default=str)
        except:
            pass
    
    def _generate_user_id(self) -> str:
        """Generate unique user ID."""
        return f"usr_{secrets.token_hex(8)}"
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA256 + salt."""
        salted = f"{PASSWORD_SALT}{password}{PASSWORD_SALT}"
        return hashlib.sha256(salted.encode()).hexdigest()
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self._hash_password(plain_password) == hashed_password
    
    def _create_access_token(self, user: User) -> Tuple[str, datetime]:
        """Create JWT access token."""
        expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "exp": expires,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token, expires
    
    def _create_refresh_token(self, user: User) -> Tuple[str, datetime]:
        """Create JWT refresh token."""
        expires = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
            "exp": expires,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token, expires
    
    def register(self, user_data: UserCreate) -> Tuple[Optional[UserResponse], Optional[str]]:
        """
        Register a new user.
        
        Returns:
            Tuple of (UserResponse, error_message)
        """
        # Check if email already exists
        for user in self._users.values():
            if user.email.lower() == user_data.email.lower():
                return None, "Email already registered"
            if user.username.lower() == user_data.username.lower():
                return None, "Username already taken"
        
        # Create new user
        user_id = self._generate_user_id()
        hashed_password = self._hash_password(user_data.password)
        
        # Determine role
        role = UserRole.BUYER  # Default to buyer
        if user_data.role:
            if user_data.role.lower() == "seller":
                role = UserRole.SELLER
            elif user_data.role.lower() == "buyer":
                role = UserRole.BUYER
        
        user = User(
            id=user_id,
            email=user_data.email.lower(),
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            default_pincode=user_data.default_pincode or "400001",
            role=role,
            is_active=True,
            is_verified=False
        )
        
        self._users[user_id] = user
        self._save_users()
        
        # If seller, create seller profile
        if role == UserRole.SELLER and user_data.platform and user_data.business_name:
            try:
                from services.negotiation_service import get_negotiation_service
                neg_service = get_negotiation_service()
                neg_service.register_seller(
                    user_id=user_id,
                    platform=user_data.platform,
                    business_name=user_data.business_name,
                    email=user_data.email,
                    phone=user_data.phone
                )
            except Exception as e:
                self._log("seller_profile_creation_failed", {"user_id": user_id, "error": str(e)})
        
        self._log("user_registered", {"user_id": user_id, "email": user.email, "role": role.value})
        
        return UserResponse(**user.model_dump(exclude={"hashed_password"})), None
    
    def login(self, login_data: UserLogin) -> Tuple[Optional[Token], Optional[str]]:
        """
        Login user and return tokens.
        
        Returns:
            Tuple of (Token, error_message)
        """
        # Find user by email or username
        user = None
        for u in self._users.values():
            if u.email.lower() == login_data.email.lower() or u.username.lower() == login_data.email.lower():
                user = u
                break
        
        if not user:
            return None, "Invalid email or password"
        
        if not user.is_active:
            return None, "Account is deactivated"
        
        if not self._verify_password(login_data.password, user.hashed_password):
            self._log("login_failed", {"email": login_data.email, "reason": "invalid_password"})
            return None, "Invalid email or password"
        
        # Update last login
        user.last_login = datetime.now()
        self._save_users()
        
        # Create tokens
        access_token, access_expires = self._create_access_token(user)
        refresh_token, refresh_expires = self._create_refresh_token(user)
        
        # Store session
        session_id = secrets.token_hex(16)
        self._sessions[session_id] = {
            "user_id": user.id,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": datetime.now().isoformat(),
            "expires_at": access_expires.isoformat()
        }
        self._save_sessions()
        
        self._log("user_login", {"user_id": user.id, "email": user.email})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ), None
    
    def verify_token(self, token: str) -> Tuple[Optional[TokenPayload], Optional[str]]:
        """
        Verify JWT token.
        
        Returns:
            Tuple of (TokenPayload, error_message)
        """
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            token_payload = TokenPayload(
                sub=payload["sub"],
                email=payload["email"],
                username=payload["username"],
                role=payload["role"],
                exp=datetime.fromtimestamp(payload["exp"]),
                iat=datetime.fromtimestamp(payload["iat"]),
                type=payload.get("type", "access")
            )
            
            # Check if token is expired
            if token_payload.exp < datetime.utcnow():
                return None, "Token expired"
            
            return token_payload, None
            
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError as e:
            return None, f"Invalid token: {str(e)}"
    
    def refresh_tokens(self, refresh_token: str) -> Tuple[Optional[Token], Optional[str]]:
        """
        Refresh access token using refresh token.
        """
        payload, error = self.verify_token(refresh_token)
        
        if error:
            return None, error
        
        if payload.type != "refresh":
            return None, "Invalid token type"
        
        # Get user
        user = self._users.get(payload.sub)
        if not user:
            return None, "User not found"
        
        if not user.is_active:
            return None, "Account deactivated"
        
        # Create new tokens
        access_token, access_expires = self._create_access_token(user)
        new_refresh_token, refresh_expires = self._create_refresh_token(user)
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ), None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    def update_user(self, user_id: str, update_data: UserUpdate) -> Tuple[Optional[UserResponse], Optional[str]]:
        """Update user profile."""
        user = self._users.get(user_id)
        if not user:
            return None, "User not found"
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(user, key, value)
        
        user.updated_at = datetime.now()
        self._save_users()
        
        return UserResponse(**user.model_dump(exclude={"hashed_password"})), None
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """Change user password."""
        user = self._users.get(user_id)
        if not user:
            return False, "User not found"
        
        if not self._verify_password(current_password, user.hashed_password):
            return False, "Current password is incorrect"
        
        user.hashed_password = self._hash_password(new_password)
        user.updated_at = datetime.now()
        self._save_users()
        
        self._log("password_changed", {"user_id": user_id})
        
        return True, None
    
    def logout(self, token: str) -> bool:
        """Logout user (invalidate session)."""
        # Remove session with this token
        for session_id, session in list(self._sessions.items()):
            if session.get("access_token") == token:
                del self._sessions[session_id]
                self._save_sessions()
                return True
        return False
    
    def get_all_users(self) -> list:
        """Get all users (admin only)."""
        return [
            UserResponse(**user.model_dump(exclude={"hashed_password"}))
            for user in self._users.values()
        ]
    
    def _log(self, event_type: str, data: Dict = None, level: str = "INFO") -> None:
        """Log auth event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "service": "auth",
            "event_type": event_type,
            "data": data or {}
        }
        
        log_file = LOGS_DIR / f"auth-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass


# Singleton
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """Get singleton auth service."""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service

