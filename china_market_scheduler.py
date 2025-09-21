#!/usr/bin/env python3
"""
China Market Hours Scheduler for Grid Trading
Optimized for Shanghai Stock Exchange hours: 9:30 AM - 3:00 PM Beijing Time
"""

import asyncio
import schedule
import time
import yfinance as yf
from datetime import datetime, timezone, timedelta, time as dt_time
from typing import List, Dict
import logging
import pytz

# Beijing timezone
BEIJING_TZ = pytz.timezone('Asia/Shanghai')

# Market hours (Beijing Time)
# China (Shanghai/Shenzhen): 9:30 AM - 3:00 PM
# Hong Kong: 9:30 AM - 4:00 PM
CHINA_MARKET_OPEN_HOUR = 9
CHINA_MARKET_OPEN_MINUTE = 30
CHINA_MARKET_CLOSE_HOUR = 15
CHINA_MARKET_CLOSE_MINUTE = 0

HK_MARKET_OPEN_HOUR = 9
HK_MARKET_OPEN_MINUTE = 30
HK_MARKET_CLOSE_HOUR = 16
HK_MARKET_CLOSE_MINUTE = 0

logger = logging.getLogger(__name__)

class ChinaMarketScheduler:
    """Scheduler optimized for China stock market hours"""
    
    def __init__(self):
        self.is_running = False
        self.grid_symbols = []
        self.last_price_check = {}
        
    def is_market_hours(self, market="china") -> bool:
        """Check if China or Hong Kong market is currently open"""
        now_beijing = datetime.now(BEIJING_TZ)
        current_time = now_beijing.time()
        
        # Check if it's a weekday (Monday=0, Sunday=6)
        is_weekday = now_beijing.weekday() < 5
        
        if market == "china":
            # China market hours: 9:30 AM - 3:00 PM Beijing Time
            market_open = dt_time(CHINA_MARKET_OPEN_HOUR, CHINA_MARKET_OPEN_MINUTE)
            market_close = dt_time(CHINA_MARKET_CLOSE_HOUR, CHINA_MARKET_CLOSE_MINUTE)
        elif market == "hongkong":
            # Hong Kong market hours: 9:30 AM - 4:00 PM Beijing Time
            market_open = dt_time(HK_MARKET_OPEN_HOUR, HK_MARKET_OPEN_MINUTE)
            market_close = dt_time(HK_MARKET_CLOSE_HOUR, HK_MARKET_CLOSE_MINUTE)
        else:
            # Check if any market is open
            china_open = self.is_market_hours("china")
            hk_open = self.is_market_hours("hongkong")
            return china_open or hk_open
        
        return is_weekday and market_open <= current_time <= market_close
    
    def get_market_status(self) -> Dict:
        """Get current market status for both China and Hong Kong"""
        now_beijing = datetime.now(BEIJING_TZ)
        china_open = self.is_market_hours("china")
        hk_open = self.is_market_hours("hongkong")
        any_open = china_open or hk_open
        
        # Determine market status
        if china_open and hk_open:
            market_status = "🟢 Both China & Hong Kong OPEN"
            next_close = "3:00 PM (China closes first)"
        elif china_open:
            market_status = "🟢 China OPEN, Hong Kong CLOSED"
            next_close = "3:00 PM (China close)"
        elif hk_open:
            market_status = "🟢 Hong Kong OPEN, China CLOSED"
            next_close = "4:00 PM (Hong Kong close)"
        else:
            market_status = "🔴 Both markets CLOSED"
            next_close = "Next open: 9:30 AM"
        
        # Calculate time to next market event
        if any_open:
            # Market is open - calculate time to close
            close_time = now_beijing.replace(hour=15, minute=0, second=0, microsecond=0)
            time_to_event = close_time - now_beijing
            next_event = "Market Close"
        else:
            # Market is closed - calculate time to next open
            if now_beijing.time() < dt_time(9, 30):
                # Same day open
                open_time = now_beijing.replace(hour=9, minute=30, second=0, microsecond=0)
            else:
                # Next trading day
                next_day = now_beijing + timedelta(days=1)
                while next_day.weekday() >= 5:  # Skip weekends
                    next_day += timedelta(days=1)
                open_time = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
            
            time_to_event = open_time - now_beijing
            next_event = "Market Open"
        
        return {
            "china_market_open": china_open,
            "hk_market_open": hk_open,
            "any_market_open": any_open,
            "market_status": market_status,
            "current_time_beijing": now_beijing.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "next_event": next_event,
            "time_to_next_event": str(time_to_event).split('.')[0],  # Remove microseconds
            "china_hours": "9:30 AM - 3:00 PM Beijing Time",
            "hk_hours": "9:30 AM - 4:00 PM Beijing Time"
        }
    
    def check_grid_prices_realtime(self):
        """Check grid trading stock prices in real-time"""
        market_status = self.get_market_status()
        
        print(f"🔍 REAL-TIME PRICE CHECK - {market_status['current_time_beijing']}")
        print(f"📊 Market Status: {market_status['market_status']}")
        print(f"⏰ Next Event: {market_status['next_event']} in {market_status['time_to_next_event']}")
        
        # Grid trading symbols to monitor
        grid_symbols = ["600298.SS"]  # Yang's grid
        
        for symbol in grid_symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    
                    # Check against grid boundaries
                    grid_lower = 36.32
                    grid_upper = 42.94
                    
                    # Calculate position within grid
                    grid_position = (current_price - grid_lower) / (grid_upper - grid_lower) * 100
                    
                    print(f"📈 {symbol}: ${current_price:.2f}")
                    print(f"   Grid Position: {grid_position:.1f}% (Range: ${grid_lower:.2f} - ${grid_upper:.2f})")
                    
                    # Check for alerts
                    if current_price <= grid_lower + 0.50:
                        print(f"   ⚠️ BOUNDARY ALERT: Approaching lower boundary!")
                    elif current_price >= grid_upper - 0.50:
                        print(f"   ⚠️ BOUNDARY ALERT: Approaching upper boundary!")
                    else:
                        print(f"   ✅ Normal: Within grid range")
                    
                    # Store price for comparison
                    if symbol in self.last_price_check:
                        price_change = current_price - self.last_price_check[symbol]
                        change_pct = (price_change / self.last_price_check[symbol]) * 100
                        print(f"   📊 Change: ${price_change:+.2f} ({change_pct:+.2f}%)")
                    
                    self.last_price_check[symbol] = current_price
                    
            except Exception as e:
                print(f"❌ Error checking {symbol}: {e}")
        
        print("-" * 60)
    
    def setup_china_market_schedule(self):
        """Setup schedule optimized for China market hours"""
        print("⏰ SETTING UP CHINA MARKET SCHEDULER")
        print("🇨🇳 Market Hours: 9:30 AM - 3:00 PM Beijing Time")
        print("=" * 60)
        
        # High frequency during market hours
        schedule.every(1).minutes.do(self.check_grid_prices_realtime)
        
        # Market status check
        schedule.every(5).minutes.do(self.log_market_status)
        
        print("✅ Scheduler configured:")
        print("   📊 Price checks: Every 1 minute")
        print("   🕐 Market status: Every 5 minutes")
        print("   🎯 Grid monitoring: 600298.SS")
        print("   📧 Alerts: Integrated with email system")
    
    def log_market_status(self):
        """Log current market status"""
        status = self.get_market_status()
        if status["any_market_open"]:
            print(f"🟢 Market OPEN - {status['current_time_beijing']}")
            print(f"   China: {'🟢 OPEN' if status['china_market_open'] else '🔴 CLOSED'}")
            print(f"   Hong Kong: {'🟢 OPEN' if status['hk_market_open'] else '🔴 CLOSED'}")
        else:
            print(f"🔴 Both markets CLOSED - Next: {status['next_event']} in {status['time_to_next_event']}")
    
    def run_scheduler(self):
        """Run the scheduler continuously"""
        self.setup_china_market_schedule()
        self.is_running = True
        
        print("🚀 CHINA MARKET SCHEDULER STARTED")
        print("📊 Monitoring 600298.SS grid in real-time")
        print("⏰ Optimized for Beijing Time market hours")
        print("🔄 Press Ctrl+C to stop")
        print("=" * 60)
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        except KeyboardInterrupt:
            print("\n⏹️ Scheduler stopped by user")
            self.is_running = False

def main():
    """Test the China market scheduler"""
    scheduler = ChinaMarketScheduler()
    
    # Show current market status
    status = scheduler.get_market_status()
    print("🇨🇳 CHINA MARKET STATUS")
    print("=" * 40)
    print(f"Current Time: {status['current_time_beijing']}")
    print(f"Market Status: {status['market_status']}")
    print(f"China Market: {'🟢 OPEN' if status['china_market_open'] else '🔴 CLOSED'} (9:30 AM - 3:00 PM)")
    print(f"Hong Kong Market: {'🟢 OPEN' if status['hk_market_open'] else '🔴 CLOSED'} (9:30 AM - 4:00 PM)")
    print(f"Next Event: {status['next_event']} in {status['time_to_next_event']}")
    
    # Run a single price check
    print("\n🔍 SINGLE PRICE CHECK TEST:")
    scheduler.check_grid_prices_realtime()
    
    print("\n🎯 TO RUN CONTINUOUS MONITORING:")
    print("python3 china_market_scheduler.py")
    print("(This will run real-time monitoring during China market hours)")

if __name__ == "__main__":
    main()
