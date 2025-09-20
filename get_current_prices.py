#!/usr/bin/env python3
"""
Get current prices for all 40 Chinese leading stocks using yfinance
"""

import yfinance as yf
import pandas as pd
from datetime import datetime

# List of all 40 stocks from the portfolio
stocks = [
    # Technology Sector (14 stocks)
    "300857.SZ",  # 协创数据
    "600487.SS",  # 亨通光电
    "300469.SZ",  # 信息发展
    "300394.SZ",  # 天孚通信
    "002236.SZ",  # 大华股份
    "002402.SZ",  # 和而泰
    "300620.SZ",  # 光库科技
    "603083.SS",  # 剑桥科技
    "688502.SS",  # 茂莱光学
    "300803.SZ",  # 指南针
    "688347.SS",  # 华虹公司
    "688205.SS",  # 德科立
    "301309.SZ",  # 德明利
    "600410.SS",  # 华胜天成
    
    # New Materials Sector (8 stocks)
    "002768.SZ",  # 国恩股份
    "600143.SS",  # 金发科技
    "002683.SZ",  # 广东宏大
    "002549.SZ",  # 凯美特气
    "002226.SZ",  # 江南化工
    "300539.SZ",  # 横河精密
    "605488.SS",  # 福莱新材
    "601958.SS",  # 金钼股份
    
    # Consumer Sector (7 stocks)
    "605499.SS",  # 东鹏饮料
    "000568.SZ",  # 泸州老窖
    "300972.SZ",  # 万辰集团
    "300918.SZ",  # 南山智尚
    "600887.SS",  # 伊利股份
    "000858.SZ",  # 五粮液
    "601579.SS",  # 会稽山
    
    # Industrial Equipment Sector (5 stocks)
    "601717.SS",  # 中创智领
    "002008.SZ",  # 大族激光
    "000988.SZ",  # 华工科技
    "002158.SZ",  # 汉钟精机
    "603757.SS",  # 大元泵业
    
    # Healthcare Sector (4 stocks)
    "688506.SS",  # 百利天恒
    "603301.SS",  # 振德医疗
    "300049.SZ",  # 福瑞股份
    "603259.SS",  # 药明康德
    
    # Automotive Sector (2 stocks)
    "002048.SZ",  # 宁波华翔
    "601689.SS",  # 拓普集团
]

# Stock names mapping
stock_names = {
    "300857.SZ": "协创数据", "600487.SS": "亨通光电", "300469.SZ": "信息发展", "300394.SZ": "天孚通信",
    "002236.SZ": "大华股份", "002402.SZ": "和而泰", "300620.SZ": "光库科技", "603083.SS": "剑桥科技",
    "688502.SS": "茂莱光学", "300803.SZ": "指南针", "688347.SS": "华虹公司", "688205.SS": "德科立",
    "301309.SZ": "德明利", "600410.SS": "华胜天成", "002768.SZ": "国恩股份", "600143.SS": "金发科技",
    "002683.SZ": "广东宏大", "002549.SZ": "凯美特气", "002226.SZ": "江南化工", "300539.SZ": "横河精密",
    "605488.SS": "福莱新材", "601958.SS": "金钼股份", "605499.SS": "东鹏饮料", "000568.SZ": "泸州老窖",
    "300972.SZ": "万辰集团", "300918.SZ": "南山智尚", "600887.SS": "伊利股份", "000858.SZ": "五粮液",
    "601579.SS": "会稽山", "601717.SS": "中创智领", "002008.SZ": "大族激光", "000988.SZ": "华工科技",
    "002158.SZ": "汉钟精机", "603757.SS": "大元泵业", "688506.SS": "百利天恒", "603301.SS": "振德医疗",
    "300049.SZ": "福瑞股份", "603259.SS": "药明康德", "002048.SZ": "宁波华翔", "601689.SS": "拓普集团"
}

def get_current_prices():
    """Get current prices for all stocks"""
    print(f"🔍 Fetching current prices for {len(stocks)} stocks...")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    prices_data = []
    successful = 0
    failed = 0
    
    for i, symbol in enumerate(stocks, 1):
        try:
            print(f"[{i:2d}/40] Fetching {symbol} ({stock_names[symbol]})...", end=" ")
            
            # Get stock data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                
                # Calculate quantity for ~250,000 RMB allocation
                target_allocation = 250000
                quantity = int(target_allocation / current_price)
                actual_allocation = quantity * current_price
                
                prices_data.append({
                    'symbol': symbol,
                    'name': stock_names[symbol],
                    'current_price': round(current_price, 2),
                    'quantity': quantity,
                    'allocation': round(actual_allocation, 2),
                    'status': 'SUCCESS'
                })
                
                print(f"✅ ${current_price:.2f}")
                successful += 1
            else:
                prices_data.append({
                    'symbol': symbol,
                    'name': stock_names[symbol],
                    'current_price': 0,
                    'quantity': 0,
                    'allocation': 0,
                    'status': 'NO_DATA'
                })
                print("❌ No data")
                failed += 1
                
        except Exception as e:
            prices_data.append({
                'symbol': symbol,
                'name': stock_names[symbol],
                'current_price': 0,
                'quantity': 0,
                'allocation': 0,
                'status': f'ERROR: {str(e)[:50]}'
            })
            print(f"❌ Error: {e}")
            failed += 1
    
    # Create DataFrame and display results
    df = pd.DataFrame(prices_data)
    
    print("\n" + "=" * 80)
    print("📊 CURRENT PRICES SUMMARY")
    print("=" * 80)
    
    # Display successful stocks
    success_df = df[df['status'] == 'SUCCESS'].copy()
    if not success_df.empty:
        print(f"\n✅ SUCCESSFUL ({len(success_df)} stocks):")
        print("-" * 80)
        for _, row in success_df.iterrows():
            print(f"{row['symbol']:<12} {row['name']:<15} ${row['current_price']:>8.2f} "
                  f"({row['quantity']:>6} shares = ${row['allocation']:>10.2f})")
    
    # Display failed stocks
    failed_df = df[df['status'] != 'SUCCESS']
    if not failed_df.empty:
        print(f"\n❌ FAILED ({len(failed_df)} stocks):")
        print("-" * 80)
        for _, row in failed_df.iterrows():
            print(f"{row['symbol']:<12} {row['name']:<15} {row['status']}")
    
    # Summary statistics
    total_allocation = success_df['allocation'].sum()
    print("\n" + "=" * 80)
    print("📈 PORTFOLIO SUMMARY")
    print("=" * 80)
    print(f"Total Stocks: {len(stocks)}")
    print(f"Successful:   {successful}")
    print(f"Failed:       {failed}")
    print(f"Success Rate: {successful/len(stocks)*100:.1f}%")
    print(f"Total Allocation: ${total_allocation:,.2f}")
    print(f"Target Capital: $10,000,000")
    print(f"Utilization: {total_allocation/10000000*100:.1f}%")
    
    # Save to CSV
    csv_filename = f"stock_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"\n💾 Data saved to: {csv_filename}")
    
    return df

if __name__ == "__main__":
    try:
        prices_df = get_current_prices()
        print("\n🎉 Price fetching completed!")
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
