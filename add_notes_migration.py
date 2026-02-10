#!/usr/bin/env python3
"""
Add notes column to transactions table
"""
import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv('DATABASE_URL') or f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

def add_notes_column():
    """Add notes column to transactions table"""
    try:
        # Create engine
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        logger.info("🔧 Adding notes column to transactions table...")
        
        with engine.connect() as conn:
            # Check if notes column already exists
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'transactions' 
                AND COLUMN_NAME = 'notes'
            """))
            
            if result.fetchone():
                logger.info("✅ Notes column already exists")
                return True
            
            # Add the notes column
            conn.execute(text("""
                ALTER TABLE transactions 
                ADD COLUMN notes TEXT NULL
            """))
            
            conn.commit()
            logger.info("✅ Notes column added successfully")
            
            # Verify the column was added
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = 'transactions' 
                AND COLUMN_NAME = 'notes'
            """))
            
            if result.fetchone():
                logger.info("✅ Notes column verified")
                return True
            else:
                logger.error("❌ Notes column not found after addition")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error adding notes column: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 GridTrader Pro - Add Notes Column Migration")
    logger.info("=" * 50)
    
    success = add_notes_column()
    
    if success:
        logger.info("✅ Migration completed successfully")
        logger.info("✅ Transactions table now supports notes field")
    else:
        logger.error("❌ Migration failed")
        exit(1)
