#!/usr/bin/env python3
"""
Migration script to add API tokens table to GridTrader Pro database
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME')}?charset=utf8mb4"

def run_migration():
    """Run the API tokens table migration"""
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Check if api_tokens table already exists
            result = conn.execute(text("SHOW TABLES LIKE 'api_tokens'"))
            if result.fetchone():
                logger.info("✅ api_tokens table already exists, skipping migration")
                return True
            
            # Create api_tokens table
            create_table_sql = """
            CREATE TABLE api_tokens (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                token VARCHAR(64) NOT NULL UNIQUE,
                permissions JSON DEFAULT ('["read", "write"]'),
                is_active BOOLEAN DEFAULT TRUE,
                expires_at DATETIME NULL,
                last_used_at DATETIME NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_token (token),
                INDEX idx_user_id (user_id),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            conn.execute(text(create_table_sql))
            conn.commit()
            
            logger.info("✅ Successfully created api_tokens table")
            
            # Verify table was created
            result = conn.execute(text("DESCRIBE api_tokens"))
            columns = result.fetchall()
            logger.info(f"📊 api_tokens table has {len(columns)} columns:")
            for col in columns:
                logger.info(f"   - {col[0]} ({col[1]})")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def verify_migration():
    """Verify the migration was successful"""
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        
        with engine.connect() as conn:
            # Check table exists
            result = conn.execute(text("SHOW TABLES LIKE 'api_tokens'"))
            if not result.fetchone():
                logger.error("❌ api_tokens table not found")
                return False
            
            # Check table structure
            result = conn.execute(text("DESCRIBE api_tokens"))
            columns = [row[0] for row in result.fetchall()]
            
            required_columns = [
                'id', 'user_id', 'name', 'description', 'token', 
                'permissions', 'is_active', 'expires_at', 'last_used_at', 
                'created_at', 'updated_at'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                logger.error(f"❌ Missing columns: {missing_columns}")
                return False
            
            logger.info("✅ Migration verification successful")
            return True
            
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 GridTrader Pro - API Tokens Migration")
    print("=" * 50)
    
    # Check database connection
    try:
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Run migration
    if run_migration():
        if verify_migration():
            print("\n🎉 Migration completed successfully!")
            print("\nNext steps:")
            print("1. Restart your GridTrader Pro application")
            print("2. Visit /tokens to create your first API token")
            print("3. Configure the token with your MCP server")
        else:
            print("\n❌ Migration verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
