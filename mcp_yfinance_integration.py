#!/usr/bin/env python3
"""
MCP Command Integration with yfinance Price Validation
This function is specifically designed to work with MCP buy_stock commands
"""

import yfinance as yf
from typing import List, Dict, Tuple
from datetime import datetime

def get_current_price_for_mcp(symbol: str) -> float:
    """
    Get current price for a single stock for MCP buy_stock command
    
    Args:
        symbol: Stock symbol (e.g., '300857.SZ', '600487.SS')
        
    Returns:
        Current price as float for direct use in MCP buy_stock
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            print(f"✅ {symbol}: ${current_price:.2f}")
            return round(float(current_price), 2)
        else:
            print(f"❌ {symbol}: No data available")
            return 0.0
            
    except Exception as e:
        print(f"❌ {symbol}: Error - {str(e)[:50]}")
        return 0.0

def get_mcp_buy_params(symbol: str, allocation: float = 250000) -> Tuple[int, float]:
    """
    Get quantity and current price for MCP buy_stock command
    
    Args:
        symbol: Stock symbol
        allocation: Target allocation in currency (default: 250000 RMB)
        
    Returns:
        Tuple of (quantity, current_price) ready for MCP buy_stock
    """
    current_price = get_current_price_for_mcp(symbol)
    
    if current_price > 0:
        quantity = int(allocation / current_price)
        return quantity, current_price
    else:
        return 0, 0.0

def validate_mcp_portfolio_prices(symbols: List[str], allocation_per_stock: float = 250000) -> Dict[str, Dict]:
    """
    Validate prices for entire portfolio before MCP execution
    
    Args:
        symbols: List of stock symbols
        allocation_per_stock: Target allocation per stock
        
    Returns:
        Dictionary with symbol -> {quantity, price, allocation} for MCP commands
    """
    print("🔍 MCP PRICE VALIDATION WITH YFINANCE")
    print(f"📊 Validating {len(symbols)} stocks for MCP buy_stock commands")
    print(f"💰 Target allocation: ${allocation_per_stock:,.2f} per stock")
    print("=" * 80)
    
    validated_data = {}
    total_allocation = 0
    successful_count = 0
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i:2d}/{len(symbols)}] {symbol}...", end=" ")
        
        quantity, price = get_mcp_buy_params(symbol, allocation_per_stock)
        
        if price > 0:
            actual_allocation = quantity * price
            validated_data[symbol] = {
                'quantity': quantity,
                'price': price,
                'allocation': actual_allocation,
                'timestamp': datetime.now().isoformat()
            }
            total_allocation += actual_allocation
            successful_count += 1
        else:
            validated_data[symbol] = {
                'quantity': 0,
                'price': 0.0,
                'allocation': 0.0,
                'error': 'Failed to fetch price'
            }
    
    print("\n" + "=" * 80)
    print("📈 MCP VALIDATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {successful_count}/{len(symbols)}")
    print(f"💰 Total allocation: ${total_allocation:,.2f}")
    print(f"🎯 Capital utilization: {total_allocation/(len(symbols)*allocation_per_stock)*100:.1f}%")
    print(f"⏰ Validation time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return validated_data

def execute_mcp_buy_commands(portfolio_id: str, validated_data: Dict[str, Dict], stock_names: Dict[str, str] = None):
    """
    Generate exact MCP buy_stock commands using validated yfinance data
    
    Args:
        portfolio_id: Portfolio ID for MCP commands
        validated_data: Output from validate_mcp_portfolio_prices()
        stock_names: Optional mapping of symbols to company names
    """
    print("🛠️ GENERATING MCP BUY_STOCK COMMANDS")
    print(f"📋 Portfolio ID: {portfolio_id}")
    print("=" * 80)
    
    successful_commands = []
    
    for symbol, data in validated_data.items():
        if data['price'] > 0:
            company_name = stock_names.get(symbol, symbol) if stock_names else symbol
            
            command_text = f"""
mcp_gridtrader-pro_buy_stock(
    portfolio_id="{portfolio_id}",
    symbol="{symbol}",
    quantity={data['quantity']},
    price={data['price']},
    notes="{company_name} - yfinance validated ${data['price']:.2f}"
)"""
            
            successful_commands.append(command_text)
            print(f"✅ {symbol}: {data['quantity']} shares @ ${data['price']:.2f} = ${data['allocation']:,.2f}")
    
    print(f"\n📊 Generated {len(successful_commands)} MCP buy commands")
    print("🚨 IMPORTANT: These prices are validated with yfinance for zero P&L!")
    
    return successful_commands

# Example usage for immediate MCP integration
def quick_mcp_validation(symbols: List[str]) -> None:
    """
    Quick validation function for immediate MCP use
    """
    print("⚡ QUICK MCP PRICE VALIDATION")
    print("=" * 50)
    
    for symbol in symbols:
        quantity, price = get_mcp_buy_params(symbol)
        if price > 0:
            print(f"{symbol}: quantity={quantity}, price={price:.2f}")
        else:
            print(f"{symbol}: ❌ FAILED TO GET PRICE")

if __name__ == "__main__":
    # Example: Validate a few stocks for MCP
    test_symbols = ["300857.SZ", "600487.SS", "300469.SZ"]
    
    print("🧪 TESTING MCP INTEGRATION")
    quick_mcp_validation(test_symbols)
    
    print("\n🎯 FOR FULL PORTFOLIO:")
    print("1. Use validate_mcp_portfolio_prices() with all 40 symbols")
    print("2. Use execute_mcp_buy_commands() to generate exact MCP calls")
    print("3. Execute the generated MCP commands")
    print("4. Verify zero P&L results")
