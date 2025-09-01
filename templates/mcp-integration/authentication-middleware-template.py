"""
Universal Authentication Middleware Template for MCP Integration
Copy this middleware to any FastAPI application for Bearer token support
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Universal Authentication Middleware (Use as-is for any app)
@app.middleware("http")
async def api_auth_middleware(request: Request, call_next):
    """
    Universal authentication middleware for API endpoints with Bearer token support
    
    Supports both:
    - Session-based authentication (web interface)
    - Bearer token authentication (MCP/API clients)
    
    Customize the skip_auth_paths for your application
    """
    
    # Skip authentication for these paths (customize for your app)
    skip_auth_paths = [
        "/api/auth/",           # Authentication endpoints
        "/health",              # Health checks
        "/debug/",              # Debug endpoints  
        "/docs",                # API documentation
        "/openapi.json",        # OpenAPI spec
        "/static/",             # Static files
        "/favicon.ico",         # Favicon
        "/robots.txt",          # SEO files
        # Add your app-specific public endpoints
    ]
    
    # Only apply to API endpoints
    if request.url.path.startswith("/api/") and not any(request.url.path.startswith(path) for path in skip_auth_paths):
        auth_header = request.headers.get("authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            # API Token Authentication
            token = auth_header.replace("Bearer ", "")
            
            # Create new database session for middleware
            db = SessionLocal()
            try:
                # Look up API token in database
                api_token = db.query(ApiToken).filter(
                    ApiToken.token == token,
                    ApiToken.is_active == True
                ).first()
                
                if api_token:
                    # Check if token is expired
                    if api_token.expires_at and datetime.utcnow() > api_token.expires_at:
                        return JSONResponse({"error": "Token expired"}, status_code=401)
                    
                    # Update last used timestamp
                    api_token.last_used_at = datetime.utcnow()
                    db.commit()
                    
                    # Get user and store in request state
                    user = db.query(User).filter(User.id == api_token.user_id).first()
                    if user:
                        request.state.user = user
                        logger.info(f"✅ API token authentication successful for user: {user.email}")
                    else:
                        logger.error("❌ User not found for valid API token")
                        return JSONResponse({"error": "User not found"}, status_code=401)
                else:
                    logger.error(f"❌ Invalid API token: {token[:10]}...")
                    return JSONResponse({"error": "Invalid API token"}, status_code=401)
            except Exception as e:
                logger.error(f"❌ API token authentication error: {e}")
                return JSONResponse({"error": "Authentication failed"}, status_code=401)
            finally:
                db.close()
        else:
            # Session-based Authentication (for web interface)
            user_id = request.session.get("user_id")
            if user_id:
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        request.state.user = user
                    else:
                        return JSONResponse({"error": "Session invalid"}, status_code=401)
                finally:
                    db.close()
            else:
                return JSONResponse({"error": "Authorization header required"}, status_code=401)
    
    response = await call_next(request)
    return response

# Enhanced require_auth function (Universal - use as-is)
def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Universal authentication function supporting both session and API tokens
    
    Works with the middleware above to provide seamless authentication
    for both web interface and MCP/API clients
    """
    # First check if user is set by API token middleware
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user
    
    # Fallback to session-based authentication (for web interface)
    user = get_current_user(request, db)  # Your existing session auth function
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

# Token generation utility (Universal - use as-is)
def generate_secure_token():
    """Generate a secure random token for API access"""
    import secrets
    return secrets.token_urlsafe(32)

# Example usage in your endpoints:
"""
@app.get("/api/your-data")
async def get_your_data(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    # This endpoint now works with both session auth and API tokens!
    # The middleware handles the authentication automatically
    
    data = db.query(YourModel).filter(YourModel.user_id == user.id).all()
    return {"data": data}
"""
