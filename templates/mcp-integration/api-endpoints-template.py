"""
Universal API Endpoints Template for MCP Integration
Copy and adapt these endpoints to your application
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
from typing import List, Optional

# Pydantic Models (Customize for your app)
class CreateApiTokenRequest(BaseModel):
    name: str
    description: str = ""
    permissions: List[str] = ["read", "write"]
    expires_in_days: Optional[int] = None

class CreateItemRequest(BaseModel):  # Replace with your entity
    name: str
    description: str = ""
    # Add your specific fields

# API Token Management (Universal - use as-is)
@app.post("/api/tokens")
async def create_api_token(request: CreateApiTokenRequest, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Create a new API token"""
    try:
        token = secrets.token_urlsafe(32)
        
        expires_at = None
        if request.expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=request.expires_in_days)
        
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
                "your-app": {  # Change this to your app name
                    "command": "your-app-mcp",  # Change this to your command
                    "env": {
                        "YOUR_APP_API_URL": "https://your-domain.com",  # Your domain
                        "YOUR_APP_ACCESS_TOKEN": token
                    }
                }
            }
        }
        
        return {
            "success": True,
            "message": "API token created successfully",
            "id": api_token.id,
            "name": api_token.name,
            "token": token,
            "mcp_config": mcp_config,
            "installation_command": "npm install -g your-app-mcp"  # Your package
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create API token")

@app.get("/api/tokens")
async def get_api_tokens(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get user's API tokens"""
    try:
        tokens = db.query(ApiToken).filter(ApiToken.user_id == user.id).all()
        
        return {
            "tokens": [
                {
                    "id": token.id,
                    "name": token.name,
                    "description": token.description,
                    "permissions": token.permissions,
                    "is_active": token.is_active,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                    "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None,
                    "created_at": token.created_at.isoformat()
                }
                for token in tokens
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch tokens")

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
        
        db.delete(token)
        db.commit()
        
        return {"success": True, "message": "Token deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete token")

# Core App Data Endpoints (Customize these for your app)
@app.get("/api/data")
async def get_app_data(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get main app data - customize for your application"""
    try:
        # Replace with your app's main data query
        items = db.query(YourMainEntity).filter(YourMainEntity.user_id == user.id).all()
        
        return {
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description,
                    "created_at": item.created_at.isoformat(),
                    # Add your specific fields
                }
                for item in items
            ],
            "summary": {
                "total_items": len(items),
                # Add your summary metrics
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get data")

@app.get("/api/items")  # Replace 'items' with your entity name
async def get_items(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Get user's items - customize for your entities"""
    try:
        items = db.query(YourEntity).filter(YourEntity.user_id == user.id).all()
        
        return {
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    # Add your fields
                }
                for item in items
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get items")

@app.post("/api/items")  # Replace 'items' with your entity name
async def create_item(request: CreateItemRequest, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Create new item - customize for your entities"""
    try:
        item = YourEntity(
            user_id=user.id,
            name=request.name,
            description=request.description,
            # Add your fields
        )
        
        db.add(item)
        db.commit()
        db.refresh(item)
        
        return {
            "success": True,
            "id": item.id,
            "message": f"Item '{request.name}' created successfully"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create item")

@app.get("/api/dashboard/summary")
async def dashboard_summary(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    """Dashboard summary - customize for your app metrics"""
    try:
        # Replace with your app's summary data
        total_items = db.query(YourEntity).filter(YourEntity.user_id == user.id).count()
        
        return {
            "success": True,
            "total_items": total_items,
            "user_name": user.email.split('@')[0],
            "last_updated": datetime.now().isoformat(),
            # Add your summary metrics
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get summary")

# Debug Endpoints (Universal - use as-is)
@app.get("/debug/test-tokens")
async def debug_test_tokens():
    """Test tokens functionality"""
    return {
        "status": "✅ Route working",
        "timestamp": datetime.utcnow().isoformat(),
        "message": "MCP integration routes are working"
    }

@app.get("/debug/test-tokens-db")
async def debug_test_tokens_db(db: Session = Depends(get_db)):
    """Test tokens database functionality"""
    try:
        token_count = db.query(ApiToken).count()
        return {
            "api_tokens_table": "✅ Exists",
            "token_count": token_count,
            "status": "Working"
        }
    except Exception as e:
        return {
            "api_tokens_table": "❌ Error",
            "error": str(e)
        }
