"""
Simplified GridTrader Pro following prombank_backup authentication pattern
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from database import get_db, User, UserProfile, Portfolio, Grid, Holding, Alert
from auth_simple import (
    setup_oauth, create_access_token, get_current_user, require_auth, 
    create_user, authenticate_user, create_or_update_user_from_google
)
import httpx
from datetime import datetime
from typing import List
from pydantic import BaseModel

# Pydantic models for API requests
class CreatePortfolioRequest(BaseModel):
    name: str
    description: str = ""
    strategy_type: str = "balanced"
    initial_capital: float

class CreateGridRequest(BaseModel):
    portfolio_id: str
    symbol: str
    name: str
    upper_price: float
    lower_price: float
    grid_count: int = 10
    investment_amount: float

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GridTrader Pro",
    description="Systematic Investment Management Platform",
    version="1.0.0"
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your_super_secret_key_change_this_in_production"),
    max_age=86400  # 24 hours
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = "static"
if not Path(static_dir).exists():
    Path(static_dir).mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

def get_user_context(request: Request, db: Session) -> dict:
    """Get user context for templates"""
    user = get_current_user(request, db)
    return {
        "user": user,
        "is_authenticated": user is not None
    }

# Routes following prombank_backup pattern

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if context["is_authenticated"]:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("index.html", {"request": request, **context})

# Authentication Routes - Simplified following prombank pattern

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if context["is_authenticated"]:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, **context})

@app.post("/auth/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, email, password)
        if not user:
            return JSONResponse({"success": False, "detail": "Invalid email or password"}, status_code=400)
        
        # Set session - simple and reliable
        request.session["user_id"] = user.id
        
        return JSONResponse({
            "success": True,
            "message": "Login successful",
            "redirect_url": "/dashboard"
        })
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JSONResponse({"success": False, "detail": "Login failed"}, status_code=500)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if context["is_authenticated"]:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, **context})

@app.post("/auth/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...), 
                  first_name: str = Form(""), last_name: str = Form(""), db: Session = Depends(get_db)):
    try:
        user = create_user(db, email, password, profile_data={
            "given_name": first_name,
            "family_name": last_name,
            "name": f"{first_name} {last_name}".strip()
        })
        
        # Set session - simple and reliable
        request.session["user_id"] = user.id
        
        return JSONResponse({
            "success": True,
            "message": "Registration successful",
            "redirect_url": "/dashboard"
        })
    except HTTPException as he:
        return JSONResponse({"success": False, "detail": he.detail}, status_code=he.status_code)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return JSONResponse({"success": False, "detail": "Registration failed"}, status_code=500)

# Simple logout routes following prombank pattern
@app.get("/logout")
async def logout_get(request: Request):
    """Simple GET logout - following prombank pattern"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.post("/logout")
async def logout_post(request: Request):
    """POST logout for forms"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/auth/logout")
async def logout_api(request: Request):
    """API logout endpoint"""
    request.session.clear()
    return JSONResponse({"success": True, "message": "Logged out successfully"})

# Google OAuth routes - following prombank pattern
@app.get("/api/auth/google")
async def google_auth(request: Request):
    """Initiate Google OAuth"""
    google_client = setup_oauth()
    if not google_client:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    redirect_uri = f"{os.getenv('FRONTEND_URL', 'https://gridsai.app')}/api/auth/google/callback"
    return await google_client.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        google_client = setup_oauth()
        if not google_client:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        # Get token from Google
        token = await google_client.authorize_access_token(request)
        
        # Get user info
        user_info = token.get('userinfo')
        if not user_info:
            # Fetch user info manually
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {token["access_token"]}'}
                )
                user_info = response.json()
        
        # Create or update user
        user = await create_or_update_user_from_google(user_info, db)
        
        # Set session - simple and reliable
        request.session["user_id"] = user.id
        
        return RedirectResponse(url="/dashboard", status_code=302)
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        return RedirectResponse(url="/login?error=oauth_failed", status_code=302)

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Simple dashboard data
    context.update({
        "portfolio_summary": {
            "total_portfolios": 0,
            "total_value": 0.00,
            "total_invested": 0.00,
            "total_return": 0.00,
            "active_grids": 0
        },
        "recent_alerts": [],
        "market_data": {}
    })
    
    return templates.TemplateResponse("dashboard.html", {"request": request, **context})

# Portfolio Management Routes
@app.get("/portfolios", response_class=HTMLResponse)
async def portfolios_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == context["user"].id).all()
    context["portfolios"] = portfolios
    return templates.TemplateResponse("portfolios.html", {"request": request, **context})

@app.get("/portfolios/create", response_class=HTMLResponse)
async def create_portfolio_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("create_portfolio.html", {"request": request, **context})

@app.post("/api/portfolios")
async def create_portfolio(request: CreatePortfolioRequest, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        portfolio = Portfolio(
            user_id=user.id,
            name=request.name,
            description=request.description,
            strategy_type=request.strategy_type,
            initial_capital=request.initial_capital,
            current_value=request.initial_capital,
            cash_balance=request.initial_capital
        )
        
        db.add(portfolio)
        db.commit()
        db.refresh(portfolio)
        
        logger.info(f"Portfolio created: {portfolio.name} for user {user.email}")
        return {"success": True, "portfolio_id": portfolio.id, "message": "Portfolio created successfully"}
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to create portfolio")

# Grid Trading Routes
@app.get("/grids", response_class=HTMLResponse)
async def grids_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    grids = db.query(Grid).join(Portfolio).filter(Portfolio.user_id == context["user"].id).all()
    context["grids"] = grids
    return templates.TemplateResponse("grids.html", {"request": request, **context})

@app.get("/grids/create", response_class=HTMLResponse)
async def create_grid_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == context["user"].id).all()
    context["portfolios"] = portfolios
    return templates.TemplateResponse("create_grid.html", {"request": request, **context})

@app.post("/api/grids")
async def create_grid(request: CreateGridRequest, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        # Verify portfolio ownership
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == request.portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Create grid
        grid = Grid(
            portfolio_id=request.portfolio_id,
            symbol=request.symbol,
            name=request.name,
            upper_price=request.upper_price,
            lower_price=request.lower_price,
            grid_spacing=(request.upper_price - request.lower_price) / request.grid_count,
            investment_amount=request.investment_amount
        )
        
        db.add(grid)
        db.commit()
        db.refresh(grid)
        
        logger.info(f"Grid created: {grid.name} for {request.symbol}")
        return {"success": True, "grid_id": grid.id, "message": "Grid created successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating grid: {e}")
        raise HTTPException(status_code=500, detail="Failed to create grid")

# Analytics Route
@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("analytics.html", {"request": request, **context})

# Market Data API for charts
@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str, period: str = "1d"):
    """Simple market data endpoint"""
    try:
        # Mock data for now - can be enhanced with real yfinance integration
        mock_data = {
            "symbol": symbol,
            "period": period,
            "data": [
                {"date": "2025-01-01", "open": 150.0, "high": 155.0, "low": 148.0, "close": 153.0, "volume": 1000000},
                {"date": "2025-01-02", "open": 153.0, "high": 158.0, "low": 151.0, "close": 156.0, "volume": 1200000},
                {"date": "2025-01-03", "open": 156.0, "high": 160.0, "low": 154.0, "close": 159.0, "volume": 900000}
            ]
        }
        return mock_data
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug/port-info")
async def port_info():
    """Debug port configuration"""
    return {
        "PORT_env": os.getenv('PORT', 'Not set'),
        "APP_PORT_env": os.getenv('APP_PORT', 'Not set'),
        "HOST_env": os.getenv('HOST', 'Not set'),
        "HOSTNAME_env": os.getenv('HOSTNAME', 'Not set'),
        "actual_port_used": 3000,
        "message": "GridTrader Pro Simple is running!"
    }

@app.get("/debug/oauth-info")
async def oauth_info():
    """Debug Google OAuth configuration"""
    from auth_simple import setup_oauth
    
    google_client = setup_oauth()
    return {
        "google_client_configured": google_client is not None,
        "GOOGLE_CLIENT_ID": "Set" if os.getenv('GOOGLE_CLIENT_ID') else "Not set",
        "GOOGLE_CLIENT_SECRET": "Set" if os.getenv('GOOGLE_CLIENT_SECRET') else "Not set",
        "FRONTEND_URL": os.getenv('FRONTEND_URL', 'Not set'),
        "expected_redirect_uri": f"{os.getenv('FRONTEND_URL', 'https://gridsai.app')}/api/auth/google/callback",
        "oauth_client_type": str(type(google_client)) if google_client else "None"
    }

# Simple startup
@app.on_event("startup")
async def startup_event():
    """Simple startup without database operations"""
    logger.info("🚀 Starting GridTrader Pro...")
    logger.info("✅ GridTrader Pro startup completed")

if __name__ == "__main__":
    import uvicorn
    # Force port 3000 to match Coolify configuration
    port = 3000  # Always use 3000 as configured in Coolify
    host = os.getenv('HOST', os.getenv('HOSTNAME', '0.0.0.0'))
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    logger.info(f"🔧 Environment PORT: {os.getenv('PORT', 'Not set')}")
    logger.info(f"🔧 Environment HOST: {os.getenv('HOST', 'Not set')}")
    
    uvicorn.run(
        "main_simple:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )
