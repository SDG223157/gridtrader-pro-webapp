#!/usr/bin/env python3
"""
Database test to debug user creation issues
"""
import os
import logging
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, User, UserProfile
from auth import hash_password

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Database Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Database Test API", "status": "ok"}

@app.get("/test-db")
async def test_database_connection(db: Session = Depends(get_db)):
    """Test basic database connectivity"""
    try:
        # Test basic query
        result = db.execute("SELECT 1 as test").fetchone()
        return {"database": "✅ Connected", "test_query": result[0]}
    except Exception as e:
        return {"database": "❌ Error", "error": str(e)}

@app.get("/test-user-table")
async def test_user_table(db: Session = Depends(get_db)):
    """Test user table structure"""
    try:
        # Test user table exists and structure
        users = db.query(User).limit(1).all()
        user_count = db.query(User).count()
        
        return {
            "user_table": "✅ Accessible",
            "user_count": user_count,
            "sample_users": len(users)
        }
    except Exception as e:
        return {"user_table": "❌ Error", "error": str(e)}

@app.post("/test-create-user")
async def test_create_user(db: Session = Depends(get_db)):
    """Test creating a user manually"""
    try:
        test_email = "test@example.com"
        
        # Check if test user already exists
        existing = db.query(User).filter(User.email == test_email).first()
        if existing:
            db.delete(existing)
            # Also delete profile if exists
            existing_profile = db.query(UserProfile).filter(UserProfile.user_id == existing.id).first()
            if existing_profile:
                db.delete(existing_profile)
            db.commit()
        
        # Create test user
        user_data = {
            "email": test_email,
            "password_hash": hash_password("testpass123"),
            "auth_provider": "local",
            "is_email_verified": False
        }
        
        user = User(**user_data)
        db.add(user)
        db.flush()  # Get the user ID
        
        # Create user profile
        profile = UserProfile(
            user_id=user.id,
            display_name="Test User",
            first_name="Test",
            last_name="User"
        )
        db.add(profile)
        db.commit()
        db.refresh(user)
        
        return {
            "user_creation": "✅ Success",
            "user_id": user.id,
            "email": user.email,
            "auth_provider": user.auth_provider
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"User creation error: {e}")
        return {"user_creation": "❌ Error", "error": str(e)}

@app.get("/test-env")
async def test_environment():
    """Test environment variables"""
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 3000))
    host = os.getenv('HOSTNAME', '0.0.0.0')
    logger.info(f"🌐 Starting database test server on {host}:{port}")
    uvicorn.run(
        "test_db:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )
