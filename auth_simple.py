"""
Simple authentication module following prombank_backup pattern
"""
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database import get_db, User, UserProfile
import httpx
import secrets
import hashlib
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# OAuth Configuration
oauth = OAuth()

def setup_oauth():
    """Setup Google OAuth client following prombank pattern"""
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not google_client_id or not google_client_secret:
        print("⚠️ Google OAuth credentials not found in environment variables")
        return None
    
    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        authorization_endpoint='https://accounts.google.com/o/oauth2/auth',
        token_endpoint='https://oauth2.googleapis.com/token',
        userinfo_endpoint='https://www.googleapis.com/oauth2/v2/userinfo',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    return oauth.google

def hash_password(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from session - simple and reliable"""
    user_id = request.session.get('user_id')
    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        return user
    return None

def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    """Require authentication, raise 401 if not authenticated"""
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

def create_user(db: Session, email: str, password: str = None, profile_data: dict = None) -> User:
    """Create new user - simplified version"""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create user
        user_data = {
            "email": email,
            "auth_provider": "local" if password else "google",
            "is_email_verified": not password  # Google users are pre-verified
        }
        
        if password:
            user_data["password_hash"] = hash_password(password)
        
        user = User(**user_data)
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create profile
        profile_data = profile_data or {}
        profile = UserProfile(
            user_id=user.id,
            display_name=profile_data.get("name", email.split("@")[0]),
            first_name=profile_data.get("given_name", ""),
            last_name=profile_data.get("family_name", ""),
            avatar_url=profile_data.get("picture", "")
        )
        db.add(profile)
        db.commit()
        db.refresh(user)
        
        return user
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create user")

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash:
        return None
    
    if verify_password(password, user.password_hash):
        return user
    return None

async def create_or_update_user_from_google(google_user_info: dict, db: Session) -> User:
    """Create or update user from Google OAuth info - following prombank pattern"""
    google_id = google_user_info.get('sub')
    email = google_user_info.get('email')
    first_name = google_user_info.get('given_name', '')
    last_name = google_user_info.get('family_name', '')
    profile_picture = google_user_info.get('picture', '')
    
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.google_id == google_id) | (User.email == email)
    ).first()
    
    if existing_user:
        # Update existing user
        existing_user.google_id = google_id
        if existing_user.profile:
            existing_user.profile.first_name = first_name
            existing_user.profile.last_name = last_name
            existing_user.profile.avatar_url = profile_picture
        existing_user.auth_provider = "google"
        db.commit()
        db.refresh(existing_user)
        return existing_user
    else:
        # Create new user
        return create_user(db, email, profile_data={
            "given_name": first_name,
            "family_name": last_name,
            "name": f"{first_name} {last_name}".strip(),
            "picture": profile_picture
        })
