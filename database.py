from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, Date, JSON, Enum, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, text
import os
import enum
import asyncio
import logging
import uuid
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Database URL: prefer DATABASE_URL env var (Neon/Postgres), fallback to MySQL
DATABASE_URL = os.getenv('DATABASE_URL') or (
    f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
)

# Clean up Neon/Postgres connection URL
if DATABASE_URL and "postgresql" in DATABASE_URL:
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    _parsed = urlparse(DATABASE_URL)
    _params = parse_qs(_parsed.query)
    _params.pop("channel_binding", None)       # Not supported by psycopg2
    _params.setdefault("sslmode", ["require"])  # Ensure SSL for Neon
    _params["sslcert"] = [""]                   # Disable client cert (avoids Permission denied)
    _params["sslkey"] = [""]                    # Disable client key
    _cleaned_query = urlencode(_params, doseq=True)
    DATABASE_URL = urlunparse(_parsed._replace(query=_cleaned_query))

# Use VARCHAR as String alias (was MySQL-specific import)
VARCHAR = String

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,      # Important for Neon idle connection timeouts
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Enums
class RiskTolerance(enum.Enum):
    conservative = "conservative"
    moderate = "moderate"
    aggressive = "aggressive"

class StrategyType(enum.Enum):
    grid_trading = "grid_trading"
    core_satellite = "core_satellite"
    balanced = "balanced"
    growth = "growth"

class MarketType(enum.Enum):
    US = "US"
    HK = "HK"
    CHINA = "CHINA"

# Market to currency mapping
MARKET_CURRENCY_MAP = {
    MarketType.US: "USD",
    MarketType.HK: "HKD",
    MarketType.CHINA: "CNY"
}

# Currency symbols for display
CURRENCY_SYMBOLS = {
    "USD": "$",
    "HKD": "HK$",
    "CNY": "¥"
}

class AuthProvider(enum.Enum):
    local = "local"
    google = "google"

class PortfolioStatus(enum.Enum):
    active = "active"
    paused = "paused"
    closed = "closed"

class GridStatus(enum.Enum):
    active = "active"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"

class OrderStatus(enum.Enum):
    pending = "pending"
    filled = "filled"
    cancelled = "cancelled"
    failed = "failed"

class TransactionType(enum.Enum):
    buy = "buy"
    sell = "sell"
    dividend = "dividend"
    fee = "fee"

class AlertType(enum.Enum):
    price = "price"
    portfolio = "portfolio"
    grid = "grid"
    system = "system"

# Database Models
class User(Base):
    __tablename__ = "users"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    auth_provider = Column(Enum(AuthProvider), default=AuthProvider.local)
    is_email_verified = Column(Boolean, default=False)
    subscription_tier = Column(String(50), default="free")
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    portfolios = relationship("Portfolio", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    oauth_sessions = relationship("OAuthSession", back_populates="user")
    api_tokens = relationship("ApiToken", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"

    user_id = Column(VARCHAR(36), ForeignKey("users.id"), primary_key=True)
    display_name = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    risk_tolerance = Column(Enum(RiskTolerance), default=RiskTolerance.moderate)
    investment_experience = Column(String(20), default="beginner")
    preferred_currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="UTC")
    locale = Column(String(10), default="en")
    google_profile_data = Column(JSON)

    user = relationship("User", back_populates="profile")

class OAuthSession(Base):
    __tablename__ = "oauth_sessions"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(VARCHAR(36), ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(AuthProvider), nullable=False)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    scope = Column(String(500))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("User", back_populates="oauth_sessions")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(VARCHAR(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_type = Column(Enum(StrategyType), nullable=False)
    market = Column(Enum(MarketType), default=MarketType.US, nullable=False)  # US, HK, CHINA
    currency = Column(String(3), default="USD", nullable=False)  # USD, HKD, CNY
    initial_capital = Column(DECIMAL(15, 2), nullable=False)
    current_value = Column(DECIMAL(15, 2), default=0.00)
    cash_balance = Column(DECIMAL(15, 2), default=0.00)
    total_return = Column(DECIMAL(15, 4), default=0.0000)
    status = Column(Enum(PortfolioStatus), default=PortfolioStatus.active)
    rebalance_frequency = Column(String(20), default="monthly")
    last_rebalanced = Column(DateTime)
    initiated_date = Column(Date, nullable=True)  # Date when portfolio was actually initiated
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")
    grids = relationship("Grid", back_populates="portfolio")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(VARCHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    quantity = Column(DECIMAL(15, 6), nullable=False)
    average_cost = Column(DECIMAL(10, 4), nullable=False)
    current_price = Column(DECIMAL(10, 4))
    market_value = Column(DECIMAL(15, 2))
    unrealized_pnl = Column(DECIMAL(15, 2))
    target_allocation = Column(DECIMAL(5, 4))
    actual_allocation = Column(DECIMAL(5, 4))
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    portfolio = relationship("Portfolio", back_populates="holdings")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(VARCHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(DECIMAL(15, 6), nullable=False)
    price = Column(DECIMAL(15, 4), nullable=False)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    fees = Column(DECIMAL(10, 2), default=0.00)
    notes = Column(Text, nullable=True)
    executed_at = Column(DateTime, server_default=func.current_timestamp())
    created_at = Column(DateTime, server_default=func.current_timestamp())

    portfolio = relationship("Portfolio", back_populates="transactions")

class Grid(Base):
    __tablename__ = "grids"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    portfolio_id = Column(VARCHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    strategy_config = Column(JSON, nullable=False, default={})
    upper_price = Column(DECIMAL(10, 4), nullable=False)
    lower_price = Column(DECIMAL(10, 4), nullable=False)
    grid_spacing = Column(DECIMAL(10, 4), nullable=False)
    investment_amount = Column(DECIMAL(15, 2), nullable=False)
    status = Column(Enum(GridStatus), default=GridStatus.active)
    total_profit = Column(DECIMAL(15, 2), default=0.00)
    completed_orders = Column(Integer, default=0)
    active_orders = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    portfolio = relationship("Portfolio", back_populates="grids")
    orders = relationship("GridOrder", back_populates="grid")

class GridOrder(Base):
    __tablename__ = "grid_orders"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    grid_id = Column(VARCHAR(36), ForeignKey("grids.id"), nullable=False)
    order_type = Column(Enum(TransactionType), nullable=False)
    target_price = Column(DECIMAL(10, 4), nullable=False)
    quantity = Column(DECIMAL(15, 6), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    filled_price = Column(DECIMAL(10, 4))
    filled_quantity = Column(DECIMAL(15, 6))
    filled_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    grid = relationship("Grid", back_populates="orders")

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open_price = Column(DECIMAL(10, 4))
    high_price = Column(DECIMAL(10, 4))
    low_price = Column(DECIMAL(10, 4))
    close_price = Column(DECIMAL(10, 4))
    volume = Column(BigInteger)
    adjusted_close = Column(DECIMAL(10, 4))
    created_at = Column(DateTime, server_default=func.current_timestamp())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(VARCHAR(36), ForeignKey("users.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    alert_metadata = Column(JSON)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="alerts")

class ApiToken(Base):
    """API tokens for MCP server authentication"""
    __tablename__ = "api_tokens"

    id = Column(VARCHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(VARCHAR(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    token = Column(VARCHAR(64), nullable=False, unique=True)
    permissions = Column(JSON, default=lambda: ["read", "write"])  # Array of permissions
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)  # NULL means no expiration
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("User", back_populates="api_tokens")

# Database connection and table creation functions
async def connect_with_retry(max_retries=5, delay=5):
    """Connect to database with retry logic"""
    for attempt in range(max_retries):
        try:
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
            else:
                logger.error("❌ All database connection attempts failed")
                raise e

def create_tables():
    """Create all database tables with proper UUID handling"""
    try:
        # Test connection first
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection verified")
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        
        # Verify tables exist (cross-database compatible)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"📊 Available tables: {', '.join(tables)}")
            
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        logger.error("💡 Try running: python init_database.py")
        raise e