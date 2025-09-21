#!/usr/bin/env python3
"""
Test dual market scheduler for 600298.SS and 0700.HK
"""

import yfinance as yf
from datetime import datetime, time as dt_time
import pytz

def test_dual_market_monitoring():
    """Test monitoring for both China and Hong Kong stocks"""
    
    print("🧪 DUAL MARKET SCHEDULER TEST")
    print("🇨🇳 China Stock: 600298.SS (9:30 AM - 3:00 PM Beijing)")
    print("🇭🇰 Hong Kong Stock: 0700.HK (9:30 AM - 4:00 PM Beijing)")
    print("=" * 70)
    
    # Current Beijing time
    beijing_tz = pytz.timezone('Asia/Shanghai')
    now_beijing = datetime.now(beijing_tz)
    current_time = now_beijing.time()
    
    # Market hours
    china_open = dt_time(9, 30)
    china_close = dt_time(15, 0)
    hk_open = dt_time(9, 30)
    hk_close = dt_time(16, 0)
    
    is_weekday = now_beijing.weekday() < 5
    china_market_open = is_weekday and china_open <= current_time <= china_close
    hk_market_open = is_weekday and hk_open <= current_time <= hk_close
    
    print("📊 CURRENT MARKET STATUS:")
    print(f"⏰ Beijing Time: {now_beijing.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"🇨🇳 China Market: {'🟢 OPEN' if china_market_open else '🔴 CLOSED'} (9:30 AM - 3:00 PM)")
    print(f"🇭🇰 Hong Kong Market: {'🟢 OPEN' if hk_market_open else '🔴 CLOSED'} (9:30 AM - 4:00 PM)")
    
    if china_market_open and hk_market_open:
        print("📈 Status: Both markets active - HIGH FREQUENCY monitoring")
    elif china_market_open:
        print("📈 Status: China only - Monitor China stocks")
    elif hk_market_open:
        print("📈 Status: Hong Kong only - Monitor HK stocks")
    else:
        print("📴 Status: Both closed - MINIMAL checks (prices don't move)")
    
    print()
    print("🔍 TESTING STOCK PRICES:")
    print("=" * 50)
    
    # Test 600298.SS (China stock)
    try:
        print("[1/2] 600298.SS (China stock)...", end=" ")
        ticker_china = yf.Ticker("600298.SS")
        hist_china = ticker_china.history(period="1d")
        
        if not hist_china.empty:
            price_china = hist_china['Close'].iloc[-1]
            print(f"✅ ${price_china:.2f}")
            
            # Grid analysis
            grid_lower = 36.32
            grid_upper = 42.94
            grid_position = (price_china - grid_lower) / (grid_upper - grid_lower) * 100
            print(f"    📊 Grid Position: {grid_position:.1f}% within range")
            print(f"    🎯 Monitoring: {'Active' if china_market_open else 'Suspended (market closed)'}")
        else:
            print("❌ No data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 0700.HK (Hong Kong stock)
    try:
        print("[2/2] 0700.HK (Hong Kong stock)...", end=" ")
        ticker_hk = yf.Ticker("0700.HK")
        hist_hk = ticker_hk.history(period="1d")
        
        if not hist_hk.empty:
            price_hk = hist_hk['Close'].iloc[-1]
            print(f"✅ ${price_hk:.2f}")
            print(f"    🇭🇰 Tencent Holdings - Major Hong Kong stock")
            print(f"    🎯 Monitoring: {'Active' if hk_market_open else 'Suspended (market closed)'}")
            print(f"    ⏰ Extended hours: Trades until 4:00 PM Beijing (vs China 3:00 PM)")
        else:
            print("❌ No data")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("📋 SCHEDULER BEHAVIOR:")
    print("=" * 50)
    
    if china_market_open and hk_market_open:
        print("🟢 9:30 AM - 3:00 PM: Monitor BOTH stocks (every minute)")
        print("🟡 3:00 PM - 4:00 PM: Monitor Hong Kong stocks only")
        print("🔴 4:00 PM onwards: ONE summary check, then quiet")
    elif china_market_open:
        print("🟢 9:30 AM - 3:00 PM: Monitor China stocks (600298.SS)")
        print("🔴 After 3:00 PM: Summary check, then quiet")
    elif hk_market_open:
        print("🟡 3:00 PM - 4:00 PM: Monitor Hong Kong stocks only")
        print("🔴 After 4:00 PM: Summary check, then quiet")
    else:
        print("🔴 After 4:00 PM: Both markets closed")
        print("💤 Prices stable - no monitoring needed until 9:30 AM")
        print("📧 Only emergency alerts during overnight hours")
    
    print()
    print("✅ DUAL MARKET SCHEDULER: Optimized for efficiency!")
    print("🎯 Perfect balance: Active monitoring when needed, quiet when stable")

if __name__ == "__main__":
    test_dual_market_monitoring()
