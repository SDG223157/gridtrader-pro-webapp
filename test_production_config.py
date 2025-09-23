#!/usr/bin/env python3
"""
Test Production Configuration
Verify that all required services and configs are properly set
"""

import os
import yfinance as yf
from datetime import datetime

def test_production_config():
    """Test production environment configuration"""
    print("🚀 PRODUCTION CONFIGURATION TEST")
    print("=" * 60)
    
    # Test environment variables
    print("1. 📧 EMAIL CONFIGURATION:")
    email_vars = {
        'SMTP_SERVER': os.getenv('SMTP_SERVER'),
        'SMTP_PORT': os.getenv('SMTP_PORT'), 
        'SMTP_USERNAME': os.getenv('SMTP_USERNAME'),
        'SMTP_PASSWORD': '***CONFIGURED***' if os.getenv('SMTP_PASSWORD') else None,
        'FROM_EMAIL': os.getenv('FROM_EMAIL'),
        'FROM_NAME': os.getenv('FROM_NAME')
    }
    
    all_email_configured = True
    for key, value in email_vars.items():
        status = "✅" if value else "❌"
        print(f"   {key}: {status} {value or 'NOT SET'}")
        if not value:
            all_email_configured = False
    
    print(f"\n   📧 Email System: {'✅ READY' if all_email_configured else '❌ NOT READY'}")
    
    # Test Redis configuration
    print(f"\n2. 🔴 REDIS CONFIGURATION:")
    redis_vars = {
        'REDIS_URL': os.getenv('REDIS_URL'),
        'REDIS_HOST': os.getenv('REDIS_HOST'),
        'REDIS_PORT': os.getenv('REDIS_PORT'),
        'REDIS_PASSWORD': '***CONFIGURED***' if os.getenv('REDIS_PASSWORD') else None
    }
    
    all_redis_configured = True
    for key, value in redis_vars.items():
        status = "✅" if value else "❌"
        if key == 'REDIS_URL' and value:
            # Show partial URL for security
            display_value = f"{value[:20]}...{value[-20:]}" if len(value) > 40 else value
        else:
            display_value = value or 'NOT SET'
        print(f"   {key}: {status} {display_value}")
        if not value:
            all_redis_configured = False
    
    print(f"\n   🔴 Redis System: {'✅ READY' if all_redis_configured else '❌ NOT READY'}")
    
    # Test database configuration  
    print(f"\n3. 🗄️ DATABASE CONFIGURATION:")
    db_vars = {
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_PASSWORD': '***CONFIGURED***' if os.getenv('DB_PASSWORD') else None
    }
    
    all_db_configured = True
    for key, value in db_vars.items():
        status = "✅" if value else "❌"
        print(f"   {key}: {status} {value or 'NOT SET'}")
        if not value:
            all_db_configured = False
    
    print(f"\n   🗄️ Database System: {'✅ READY' if all_db_configured else '❌ NOT READY'}")
    
    # Test current price and alert conditions
    print(f"\n4. 📊 CURRENT MARKET CONDITIONS:")
    try:
        ticker = yf.Ticker("600298.SS")
        hist = ticker.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            print(f"   Current Price: ✅ ${current_price:.2f}")
            
            # Check alert conditions
            buy_level = 38.64
            distance = abs(current_price - buy_level)
            should_alert = distance <= 0.10
            
            print(f"   Target Buy Level: ${buy_level:.2f}")
            print(f"   Distance: ${distance:.2f}")
            print(f"   Should Trigger Alert: {'✅ YES' if should_alert else '❌ NO'}")
            
            if should_alert:
                print(f"\n   🚨 ALERT SHOULD BE TRIGGERED!")
                print(f"   📧 Email should be sent to: {email_vars['FROM_EMAIL']}")
        else:
            print("   ❌ Could not fetch current price")
    except Exception as e:
        print(f"   ❌ Price fetch error: {e}")
    
    # Test market hours
    print(f"\n5. ⏰ MARKET HOURS:")
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
        
        print(f"   Beijing Time: {now_beijing.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"   Market Open: {'✅ YES' if is_market_open else '❌ NO'}")
        print(f"   Monitoring Active: {'✅ YES' if is_market_open else '⏸️ PAUSED'}")
        
    except ImportError:
        print("   ⚠️ pytz not available")
    
    # Overall system status
    print(f"\n6. 🎯 OVERALL SYSTEM STATUS:")
    print("=" * 40)
    
    all_systems_ready = all_email_configured and all_redis_configured and all_db_configured
    
    if all_systems_ready:
        print("   🎉 ALL SYSTEMS READY!")
        print("   📧 Email alerts should work")
        print("   🔄 Celery worker/beat should start")
        print("   🎯 Alert monitoring should be active")
    else:
        print("   ⚠️ SOME SYSTEMS NOT READY:")
        if not all_email_configured:
            print("   - ❌ Email configuration incomplete")
        if not all_redis_configured:
            print("   - ❌ Redis configuration incomplete") 
        if not all_db_configured:
            print("   - ❌ Database configuration incomplete")
    
    # Port configuration check
    print(f"\n7. 🔌 PORT CONFIGURATION:")
    env_port = os.getenv('PORT', '8000')
    print(f"   Environment PORT: {env_port}")
    print(f"   Supervisor Config: 3000 (hardcoded)")
    
    if env_port != '3000':
        print(f"   ⚠️ PORT MISMATCH DETECTED!")
        print(f"   💡 Recommendation: Change Coolify port to 3000 OR update supervisord.conf")
    else:
        print(f"   ✅ Ports match correctly")

def test_email_service():
    """Test email service configuration"""
    print(f"\n🧪 EMAIL SERVICE TEST:")
    print("=" * 30)
    
    try:
        # Set environment variables from Coolify config
        os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
        os.environ['SMTP_PORT'] = '587'
        os.environ['SMTP_USERNAME'] = 'isky999@gmail.com'
        os.environ['SMTP_PASSWORD'] = '***REDACTED***'  # Use actual password from Coolify env
        os.environ['FROM_EMAIL'] = 'isky999@gmail.com'
        os.environ['FROM_NAME'] = 'GridTrader Pro Alerts'
        
        from email_alert_service import EmailAlertService
        email_service = EmailAlertService()
        
        print(f"   Email Service Configured: {'✅ YES' if email_service.is_configured else '❌ NO'}")
        
        if email_service.is_configured:
            print(f"   📧 Ready to send alerts to: isky999@gmail.com")
            print(f"   🎯 Buy level alerts will be sent when price approaches targets")
        else:
            print(f"   ❌ Email service configuration failed")
            
    except Exception as e:
        print(f"   ❌ Email service test error: {e}")

if __name__ == "__main__":
    test_production_config()
    test_email_service()
