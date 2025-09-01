#!/usr/bin/env python3
"""
Database migration to fix Transaction.price column size
Changes DECIMAL(10,4) to DECIMAL(15,4) to handle large balance adjustments
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the database migration"""
    load_dotenv()
    
    # MySQL connection string
    DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"
    
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Test connection
            logger.info("🔗 Testing database connection...")
            conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            
            # Check current column definition
            logger.info("🔍 Checking current price column definition...")
            result = conn.execute(text("""
                SELECT COLUMN_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'transactions' 
                AND COLUMN_NAME = 'price'
            """))
            
            current_type = result.fetchone()
            if current_type:
                logger.info(f"📊 Current price column type: {current_type[0]}")
            else:
                logger.error("❌ Price column not found!")
                return False
            
            # Check if migration is needed
            if "decimal(15,4)" in current_type[0].lower():
                logger.info("✅ Price column already has correct size (15,4)")
                return True
            
            # Perform the migration
            logger.info("🔄 Updating price column from DECIMAL(10,4) to DECIMAL(15,4)...")
            
            # Start transaction
            trans = conn.begin()
            try:
                # Modify the column
                conn.execute(text("""
                    ALTER TABLE transactions 
                    MODIFY COLUMN price DECIMAL(15,4) NOT NULL
                """))
                
                trans.commit()
                logger.info("✅ Price column updated successfully!")
                
                # Verify the change
                result = conn.execute(text("""
                    SELECT COLUMN_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'transactions' 
                    AND COLUMN_NAME = 'price'
                """))
                
                new_type = result.fetchone()
                logger.info(f"📊 New price column type: {new_type[0]}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                logger.error(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("🎉 Migration completed successfully!")
        sys.exit(0)
    else:
        logger.error("💥 Migration failed!")
        sys.exit(1)
