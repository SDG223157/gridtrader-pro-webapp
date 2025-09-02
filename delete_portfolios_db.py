#!/usr/bin/env python3
"""
Direct database script to delete all portfolios
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration (using the same as main_simple.py)
DATABASE_URL = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://root:password@localhost:3306/gridtrader_pro')

def delete_all_portfolios():
    """Delete all portfolios and associated data directly from database"""
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("🗑️ GridTrader Pro Database Portfolio Deletion")
        print("=" * 50)
        
        # Get portfolio count first
        result = session.execute(text("SELECT COUNT(*) FROM portfolios"))
        portfolio_count = result.fetchone()[0]
        
        if portfolio_count == 0:
            print("✅ No portfolios found to delete")
            return
            
        print(f"📊 Found {portfolio_count} portfolio(s) to delete")
        
        # Get portfolio details for confirmation
        result = session.execute(text("""
            SELECT id, name, current_value 
            FROM portfolios 
            ORDER BY name
        """))
        portfolios = result.fetchall()
        
        print("\n📋 Portfolios to delete:")
        for portfolio in portfolios:
            print(f"   • {portfolio[1]} (ID: {portfolio[0]}) - ${portfolio[2]:,.2f}")
        
        print("\n⚠️  WARNING: This will permanently delete ALL portfolios and their data!")
        print("⚠️  This includes: holdings, transactions, grids, grid orders")
        print("⚠️  This action cannot be undone!")
        
        # Confirm deletion
        confirm = input("\nType 'DELETE ALL' to confirm: ")
        if confirm != "DELETE ALL":
            print("❌ Deletion cancelled")
            return
        
        print("\n🗑️ Starting deletion process...")
        
        # Delete in proper order to avoid foreign key constraints
        
        # 1. Delete grid orders
        result = session.execute(text("DELETE FROM grid_orders"))
        grid_orders_deleted = result.rowcount
        print(f"✅ Deleted {grid_orders_deleted} grid orders")
        
        # 2. Delete grids
        result = session.execute(text("DELETE FROM grids"))
        grids_deleted = result.rowcount
        print(f"✅ Deleted {grids_deleted} grids")
        
        # 3. Delete holdings
        result = session.execute(text("DELETE FROM holdings"))
        holdings_deleted = result.rowcount
        print(f"✅ Deleted {holdings_deleted} holdings")
        
        # 4. Delete transactions
        result = session.execute(text("DELETE FROM transactions"))
        transactions_deleted = result.rowcount
        print(f"✅ Deleted {transactions_deleted} transactions")
        
        # 5. Delete portfolios
        result = session.execute(text("DELETE FROM portfolios"))
        portfolios_deleted = result.rowcount
        print(f"✅ Deleted {portfolios_deleted} portfolios")
        
        # Commit all changes
        session.commit()
        
        print("\n" + "=" * 50)
        print("🎉 ALL PORTFOLIOS DELETED SUCCESSFULLY!")
        print(f"📊 Deletion Summary:")
        print(f"   • Portfolios: {portfolios_deleted}")
        print(f"   • Holdings: {holdings_deleted}")
        print(f"   • Transactions: {transactions_deleted}")
        print(f"   • Grids: {grids_deleted}")
        print(f"   • Grid Orders: {grid_orders_deleted}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during deletion: {e}")
        logger.error(f"Deletion failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    delete_all_portfolios()
