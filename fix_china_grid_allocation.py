#!/usr/bin/env python3
"""
Fix China/HK Grid Allocation for 600298.SS

For China and Hong Kong stocks, short selling is not allowed.
Therefore, grid trading should only use BUY orders below the current price.

Current Issue:
- 600298.SS grid has 12 levels with $1M allocated across all levels
- This includes sell orders above current price (not allowed in China/HK)

Solution:
- Allocate $1M ONLY across the 6 buy levels below current price
- Remove/disable sell orders above current price
- Each buy level gets $1M / 6 = $166,666.67 investment
"""

import os
import sys
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from database import engine, Grid, GridOrder, OrderStatus, TransactionType
import yfinance as yf
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_current_price(symbol):
    """Get current price using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        return None
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        return None

def fix_china_hk_grid_allocation(symbol='600298.SS'):
    """Fix grid allocation for China/HK stocks - only buy orders allowed"""
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get the active grid for this symbol
        grid = db.query(Grid).filter(
            Grid.symbol == symbol,
            Grid.status == 'active'
        ).first()
        
        if not grid:
            logger.error(f"No active grid found for {symbol}")
            return False
        
        logger.info(f"🎯 FIXING CHINA GRID ALLOCATION FOR {symbol}")
        logger.info(f"Grid ID: {grid.id}")
        logger.info(f"Current Investment: ${grid.investment_amount}")
        logger.info(f"Current Range: ${grid.lower_price} - ${grid.upper_price}")
        
        # Get current price
        current_price = get_current_price(symbol)
        if not current_price:
            logger.error(f"Could not get current price for {symbol}")
            return False
        
        logger.info(f"Current Price: ${current_price:.2f}")
        
        # Calculate grid parameters
        price_range = float(grid.upper_price) - float(grid.lower_price)
        grid_spacing = price_range / 12  # Original 12 levels
        
        logger.info(f"Grid Spacing: ${grid_spacing:.4f}")
        
        # Identify buy levels (below current price)
        buy_levels = []
        for i in range(13):  # 0 to 12 levels
            level_price = float(grid.lower_price) + (i * grid_spacing)
            if level_price < current_price:
                buy_levels.append({
                    'level': i,
                    'price': level_price,
                    'distance_from_current': current_price - level_price
                })
        
        logger.info(f"📊 BUY LEVELS IDENTIFIED: {len(buy_levels)}")
        for level in buy_levels:
            logger.info(f"   Level {level['level']}: ${level['price']:.2f} (${level['distance_from_current']:.2f} below current)")
        
        if len(buy_levels) == 0:
            logger.warning("No buy levels below current price - price may be at lower bound")
            return False
        
        # Calculate new allocation per buy level
        total_investment = float(grid.investment_amount)
        investment_per_buy_level = total_investment / len(buy_levels)
        
        logger.info(f"💰 NEW ALLOCATION:")
        logger.info(f"   Total Investment: ${total_investment:,.2f}")
        logger.info(f"   Buy Levels: {len(buy_levels)}")
        logger.info(f"   Investment per Buy Level: ${investment_per_buy_level:,.2f}")
        
        # Delete existing orders
        existing_orders = db.query(GridOrder).filter(GridOrder.grid_id == grid.id).all()
        logger.info(f"🗑️ Deleting {len(existing_orders)} existing orders")
        
        for order in existing_orders:
            db.delete(order)
        
        # Create new buy orders with correct allocation
        new_orders_created = 0
        
        for level in buy_levels:
            level_price = level['price']
            quantity = investment_per_buy_level / level_price
            
            order = GridOrder(
                grid_id=grid.id,
                order_type=TransactionType.buy,
                target_price=Decimal(str(level_price)),
                quantity=Decimal(str(quantity)),
                status=OrderStatus.pending,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(order)
            new_orders_created += 1
            
            logger.info(f"✅ Created BUY order: ${level_price:.2f} x {quantity:,.0f} shares = ${investment_per_buy_level:,.2f}")
        
        # Update grid configuration
        grid.active_orders = new_orders_created
        
        # Update strategy config to reflect China/HK constraints
        if hasattr(grid, 'strategy_config') and grid.strategy_config:
            grid.strategy_config['market_type'] = 'china_hk'
            grid.strategy_config['short_selling_allowed'] = False
            grid.strategy_config['buy_levels_only'] = True
            grid.strategy_config['buy_levels_count'] = len(buy_levels)
            grid.strategy_config['investment_per_buy_level'] = investment_per_buy_level
            grid.strategy_config['updated_at'] = datetime.now().isoformat()
        
        db.commit()
        
        logger.info(f"🎉 SUCCESS: China Grid Allocation Fixed!")
        logger.info(f"✅ Created {new_orders_created} BUY orders")
        logger.info(f"✅ Investment per level: ${investment_per_buy_level:,.2f}")
        logger.info(f"✅ No sell orders (China/HK market compliant)")
        logger.info(f"✅ Total allocated: ${total_investment:,.2f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error fixing grid allocation: {e}")
        db.rollback()
        return False
        
    finally:
        db.close()

def verify_china_grid_fix(symbol='600298.SS'):
    """Verify the grid allocation fix"""
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        grid = db.query(Grid).filter(
            Grid.symbol == symbol,
            Grid.status == 'active'
        ).first()
        
        if not grid:
            logger.error(f"No active grid found for {symbol}")
            return
        
        orders = db.query(GridOrder).filter(
            GridOrder.grid_id == grid.id,
            GridOrder.status == OrderStatus.pending
        ).all()
        
        logger.info(f"🔍 VERIFICATION FOR {symbol}")
        logger.info(f"Grid Investment: ${grid.investment_amount}")
        logger.info(f"Active Orders: {len(orders)}")
        
        buy_orders = [o for o in orders if o.order_type == TransactionType.buy]
        sell_orders = [o for o in orders if o.order_type == TransactionType.sell]
        
        logger.info(f"📊 ORDER BREAKDOWN:")
        logger.info(f"   BUY orders: {len(buy_orders)}")
        logger.info(f"   SELL orders: {len(sell_orders)}")
        
        if sell_orders:
            logger.warning(f"⚠️ WARNING: {len(sell_orders)} sell orders still exist (should be 0 for China/HK)")
        
        total_buy_investment = sum(float(order.target_price) * float(order.quantity) for order in buy_orders)
        
        logger.info(f"💰 INVESTMENT ALLOCATION:")
        logger.info(f"   Total in BUY orders: ${total_buy_investment:,.2f}")
        logger.info(f"   Expected: ${float(grid.investment_amount):,.2f}")
        logger.info(f"   Difference: ${abs(total_buy_investment - float(grid.investment_amount)):,.2f}")
        
        if len(buy_orders) > 0:
            avg_investment_per_level = total_buy_investment / len(buy_orders)
            logger.info(f"   Average per BUY level: ${avg_investment_per_level:,.2f}")
        
        logger.info(f"✅ CHINA/HK COMPLIANCE: {'PASS' if len(sell_orders) == 0 else 'FAIL'}")
        
    except Exception as e:
        logger.error(f"❌ Error verifying grid: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🇨🇳 FIXING CHINA/HK GRID ALLOCATION")
    print("=" * 50)
    
    # Fix the grid allocation
    success = fix_china_hk_grid_allocation('600298.SS')
    
    if success:
        print("\n🔍 VERIFYING THE FIX...")
        verify_china_grid_fix('600298.SS')
        
        print("\n🎯 CHINA GRID ALLOCATION FIXED!")
        print("✅ Only BUY orders below current price")
        print("✅ $1M allocated across buy levels only")
        print("✅ No sell orders (China/HK compliant)")
        print("✅ Ready for grid trading during China market hours")
        
    else:
        print("\n❌ FAILED TO FIX GRID ALLOCATION")
        print("Please check the logs for details")
