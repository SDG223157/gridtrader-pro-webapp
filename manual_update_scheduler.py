#!/usr/bin/env python3
"""
Manual Portfolio and Market Data Update Script
Simulates the scheduler tasks without requiring Celery/Redis infrastructure
"""

import os
import sys
from datetime import datetime, time as dt_time
import pytz
import logging
from sqlalchemy.orm import sessionmaker
from database import engine, Portfolio, Holding, Grid, MarketData, GridStatus
from data_provider import YFinanceDataProvider
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    """Get database session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def update_market_data_manual():
    """Update market data ONLY for stocks with active grid trading strategies"""
    try:
        logger.info("🚀 Starting manual market data update...")
        
        # Market time checking
        us_tz = pytz.timezone('US/Eastern')
        beijing_tz = pytz.timezone('Asia/Shanghai')
        
        now_us = datetime.now(us_tz)
        now_beijing = datetime.now(beijing_tz)
        
        is_weekday = now_us.weekday() < 5
        
        # Market hours check
        us_market_open = (is_weekday and dt_time(9, 30) <= now_us.time() <= dt_time(16, 0))
        china_market_open = (is_weekday and dt_time(9, 30) <= now_beijing.time() <= dt_time(15, 0))
        hk_market_open = (is_weekday and dt_time(9, 30) <= now_beijing.time() <= dt_time(16, 0))
        
        active_markets = []
        if us_market_open:
            active_markets.append("🇺🇸 US")
        if china_market_open:
            active_markets.append("🇨🇳 China")
        if hk_market_open:
            active_markets.append("🇭🇰 Hong Kong")
        
        logger.info(f"⏰ Current Times:")
        logger.info(f"   US Eastern: {now_us.strftime('%H:%M:%S %Z')}")
        logger.info(f"   Beijing: {now_beijing.strftime('%H:%M:%S %Z')}")
        logger.info(f"   Active Markets: {', '.join(active_markets) if active_markets else 'All closed'}")
        
        db = get_db()
        data_provider = YFinanceDataProvider()
        
        try:
            # Get ONLY symbols that have ACTIVE grid trading strategies
            active_grid_symbols = db.query(Grid.symbol).filter(
                Grid.status == GridStatus.active
            ).distinct().all()
            
            if not active_grid_symbols:
                logger.info("📝 No active grid trading strategies found")
                return {"status": "success", "reason": "no_active_grids"}
            
            symbols_to_monitor = [symbol[0] for symbol in active_grid_symbols]
            logger.info(f"🎯 Found {len(symbols_to_monitor)} active grid symbols: {symbols_to_monitor}")
            
            # For manual update, we'll update regardless of market hours to get current data
            symbols_to_update = symbols_to_monitor
            
            logger.info(f"📊 Updating market data for {len(symbols_to_update)} grid symbols...")
            
            updated_count = 0
            failed_count = 0
            
            for symbol in symbols_to_update:
                try:
                    # Get current price using data provider
                    current_data = data_provider.get_current_price(symbol)
                    
                    if current_data and 'price' in current_data:
                        price = Decimal(str(current_data['price']))
                        
                        # Update or create market data record
                        market_data = db.query(MarketData).filter_by(symbol=symbol).first()
                        if market_data:
                            market_data.current_price = price
                            market_data.updated_at = datetime.utcnow()
                        else:
                            market_data = MarketData(
                                symbol=symbol,
                                current_price=price,
                                updated_at=datetime.utcnow()
                            )
                            db.add(market_data)
                        
                        updated_count += 1
                        logger.info(f"✅ Updated {symbol}: ${price}")
                    else:
                        failed_count += 1
                        logger.warning(f"❌ Failed to get price for {symbol}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"❌ Error updating {symbol}: {e}")
                    continue
            
            db.commit()
            
            result = {
                "status": "success",
                "symbols_updated": updated_count,
                "symbols_failed": failed_count,
                "total_symbols": len(symbols_to_update),
                "active_grid_symbols": symbols_to_monitor
            }
            
            logger.info(f"✅ Market data update complete: {updated_count} updated, {failed_count} failed")
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in market data update: {e}")
        return {"status": "error", "message": str(e)}

def update_portfolio_values_manual():
    """Update portfolio values and holdings"""
    try:
        logger.info("🚀 Starting manual portfolio values update...")
        
        db = get_db()
        data_provider = YFinanceDataProvider()
        
        try:
            portfolios = db.query(Portfolio).all()
            updated_count = 0
            
            logger.info(f"📊 Found {len(portfolios)} portfolios to update")
            
            for portfolio in portfolios:
                try:
                    holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
                    
                    if not holdings:
                        logger.info(f"⏭️ Skipping {portfolio.name} - no holdings")
                        continue
                    
                    logger.info(f"💼 Updating portfolio: {portfolio.name} ({len(holdings)} holdings)")
                    
                    # Get current prices for all holdings
                    symbols = [h.symbol for h in holdings]
                    total_value = 0.0
                    holdings_updated = 0
                    
                    for holding in holdings:
                        try:
                            current_data = data_provider.get_current_price(holding.symbol)
                            if current_data and 'price' in current_data:
                                current_price = float(current_data['price'])
                                
                                # Update holding values
                                holding.current_price = current_price
                                holding.market_value = float(holding.quantity) * current_price
                                holding.unrealized_pnl = holding.market_value - (float(holding.quantity) * float(holding.average_cost))
                                
                                total_value += holding.market_value
                                holdings_updated += 1
                                
                                logger.info(f"   ✅ {holding.symbol}: ${current_price:.2f} (Market Value: ${holding.market_value:,.2f})")
                            else:
                                logger.warning(f"   ❌ Failed to get price for {holding.symbol}")
                        except Exception as e:
                            logger.error(f"   ❌ Error updating holding {holding.symbol}: {e}")
                    
                    # Update portfolio value
                    old_value = portfolio.current_value
                    portfolio.current_value = total_value + float(portfolio.cash_balance or 0)
                    
                    # Calculate return
                    if float(portfolio.initial_capital) > 0:
                        portfolio.total_return = ((portfolio.current_value - float(portfolio.initial_capital)) / float(portfolio.initial_capital))
                    
                    updated_count += 1
                    
                    logger.info(f"   📈 Portfolio value: ${old_value:,.2f} → ${portfolio.current_value:,.2f}")
                    logger.info(f"   💰 Cash balance: ${float(portfolio.cash_balance):,.2f}")
                    logger.info(f"   📊 Total return: {portfolio.total_return*100:.2f}%")
                    
                except Exception as e:
                    logger.error(f"❌ Error updating portfolio {portfolio.name}: {e}")
                    continue
            
            db.commit()
            
            result = {
                "status": "success",
                "portfolios_updated": updated_count,
                "total_portfolios": len(portfolios)
            }
            
            logger.info(f"✅ Portfolio values update complete: {updated_count} portfolios updated")
            return result
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in portfolio values update: {e}")
        return {"status": "error", "message": str(e)}

def main():
    """Run manual scheduler update"""
    print("🚀 MANUAL SCHEDULER UPDATE")
    print("=" * 50)
    
    # Step 1: Update market data for grid trading stocks
    print("\n📊 STEP 1: UPDATING MARKET DATA (Grid Trading Stocks)")
    print("-" * 50)
    market_result = update_market_data_manual()
    print(f"Result: {market_result}")
    
    # Step 2: Update portfolio values
    print("\n💼 STEP 2: UPDATING PORTFOLIO VALUES")
    print("-" * 50)
    portfolio_result = update_portfolio_values_manual()
    print(f"Result: {portfolio_result}")
    
    # Summary
    print("\n🎯 SCHEDULER UPDATE SUMMARY")
    print("=" * 50)
    
    if market_result["status"] == "success":
        if "symbols_updated" in market_result:
            print(f"✅ Market Data: {market_result['symbols_updated']} symbols updated")
            if market_result.get('active_grid_symbols'):
                print(f"   Grid Symbols: {market_result['active_grid_symbols']}")
        else:
            print(f"✅ Market Data: {market_result.get('reason', 'completed')}")
    else:
        print(f"❌ Market Data: {market_result.get('message', 'failed')}")
    
    if portfolio_result["status"] == "success":
        print(f"✅ Portfolio Values: {portfolio_result['portfolios_updated']} portfolios updated")
    else:
        print(f"❌ Portfolio Values: {portfolio_result.get('message', 'failed')}")
    
    print("\n🎯 All scheduler tasks completed!")
    print("Your portfolio stocks' prices and portfolio values have been updated.")

if __name__ == "__main__":
    main()
