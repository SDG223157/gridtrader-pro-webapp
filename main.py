import os
import logging
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text, func, desc
from database import get_db, connect_with_retry, create_tables, User, UserProfile, Portfolio, Holding, Grid, MarketData, Alert
from auth import (
    create_access_token, get_current_user, require_auth, create_user, authenticate_user,
    setup_google_oauth, create_or_update_user_from_google, get_current_user_from_session
)
from data_provider import YFinanceDataProvider
from app.algorithms.grid_trading import GridTradingStrategy, DynamicGridStrategy, GridBacktester
import uuid
import httpx
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

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
    allow_origins=["*"],  # Configure this properly for production
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

# Initialize data provider
data_provider = YFinanceDataProvider()

# Pydantic models for API
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

class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    first_name: str = ""
    last_name: str = ""

class UserLoginRequest(BaseModel):
    email: str
    password: str

# Helper functions
def get_user_context(request: Request, db: Session) -> Dict:
    """Get user context for templates"""
    user = get_current_user_from_session(request, db)
    return {
        "user": user,
        "is_authenticated": user is not None
    }

def calculate_portfolio_summary(db: Session, user_id: str) -> Dict:
    """Calculate portfolio summary for user"""
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    
    total_value = sum(p.current_value or 0 for p in portfolios)
    total_invested = sum(p.initial_capital or 0 for p in portfolios)
    total_return = ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "total_portfolios": len(portfolios),
        "total_value": total_value,
        "total_invested": total_invested,
        "total_return": round(total_return, 2),
        "active_grids": db.query(Grid).join(Portfolio).filter(Portfolio.user_id == user_id, Grid.status == "active").count()
    }

# Routes

# Homepage
@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    return templates.TemplateResponse("index.html", {"request": request, **context})

# Authentication Routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if context["is_authenticated"]:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, **context})

@app.post("/api/auth/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, email, password)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid email or password")
        
        # Set session
        request.session["user_id"] = user.id
        
        # Create JWT token for API access
        access_token = create_access_token(data={"sub": user.id})
        
        return JSONResponse({
            "success": True,
            "message": "Login successful",
            "access_token": access_token,
            "redirect_url": "/dashboard"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if context["is_authenticated"]:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("register.html", {"request": request, **context})

@app.post("/api/auth/register")
async def register(request: Request, email: str = Form(...), password: str = Form(...), 
                  first_name: str = Form(""), last_name: str = Form(""), db: Session = Depends(get_db)):
    try:
        user = create_user(db, email, password, profile_data={
            "given_name": first_name,
            "family_name": last_name,
            "name": f"{first_name} {last_name}".strip()
        })
        
        # Set session
        request.session["user_id"] = user.id
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.id})
        
        return JSONResponse({
            "success": True,
            "message": "Registration successful",
            "access_token": access_token,
            "redirect_url": "/dashboard"
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/logout")
async def logout_post(request: Request):
    """POST logout route"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/logout")
async def logout_get(request: Request):
    """GET logout route for convenience"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

@app.get("/api/auth/logout")
async def logout_api(request: Request):
    """API logout route"""
    request.session.clear()
    return JSONResponse({"success": True, "message": "Logged out successfully", "redirect_url": "/"})

# Google OAuth routes
@app.get("/api/auth/google")
async def google_auth():
    flow = setup_google_oauth()
    if not flow:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return RedirectResponse(authorization_url)

@app.get("/api/auth/google/callback")
async def google_callback(request: Request, code: str, db: Session = Depends(get_db)):
    try:
        flow = setup_google_oauth()
        if not flow:
            raise HTTPException(status_code=500, detail="Google OAuth not configured")
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Get user info from Google
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={credentials.token}"
            )
            google_data = response.json()
        
        # Create or update user
        user = create_or_update_user_from_google(db, google_data)
        
        # Set session
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
    
    # Get portfolio summary
    portfolio_summary = calculate_portfolio_summary(db, context["user"].id)
    
    # Get recent alerts
    recent_alerts = db.query(Alert).filter(
        Alert.user_id == context["user"].id
    ).order_by(desc(Alert.created_at)).limit(5).all()
    
    # Get market data for popular symbols
    popular_symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT']
    market_data = {}
    for symbol in popular_symbols:
        price = data_provider.get_current_price(symbol)
        if price:
            market_data[symbol] = price
    
    context.update({
        "portfolio_summary": portfolio_summary,
        "recent_alerts": recent_alerts,
        "market_data": market_data
    })
    
    return templates.TemplateResponse("dashboard.html", {"request": request, **context})

# Portfolios
@app.get("/portfolios", response_class=HTMLResponse)
async def portfolios_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == context["user"].id).all()
    
    # Calculate performance for each portfolio
    for portfolio in portfolios:
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if holdings:
            holdings_data = [{
                'symbol': h.symbol,
                'quantity': float(h.quantity),
                'average_cost': float(h.average_cost)
            } for h in holdings]
            
            performance = data_provider.get_portfolio_performance(holdings_data)
            portfolio.performance = performance
        else:
            portfolio.performance = {
                'total_value': float(portfolio.current_value or 0),
                'total_cost': float(portfolio.initial_capital),
                'total_pnl': 0,
                'total_pnl_percent': 0,
                'day_change': 0,
                'day_change_percent': 0
            }
    
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

# Grid Trading
@app.get("/grids", response_class=HTMLResponse)
async def grids_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    grids = db.query(Grid).join(Portfolio).filter(Portfolio.user_id == context["user"].id).all()
    
    # Get current prices for grid symbols
    for grid in grids:
        current_price = data_provider.get_current_price(grid.symbol)
        grid.current_price = current_price
        
        # Calculate grid performance
        if current_price:
            grid.price_position = "in_range"
            if current_price > grid.upper_price:
                grid.price_position = "above_range"
            elif current_price < grid.lower_price:
                grid.price_position = "below_range"
    
    context["grids"] = grids
    return templates.TemplateResponse("grids.html", {"request": request, **context})

@app.get("/grids/create", response_class=HTMLResponse)
async def create_grid_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get user's portfolios
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
        
        # Validate symbol
        if not data_provider.validate_symbol(request.symbol):
            raise HTTPException(status_code=400, detail="Invalid symbol")
        
        # Create grid strategy
        strategy = GridTradingStrategy(
            symbol=request.symbol,
            upper_price=request.upper_price,
            lower_price=request.lower_price,
            grid_count=request.grid_count,
            investment_amount=request.investment_amount
        )
        
        # Create grid record
        grid = Grid(
            portfolio_id=request.portfolio_id,
            symbol=request.symbol,
            name=request.name,
            strategy_config=strategy.get_strategy_metrics(),
            upper_price=request.upper_price,
            lower_price=request.lower_price,
            grid_spacing=strategy.grid_spacing,
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

# Market Data API
@app.get("/api/market/{symbol}")
async def get_market_data(symbol: str, period: str = "1d"):
    try:
        if period == "current":
            price = data_provider.get_current_price(symbol)
            return {"symbol": symbol, "price": price}
        else:
            data = data_provider.get_historical_data(symbol, period=period)
            if data is None:
                raise HTTPException(status_code=404, detail="Symbol not found")
            
            return {
                "symbol": symbol,
                "period": period,
                "data": data.to_dict('records')
            }
    except Exception as e:
        logger.error(f"Error fetching market data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")

@app.get("/api/search/symbols")
async def search_symbols(q: str):
    try:
        results = data_provider.search_symbols(q)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching symbols: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

# Analytics
@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("analytics.html", {"request": request, **context})

# Settings
@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, db: Session = Depends(get_db)):
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("settings.html", {"request": request, **context})

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Debug endpoints for authentication issues
@app.get("/debug/db-test")
async def debug_database(db: Session = Depends(get_db)):
    """Debug database connectivity"""
    try:
        result = db.execute(text("SELECT 1 as test")).fetchone()
        user_count = db.query(User).count()
        return {
            "database": "✅ Connected", 
            "test_query": result[0],
            "user_count": user_count,
            "tables_check": "OK"
        }
    except Exception as e:
        return {"database": "❌ Error", "error": str(e)}

@app.get("/debug/env-test")
async def debug_environment():
    """Debug environment variables"""
    return {
        "DB_HOST": os.getenv("DB_HOST", "Not set"),
        "DB_USER": os.getenv("DB_USER", "Not set"), 
        "DB_NAME": os.getenv("DB_NAME", "Not set"),
        "GOOGLE_CLIENT_ID": "Set" if os.getenv("GOOGLE_CLIENT_ID") else "Not set",
        "GOOGLE_CLIENT_SECRET": "Set" if os.getenv("GOOGLE_CLIENT_SECRET") else "Not set",
        "SECRET_KEY": "Set" if os.getenv("SECRET_KEY") else "Not set",
        "ENVIRONMENT": os.getenv("ENVIRONMENT", "Not set"),
        "PORT": os.getenv("PORT", "Not set")
    }

@app.get("/debug/session-test")
async def debug_session(request: Request, db: Session = Depends(get_db)):
    """Debug session and authentication status"""
    try:
        user_id = request.session.get("user_id")
        user = None
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
        
        return {
            "session_user_id": user_id,
            "user_found": user is not None,
            "user_email": user.email if user else None,
            "session_keys": list(request.session.keys()),
            "is_authenticated": user is not None
        }
    except Exception as e:
        return {"session_debug": "❌ Error", "error": str(e)}

@app.get("/debug/create-test-user")
async def debug_create_user(db: Session = Depends(get_db)):
    """Debug user creation"""
    try:
        test_email = "debug@test.com"
        
        # Remove existing test user if present
        existing = db.query(User).filter(User.email == test_email).first()
        if existing:
            # Delete profile first due to foreign key constraint
            profile = db.query(UserProfile).filter(UserProfile.user_id == existing.id).first()
            if profile:
                db.delete(profile)
            db.delete(existing)
            db.commit()
        
        # Try to create user manually with explicit ID generation
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        user_data = {
            "email": test_email,
            "password_hash": pwd_context.hash("testpass123"),
            "auth_provider": "local",
            "is_email_verified": False
        }
        
        user = User(**user_data)
        db.add(user)
        db.flush()  # Get the user ID (should work now with fixed UUID generation)
        
        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            display_name="Debug User",
            first_name="Debug",
            last_name="User"
        )
        db.add(profile)
        db.commit()
        db.refresh(user)
        
        return {
            "user_creation": "✅ Success",
            "user_id": user.id,
            "email": user.email,
            "method": "direct_database"
        }
        
    except Exception as e:
        db.rollback()
        import traceback
        return {
            "user_creation": "❌ Raw Error", 
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database connection and tables on startup"""
    logger.info("🚀 Starting GridTrader Pro...")
    # Skip database initialization since it's already done by init_database.py
    # This prevents startup crashes due to database connection issues
    logger.info("✅ GridTrader Pro startup completed")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 3000))
    host = os.getenv('HOSTNAME', '0.0.0.0')
    logger.info(f"🌐 Starting server on {host}:{port}")
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )