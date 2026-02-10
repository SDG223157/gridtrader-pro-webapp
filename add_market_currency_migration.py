#!/usr/bin/env python3
"""
Migration Script: Add market and currency columns to portfolios table
This script adds market and currency columns to support multi-market portfolios (US, HK, CHINA).
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection (prefer DATABASE_URL for Neon/Postgres)
DATABASE_URL = os.getenv('DATABASE_URL') or f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

def run_migration():
    """Add market and currency columns to portfolios table"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if market column already exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db_name
                AND TABLE_NAME = 'portfolios'
                AND COLUMN_NAME = 'market'
            """), {"db_name": os.getenv('DB_NAME')})
            
            market_exists = result.fetchone()[0] > 0
            
            # Check if currency column already exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db_name
                AND TABLE_NAME = 'portfolios'
                AND COLUMN_NAME = 'currency'
            """), {"db_name": os.getenv('DB_NAME')})
            
            currency_exists = result.fetchone()[0] > 0
            
            if market_exists and currency_exists:
                logger.info("✅ Both 'market' and 'currency' columns already exist in portfolios table")
                return
            
            # Add the market column if it doesn't exist
            if not market_exists:
                logger.info("📝 Adding 'market' column to portfolios table...")
                conn.execute(text("""
                    ALTER TABLE portfolios
                    ADD COLUMN market ENUM('US', 'HK', 'CHINA') NOT NULL DEFAULT 'US'
                    COMMENT 'Market type: US, HK, or CHINA'
                    AFTER strategy_type
                """))
                conn.commit()
                logger.info("✅ Successfully added 'market' column")
            else:
                logger.info("✅ Column 'market' already exists")
            
            # Add the currency column if it doesn't exist
            if not currency_exists:
                logger.info("📝 Adding 'currency' column to portfolios table...")
                conn.execute(text("""
                    ALTER TABLE portfolios
                    ADD COLUMN currency VARCHAR(3) NOT NULL DEFAULT 'USD'
                    COMMENT 'Currency code: USD, HKD, or CNY'
                    AFTER market
                """))
                conn.commit()
                logger.info("✅ Successfully added 'currency' column")
            else:
                logger.info("✅ Column 'currency' already exists")
            
            # Show updated table structure
            result = conn.execute(text("DESCRIBE portfolios"))
            logger.info("\n📊 Updated portfolios table structure:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} {row[2]} {row[3]}")
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🚀 Starting migration: Add market and currency to portfolios")
    run_migration()
    logger.info("✅ Migration completed successfully!")
