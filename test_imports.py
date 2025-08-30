#!/usr/bin/env python3
"""
Test imports from main.py one by one to identify the failing import
"""
import os
import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Import Test", version="1.0.0")

@app.get("/")
async def root():
    results = {}
    
    # Test basic imports first
    try:
        import os
        results["os"] = "✅ OK"
    except Exception as e:
        results["os"] = f"❌ {str(e)}"
    
    try:
        import logging
        results["logging"] = "✅ OK"
    except Exception as e:
        results["logging"] = f"❌ {str(e)}"
    
    try:
        import asyncio
        results["asyncio"] = "✅ OK"
    except Exception as e:
        results["asyncio"] = f"❌ {str(e)}"
    
    try:
        from pathlib import Path
        results["pathlib"] = "✅ OK"
    except Exception as e:
        results["pathlib"] = f"❌ {str(e)}"
    
    # Test FastAPI imports
    try:
        from fastapi import FastAPI, HTTPException, Depends, Request, Form
        results["fastapi_core"] = "✅ OK"
    except Exception as e:
        results["fastapi_core"] = f"❌ {str(e)}"
    
    try:
        from fastapi.middleware.cors import CORSMiddleware
        results["fastapi_cors"] = "✅ OK"
    except Exception as e:
        results["fastapi_cors"] = f"❌ {str(e)}"
    
    try:
        from fastapi.staticfiles import StaticFiles
        results["fastapi_static"] = "✅ OK"
    except Exception as e:
        results["fastapi_static"] = f"❌ {str(e)}"
    
    try:
        from fastapi.templating import Jinja2Templates
        results["fastapi_templates"] = "✅ OK"
    except Exception as e:
        results["fastapi_templates"] = f"❌ {str(e)}"
    
    # Test Starlette imports
    try:
        from starlette.middleware.sessions import SessionMiddleware
        results["starlette_sessions"] = "✅ OK"
    except Exception as e:
        results["starlette_sessions"] = f"❌ {str(e)}"
    
    # Test SQLAlchemy imports
    try:
        from sqlalchemy.orm import Session
        results["sqlalchemy_orm"] = "✅ OK"
    except Exception as e:
        results["sqlalchemy_orm"] = f"❌ {str(e)}"
    
    try:
        from sqlalchemy import text, func, desc
        results["sqlalchemy_core"] = "✅ OK"
    except Exception as e:
        results["sqlalchemy_core"] = f"❌ {str(e)}"
    
    # Test local module imports (these are likely to fail)
    try:
        from database import get_db
        results["database_get_db"] = "✅ OK"
    except Exception as e:
        results["database_get_db"] = f"❌ {str(e)}"
    
    try:
        from auth import create_access_token
        results["auth_module"] = "✅ OK"
    except Exception as e:
        results["auth_module"] = f"❌ {str(e)}"
    
    try:
        from data_provider import YFinanceDataProvider
        results["data_provider"] = "✅ OK"
    except Exception as e:
        results["data_provider"] = f"❌ {str(e)}"
    
    try:
        from app.algorithms.grid_trading import GridTradingStrategy
        results["grid_trading"] = "✅ OK"
    except Exception as e:
        results["grid_trading"] = f"❌ {str(e)}"
    
    # Test other imports
    try:
        import uuid
        results["uuid"] = "✅ OK"
    except Exception as e:
        results["uuid"] = f"❌ {str(e)}"
    
    try:
        import httpx
        results["httpx"] = "✅ OK"
    except Exception as e:
        results["httpx"] = f"❌ {str(e)}"
    
    try:
        from datetime import datetime, timedelta
        results["datetime"] = "✅ OK"
    except Exception as e:
        results["datetime"] = f"❌ {str(e)}"
    
    try:
        from pydantic import BaseModel
        results["pydantic"] = "✅ OK"
    except Exception as e:
        results["pydantic"] = f"❌ {str(e)}"
    
    return {"message": "Import Test Results", "results": results}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 3000))
    host = os.getenv('HOSTNAME', '0.0.0.0')
    logger.info(f"🌐 Starting import test server on {host}:{port}")
    uvicorn.run(
        "test_imports:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )
