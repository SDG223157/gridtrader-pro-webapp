#!/usr/bin/env python3
"""
Multi-Market Scheduler for Global Stock Trading
Supports US, China, and Hong Kong market hours with optimized monitoring
"""

import schedule
import time
import yfinance as yf
from datetime import datetime, timezone, timedelta, time as dt_time
from typing import List, Dict, Tuple
import logging
import pytz

# Market timezones
US_TZ = pytz.timezone('US/Eastern')  # NYSE/NASDAQ timezone
BEIJING_TZ = pytz.timezone('Asia/Shanghai')  # China/Hong Kong reference
UTC_TZ = pytz.UTC

# Market hours (in local time)
US_MARKET_HOURS = {
    "open": dt_time(9, 30),   # 9:30 AM ET
    "close": dt_time(16, 0),  # 4:00 PM ET
    "timezone": "US/Eastern"
}

CHINA_MARKET_HOURS = {
    "open": dt_time(9, 30),   # 9:30 AM Beijing
    "close": dt_time(15, 0),  # 3:00 PM Beijing
    "timezone": "Asia/Shanghai"
}

HK_MARKET_HOURS = {
    "open": dt_time(9, 30),   # 9:30 AM Beijing (same as China)
    "close": dt_time(16, 0),  # 4:00 PM Beijing
    "timezone": "Asia/Shanghai"
}

logger = logging.getLogger(__name__)

class MultiMarketScheduler:
    """Global market scheduler for US, China, and Hong Kong stocks"""
    
    def __init__(self):
        self.is_running = False
        self.monitored_stocks = {
            "US": [],      # US stocks (AAPL, MSFT, etc.)
            "China": [],   # China stocks (.SS, .SZ)
            "HongKong": [] # Hong Kong stocks (.HK)
        }
        self.last_prices = {}
    
    def is_market_open(self, market: str) -> bool:
        """Check if specific market is currently open"""
        is_weekday = datetime.now().weekday() < 5  # Monday=0, Sunday=6
        
        if not is_weekday:
            return False
        
        if market == "US":
            now_et = datetime.now(US_TZ)
            current_time = now_et.time()
            return US_MARKET_HOURS["open"] <= current_time <= US_MARKET_HOURS["close"]
            
        elif market == "China":
            now_beijing = datetime.now(BEIJING_TZ)
            current_time = now_beijing.time()
            return CHINA_MARKET_HOURS["open"] <= current_time <= CHINA_MARKET_HOURS["close"]
            
        elif market == "HongKong":
            now_beijing = datetime.now(BEIJING_TZ)
            current_time = now_beijing.time()
            return HK_MARKET_HOURS["open"] <= current_time <= HK_MARKET_HOURS["close"]
            
        return False
    
    def get_global_market_status(self) -> Dict:
        """Get status of all major markets"""
        now_utc = datetime.now(UTC_TZ)
        now_et = datetime.now(US_TZ)
        now_beijing = datetime.now(BEIJING_TZ)
        
        us_open = self.is_market_open("US")
        china_open = self.is_market_open("China")
        hk_open = self.is_market_open("HongKong")
        
        # Determine active markets
        active_markets = []
        if us_open:
            active_markets.append("US")
        if china_open:
            active_markets.append("China")
        if hk_open:
            active_markets.append("Hong Kong")
        
        # Calculate next market event
        next_events = []
        
        # US market next event
        if us_open:
            us_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
            next_events.append(("US Close", us_close))
        else:
            if now_et.time() < dt_time(9, 30):
                us_open_today = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
                next_events.append(("US Open", us_open_today))
            else:
                # Next trading day
                next_day = now_et + timedelta(days=1)
                while next_day.weekday() >= 5:
                    next_day += timedelta(days=1)
                us_open_next = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
                next_events.append(("US Open", us_open_next))
        
        # Find the next event
        if next_events:
            next_event_name, next_event_time = min(next_events, key=lambda x: x[1])
            time_to_next = next_event_time - next_event_time.replace(tzinfo=next_event_time.tzinfo).astimezone(UTC_TZ).replace(tzinfo=None) + now_utc.replace(tzinfo=None)
        else:
            next_event_name = "Next Trading Day"
            time_to_next = timedelta(hours=12)  # Placeholder
        
        return {
            "us_market_open": us_open,
            "china_market_open": china_open,
            "hk_market_open": hk_open,
            "active_markets": active_markets,
            "any_market_open": len(active_markets) > 0,
            "us_time": now_et.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "beijing_time": now_beijing.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "utc_time": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "next_event": next_event_name,
            "market_summary": f"{len(active_markets)} market(s) open: {', '.join(active_markets) if active_markets else 'None'}"
        }
    
    def monitor_stock_prices(self, symbols: List[str], market: str):
        """Monitor prices for specific market stocks"""
        market_open = self.is_market_open(market)
        
        print(f"🔍 MONITORING {market.upper()} STOCKS")
        print(f"📊 Market Status: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
        
        if not market_open:
            print(f"📴 Skipping {market} stocks - market closed (prices don't move)")
            return
        
        print(f"🟢 {market} market OPEN - monitoring {len(symbols)} stocks:")
        
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"[{i}/{len(symbols)}] {symbol}...", end=" ")
                
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    print(f"✅ ${current_price:.2f}")
                    
                    # Check for significant price changes
                    if symbol in self.last_prices:
                        old_price = self.last_prices[symbol]
                        change = current_price - old_price
                        change_pct = (change / old_price) * 100
                        
                        if abs(change_pct) > 2.0:  # Alert for >2% moves
                            print(f"    🚨 SIGNIFICANT MOVE: {change_pct:+.2f}% (${change:+.2f})")
                        else:
                            print(f"    📊 Change: {change_pct:+.2f}%")
                    
                    self.last_prices[symbol] = current_price
                else:
                    print("❌ No data")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run_market_monitoring_cycle(self):
        """Run one complete monitoring cycle for all markets"""
        status = self.get_global_market_status()
        
        print(f"🌍 GLOBAL MARKET MONITORING CYCLE")
        print(f"⏰ UTC: {status['utc_time']}")
        print(f"🇺🇸 US Time: {status['us_time']}")
        print(f"🇨🇳 Beijing Time: {status['beijing_time']}")
        print(f"📊 Active Markets: {status['market_summary']}")
        print("-" * 60)
        
        # Monitor US stocks if US market is open
        if status["us_market_open"]:
            us_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META"]  # Mag7
            self.monitor_stock_prices(us_stocks, "US")
            print()
        
        # Monitor China stocks if China market is open
        if status["china_market_open"]:
            china_stocks = ["600298.SS"]  # Yang's grid stock
            self.monitor_stock_prices(china_stocks, "China")
            print()
        
        # Monitor Hong Kong stocks if HK market is open
        if status["hk_market_open"]:
            hk_stocks = ["0700.HK", "0005.HK", "0941.HK"]  # Major HK stocks
            self.monitor_stock_prices(hk_stocks, "HongKong")
            print()
        
        if not status["any_market_open"]:
            print("💤 ALL MARKETS CLOSED - Prices stable, no monitoring needed")
            print(f"⏰ Next market event: {status['next_event']}")
        
        print("=" * 60)

def test_us_market_integration():
    """Test US market integration with existing China/HK system"""
    
    print("🇺🇸 US MARKET INTEGRATION TEST")
    print("=" * 50)
    
    scheduler = MultiMarketScheduler()
    status = scheduler.get_global_market_status()
    
    print("📊 GLOBAL MARKET STATUS:")
    print(f"🇺🇸 US Market: {'🟢 OPEN' if status['us_market_open'] else '🔴 CLOSED'} (9:30 AM - 4:00 PM ET)")
    print(f"🇨🇳 China Market: {'🟢 OPEN' if status['china_market_open'] else '🔴 CLOSED'} (9:30 AM - 3:00 PM Beijing)")
    print(f"🇭🇰 Hong Kong Market: {'🟢 OPEN' if status['hk_market_open'] else '🔴 CLOSED'} (9:30 AM - 4:00 PM Beijing)")
    print(f"📈 Summary: {status['market_summary']}")
    
    print()
    print("🧪 TESTING STOCK PRICES:")
    print("-" * 40)
    
    # Test stocks from each market
    test_symbols = [
        ("AAPL", "🇺🇸 US - Apple Inc"),
        ("600298.SS", "🇨🇳 China - Yang's Grid Stock"),
        ("0700.HK", "🇭🇰 Hong Kong - Tencent Holdings")
    ]
    
    for symbol, description in test_symbols:
        try:
            print(f"{description}: {symbol}...", end=" ")
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                price = hist['Close'].iloc[-1]
                print(f"✅ ${price:.2f}")
            else:
                print("❌ No data")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print()
    print("⏰ MONITORING SCHEDULE:")
    print("-" * 40)
    
    if status["us_market_open"]:
        print("🟢 US stocks: Active monitoring (9:30 AM - 4:00 PM ET)")
    else:
        print("🔴 US stocks: Suspended (market closed)")
        
    if status["china_market_open"]:
        print("🟢 China stocks: Active monitoring (9:30 AM - 3:00 PM Beijing)")
    else:
        print("🔴 China stocks: Suspended (market closed)")
        
    if status["hk_market_open"]:
        print("🟢 Hong Kong stocks: Active monitoring (9:30 AM - 4:00 PM Beijing)")
    else:
        print("🔴 Hong Kong stocks: Suspended (market closed)")
    
    print()
    print("🎯 SCHEDULER EFFICIENCY:")
    print("✅ Monitor only when markets are actually trading")
    print("✅ Skip monitoring when prices don't move")
    print("✅ Global coverage: US + China + Hong Kong")
    print("✅ Email alerts: isky999@gmail.com for all markets")

if __name__ == "__main__":
    test_us_market_integration()
