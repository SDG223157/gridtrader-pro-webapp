import os
import asyncio
from celery import Celery
from sqlalchemy.orm import sessionmaker
from database import engine, User, Portfolio, Holding, Grid, MarketData, Alert, GridOrder, OrderStatus, TransactionType
from decimal import Decimal
from data_provider import YFinanceDataProvider
from app.algorithms.grid_trading import GridTradingStrategy
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize Celery with error handling
try:
    celery_app = Celery(
        'gridtrader_tasks',
        broker=REDIS_URL,
        backend=REDIS_URL,
        include=['tasks']
    )
    logger.info(f"✅ Celery initialized with Redis: {REDIS_URL}")
except Exception as e:
    logger.warning(f"⚠️ Celery initialization failed: {e}")
    # Create a dummy celery app for development
    celery_app = Celery('gridtrader_tasks')
    logger.info("📝 Using dummy Celery app (Redis not available)")

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
data_provider = YFinanceDataProvider()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

@celery_app.task(bind=True, name='tasks.update_market_data')
def update_market_data(self):
    """Update market data for all tracked symbols"""
    try:
        db = get_db()
        
        # Get all unique symbols from holdings and grids
        holdings_symbols = db.query(Holding.symbol).distinct().all()
        grid_symbols = db.query(Grid.symbol).distinct().all()
        
        symbols = set()
        symbols.update([h.symbol for h in holdings_symbols])
        symbols.update([g.symbol for g in grid_symbols])
        
        # Add popular market symbols
        symbols.update(['SPY', 'QQQ', 'VTI', 'BTC-USD', 'ETH-USD'])
        
        symbols_list = list(symbols)
        
        if not symbols_list:
            logger.info("No symbols to update")
            return {"status": "success", "message": "No symbols to update"}
        
        logger.info(f"Updating market data for {len(symbols_list)} symbols")
        
        # Update market data
        results = data_provider.update_market_data(db, symbols_list, period="5d")
        
        db.close()
        
        logger.info(f"Market data update completed: {results}")
        return {
            "status": "success", 
            "symbols_updated": results["success"],
            "symbols_failed": results["failed"],
            "total_symbols": len(symbols_list)
        }
        
    except Exception as e:
        logger.error(f"Error updating market data: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name='tasks.update_portfolio_values')
def update_portfolio_values(self):
    """Update portfolio values and holdings"""
    try:
        db = get_db()
        
        portfolios = db.query(Portfolio).filter(Portfolio.status == "active").all()
        updated_count = 0
        
        for portfolio in portfolios:
            try:
                holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
                
                if not holdings:
                    continue
                
                # Get current prices for all holdings
                symbols = [h.symbol for h in holdings]
                current_prices = data_provider.get_multiple_prices(symbols)
                
                total_value = 0.0
                
                for holding in holdings:
                    current_price = current_prices.get(holding.symbol)
                    if current_price:
                        # Update holding values
                        holding.current_price = current_price
                        holding.market_value = float(holding.quantity) * current_price
                        holding.unrealized_pnl = holding.market_value - (float(holding.quantity) * float(holding.average_cost))
                        
                        total_value += holding.market_value
                
                # Update portfolio value
                portfolio.current_value = total_value + float(portfolio.cash_balance or 0)
                
                if float(portfolio.initial_capital) > 0:
                    portfolio.total_return = ((portfolio.current_value - float(portfolio.initial_capital)) / float(portfolio.initial_capital))
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error updating portfolio {portfolio.id}: {e}")
                continue
        
        db.commit()
        db.close()
        
        logger.info(f"Updated {updated_count} portfolios")
        return {
            "status": "success",
            "portfolios_updated": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error updating portfolio values: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name='tasks.process_grid_orders')
def process_grid_orders(self):
    """Process grid trading orders"""
    try:
        db = get_db()
        
        active_grids = db.query(Grid).filter(Grid.status == "active").all()
        processed_count = 0
        
        for grid in active_grids:
            try:
                current_price = data_provider.get_current_price(grid.symbol)
                if not current_price:
                    continue
                
                # Create grid strategy instance
                strategy = GridTradingStrategy(
                    symbol=grid.symbol,
                    upper_price=float(grid.upper_price),
                    lower_price=float(grid.lower_price),
                    grid_count=grid.strategy_config.get('grid_count', 10),
                    investment_amount=float(grid.investment_amount)
                )
                
                # Check if price is within grid bounds
                if current_price > float(grid.upper_price):
                    # Price above grid - create alert
                    alert = Alert(
                        user_id=grid.portfolio.user_id,
                        alert_type="grid",
                        title=f"Grid {grid.name} - Price Above Range",
                        message=f"{grid.symbol} price ${current_price:.2f} is above grid upper bound ${grid.upper_price:.2f}",
                        alert_metadata={"grid_id": grid.id, "symbol": grid.symbol, "price": current_price}
                    )
                    db.add(alert)
                    
                elif current_price < float(grid.lower_price):
                    # Price below grid - create alert
                    alert = Alert(
                        user_id=grid.portfolio.user_id,
                        alert_type="grid",
                        title=f"Grid {grid.name} - Price Below Range",
                        message=f"{grid.symbol} price ${current_price:.2f} is below grid lower bound ${grid.lower_price:.2f}",
                        alert_metadata={"grid_id": grid.id, "symbol": grid.symbol, "price": current_price}
                    )
                    db.add(alert)
                
                # Update grid status based on price position
                grid.strategy_config['current_price'] = current_price
                grid.strategy_config['last_updated'] = datetime.utcnow().isoformat()
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing grid {grid.id}: {e}")
                continue
        
        db.commit()
        db.close()
        
        logger.info(f"Processed {processed_count} grids")
        return {
            "status": "success",
            "grids_processed": processed_count
        }
        
    except Exception as e:
        logger.error(f"Error processing grid orders: {e}")
        return {"status": "error", "message": str(e)}

async def create_rebalancing_order(grid: Grid, filled_order: GridOrder, current_price: float, db: Session):
    """Create a new order to rebalance the grid after an order is filled"""
    try:
        if filled_order.order_type == TransactionType.buy:
            # After buy, create sell order at next grid level
            new_target_price = current_price + float(grid.grid_spacing)
            if new_target_price <= float(grid.upper_price):
                new_order = GridOrder(
                    grid_id=grid.id,
                    order_type=TransactionType.sell,
                    target_price=Decimal(str(new_target_price)),
                    quantity=filled_order.quantity,
                    status=OrderStatus.pending
                )
                db.add(new_order)
                grid.active_orders += 1
                logger.info(f"🔄 Created rebalancing SELL order at ${new_target_price:.2f}")
                
        elif filled_order.order_type == TransactionType.sell:
            # After sell, create buy order at next grid level
            new_target_price = current_price - float(grid.grid_spacing)
            if new_target_price >= float(grid.lower_price):
                new_order = GridOrder(
                    grid_id=grid.id,
                    order_type=TransactionType.buy,
                    target_price=Decimal(str(new_target_price)),
                    quantity=filled_order.quantity,
                    status=OrderStatus.pending
                )
                db.add(new_order)
                grid.active_orders += 1
                logger.info(f"🔄 Created rebalancing BUY order at ${new_target_price:.2f}")
                
    except Exception as e:
        logger.error(f"Error creating rebalancing order: {e}")

async def check_dynamic_grid_rebalancing(grid: Grid, current_price: float, db: Session):
    """Check if a dynamic grid needs bounds adjustment"""
    try:
        strategy_config = grid.strategy_config
        if not strategy_config or strategy_config.get('type') != 'dynamic_grid':
            return
            
        # Get volatility parameters
        center_price = strategy_config.get('center_price', current_price)
        volatility = strategy_config.get('volatility', 0.2)
        volatility_multiplier = strategy_config.get('volatility_multiplier', 2.0)
        
        # Calculate current bounds
        upper_bound = float(grid.upper_price)
        lower_bound = float(grid.lower_price)
        price_range = upper_bound - lower_bound
        
        # Check if price is approaching bounds (within 20% of boundary)
        upper_distance = (upper_bound - current_price) / price_range
        lower_distance = (current_price - lower_bound) / price_range
        
        should_rebalance = False
        rebalance_reason = ""
        
        if upper_distance < 0.2:  # Price within 20% of upper bound
            should_rebalance = True
            rebalance_reason = "approaching upper bound"
        elif lower_distance < 0.2:  # Price within 20% of lower bound
            should_rebalance = True
            rebalance_reason = "approaching lower bound"
        
        if should_rebalance:
            # Create alert for dynamic grid rebalancing
            alert = Alert(
                user_id=grid.portfolio.user_id,
                alert_type="grid",
                title=f"🧠 Dynamic Grid Rebalancing - {grid.name}",
                message=f"{grid.symbol} price ${current_price:.2f} is {rebalance_reason}. Dynamic grid bounds should be adjusted.",
                alert_metadata={
                    "grid_id": grid.id,
                    "symbol": grid.symbol,
                    "price": current_price,
                    "reason": rebalance_reason,
                    "alert_type": "dynamic_rebalancing_needed"
                }
            )
            db.add(alert)
            logger.info(f"🧠 Dynamic grid rebalancing alert created for {grid.symbol}")
            
    except Exception as e:
        logger.error(f"Error checking dynamic grid rebalancing: {e}")

@celery_app.task(bind=True, name='tasks.generate_alerts')
def generate_alerts(self):
    """Generate price and portfolio alerts"""
    try:
        db = get_db()
        
        # Get all active portfolios
        portfolios = db.query(Portfolio).filter(Portfolio.status == "active").all()
        alerts_created = 0
        
        for portfolio in portfolios:
            try:
                holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
                
                for holding in holdings:
                    current_price = data_provider.get_current_price(holding.symbol)
                    if not current_price:
                        continue
                    
                    # Check for significant price movements (>5% change)
                    if holding.current_price:
                        price_change = (current_price - float(holding.current_price)) / float(holding.current_price)
                        
                        if abs(price_change) > 0.05:  # 5% threshold
                            direction = "increased" if price_change > 0 else "decreased"
                            alert = Alert(
                                user_id=portfolio.user_id,
                                alert_type="price",
                                title=f"{holding.symbol} Price Alert",
                                message=f"{holding.symbol} has {direction} by {abs(price_change)*100:.1f}% to ${current_price:.2f}",
                                alert_metadata={
                                    "symbol": holding.symbol,
                                    "old_price": float(holding.current_price),
                                    "new_price": current_price,
                                    "change_percent": price_change * 100
                                }
                            )
                            db.add(alert)
                            alerts_created += 1
                
            except Exception as e:
                logger.error(f"Error generating alerts for portfolio {portfolio.id}: {e}")
                continue
        
        db.commit()
        db.close()
        
        logger.info(f"Generated {alerts_created} alerts")
        return {
            "status": "success",
            "alerts_created": alerts_created
        }
        
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name='tasks.cleanup_old_data')
def cleanup_old_data(self):
    """Clean up old market data and alerts"""
    try:
        db = get_db()
        
        # Remove market data older than 1 year
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        old_market_data = db.query(MarketData).filter(MarketData.created_at < one_year_ago).delete()
        
        # Remove read alerts older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        old_alerts = db.query(Alert).filter(
            Alert.created_at < thirty_days_ago,
            Alert.is_read == True
        ).delete()
        
        db.commit()
        db.close()
        
        logger.info(f"Cleaned up {old_market_data} market data records and {old_alerts} old alerts")
        return {
            "status": "success",
            "market_data_removed": old_market_data,
            "alerts_removed": old_alerts
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old data: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name='tasks.monitor_china_market_hours')
def monitor_china_market_hours(self):
    """Monitor China market hours and adjust task frequency"""
    try:
        import pytz
        from datetime import datetime, time as dt_time
        
        # Beijing timezone
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(beijing_tz)
        current_time = now_beijing.time()
        
        # Market hours: 9:30 AM - 3:00 PM Beijing Time
        market_open = dt_time(9, 30)
        market_close = dt_time(15, 0)
        is_weekday = now_beijing.weekday() < 5
        is_market_open = is_weekday and market_open <= current_time <= market_close
        
        # Log market status
        if is_market_open:
            logger.info(f"🟢 China market OPEN - {now_beijing.strftime('%H:%M:%S')} Beijing Time")
            
            # During market hours, trigger more frequent updates for grid trading
            # This could be used to dynamically adjust task frequencies
            
        else:
            logger.info(f"🔴 China market CLOSED - {now_beijing.strftime('%H:%M:%S')} Beijing Time")
            
            # Calculate time to next market open
            if current_time < market_open:
                next_open = now_beijing.replace(hour=9, minute=30, second=0, microsecond=0)
            else:
                # Next trading day
                next_day = now_beijing + timedelta(days=1)
                while next_day.weekday() >= 5:  # Skip weekends
                    next_day += timedelta(days=1)
                next_open = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
            
            time_to_open = next_open - now_beijing
            logger.info(f"⏰ Next market open in: {str(time_to_open).split('.')[0]}")
        
        return {
            "status": "success",
            "market_open": is_market_open,
            "beijing_time": now_beijing.strftime('%Y-%m-%d %H:%M:%S %Z'),
            "market_hours": "9:30 AM - 3:00 PM Beijing Time"
        }
        
    except Exception as e:
        logger.error(f"Error monitoring China market hours: {e}")
        return {"status": "error", "message": str(e)}

@celery_app.task(bind=True, name='tasks.monitor_grid_prices_realtime')
def monitor_grid_prices_realtime(self):
    """Monitor grid trading stock prices in real-time during China market hours"""
    try:
        import pytz
        from datetime import datetime, time as dt_time
        
        # Check if China market is open
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(beijing_tz)
        current_time = now_beijing.time()
        market_open = dt_time(9, 30)
        market_close = dt_time(15, 0)
        is_weekday = now_beijing.weekday() < 5
        is_market_open = is_weekday and market_open <= current_time <= market_close
        
        if not is_market_open:
            logger.info("📴 Skipping grid price monitoring - China market closed")
            return {"status": "skipped", "reason": "market_closed"}
        
        db = get_db()
        
        # Get all active grids
        active_grids = db.query(Grid).filter(Grid.status == "active").all()
        
        if not active_grids:
            logger.info("No active grids to monitor")
            return {"status": "success", "grids_monitored": 0}
        
        monitored_count = 0
        alerts_created = 0
        
        for grid in active_grids:
            try:
                # Get current price using yfinance (most reliable for China stocks)
                current_price = data_provider.get_current_price(grid.symbol)
                
                if not current_price:
                    continue
                
                # Check grid boundaries
                upper_boundary = float(grid.upper_price)
                lower_boundary = float(grid.lower_price)
                boundary_buffer = 0.50  # $0.50 buffer for alerts
                
                # Create boundary alerts
                if current_price <= lower_boundary + boundary_buffer:
                    # Approaching lower boundary
                    alert = Alert(
                        user_id=grid.portfolio.user_id,
                        alert_type="grid",
                        title=f"⚠️ Grid Boundary Alert - {grid.symbol}",
                        message=f"{grid.symbol} price ${current_price:.2f} approaching lower boundary ${lower_boundary:.2f}",
                        alert_metadata={
                            "grid_id": grid.id,
                            "symbol": grid.symbol,
                            "current_price": current_price,
                            "boundary_price": lower_boundary,
                            "boundary_type": "lower",
                            "distance": current_price - lower_boundary
                        }
                    )
                    db.add(alert)
                    alerts_created += 1
                    logger.info(f"⚠️ Lower boundary alert created for {grid.symbol}")
                    
                elif current_price >= upper_boundary - boundary_buffer:
                    # Approaching upper boundary
                    alert = Alert(
                        user_id=grid.portfolio.user_id,
                        alert_type="grid",
                        title=f"⚠️ Grid Boundary Alert - {grid.symbol}",
                        message=f"{grid.symbol} price ${current_price:.2f} approaching upper boundary ${upper_boundary:.2f}",
                        alert_metadata={
                            "grid_id": grid.id,
                            "symbol": grid.symbol,
                            "current_price": current_price,
                            "boundary_price": upper_boundary,
                            "boundary_type": "upper",
                            "distance": upper_boundary - current_price
                        }
                    )
                    db.add(alert)
                    alerts_created += 1
                    logger.info(f"⚠️ Upper boundary alert created for {grid.symbol}")
                
                monitored_count += 1
                
            except Exception as e:
                logger.error(f"Error monitoring grid {grid.id}: {e}")
                continue
        
        db.commit()
        db.close()
        
        logger.info(f"🔍 Monitored {monitored_count} grids, created {alerts_created} alerts")
        return {
            "status": "success",
            "grids_monitored": monitored_count,
            "alerts_created": alerts_created,
            "market_open": is_market_open,
            "beijing_time": now_beijing.strftime('%H:%M:%S')
        }
        
    except Exception as e:
        logger.error(f"Error monitoring grid prices: {e}")
        return {"status": "error", "message": str(e)}

# Schedule tasks optimized for China market hours (9:30 AM - 3:00 PM Beijing Time)
celery_app.conf.beat_schedule = {
    'update-market-data-frequent': {
        'task': 'tasks.update_market_data',
        'schedule': 60.0,  # Every 1 minute during market hours for grid trading
    },
    'update-portfolio-values': {
        'task': 'tasks.update_portfolio_values',
        'schedule': 300.0,  # Every 5 minutes (optimized for China stocks)
    },
    'process-grid-orders': {
        'task': 'tasks.process_grid_orders',
        'schedule': 60.0,  # Every 1 minute for real-time grid execution
    },
    'generate-alerts': {
        'task': 'tasks.generate_alerts',
        'schedule': 180.0,  # Every 3 minutes for faster alert response
    },
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': 86400.0,  # Once per day
    },
    'china-market-monitor': {
        'task': 'tasks.monitor_china_market_hours',
        'schedule': 300.0,  # Every 5 minutes - market status check
    },
    'grid-prices-realtime': {
        'task': 'tasks.monitor_grid_prices_realtime',
        'schedule': 60.0,  # Every 1 minute during China market hours
    },
}

celery_app.conf.timezone = 'UTC'

if __name__ == '__main__':
    celery_app.start()