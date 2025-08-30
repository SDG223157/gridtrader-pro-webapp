from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, DateTime, Date, JSON, Enum, BigInteger, ForeignKey
from sqlalchemy.dialects.mysql import VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import os
import enum
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# MySQL connection string
DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=20,
    max_overflow=0
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

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
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

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
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

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
    user_id = Column(VARCHAR(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_type = Column(Enum(StrategyType), nullable=False)
    initial_capital = Column(DECIMAL(15, 2), nullable=False)
    current_value = Column(DECIMAL(15, 2), default=0.00)
    cash_balance = Column(DECIMAL(15, 2), default=0.00)
    total_return = Column(DECIMAL(15, 4), default=0.0000)
    status = Column(Enum(PortfolioStatus), default=PortfolioStatus.active)
    rebalance_frequency = Column(String(20), default="monthly")
    last_rebalanced = Column(DateTime)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")
    transactions = relationship("Transaction", back_populates="portfolio")
    grids = relationship("Grid", back_populates="portfolio")

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
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

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
    portfolio_id = Column(VARCHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    quantity = Column(DECIMAL(15, 6), nullable=False)
    price = Column(DECIMAL(10, 4), nullable=False)
    total_amount = Column(DECIMAL(15, 2), nullable=False)
    fees = Column(DECIMAL(10, 2), default=0.00)
    executed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    portfolio = relationship("Portfolio", back_populates="transactions")

class Grid(Base):
    __tablename__ = "grids"

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
    portfolio_id = Column(VARCHAR(36), ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    strategy_config = Column(JSON, nullable=False)
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

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
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

    id = Column(VARCHAR(36), primary_key=True, server_default=func.uuid())
    user_id = Column(VARCHAR(36), ForeignKey("users.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    metadata = Column(JSON)
    created_at = Column(DateTime, server_default=func.current_timestamp())

    user = relationship("User", back_populates="alerts")

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
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
        raise e