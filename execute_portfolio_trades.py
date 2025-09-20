#!/usr/bin/env python3
"""
Execute all 40 stock trades for the portfolio using current yfinance prices
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime

# Portfolio ID
PORTFOLIO_ID = "498de2eb-073c-42d8-99ca-783cc8863423"

# API Configuration
API_URL = "https://gridsai.app"
ACCESS_TOKEN = "FG08bkU8TcGzqQJWy0QuoXqANJT2EuJwP2a6nLZlKoU"

# Headers for API calls
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}',
    'Content-Type': 'application/json'
}

# Stock data from yfinance (current prices)
stocks_data = [
    # Technology Sector (14 stocks)
    {"symbol": "300857.SZ", "name": "协创数据", "price": 163.43, "quantity": 1529, "sector": "科技板块"},
    {"symbol": "600487.SS", "name": "亨通光电", "price": 22.90, "quantity": 10917, "sector": "科技板块"},
    {"symbol": "300469.SZ", "name": "信息发展", "price": 86.60, "quantity": 2886, "sector": "科技板块"},
    {"symbol": "300394.SZ", "name": "天孚通信", "price": 187.98, "quantity": 1329, "sector": "科技板块"},
    {"symbol": "002236.SZ", "name": "大华股份", "price": 19.38, "quantity": 12899, "sector": "科技板块"},
    {"symbol": "002402.SZ", "name": "和而泰", "price": 45.61, "quantity": 5481, "sector": "科技板块"},
    {"symbol": "300620.SZ", "name": "光库科技", "price": 125.34, "quantity": 1994, "sector": "科技板块"},
    {"symbol": "603083.SS", "name": "剑桥科技", "price": 112.02, "quantity": 2231, "sector": "科技板块"},
    {"symbol": "688502.SS", "name": "茂莱光学", "price": 460.10, "quantity": 543, "sector": "科技板块"},
    {"symbol": "300803.SZ", "name": "指南针", "price": 153.40, "quantity": 1629, "sector": "科技板块"},
    {"symbol": "688347.SS", "name": "华虹公司", "price": 83.00, "quantity": 3012, "sector": "科技板块"},
    {"symbol": "688205.SS", "name": "德科立", "price": 154.00, "quantity": 1623, "sector": "科技板块"},
    {"symbol": "301309.SZ", "name": "德明利", "price": 29.88, "quantity": 8366, "sector": "科技板块"},
    {"symbol": "600410.SS", "name": "华胜天成", "price": 22.25, "quantity": 11235, "sector": "科技板块"},
    
    # New Materials Sector (8 stocks)
    {"symbol": "002768.SZ", "name": "国恩股份", "price": 48.01, "quantity": 5207, "sector": "新材料板块"},
    {"symbol": "600143.SS", "name": "金发科技", "price": 21.67, "quantity": 11536, "sector": "新材料板块"},
    {"symbol": "002683.SZ", "name": "广东宏大", "price": 44.87, "quantity": 5571, "sector": "新材料板块"},
    {"symbol": "002549.SZ", "name": "凯美特气", "price": 20.76, "quantity": 12042, "sector": "新材料板块"},
    {"symbol": "002226.SZ", "name": "江南化工", "price": 6.80, "quantity": 36764, "sector": "新材料板块"},
    {"symbol": "300539.SZ", "name": "横河精密", "price": 40.40, "quantity": 6188, "sector": "新材料板块"},
    {"symbol": "605488.SS", "name": "福莱新材", "price": 36.73, "quantity": 6806, "sector": "新材料板块"},
    {"symbol": "601958.SS", "name": "金钼股份", "price": 14.83, "quantity": 16857, "sector": "新材料板块"},
    
    # Consumer Sector (7 stocks)
    {"symbol": "605499.SS", "name": "东鹏饮料", "price": 299.34, "quantity": 835, "sector": "消费板块"},
    {"symbol": "000568.SZ", "name": "泸州老窖", "price": 134.85, "quantity": 1853, "sector": "消费板块"},
    {"symbol": "300972.SZ", "name": "万辰集团", "price": 171.55, "quantity": 1457, "sector": "消费板块"},
    {"symbol": "300918.SZ", "name": "南山智尚", "price": 23.28, "quantity": 10738, "sector": "消费板块"},
    {"symbol": "600887.SS", "name": "伊利股份", "price": 27.70, "quantity": 9025, "sector": "消费板块"},
    {"symbol": "000858.SZ", "name": "五粮液", "price": 124.08, "quantity": 2014, "sector": "消费板块"},
    {"symbol": "601579.SS", "name": "会稽山", "price": 22.08, "quantity": 11322, "sector": "消费板块"},
    
    # Industrial Equipment Sector (5 stocks)
    {"symbol": "601717.SS", "name": "中创智领", "price": 24.26, "quantity": 10305, "sector": "工业设备板块"},
    {"symbol": "002008.SZ", "name": "大族激光", "price": 41.26, "quantity": 6059, "sector": "工业设备板块"},
    {"symbol": "000988.SZ", "name": "华工科技", "price": 91.12, "quantity": 2743, "sector": "工业设备板块"},
    {"symbol": "002158.SZ", "name": "汉钟精机", "price": 28.18, "quantity": 8871, "sector": "工业设备板块"},
    {"symbol": "603757.SS", "name": "大元泵业", "price": 51.78, "quantity": 4828, "sector": "工业设备板块"},
    
    # Healthcare Sector (4 stocks)
    {"symbol": "688506.SS", "name": "百利天恒", "price": 374.91, "quantity": 666, "sector": "医疗保健板块"},
    {"symbol": "603301.SS", "name": "振德医疗", "price": 39.95, "quantity": 6257, "sector": "医疗保健板块"},
    {"symbol": "300049.SZ", "name": "福瑞股份", "price": 80.70, "quantity": 3097, "sector": "医疗保健板块"},
    {"symbol": "603259.SS", "name": "药明康德", "price": 108.75, "quantity": 2298, "sector": "医疗保健板块"},
    
    # Automotive Sector (2 stocks)
    {"symbol": "002048.SZ", "name": "宁波华翔", "price": 34.04, "quantity": 7344, "sector": "汽车板块"},
    {"symbol": "601689.SS", "name": "拓普集团", "price": 74.71, "quantity": 3346, "sector": "汽车板块"},
]

def execute_buy_order(stock_data):
    """Execute a buy order for a single stock"""
    try:
        transaction_data = {
            "portfolio_id": PORTFOLIO_ID,
            "symbol": stock_data["symbol"],
            "transaction_type": "buy",
            "quantity": stock_data["quantity"],
            "price": stock_data["price"],
            "fees": 0,
            "notes": f"{stock_data['name']} - {stock_data['sector']}"
        }
        
        response = requests.post(
            f"{API_URL}/api/transactions",
            headers=headers,
            json=transaction_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            total_cost = stock_data["quantity"] * stock_data["price"]
            print(f"✅ {stock_data['symbol']} ({stock_data['name']}): "
                  f"{stock_data['quantity']} shares @ ${stock_data['price']:.2f} = ${total_cost:,.2f}")
            return True
        else:
            print(f"❌ {stock_data['symbol']} ({stock_data['name']}): "
                  f"HTTP {response.status_code} - {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ {stock_data['symbol']} ({stock_data['name']}): Error - {str(e)[:100]}")
        return False

def main():
    """Execute all trades"""
    print("🚀 Starting portfolio construction with 40 Chinese leading stocks")
    print(f"📊 Portfolio ID: {PORTFOLIO_ID}")
    print(f"💰 Total Investment: $10,000,000")
    print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    successful_trades = 0
    failed_trades = 0
    total_investment = 0
    
    # Group by sector for organized execution
    sectors = {}
    for stock in stocks_data:
        sector = stock["sector"]
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    # Execute trades by sector
    for sector_name, sector_stocks in sectors.items():
        print(f"\n📈 {sector_name} ({len(sector_stocks)} stocks)")
        print("-" * 60)
        
        for stock in sector_stocks:
            success = execute_buy_order(stock)
            if success:
                successful_trades += 1
                total_investment += stock["quantity"] * stock["price"]
            else:
                failed_trades += 1
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Stocks: {len(stocks_data)}")
    print(f"Successful: {successful_trades}")
    print(f"Failed: {failed_trades}")
    print(f"Success Rate: {successful_trades/len(stocks_data)*100:.1f}%")
    print(f"Total Investment: ${total_investment:,.2f}")
    print(f"Target Capital: $10,000,000")
    print(f"Utilization: {total_investment/10000000*100:.1f}%")
    print(f"Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if failed_trades == 0:
        print("\n🎉 Portfolio construction completed successfully!")
        print("✅ All 40 stocks purchased at current market prices with 0% P&L")
    else:
        print(f"\n⚠️ {failed_trades} trades failed - manual intervention required")

if __name__ == "__main__":
    main()
