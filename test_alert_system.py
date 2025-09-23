#!/usr/bin/env python3
"""
Test Grid Alert System
Test the enhanced alert system with current 600298.SS price
"""

import yfinance as yf
from email_alert_service import EmailAlertService
from datetime import datetime

def test_current_price_alerts():
    """Test alerts with current 600298.SS price"""
    print("🔔 TESTING GRID ALERT SYSTEM")
    print("=" * 60)
    
    # Get current price
    ticker = yf.Ticker("600298.SS")
    hist = ticker.history(period="1d")
    
    if hist.empty:
        print("❌ Could not get current price")
        return
    
    current_price = hist['Close'].iloc[-1]
    print(f"📊 Current Price: ${current_price:.2f}")
    
    # Grid configuration from email_alert_config.json
    grid_config = {
        "symbol": "600298.SS",
        "lower_boundary": 36.32,
        "upper_boundary": 42.94,
        "buy_levels": [33.69, 34.68, 35.67, 36.66, 37.65, 38.64]
    }
    
    print(f"🎯 Grid Range: ${grid_config['lower_boundary']:.2f} - ${grid_config['upper_boundary']:.2f}")
    
    # Check boundary alerts
    boundary_buffer = 0.50
    print(f"\n⚠️ BOUNDARY ALERT CHECKS:")
    print(f"Lower alert threshold: ${grid_config['lower_boundary'] + boundary_buffer:.2f}")
    print(f"Upper alert threshold: ${grid_config['upper_boundary'] - boundary_buffer:.2f}")
    
    if current_price <= grid_config['lower_boundary'] + boundary_buffer:
        print(f"🚨 BOUNDARY ALERT: Price ${current_price:.2f} approaching lower boundary!")
    elif current_price >= grid_config['upper_boundary'] - boundary_buffer:
        print(f"🚨 BOUNDARY ALERT: Price ${current_price:.2f} approaching upper boundary!")
    else:
        print(f"✅ No boundary alerts needed")
    
    # Check buy level alerts
    print(f"\n🎯 BUY LEVEL ALERT CHECKS:")
    buy_level_triggered = False
    for buy_level in grid_config['buy_levels']:
        distance = abs(current_price - buy_level)
        print(f"Level ${buy_level:.2f}: Distance ${distance:.2f}")
        
        if distance <= 0.10:  # Within $0.10
            print(f"🎯 BUY LEVEL ALERT: Price ${current_price:.2f} near buy level ${buy_level:.2f}!")
            buy_level_triggered = True
            
            # Test email alert
            email_service = EmailAlertService()
            if email_service.is_configured:
                print("📧 Email service configured - would send alert")
            else:
                print("⚠️ Email service not configured")
            
            break
    
    if not buy_level_triggered:
        print("✅ No buy level alerts triggered")
    
    # Show what should happen
    print(f"\n💡 ANALYSIS:")
    print(f"Current price ${current_price:.2f} is:")
    
    if current_price < 38.64:
        print(f"- Below buy level $38.64 (difference: ${38.64 - current_price:.2f})")
        if abs(current_price - 38.64) <= 0.10:
            print(f"- ✅ SHOULD trigger buy level alert (within $0.10)")
        else:
            print(f"- ❌ Should NOT trigger buy level alert (>${0.10:.2f} away)")
    else:
        print(f"- Above buy level $38.64")
    
    print(f"\n🔄 NEXT STEPS:")
    print(f"1. Ensure Celery worker is running")
    print(f"2. Ensure Redis is running")
    print(f"3. Check that monitor_grid_prices_realtime task runs every 2 minutes")
    print(f"4. Verify SMTP credentials are configured")
    print(f"5. Check database has active grid for 600298.SS")

def test_email_configuration():
    """Test email service configuration"""
    print(f"\n📧 EMAIL SERVICE TEST:")
    print("=" * 40)
    
    email_service = EmailAlertService()
    print(f"SMTP Server: {email_service.smtp_server}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"Username: {email_service.smtp_username}")
    print(f"From Email: {email_service.from_email}")
    print(f"From Name: {email_service.from_name}")
    print(f"Configured: {email_service.is_configured}")
    
    if not email_service.is_configured:
        print("\n⚠️ EMAIL NOT CONFIGURED")
        print("Set these environment variables:")
        print("- SMTP_USERNAME")
        print("- SMTP_PASSWORD") 
        print("- FROM_EMAIL (optional)")
        print("- FROM_NAME (optional)")

if __name__ == "__main__":
    test_current_price_alerts()
    test_email_configuration()
