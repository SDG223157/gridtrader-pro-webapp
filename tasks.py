"""
Standalone helper functions for portfolio calculations.
Celery/Redis has been removed — background tasks are no longer used.
"""
import logging
from decimal import Decimal
from sqlalchemy.orm import sessionmaker, Session
from database import engine, Portfolio, Holding, Grid, GridStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def calculate_portfolio_value(portfolio: Portfolio, db: Session) -> Decimal:
    """Calculate total portfolio value including cash balance, holdings, and active grid allocations."""
    try:
        total_value = portfolio.cash_balance or Decimal('0')

        holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        holdings_value = Decimal('0')
        for holding in holdings:
            holding_market_value = (holding.quantity or Decimal('0')) * (holding.current_price or Decimal('0'))
            total_value += holding_market_value
            holdings_value += holding_market_value

        active_grids = db.query(Grid).filter(
            Grid.portfolio_id == portfolio.id,
            Grid.status == GridStatus.active
        ).all()

        grid_allocations = Decimal('0')
        for grid in active_grids:
            grid_allocation = grid.investment_amount or Decimal('0')
            total_value += grid_allocation
            grid_allocations += grid_allocation

        logger.info(
            f"Portfolio {portfolio.name} total value: {total_value} "
            f"(cash: {portfolio.cash_balance}, holdings: {holdings_value}, grids: {grid_allocations})"
        )
        return total_value

    except Exception as e:
        logger.error(f"Error calculating portfolio value: {e}")
        return portfolio.cash_balance or Decimal('0')


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e
