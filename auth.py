import os
import jwt
import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db, User, UserProfile, OAuthSession
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_jwt_key_at_least_32_characters_long")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

# Google OAuth settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Security
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Get current user from JWT token"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

def create_user(db: Session, email: str, password: str = None, google_id: str = None, 
                auth_provider: str = "local", profile_data: dict = None) -> User:
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        user_data = {
            "id": str(uuid.uuid4()),
            "email": email,
            "auth_provider": auth_provider,
            "is_email_verified": auth_provider == "google"  # Google users are pre-verified
        }
        
        if password:
            user_data["password_hash"] = hash_password(password)
        
        if google_id:
            user_data["google_id"] = google_id
        
        user = User(**user_data)
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create user profile
        profile_data = profile_data or {}
        profile = UserProfile(
            user_id=user.id,
            display_name=profile_data.get("name", email.split("@")[0]),
            first_name=profile_data.get("given_name", ""),
            last_name=profile_data.get("family_name", ""),
            avatar_url=profile_data.get("picture", ""),
            google_profile_data=profile_data if auth_provider == "google" else None
        )
        db.add(profile)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ User created: {email}")
        return user
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.password_hash:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def setup_google_oauth():
    """Setup Google OAuth flow"""
    if not all([GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI]):
        logger.warning("⚠️ Google OAuth not configured - missing credentials")
        return None
    
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [GOOGLE_REDIRECT_URI]
                }
            },
            scopes=["openid", "email", "profile"]
        )
        flow.redirect_uri = GOOGLE_REDIRECT_URI
        return flow
    except Exception as e:
        logger.error(f"❌ Error setting up Google OAuth: {e}")
        return None

def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Google ID token"""
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        return idinfo
    except Exception as e:
        logger.error(f"❌ Google token verification failed: {e}")
        return None

def create_or_update_user_from_google(db: Session, google_data: Dict[str, Any]) -> User:
    """Create or update user from Google OAuth data"""
    try:
        email = google_data.get("email")
        google_id = google_data.get("sub")
        
        # Check if user exists
        user = db.query(User).filter(
            (User.email == email) | (User.google_id == google_id)
        ).first()
        
        if user:
            # Update existing user
            user.google_id = google_id
            user.is_email_verified = True
            
            # Update profile if it exists
            if user.profile:
                user.profile.google_profile_data = google_data
                user.profile.avatar_url = google_data.get("picture", user.profile.avatar_url)
            
            db.commit()
            db.refresh(user)
            logger.info(f"✅ User updated from Google: {email}")
            return user
        else:
            # Create new user
            return create_user(
                db=db,
                email=email,
                google_id=google_id,
                auth_provider="google",
                profile_data=google_data
            )
    
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating/updating user from Google: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process Google authentication"
        )

def require_auth(user: User = Depends(get_current_user)) -> User:
    """Dependency to require authentication"""
    return user

# API Token system (for MCP integration)
def generate_api_token() -> str:
    """Generate a secure API token"""
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    """Hash API token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

# Optional: Session-based authentication for web interface
def get_current_user_from_session(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from session (for web interface)"""
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user
    except Exception as e:
        logger.error(f"Session authentication error: {e}")
        return None