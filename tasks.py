import os
import asyncio
from celery import Celery
from sqlalchemy.orm import sessionmaker
from database import engine, User, Portfolio, Holding, Grid, MarketData, Alert
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
                        metadata={"grid_id": grid.id, "symbol": grid.symbol, "price": current_price}
                    )
                    db.add(alert)
                    
                elif current_price < float(grid.lower_price):
                    # Price below grid - create alert
                    alert = Alert(
                        user_id=grid.portfolio.user_id,
                        alert_type="grid",
                        title=f"Grid {grid.name} - Price Below Range",
                        message=f"{grid.symbol} price ${current_price:.2f} is below grid lower bound ${grid.lower_price:.2f}",
                        metadata={"grid_id": grid.id, "symbol": grid.symbol, "price": current_price}
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
                                metadata={
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

# Schedule tasks
celery_app.conf.beat_schedule = {
    'update-market-data': {
        'task': 'tasks.update_market_data',
        'schedule': 300.0,  # Every 5 minutes during market hours
    },
    'update-portfolio-values': {
        'task': 'tasks.update_portfolio_values',
        'schedule': 600.0,  # Every 10 minutes
    },
    'process-grid-orders': {
        'task': 'tasks.process_grid_orders',
        'schedule': 180.0,  # Every 3 minutes
    },
    'generate-alerts': {
        'task': 'tasks.generate_alerts',
        'schedule': 900.0,  # Every 15 minutes
    },
    'cleanup-old-data': {
        'task': 'tasks.cleanup_old_data',
        'schedule': 86400.0,  # Once per day
    },
}

celery_app.conf.timezone = 'UTC'

if __name__ == '__main__':
    celery_app.start()