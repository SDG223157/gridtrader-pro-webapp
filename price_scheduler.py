"""
Daily price refresh scheduler.
Runs once per day after each market closes to update all holdings.
No Redis/Celery — uses APScheduler in-process.

Schedule (all times local to each market):
  - China (SH/SZ):  3:30 PM Asia/Shanghai  (market closes 3:00 PM)
  - Hong Kong:      4:30 PM Asia/Shanghai  (market closes 4:00 PM)
  - US:             4:30 PM US/Eastern     (market closes 4:00 PM)
"""
import logging
from decimal import Decimal
from datetime import datetime

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from database import SessionLocal, Portfolio, Holding
from data_provider import YFinanceDataProvider

logger = logging.getLogger(__name__)
data_provider = YFinanceDataProvider()


def _get_db() -> Session:
    return SessionLocal()


def _classify_symbol(symbol: str) -> str:
    if symbol.endswith('.SS') or symbol.endswith('.SZ'):
        return 'CN'
    if symbol.endswith('.HK'):
        return 'HK'
    return 'US'


def refresh_prices(market_filter: str | None = None):
    """
    Fetch latest closing prices and update holdings + portfolio values.
    market_filter: 'CN', 'HK', 'US', or None for all.
    """
    label = market_filter or 'ALL'
    logger.info(f"[Scheduler] Starting daily price refresh for {label} holdings")

    db = _get_db()
    try:
        portfolios = db.query(Portfolio).all()
        total_updated = 0

        for portfolio in portfolios:
            holdings = db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
            if not holdings:
                continue

            symbols = [h.symbol for h in holdings
                       if market_filter is None or _classify_symbol(h.symbol) == market_filter]
            if not symbols:
                continue

            prices = data_provider.get_multiple_prices(symbols)

            for holding in holdings:
                price = prices.get(holding.symbol)
                if price is None:
                    continue
                holding.current_price = Decimal(str(price))
                holding.market_value = float(holding.quantity or 0) * price
                avg_cost = float(holding.average_cost or 0)
                holding.unrealized_pnl = holding.market_value - (float(holding.quantity or 0) * avg_cost)
                total_updated += 1

            cash = float(portfolio.cash_balance or 0)
            holdings_val = sum(
                float(h.quantity or 0) * float(h.current_price or 0)
                for h in holdings
            )
            portfolio.current_value = cash + holdings_val
            if float(portfolio.initial_capital or 0) > 0:
                portfolio.total_return = (
                    (portfolio.current_value - float(portfolio.initial_capital))
                    / float(portfolio.initial_capital)
                )

        db.commit()
        logger.info(f"[Scheduler] {label} refresh done — {total_updated} holdings updated across {len(portfolios)} portfolios")

    except Exception as e:
        logger.exception(f"[Scheduler] {label} price refresh failed: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(daemon=True)

    # China A-shares: daily at 15:30 Asia/Shanghai (Mon-Fri)
    scheduler.add_job(
        refresh_prices,
        CronTrigger(hour=15, minute=30, day_of_week='mon-fri', timezone=pytz.timezone('Asia/Shanghai')),
        args=['CN'],
        id='refresh_cn',
        replace_existing=True,
    )

    # Hong Kong: daily at 16:30 Asia/Shanghai (Mon-Fri)
    scheduler.add_job(
        refresh_prices,
        CronTrigger(hour=16, minute=30, day_of_week='mon-fri', timezone=pytz.timezone('Asia/Shanghai')),
        args=['HK'],
        id='refresh_hk',
        replace_existing=True,
    )

    # US: daily at 16:30 US/Eastern (Mon-Fri)
    scheduler.add_job(
        refresh_prices,
        CronTrigger(hour=16, minute=30, day_of_week='mon-fri', timezone=pytz.timezone('US/Eastern')),
        args=['US'],
        id='refresh_us',
        replace_existing=True,
    )

    scheduler.start()

    jobs = scheduler.get_jobs()
    for job in jobs:
        logger.info(f"[Scheduler] Job '{job.id}' → next run: {job.next_run_time}")

    return scheduler
