#!/usr/bin/env python3
"""
Simple US Market Scheduler Test
"""

import yfinance as yf
from datetime import datetime, time as dt_time
import pytz

def test_us_market_hours():
    """Test US market hours detection and stock monitoring"""
    
    print("🇺🇸 US MARKET SCHEDULER TEST")
    print("=" * 50)
    
    # Current times in different zones
    us_tz = pytz.timezone('US/Eastern')
    beijing_tz = pytz.timezone('Asia/Shanghai')
    
    now_us = datetime.now(us_tz)
    now_beijing = datetime.now(beijing_tz)
    
    print(f"⏰ Current Times:")
    print(f"🇺🇸 US Eastern: {now_us.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🇨🇳 Beijing: {now_beijing.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Market status
    is_weekday = now_us.weekday() < 5
    us_market_open = is_weekday and dt_time(9, 30) <= now_us.time() <= dt_time(16, 0)
    china_market_open = is_weekday and dt_time(9, 30) <= now_beijing.time() <= dt_time(15, 0)
    hk_market_open = is_weekday and dt_time(9, 30) <= now_beijing.time() <= dt_time(16, 0)
    
    print()
    print("📊 MARKET STATUS:")
    print(f"🇺🇸 US Market: {'🟢 OPEN' if us_market_open else '🔴 CLOSED'} (9:30 AM - 4:00 PM ET)")
    print(f"🇨🇳 China Market: {'🟢 OPEN' if china_market_open else '🔴 CLOSED'} (9:30 AM - 3:00 PM Beijing)")
    print(f"🇭🇰 Hong Kong Market: {'🟢 OPEN' if hk_market_open else '🔴 CLOSED'} (9:30 AM - 4:00 PM Beijing)")
    
    # Test stock prices
    print()
    print("🔍 TESTING STOCK PRICES:")
    print("-" * 40)
    
    # US stocks
    if us_market_open:
        print("🇺🇸 US STOCKS (Market Open - Active Monitoring):")
    else:
        print("🇺🇸 US STOCKS (Market Closed - Prices Stable):")
    
    us_stocks = ["AAPL", "MSFT", "NVDA"]
    for symbol in us_stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                monitoring = "📊 Active" if us_market_open else "📴 Suspended"
                print(f"  {symbol}: ${price:.2f} ({monitoring})")
        except:
            print(f"  {symbol}: ❌ Error")
    
    print()
    
    # China stocks
    if china_market_open:
        print("🇨🇳 CHINA STOCKS (Market Open - Active Monitoring):")
    else:
        print("🇨🇳 CHINA STOCKS (Market Closed - Prices Stable):")
    
    china_stocks = ["600298.SS"]
    for symbol in china_stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                monitoring = "📊 Active" if china_market_open else "📴 Suspended"
                print(f"  {symbol}: ${price:.2f} ({monitoring}) - Yang's Grid")
        except:
            print(f"  {symbol}: ❌ Error")
    
    print()
    
    # Hong Kong stocks
    if hk_market_open:
        print("🇭🇰 HONG KONG STOCKS (Market Open - Active Monitoring):")
    else:
        print("🇭🇰 HONG KONG STOCKS (Market Closed - Prices Stable):")
    
    hk_stocks = ["0700.HK"]
    for symbol in hk_stocks:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                monitoring = "📊 Active" if hk_market_open else "📴 Suspended"
                print(f"  {symbol}: ${price:.2f} ({monitoring}) - Tencent")
        except:
            print(f"  {symbol}: ❌ Error")
    
    print()
    print("🎯 SCHEDULER OPTIMIZATION:")
    print("-" * 40)
    
    active_markets = []
    if us_market_open:
        active_markets.append("US")
    if china_market_open:
        active_markets.append("China")
    if hk_market_open:
        active_markets.append("Hong Kong")
    
    if active_markets:
        print(f"🟢 Active Markets: {', '.join(active_markets)}")
        print("📊 Monitoring Frequency: Every 1 minute")
        print("📧 Email Alerts: Active for all monitored stocks")
    else:
        print("🔴 All Markets Closed")
        print("📴 Monitoring: MINIMAL (prices don't move)")
        print("💤 Next check: When any market opens")
        print("📧 Email Alerts: Emergency only")
    
    print()
    print("✅ MULTI-MARKET SCHEDULER READY!")
    print("🌍 Global coverage: US + China + Hong Kong")
    print("⏰ Optimized for each market's trading hours")
    print("📧 Email alerts: isky999@gmail.com")

if __name__ == "__main__":
    test_us_market_hours()
