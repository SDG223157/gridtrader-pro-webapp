#!/usr/bin/env python3
"""
Database initialization script for GridTrader Pro
Handles MySQL-specific UUID generation and table creation
"""

import os
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from database import Base, User, UserProfile, Portfolio, Holding, Grid, MarketData, Alert
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    return os.getenv('DATABASE_URL') or (
        f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    )

def create_database_tables():
    """Create database tables with proper error handling"""
    try:
        database_url = get_database_url()
        logger.info(f"Connecting to database: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
        
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=0,
            echo=False  # Set to True for SQL debugging
        )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        
        # Create tables
        logger.info("🔧 Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Verify tables were created (cross-database compatible)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"📊 Created tables: {', '.join(tables)}")
        
        return True
        
    except OperationalError as e:
        logger.error(f"❌ Database connection error: {e}")
        logger.error("🔍 Check your database credentials and network connectivity")
        return False
        
    except ProgrammingError as e:
        logger.error(f"❌ Database schema error: {e}")
        logger.error("🔍 Check your database permissions and schema compatibility")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected database error: {e}")
        return False

def check_database_status():
    """Check database connection and table status"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Check connection
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection: OK")
            
            # Check tables (cross-database compatible)
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['users', 'user_profiles', 'oauth_sessions', 'portfolios', 
                             'holdings', 'transactions', 'grids', 'grid_orders', 
                             'market_data', 'alerts']
            
            missing_tables = [t for t in expected_tables if t not in tables]
            
            if missing_tables:
                logger.warning(f"⚠️ Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                logger.info(f"✅ All tables present: {len(tables)} tables")
                return True
                
    except Exception as e:
        logger.error(f"❌ Database status check failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 GridTrader Pro - Database Initialization")
    logger.info("=" * 50)
    
    # Check if required environment variables are set
    if not os.getenv('DATABASE_URL'):
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            logger.error("Please set DATABASE_URL or all required DB_ variables")
            exit(1)
    
    # Check current database status
    logger.info("🔍 Checking current database status...")
    if check_database_status():
        logger.info("✅ Database is already properly initialized")
    else:
        logger.info("🔧 Initializing database...")
        if create_database_tables():
            logger.info("🎉 Database initialization completed successfully!")
        else:
            logger.error("❌ Database initialization failed")
            exit(1)
    
    logger.info("✅ Database ready for GridTrader Pro!")