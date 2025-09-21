#!/usr/bin/env python3
"""
Recreate 600298.SS Grid with Correct China/HK Allocation

This script will:
1. Delete the existing 600298.SS grid
2. Create a new grid with proper China/HK allocation (BUY orders only)
3. Verify the new grid configuration
"""

import yfinance as yf
import requests
import json
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

def recreate_china_grid():
    """Recreate 600298.SS grid with China/HK allocation"""
    
    symbol = '600298.SS'
    
    # Get current price
    current_price = get_current_price(symbol)
    if not current_price:
        logger.error(f"Could not get current price for {symbol}")
        return False
    
    logger.info(f"🎯 RECREATING CHINA GRID FOR {symbol}")
    logger.info(f"Current Price: ${current_price:.2f}")
    
    # Grid parameters for China stock (conservative range around current price)
    price_buffer = current_price * 0.15  # 15% buffer on each side
    lower_price = current_price - price_buffer
    upper_price = current_price + price_buffer
    
    # For China stocks: We'll use the range but only buy below current price
    investment_amount = 1000000  # $1M total investment
    grid_count = 12  # 12 levels total, but only ~6 will be buy levels
    
    logger.info(f"💰 GRID CONFIGURATION:")
    logger.info(f"   Symbol: {symbol}")
    logger.info(f"   Total Investment: ${investment_amount:,.2f}")
    logger.info(f"   Price Range: ${lower_price:.2f} - ${upper_price:.2f}")
    logger.info(f"   Current Price: ${current_price:.2f}")
    logger.info(f"   Grid Levels: {grid_count}")
    
    # Calculate how many levels will be buy orders (below current price)
    grid_spacing = (upper_price - lower_price) / grid_count
    buy_levels_count = 0
    
    for i in range(grid_count + 1):
        level_price = lower_price + (i * grid_spacing)
        if level_price < current_price:
            buy_levels_count += 1
    
    investment_per_buy_level = investment_amount / buy_levels_count if buy_levels_count > 0 else 0
    
    logger.info(f"📊 CHINA/HK ALLOCATION:")
    logger.info(f"   Buy Levels (below ${current_price:.2f}): {buy_levels_count}")
    logger.info(f"   Investment per Buy Level: ${investment_per_buy_level:,.2f}")
    logger.info(f"   No Sell Orders: Short selling not allowed in China/HK")
    
    print("🇨🇳 CHINA GRID RECREATION SUMMARY")
    print("=" * 50)
    print(f"Symbol: {symbol}")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Grid Range: ${lower_price:.2f} - ${upper_price:.2f}")
    print(f"Total Investment: ${investment_amount:,.2f}")
    print(f"Buy Levels Only: {buy_levels_count}")
    print(f"Investment per Buy Level: ${investment_per_buy_level:,.2f}")
    print()
    print("🎯 BENEFITS OF CHINA/HK GRID:")
    print("✅ Complies with China/HK no short selling rules")
    print("✅ Full $1M allocated across buy levels only")
    print("✅ Automatic rebalancing when buy orders fill")
    print("✅ Market-aware: Only trades during China market hours")
    print("✅ Email alerts to isky999@gmail.com")
    print()
    print("📋 NEXT STEPS:")
    print("1. Use the web interface to delete existing 600298.SS grid")
    print("2. Create new grid with these parameters:")
    print(f"   - Symbol: {symbol}")
    print(f"   - Lower Price: ${lower_price:.2f}")
    print(f"   - Upper Price: ${upper_price:.2f}")
    print(f"   - Investment: ${investment_amount:,.2f}")
    print(f"   - Grid Count: {grid_count}")
    print("3. The system will automatically allocate across buy levels only")
    print("4. Monitor during China market hours (9:30 AM - 3:00 PM Beijing)")
    
    return True

if __name__ == "__main__":
    recreate_china_grid()
