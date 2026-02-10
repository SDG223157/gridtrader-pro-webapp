#!/usr/bin/env python3
"""
Migration Script: Add initiated_date column to portfolios table
This script adds an initiated_date column to track when a portfolio was actually initiated.
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
    """Add initiated_date column to portfolios table"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = :db_name
                AND TABLE_NAME = 'portfolios'
                AND COLUMN_NAME = 'initiated_date'
            """), {"db_name": os.getenv('DB_NAME')})
            
            column_exists = result.fetchone()[0] > 0
            
            if column_exists:
                logger.info("✅ Column 'initiated_date' already exists in portfolios table")
                return
            
            # Add the column
            logger.info("📝 Adding 'initiated_date' column to portfolios table...")
            conn.execute(text("""
                ALTER TABLE portfolios
                ADD COLUMN initiated_date DATE NULL
                COMMENT 'Date when portfolio was actually initiated (can differ from created_at)'
                AFTER last_rebalanced
            """))
            conn.commit()
            
            logger.info("✅ Successfully added 'initiated_date' column to portfolios table")
            
            # Show updated table structure
            result = conn.execute(text("DESCRIBE portfolios"))
            logger.info("\n📊 Updated portfolios table structure:")
            for row in result:
                logger.info(f"  {row[0]}: {row[1]} {row[2]} {row[3]}")
                
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🚀 Starting migration: Add initiated_date to portfolios")
    run_migration()
    logger.info("✅ Migration completed successfully!")

