#!/usr/bin/env python3
"""
Standardized Portfolio Building Workflow with yfinance Price Validation
This script ensures accurate pricing and zero P&L when building portfolios with MCP tools.
"""

import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime
from typing import List, Dict, Any

class PortfolioBuilder:
    """
    Standardized portfolio builder that enforces yfinance price validation
    """
    
    def __init__(self, total_capital: float = 10000000, allocation_per_stock: float = 250000):
        """
        Initialize portfolio builder
        
        Args:
            total_capital: Total portfolio capital (default: 10M RMB)
            allocation_per_stock: Target allocation per stock (default: 250K RMB)
        """
        self.total_capital = total_capital
        self.allocation_per_stock = allocation_per_stock
        self.stocks_data = []
        self.price_fetch_timestamp = None
        
    def fetch_current_prices(self, stock_symbols: List[str], stock_names: Dict[str, str] = None) -> pd.DataFrame:
        """
        MANDATORY STEP 1: Fetch current prices using yfinance
        
        Args:
            stock_symbols: List of stock symbols (e.g., ['300857.SZ', '600487.SS'])
            stock_names: Optional mapping of symbols to names
            
        Returns:
            DataFrame with current prices and calculated quantities
        """
        print("🔍 STEP 1: Fetching current prices with yfinance...")
        print(f"📊 Stocks to fetch: {len(stock_symbols)}")
        print(f"💰 Total capital: ${self.total_capital:,.2f}")
        print(f"🎯 Target allocation per stock: ${self.allocation_per_stock:,.2f}")
        print("=" * 80)
        
        self.price_fetch_timestamp = datetime.now()
        successful_fetches = 0
        failed_fetches = 0
        
        for i, symbol in enumerate(stock_symbols, 1):
            try:
                print(f"[{i:2d}/{len(stock_symbols)}] Fetching {symbol}...", end=" ")
                
                # Get stock data using yfinance
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    
                    # Calculate quantity for target allocation
                    quantity = int(self.allocation_per_stock / current_price)
                    actual_allocation = quantity * current_price
                    
                    stock_info = {
                        'symbol': symbol,
                        'name': stock_names.get(symbol, symbol) if stock_names else symbol,
                        'current_price': round(current_price, 2),
                        'quantity': quantity,
                        'allocation': round(actual_allocation, 2),
                        'status': 'SUCCESS',
                        'fetch_time': self.price_fetch_timestamp.isoformat()
                    }
                    
                    self.stocks_data.append(stock_info)
                    print(f"✅ ${current_price:.2f} ({quantity:,} shares)")
                    successful_fetches += 1
                else:
                    print("❌ No data available")
                    failed_fetches += 1
                    
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}")
                failed_fetches += 1
                
            # Small delay to avoid rate limiting
            time.sleep(0.1)
        
        # Create DataFrame
        df = pd.DataFrame(self.stocks_data)
        
        # Summary
        total_allocation = df['allocation'].sum() if not df.empty else 0
        print("\n" + "=" * 80)
        print("📈 YFINANCE PRICE FETCH SUMMARY")
        print("=" * 80)
        print(f"✅ Successful: {successful_fetches}/{len(stock_symbols)} ({successful_fetches/len(stock_symbols)*100:.1f}%)")
        print(f"❌ Failed: {failed_fetches}")
        print(f"💰 Total Allocation: ${total_allocation:,.2f}")
        print(f"🎯 Capital Utilization: {total_allocation/self.total_capital*100:.1f}%")
        print(f"⏰ Fetch Time: {self.price_fetch_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save to CSV for reference
        csv_filename = f"portfolio_prices_{self.price_fetch_timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"💾 Data saved to: {csv_filename}")
        
        return df
    
    def validate_prices(self) -> bool:
        """
        MANDATORY STEP 2: Validate that prices were fetched recently
        
        Returns:
            True if prices are valid and recent, False otherwise
        """
        if not self.stocks_data:
            print("❌ ERROR: No price data available. Run fetch_current_prices() first!")
            return False
            
        if not self.price_fetch_timestamp:
            print("❌ ERROR: No price fetch timestamp. Run fetch_current_prices() first!")
            return False
            
        # Check if prices are recent (within last 30 minutes)
        time_diff = (datetime.now() - self.price_fetch_timestamp).total_seconds()
        if time_diff > 1800:  # 30 minutes
            print(f"⚠️ WARNING: Prices are {time_diff/60:.1f} minutes old. Consider refetching.")
            return False
            
        print(f"✅ VALIDATION PASSED: Prices are {time_diff/60:.1f} minutes old and valid.")
        return True
    
    def generate_mcp_commands(self, portfolio_id: str) -> List[str]:
        """
        STEP 3: Generate MCP buy_stock commands with validated prices
        
        Args:
            portfolio_id: The portfolio ID to buy stocks for
            
        Returns:
            List of MCP command strings ready for execution
        """
        if not self.validate_prices():
            raise ValueError("Price validation failed. Fetch current prices first!")
            
        print("🛠️ STEP 3: Generating MCP buy_stock commands...")
        print(f"📋 Portfolio ID: {portfolio_id}")
        print("=" * 80)
        
        commands = []
        
        for stock in self.stocks_data:
            if stock['status'] == 'SUCCESS':
                command = (
                    f"mcp_gridtrader-pro_buy_stock("
                    f"portfolio_id='{portfolio_id}', "
                    f"symbol='{stock['symbol']}', "
                    f"quantity={stock['quantity']}, "
                    f"price={stock['current_price']}, "
                    f"notes='{stock['name']} - yfinance validated price')"
                )
                commands.append(command)
                print(f"✅ {stock['symbol']}: {stock['quantity']} shares @ ${stock['current_price']:.2f}")
        
        print(f"\n📊 Generated {len(commands)} MCP buy commands")
        return commands
    
    def save_execution_plan(self) -> str:
        """
        Save complete execution plan for reference
        """
        plan = {
            "metadata": {
                "total_capital": self.total_capital,
                "allocation_per_stock": self.allocation_per_stock,
                "price_fetch_timestamp": self.price_fetch_timestamp.isoformat(),
                "total_stocks": len(self.stocks_data),
                "successful_fetches": len([s for s in self.stocks_data if s['status'] == 'SUCCESS'])
            },
            "stocks": self.stocks_data,
            "workflow_steps": [
                "1. Fetch current prices with yfinance ✅",
                "2. Validate price data ✅", 
                "3. Generate MCP commands ✅",
                "4. Execute MCP buy_stock commands (manual)",
                "5. Verify zero P&L results (manual)"
            ]
        }
        
        filename = f"portfolio_execution_plan_{self.price_fetch_timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(plan, f, indent=2)
            
        print(f"💾 Execution plan saved to: {filename}")
        return filename

def main():
    """
    Example usage of the standardized portfolio building workflow
    """
    print("🚀 STANDARDIZED PORTFOLIO BUILDING WORKFLOW")
    print("=" * 80)
    
    # Example: 40 Chinese leading stocks
    chinese_stocks = [
        # Technology Sector (14 stocks)
        "300857.SZ", "600487.SS", "300469.SZ", "300394.SZ", "002236.SZ", 
        "002402.SZ", "300620.SZ", "603083.SS", "688502.SS", "300803.SZ",
        "688347.SS", "688205.SS", "301309.SZ", "600410.SS",
        
        # New Materials Sector (8 stocks)
        "002768.SZ", "600143.SS", "002683.SZ", "002549.SZ", "002226.SZ",
        "300539.SZ", "605488.SS", "601958.SS",
        
        # Consumer Sector (7 stocks)
        "605499.SS", "000568.SZ", "300972.SZ", "300918.SZ", "600887.SS",
        "000858.SZ", "601579.SS",
        
        # Industrial Equipment Sector (5 stocks)
        "601717.SS", "002008.SZ", "000988.SZ", "002158.SZ", "603757.SS",
        
        # Healthcare Sector (4 stocks)
        "688506.SS", "603301.SS", "300049.SZ", "603259.SS",
        
        # Automotive Sector (2 stocks)
        "002048.SZ", "601689.SS"
    ]
    
    # Stock names mapping
    stock_names = {
        "300857.SZ": "协创数据", "600487.SS": "亨通光电", "300469.SZ": "信息发展", 
        "300394.SZ": "天孚通信", "002236.SZ": "大华股份", "002402.SZ": "和而泰",
        # ... (add all 40 stock names)
    }
    
    # Initialize portfolio builder
    builder = PortfolioBuilder(total_capital=10000000, allocation_per_stock=250000)
    
    # MANDATORY STEP 1: Fetch current prices
    prices_df = builder.fetch_current_prices(chinese_stocks, stock_names)
    
    # MANDATORY STEP 2: Validate prices
    if not builder.validate_prices():
        print("❌ Price validation failed. Aborting.")
        return
    
    # STEP 3: Generate MCP commands
    portfolio_id = "YOUR_PORTFOLIO_ID_HERE"  # Replace with actual portfolio ID
    mcp_commands = builder.generate_mcp_commands(portfolio_id)
    
    # STEP 4: Save execution plan
    plan_file = builder.save_execution_plan()
    
    print("\n🎉 WORKFLOW COMPLETE!")
    print("=" * 80)
    print("📋 Next Steps:")
    print("1. ✅ Prices fetched and validated")
    print("2. ✅ MCP commands generated")
    print("3. 🔄 Execute MCP commands manually")
    print("4. 🔍 Verify all stocks have 0% P&L")
    print(f"5. 📁 Reference files: {plan_file}")

if __name__ == "__main__":
    main()
