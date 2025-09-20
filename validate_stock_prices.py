#!/usr/bin/env python3
"""
Quick price validation script - Use BEFORE any MCP portfolio building
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

def validate_and_get_prices(symbols, allocation_per_stock=250000):
    """
    Fetch and validate current prices for portfolio building
    
    MANDATORY: Always run this before using MCP buy_stock commands!
    """
    print("🔍 VALIDATING STOCK PRICES WITH YFINANCE")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target allocation: ${allocation_per_stock:,.2f} per stock")
    print("=" * 80)
    
    results = []
    
    for i, symbol in enumerate(symbols, 1):
        try:
            print(f"[{i:2d}/{len(symbols)}] {symbol}...", end=" ")
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                quantity = int(allocation_per_stock / current_price)
                actual_allocation = quantity * current_price
                
                results.append({
                    'symbol': symbol,
                    'current_price': round(current_price, 2),
                    'quantity': quantity,
                    'allocation': round(actual_allocation, 2)
                })
                
                print(f"✅ ${current_price:.2f} ({quantity:,} shares)")
            else:
                print("❌ No data")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Create DataFrame and save
    df = pd.DataFrame(results)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"validated_prices_{timestamp}.csv"
    df.to_csv(filename, index=False)
    
    total_allocation = df['allocation'].sum()
    
    print("\n" + "=" * 80)
    print("✅ PRICE VALIDATION COMPLETE")
    print("=" * 80)
    print(f"📊 Successful: {len(df)}/{len(symbols)} stocks")
    print(f"💰 Total allocation: ${total_allocation:,.2f}")
    print(f"🎯 Capital utilization: {total_allocation/10000000*100:.1f}%")
    print(f"💾 Data saved to: {filename}")
    print("\n🚨 IMPORTANT: Use these exact prices in MCP buy_stock commands!")
    print("🚨 Do NOT use estimated or outdated prices!")
    
    return df

# Example usage for 40 Chinese stocks
if __name__ == "__main__":
    chinese_stocks = [
        # Technology (14)
        "300857.SZ", "600487.SS", "300469.SZ", "300394.SZ", "002236.SZ", 
        "002402.SZ", "300620.SZ", "603083.SS", "688502.SS", "300803.SZ",
        "688347.SS", "688205.SS", "301309.SZ", "600410.SS",
        
        # New Materials (8)
        "002768.SZ", "600143.SS", "002683.SZ", "002549.SZ", "002226.SZ",
        "300539.SZ", "605488.SS", "601958.SS",
        
        # Consumer (7)
        "605499.SS", "000568.SZ", "300972.SZ", "300918.SZ", "600887.SS",
        "000858.SZ", "601579.SS",
        
        # Industrial Equipment (5)
        "601717.SS", "002008.SZ", "000988.SZ", "002158.SZ", "603757.SS",
        
        # Healthcare (4)
        "688506.SS", "603301.SS", "300049.SZ", "603259.SS",
        
        # Automotive (2)
        "002048.SZ", "601689.SS"
    ]
    
    # Validate prices
    validated_df = validate_and_get_prices(chinese_stocks)
    
    print("\n🎯 NEXT STEPS:")
    print("1. Create portfolio with MCP: mcp_gridtrader-pro_create_portfolio")
    print("2. Use the validated prices from the CSV file")
    print("3. Execute buy_stock commands with exact prices shown above")
    print("4. Verify all positions have 0% P&L")
