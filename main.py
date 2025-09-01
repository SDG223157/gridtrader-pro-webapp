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
from database import get_db, connect_with_retry, create_tables, User, UserProfile, Portfolio, Holding, Grid, MarketData, Alert, ApiToken
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
import secrets
import hashlib

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

class CreateApiTokenRequest(BaseModel):
    name: str
    description: str = ""
    permissions: List[str] = ["read", "write"]
    expires_in_days: Optional[int] = None  # None means no expiration

class UpdateApiTokenRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

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

# MCP API Endpoints for external access
@app.get("/api/portfolios")
async def api_get_portfolios(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        
        # Calculate performance for each portfolio
        portfolio_list = []
        for portfolio in portfolios:
            holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
            
            portfolio_dict = {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "strategy_type": portfolio.strategy_type,
                "initial_capital": float(portfolio.initial_capital),
                "current_value": float(portfolio.current_value or 0),
                "cash_balance": float(portfolio.cash_balance or 0),
                "created_at": portfolio.created_at.isoformat(),
                "updated_at": portfolio.updated_at.isoformat()
            }
            
            if holdings:
                holdings_data = [{
                    'symbol': h.symbol,
                    'quantity': float(h.quantity),
                    'average_cost': float(h.average_cost)
                } for h in holdings]
                
                performance = data_provider.get_portfolio_performance(holdings_data)
                portfolio_dict["performance"] = performance
            
            portfolio_list.append(portfolio_dict)
        
        return {"portfolios": portfolio_list}
    
    except Exception as e:
        logger.error(f"Error fetching portfolios: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolios")

@app.get("/api/portfolios/{portfolio_id}")
async def api_get_portfolio_details(portfolio_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return {
            "id": portfolio.id,
            "name": portfolio.name,
            "description": portfolio.description,
            "strategy_type": portfolio.strategy_type,
            "initial_capital": float(portfolio.initial_capital),
            "current_value": float(portfolio.current_value or 0),
            "cash_balance": float(portfolio.cash_balance or 0),
            "created_at": portfolio.created_at.isoformat(),
            "updated_at": portfolio.updated_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio details")

@app.get("/api/grids")
async def api_get_grids(portfolio_id: str = None, symbol: str = None, status: str = None, 
                       user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        query = db.query(Grid).join(Portfolio).filter(Portfolio.user_id == user.id)
        
        if portfolio_id:
            query = query.filter(Grid.portfolio_id == portfolio_id)
        if symbol:
            query = query.filter(Grid.symbol == symbol)
        if status:
            query = query.filter(Grid.status == status)
        
        grids = query.all()
        
        grid_list = []
        for grid in grids:
            # Get current price
            current_price = data_provider.get_current_price(grid.symbol)
            
            grid_dict = {
                "id": grid.id,
                "portfolio_id": grid.portfolio_id,
                "symbol": grid.symbol,
                "name": grid.name,
                "upper_price": float(grid.upper_price),
                "lower_price": float(grid.lower_price),
                "grid_spacing": float(grid.grid_spacing),
                "investment_amount": float(grid.investment_amount),
                "status": grid.status,
                "current_price": current_price,
                "created_at": grid.created_at.isoformat(),
                "updated_at": grid.updated_at.isoformat()
            }
            
            # Calculate price position
            if current_price:
                if current_price > grid.upper_price:
                    grid_dict["price_position"] = "above_range"
                elif current_price < grid.lower_price:
                    grid_dict["price_position"] = "below_range"
                else:
                    grid_dict["price_position"] = "in_range"
            
            grid_list.append(grid_dict)
        
        return {"grids": grid_list}
    
    except Exception as e:
        logger.error(f"Error fetching grids: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch grids")

@app.get("/api/grids/{grid_id}")
async def api_get_grid_details(grid_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        grid = db.query(Grid).join(Portfolio).filter(
            Grid.id == grid_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not grid:
            raise HTTPException(status_code=404, detail="Grid not found")
        
        # Get current price
        current_price = data_provider.get_current_price(grid.symbol)
        
        grid_dict = {
            "id": grid.id,
            "portfolio_id": grid.portfolio_id,
            "symbol": grid.symbol,
            "name": grid.name,
            "upper_price": float(grid.upper_price),
            "lower_price": float(grid.lower_price),
            "grid_spacing": float(grid.grid_spacing),
            "investment_amount": float(grid.investment_amount),
            "status": grid.status,
            "current_price": current_price,
            "created_at": grid.created_at.isoformat(),
            "updated_at": grid.updated_at.isoformat()
        }
        
        # Calculate price position
        if current_price:
            if current_price > grid.upper_price:
                grid_dict["price_position"] = "above_range"
            elif current_price < grid.lower_price:
                grid_dict["price_position"] = "below_range"
            else:
                grid_dict["price_position"] = "in_range"
        
        return grid_dict
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching grid details: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch grid details")

@app.get("/api/alerts")
async def api_get_alerts(limit: int = 10, alert_type: str = None, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        query = db.query(Alert).filter(Alert.user_id == user.id)
        
        if alert_type:
            query = query.filter(Alert.alert_type == alert_type)
        
        alerts = query.order_by(desc(Alert.created_at)).limit(limit).all()
        
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "id": alert.id,
                "type": alert.alert_type,
                "message": alert.message,
                "created_at": alert.created_at.isoformat()
            })
        
        return {"alerts": alert_list}
    
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@app.get("/api/portfolios/{portfolio_id}/metrics")
async def api_get_portfolio_metrics(portfolio_id: str, period: str = "1m", 
                                  user: User = Depends(require_auth), db: Session = Depends(get_db)):
    try:
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get holdings for performance calculation
        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        
        if not holdings:
            return {
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "volatility": 0,
                "period": period
            }
        
        holdings_data = [{
            'symbol': h.symbol,
            'quantity': float(h.quantity),
            'average_cost': float(h.average_cost)
        } for h in holdings]
        
        performance = data_provider.get_portfolio_performance(holdings_data)
        
        # Calculate additional metrics (simplified)
        total_return = performance.get('total_pnl_percent', 0)
        
        return {
            "total_return": total_return,
            "sharpe_ratio": max(0, total_return / 10) if total_return > 0 else 0,  # Simplified
            "max_drawdown": min(0, total_return * 0.3),  # Simplified
            "volatility": abs(total_return * 0.2),  # Simplified
            "period": period
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating portfolio metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate metrics")

# Authentication middleware for API endpoints
@app.middleware("http")
async def api_auth_middleware(request: Request, call_next):
    """Authentication middleware for API endpoints"""
    # Skip authentication for certain endpoints
    skip_auth_paths = [
        "/api/auth/login", "/api/auth/register", "/api/auth/google", "/api/auth/google/callback"
    ]
    
    if request.url.path.startswith("/api/") and request.url.path not in skip_auth_paths:
        auth_header = request.headers.get("authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            # Try to find API token in database
            db = SessionLocal()
            try:
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
                    
                    # Get user
                    user = db.query(User).filter(User.id == api_token.user_id).first()
                    if user:
                        request.state.user = user
                        request.state.api_token = api_token
                    else:
                        return JSONResponse({"error": "User not found"}, status_code=401)
                else:
                    # Fallback: try development token
                    if token == "gridtrader_dev_token_123":
                        # Create a mock user for development
                        request.state.user = type('User', (), {
                            'id': 'dev_user_123',
                            'email': 'dev@gridtrader.com'
                        })()
                    else:
                        # Try JWT token validation (existing implementation)
                        try:
                            from jose import jwt, JWTError
                            payload = jwt.decode(token, os.getenv("SECRET_KEY", "your_super_secret_key_change_this_in_production"), algorithms=["HS256"])
                            user_id = payload.get("sub")
                            if user_id:
                                user = db.query(User).filter(User.id == user_id).first()
                                if user:
                                    request.state.user = user
                                else:
                                    return JSONResponse({"error": "User not found"}, status_code=401)
                            else:
                                return JSONResponse({"error": "Invalid token"}, status_code=401)
                        except:
                            return JSONResponse({"error": "Invalid token"}, status_code=401)
            finally:
                db.close()
        else:
            return JSONResponse({"error": "Authorization header required"}, status_code=401)
    
    response = await call_next(request)
    return response

# API Token Management Endpoints
def generate_secure_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)

@app.get("/tokens", response_class=HTMLResponse)
async def tokens_page(request: Request, db: Session = Depends(get_db)):
    """Token management page"""
    context = get_user_context(request, db)
    if not context["is_authenticated"]:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get user's tokens
    tokens = db.query(ApiToken).filter(ApiToken.user_id == context["user"].id).all()
    context["tokens"] = tokens
    
    return templates.TemplateResponse("tokens.html", {"request": request, **context})

@app.post("/api/tokens")
async def create_api_token(request: CreateApiTokenRequest, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Create a new API token"""
    try:
        # Generate secure token
        token = generate_secure_token()
        
        # Calculate expiration date
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
        # Create token record
        api_token = ApiToken(
            user_id=user.id,
            name=request.name,
            description=request.description,
            token=token,
            permissions=request.permissions,
            expires_at=expires_at
        )
        
        db.add(api_token)
        db.commit()
        db.refresh(api_token)
        
        # Generate MCP configuration
        mcp_config = {
            "mcpServers": {
                "gridtrader-pro": {
                    "command": "gridtrader-pro-mcp",
                    "env": {
                        "GRIDTRADER_API_URL": f"{os.getenv('FRONTEND_URL', 'https://gridsai.app')}",
                        "GRIDTRADER_ACCESS_TOKEN": token
                    }
                }
            }
        }
        
        # Installation command
        install_command = "curl -fsSL https://raw.githubusercontent.com/SDG223157/gridtrader-pro-webapp/main/install-mcp.sh | bash"
        
        logger.info(f"API token created: {api_token.name} for user {user.email}")
        
        return {
            "success": True,
            "message": "API token created successfully. Save this token - it won't be shown again!",
            "token": {
                "id": api_token.id,
                "name": api_token.name,
                "description": api_token.description,
                "token": token,  # Only shown once
                "permissions": api_token.permissions,
                "expires_at": api_token.expires_at.isoformat() if api_token.expires_at else None,
                "created_at": api_token.created_at.isoformat()
            },
            "mcp_config": mcp_config,
            "installation_command": install_command
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating API token: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API token")

@app.get("/api/tokens")
async def get_api_tokens(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get user's API tokens (without token values)"""
    try:
        tokens = db.query(ApiToken).filter(ApiToken.user_id == user.id).all()
        
        token_list = []
        for token in tokens:
            token_list.append({
                "id": token.id,
                "name": token.name,
                "description": token.description,
                "permissions": token.permissions,
                "is_active": token.is_active,
                "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
                "created_at": token.created_at.isoformat(),
                "updated_at": token.updated_at.isoformat()
            })
        
        return {"tokens": token_list}
    
    except Exception as e:
        logger.error(f"Error fetching API tokens: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch API tokens")

@app.get("/api/tokens/{token_id}/mcp-config")
async def get_token_mcp_config(token_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get MCP configuration for a specific token"""
    try:
        token = db.query(ApiToken).filter(
            ApiToken.id == token_id,
            ApiToken.user_id == user.id
        ).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        # Generate MCP configuration template (without actual token)
        mcp_config = {
            "mcpServers": {
                "gridtrader-pro": {
                    "command": "gridtrader-pro-mcp",
                    "env": {
                        "GRIDTRADER_API_URL": f"{os.getenv('FRONTEND_URL', 'https://gridsai.app')}",
                        "GRIDTRADER_ACCESS_TOKEN": "YOUR_API_TOKEN_HERE"
                    }
                }
            }
        }
        
        return {
            "token_name": token.name,
            "token_id": token.id,
            "mcp_config": mcp_config,
            "installation_command": "curl -fsSL https://raw.githubusercontent.com/SDG223157/gridtrader-pro-webapp/main/install-mcp.sh | bash",
            "note": "Replace 'YOUR_API_TOKEN_HERE' with your actual API token"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting MCP config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get MCP configuration")

@app.put("/api/tokens/{token_id}")
async def update_api_token(token_id: str, request: UpdateApiTokenRequest, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Update an API token"""
    try:
        token = db.query(ApiToken).filter(
            ApiToken.id == token_id,
            ApiToken.user_id == user.id
        ).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        # Update fields
        if request.name is not None:
            token.name = request.name
        if request.description is not None:
            token.description = request.description
        if request.is_active is not None:
            token.is_active = request.is_active
        
        db.commit()
        db.refresh(token)
        
        return {
            "success": True,
            "message": "Token updated successfully",
            "token": {
                "id": token.id,
                "name": token.name,
                "description": token.description,
                "is_active": token.is_active,
                "updated_at": token.updated_at.isoformat()
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating API token: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API token")

@app.delete("/api/tokens/{token_id}")
async def delete_api_token(token_id: str, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Delete an API token"""
    try:
        token = db.query(ApiToken).filter(
            ApiToken.id == token_id,
            ApiToken.user_id == user.id
        ).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        token_name = token.name
        db.delete(token)
        db.commit()
        
        return {
            "success": True,
            "message": f"Token '{token_name}' deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting API token: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API token")

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

@app.get("/debug/logout-test", response_class=HTMLResponse)
async def debug_logout_test(request: Request, db: Session = Depends(get_db)):
    """Debug logout functionality with test buttons"""
    context = get_user_context(request, db)
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Logout Debug Test</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .test-button {{ 
                display: block; 
                margin: 10px 0; 
                padding: 15px; 
                background: #007bff; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px; 
                text-align: center;
                font-weight: bold;
            }}
            .test-button:hover {{ background: #0056b3; }}
            .debug-info {{ background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>🔍 Logout Debug Test Page</h1>
        
        <div class="debug-info">
            <h3>Current Session Status:</h3>
            <p><strong>Authenticated:</strong> {context['is_authenticated']}</p>
            <p><strong>User:</strong> {context['user'].email if context['user'] else 'None'}</p>
            <p><strong>Session ID:</strong> {request.session.get('user_id', 'None')}</p>
        </div>
        
        <h3>Test Different Logout Methods:</h3>
        
        <a href="/logout" class="test-button">
            🔗 Method 1: Simple Link to /logout
        </a>
        
        <a href="javascript:window.location.href='/logout'" class="test-button">
            🔗 Method 2: JavaScript Navigation
        </a>
        
        <button onclick="fetch('/api/auth/logout').then(() => window.location.href='/')" class="test-button">
            🔗 Method 3: API Call + Redirect
        </button>
        
        <button onclick="document.cookie='session=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;'; window.location.href='/'" class="test-button">
            🔗 Method 4: Clear Cookie + Redirect
        </button>
        
        <form method="post" action="/logout" style="display: inline;">
            <button type="submit" class="test-button">
                🔗 Method 5: POST Form
            </button>
        </form>
        
        <p><a href="/dashboard">← Back to Dashboard</a></p>
        
        <script>
            console.log('Logout debug page loaded');
            console.log('Current URL:', window.location.href);
            console.log('Session storage:', sessionStorage);
            console.log('Local storage:', localStorage);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

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