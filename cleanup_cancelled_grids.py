#!/usr/bin/env python3
"""
Clean up cancelled grids that should have been deleted
"""

import os
import sys
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database import engine, Grid, GridOrder, Portfolio, GridStatus, OrderStatus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_cancelled_grids():
    """Clean up cancelled grids and return funds to portfolios"""
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find all cancelled grids
        cancelled_grids = db.query(Grid).filter(Grid.status == GridStatus.cancelled).all()
        
        if not cancelled_grids:
            logger.info("✅ No cancelled grids found - cleanup not needed")
            return
        
        logger.info(f"🧹 Found {len(cancelled_grids)} cancelled grids to clean up")
        
        total_funds_returned = 0.0
        
        for grid in cancelled_grids:
            logger.info(f"🗑️ Processing cancelled grid: {grid.name}")
            
            # Get the portfolio
            portfolio = db.query(Portfolio).filter(Portfolio.id == grid.portfolio_id).first()
            if not portfolio:
                logger.warning(f"⚠️ Portfolio not found for grid {grid.name}")
                continue
            
            # Calculate funds to return
            investment_amount = float(grid.investment_amount)
            
            # Get all orders for this grid
            orders = db.query(GridOrder).filter(GridOrder.grid_id == grid.id).all()
            
            # Delete all orders
            for order in orders:
                db.delete(order)
            
            # Return funds to portfolio
            portfolio.cash_balance = float(portfolio.cash_balance) + investment_amount
            total_funds_returned += investment_amount
            
            logger.info(f"💰 Returned ${investment_amount:,.2f} to portfolio: {portfolio.name}")
            
            # Delete the grid completely
            db.delete(grid)
            
            logger.info(f"🗑️ Deleted cancelled grid: {grid.name}")
        
        db.commit()
        
        logger.info(f"✅ Cleanup complete!")
        logger.info(f"📊 Summary:")
        logger.info(f"   Grids cleaned up: {len(cancelled_grids)}")
        logger.info(f"   Total funds returned: ${total_funds_returned:,.2f}")
        logger.info(f"   Orders deleted: {sum(len(db.query(GridOrder).filter(GridOrder.grid_id == g.id).all()) for g in cancelled_grids)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 CLEANING UP CANCELLED GRIDS")
    print("=" * 50)
    
    success = cleanup_cancelled_grids()
    
    if success:
        print("\n✅ CLEANUP SUCCESSFUL!")
        print("All cancelled grids have been removed and funds returned to portfolios.")
    else:
        print("\n❌ CLEANUP FAILED!")
        print("Please check the logs for details.")
