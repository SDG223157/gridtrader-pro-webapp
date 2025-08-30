#!/usr/bin/env python3
"""
Minimal FastAPI test to isolate startup issues
"""
import os
import logging
from fastapi import FastAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal FastAPI app
app = FastAPI(title="GridTrader Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "GridTrader Test is running!", "status": "ok"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 3000))
    host = os.getenv('HOSTNAME', '0.0.0.0')
    logger.info(f"🌐 Starting minimal test server on {host}:{port}")
    uvicorn.run(
        "test_minimal:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=False
    )
