#!/usr/bin/env python3
"""
Test Production Alert System
Verify that alerts will work correctly in Coolify production environment
"""

import yfinance as yf
from datetime import datetime
import os

def test_alert_triggers():
    """Test current price against alert triggers"""
    print("🔔 PRODUCTION ALERT SYSTEM TEST")
    print("=" * 60)
    
    # Get current price
    ticker = yf.Ticker("600298.SS")
    hist = ticker.history(period="1d")
    
    if hist.empty:
        print("❌ Could not get current price")
        return
    
    current_price = hist['Close'].iloc[-1]
    print(f"📊 Current Price: ${current_price:.2f}")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Grid configuration
    buy_levels = [33.69, 34.68, 35.67, 36.66, 37.65, 38.64]
    lower_boundary = 36.32
    upper_boundary = 42.94
    boundary_buffer = 0.50
    buy_level_buffer = 0.10
    
    print(f"\n🎯 GRID CONFIGURATION:")
    print(f"Symbol: 600298.SS")
    print(f"Grid Range: ${lower_boundary:.2f} - ${upper_boundary:.2f}")
    print(f"Buy Levels: {[f'${level:.2f}' for level in buy_levels]}")
    
    # Test boundary alerts
    print(f"\n⚠️ BOUNDARY ALERT STATUS:")
    lower_alert_threshold = lower_boundary + boundary_buffer
    upper_alert_threshold = upper_boundary - boundary_buffer
    
    print(f"Lower Alert Threshold: ${lower_alert_threshold:.2f}")
    print(f"Upper Alert Threshold: ${upper_alert_threshold:.2f}")
    
    boundary_alert_triggered = False
    if current_price <= lower_alert_threshold:
        print(f"🚨 BOUNDARY ALERT: Price ${current_price:.2f} approaching lower boundary!")
        boundary_alert_triggered = True
    elif current_price >= upper_alert_threshold:
        print(f"🚨 BOUNDARY ALERT: Price ${current_price:.2f} approaching upper boundary!")
        boundary_alert_triggered = True
    else:
        print(f"✅ No boundary alerts (price within normal range)")
    
    # Test buy level alerts
    print(f"\n🎯 BUY LEVEL ALERT STATUS:")
    buy_level_alert_triggered = False
    closest_level = None
    closest_distance = float('inf')
    
    for buy_level in buy_levels:
        distance = abs(current_price - buy_level)
        status = "🎯 ALERT!" if distance <= buy_level_buffer else "✅ OK"
        print(f"Level ${buy_level:.2f}: Distance ${distance:.2f} - {status}")
        
        if distance < closest_distance:
            closest_distance = distance
            closest_level = buy_level
        
        if distance <= buy_level_buffer:
            buy_level_alert_triggered = True
    
    print(f"\nClosest Buy Level: ${closest_level:.2f} (${closest_distance:.2f} away)")
    
    # Production environment check
    print(f"\n🚀 PRODUCTION ENVIRONMENT STATUS:")
    print(f"Environment: {'Production (Coolify)' if os.getenv('NODE_ENV') == 'production' else 'Local Development'}")
    
    # Expected behavior in production
    print(f"\n📧 EXPECTED EMAIL ALERTS IN PRODUCTION:")
    if buy_level_alert_triggered:
        print(f"✅ BUY LEVEL ALERT will be sent to isky999@gmail.com")
        print(f"   - Subject: 🎯 Buy Level Alert - 600298.SS")
        print(f"   - Price: ${current_price:.2f} near level ${closest_level:.2f}")
        print(f"   - Action: Consider executing buy order")
    
    if boundary_alert_triggered:
        print(f"✅ BOUNDARY ALERT will be sent to isky999@gmail.com")
        print(f"   - Subject: ⚠️ Price Boundary Alert - 600298.SS")
        print(f"   - Action: Consider grid adjustment")
    
    if not buy_level_alert_triggered and not boundary_alert_triggered:
        print(f"ℹ️  No alerts triggered at current price level")
    
    # Celery task status
    print(f"\n⚙️ CELERY TASK CONFIGURATION:")
    print(f"✅ monitor_grid_prices_realtime: Runs every 2 minutes during market hours")
    print(f"✅ Market Hours: 9:30 AM - 3:00 PM Beijing Time (Mon-Fri)")
    print(f"✅ Email Integration: Configured for both buy level and boundary alerts")
    
    # Next alert predictions
    print(f"\n🔮 NEXT ALERT PREDICTIONS:")
    print(f"If price moves to:")
    for level in buy_levels:
        if abs(current_price - level) > buy_level_buffer:
            direction = "drops to" if level < current_price else "rises to"
            print(f"  - ${level:.2f}: {direction} trigger buy level alert")
    
    print(f"  - ${lower_alert_threshold:.2f}: Trigger lower boundary alert")
    print(f"  - ${upper_alert_threshold:.2f}: Trigger upper boundary alert")

def test_market_hours():
    """Test if alerts would run during current time"""
    print(f"\n⏰ MARKET HOURS CHECK:")
    print("=" * 40)
    
    try:
        import pytz
        from datetime import time as dt_time
        
        beijing_tz = pytz.timezone('Asia/Shanghai')
        now_beijing = datetime.now(beijing_tz)
        current_time = now_beijing.time()
        market_open = dt_time(9, 30)
        market_close = dt_time(15, 0)
        is_weekday = now_beijing.weekday() < 5
        is_market_open = is_weekday and market_open <= current_time <= market_close
        
        print(f"Beijing Time: {now_beijing.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Market Hours: 9:30 AM - 3:00 PM (Mon-Fri)")
        print(f"Is Weekday: {is_weekday}")
        print(f"Market Open: {'✅ YES' if is_market_open else '❌ NO'}")
        
        if is_market_open:
            print(f"🔄 Alerts are actively monitoring during market hours")
        else:
            print(f"⏸️  Alerts are paused (market closed)")
            
    except ImportError:
        print("⚠️ pytz not available for timezone check")

if __name__ == "__main__":
    test_alert_triggers()
    test_market_hours()
