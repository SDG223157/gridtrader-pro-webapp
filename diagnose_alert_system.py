#!/usr/bin/env python3
"""
Alert System Diagnostic Tool
Identify why email alerts are not being sent for 600298.SS grid
"""

import yfinance as yf
import os
from datetime import datetime

def diagnose_alert_system():
    """Comprehensive diagnostic of the alert system"""
    print("🔍 GRID ALERT SYSTEM DIAGNOSTIC")
    print("=" * 60)
    
    # 1. Check current price
    print("1. 📊 PRICE CHECK:")
    try:
        ticker = yf.Ticker("600298.SS")
        hist = ticker.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            print(f"   ✅ Current Price: ${current_price:.2f}")
        else:
            print("   ❌ Could not fetch current price")
            return
    except Exception as e:
        print(f"   ❌ Price fetch error: {e}")
        return
    
    # 2. Check grid configuration from screenshot
    print(f"\n2. 🎯 GRID CONFIGURATION (from your screenshot):")
    grid_info = {
        "symbol": "600298.SS",
        "current_price_shown": 38.59,
        "upper_bound": 45.57,
        "lower_bound": 33.69,
        "investment": 1000000.00,
        "status": "Active",
        "active_orders": 12
    }
    
    buy_orders = [
        {"price": 33.69, "quantity": 4947.0664},
        {"price": 34.68, "quantity": 4805.8439},
        {"price": 35.67, "quantity": 4672.4605},
        {"price": 36.66, "quantity": 4546.2811},
        {"price": 37.65, "quantity": 4426.7375},
        {"price": 38.64, "quantity": 4313.3195}
    ]
    
    print(f"   Symbol: {grid_info['symbol']}")
    print(f"   Status: {grid_info['status']}")
    print(f"   Price Range: ${grid_info['lower_bound']:.2f} - ${grid_info['upper_bound']:.2f}")
    print(f"   Active Orders: {grid_info['active_orders']}")
    
    # 3. Check alert triggers
    print(f"\n3. 🚨 ALERT TRIGGER ANALYSIS:")
    print(f"   Current Price: ${current_price:.2f}")
    
    # Check boundary alerts
    boundary_buffer = 0.50
    lower_alert_threshold = grid_info['lower_bound'] + boundary_buffer
    upper_alert_threshold = grid_info['upper_bound'] - boundary_buffer
    
    print(f"   Boundary Alert Thresholds:")
    print(f"   - Lower: ${lower_alert_threshold:.2f}")
    print(f"   - Upper: ${upper_alert_threshold:.2f}")
    
    boundary_alert_needed = False
    if current_price <= lower_alert_threshold:
        print(f"   🚨 SHOULD trigger lower boundary alert!")
        boundary_alert_needed = True
    elif current_price >= upper_alert_threshold:
        print(f"   🚨 SHOULD trigger upper boundary alert!")
        boundary_alert_needed = True
    else:
        print(f"   ✅ No boundary alerts needed")
    
    # Check buy level alerts
    print(f"\n   Buy Level Alert Analysis:")
    buy_level_buffer = 0.10
    buy_level_alert_needed = False
    
    for order in buy_orders:
        distance = abs(current_price - order['price'])
        should_alert = distance <= buy_level_buffer
        status = "🚨 ALERT!" if should_alert else "✅ OK"
        print(f"   - ${order['price']:.2f}: Distance ${distance:.2f} - {status}")
        
        if should_alert:
            buy_level_alert_needed = True
    
    # 4. Check environment configuration
    print(f"\n4. 🔧 ENVIRONMENT CONFIGURATION:")
    env_vars = [
        "SMTP_SERVER", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", 
        "FROM_EMAIL", "FROM_NAME", "REDIS_URL", "DATABASE_URL"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if var == "SMTP_PASSWORD":
            status = "✅ SET" if value else "❌ NOT SET"
        else:
            status = f"✅ {value}" if value else "❌ NOT SET"
        print(f"   {var}: {status}")
    
    # 5. Check email service
    print(f"\n5. 📧 EMAIL SERVICE CHECK:")
    try:
        from email_alert_service import EmailAlertService
        email_service = EmailAlertService()
        print(f"   Configured: {'✅ YES' if email_service.is_configured else '❌ NO'}")
        print(f"   SMTP Server: {email_service.smtp_server}")
        print(f"   SMTP Port: {email_service.smtp_port}")
        print(f"   Username: {email_service.smtp_username or 'Not set'}")
        print(f"   From Email: {email_service.from_email or 'Not set'}")
    except Exception as e:
        print(f"   ❌ Email service error: {e}")
    
    # 6. Check market hours
    print(f"\n6. ⏰ MARKET HOURS CHECK:")
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
        
        print(f"   Beijing Time: {now_beijing.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Is Weekday: {'✅ YES' if is_weekday else '❌ NO'}")
        print(f"   Market Open: {'✅ YES' if is_market_open else '❌ NO'}")
        print(f"   Should Monitor: {'✅ YES' if is_market_open else '❌ NO'}")
        
    except ImportError:
        print("   ⚠️ pytz not available")
    
    # 7. Diagnosis summary
    print(f"\n7. 🎯 DIAGNOSIS SUMMARY:")
    print("=" * 40)
    
    if buy_level_alert_needed or boundary_alert_needed:
        print("   🚨 ALERTS SHOULD BE TRIGGERED!")
        if buy_level_alert_needed:
            print("   - Buy level alert should be sent")
        if boundary_alert_needed:
            print("   - Boundary alert should be sent")
    else:
        print("   ✅ No alerts should be triggered at current price")
    
    # 8. Likely issues
    print(f"\n8. 🔍 LIKELY ISSUES:")
    issues = []
    
    if not os.getenv('SMTP_USERNAME'):
        issues.append("❌ SMTP credentials not configured in environment")
    
    if not os.getenv('REDIS_URL'):
        issues.append("❌ Redis URL not configured - Celery won't work")
    
    issues.append("❌ Celery worker/beat might not be running in production")
    issues.append("❌ Database connection might be failing")
    issues.append("❌ Grid might not exist in production database")
    
    for issue in issues:
        print(f"   {issue}")
    
    # 9. Next steps
    print(f"\n9. 🚀 NEXT STEPS TO DEBUG:")
    print("   1. Check Coolify deployment logs for Celery worker/beat")
    print("   2. Verify SMTP environment variables are set in Coolify")
    print("   3. Check Redis service is running")
    print("   4. Verify database contains the 600298.SS grid")
    print("   5. Check application logs for alert system errors")
    print("   6. Test email service manually")

def create_manual_test():
    """Create a manual test to trigger an alert"""
    print(f"\n🧪 MANUAL ALERT TEST:")
    print("=" * 30)
    
    try:
        from email_alert_service import EmailAlertService, send_grid_alert_to_user
        
        # Test data matching your grid
        test_alert_data = {
            "symbol": "600298.SS",
            "current_price": 38.59,
            "buy_level": 38.64,
            "grid_name": "600298.SS China Grid - Fixed Allocation",
            "grid_id": "test-grid-id",
            "alert_type": "buy_level"
        }
        
        email_service = EmailAlertService()
        
        if email_service.is_configured:
            print("   📧 Attempting to send test email...")
            try:
                success = email_service.send_buy_level_alert(
                    "isky999@gmail.com", 
                    "Yang", 
                    test_alert_data
                )
                print(f"   {'✅ SUCCESS' if success else '❌ FAILED'}: Test email send")
            except Exception as e:
                print(f"   ❌ Email send error: {e}")
        else:
            print("   ⚠️ Email service not configured - cannot send test")
            
    except Exception as e:
        print(f"   ❌ Test setup error: {e}")

if __name__ == "__main__":
    diagnose_alert_system()
    create_manual_test()
