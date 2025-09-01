#!/usr/bin/env python3
"""
Test China Sector Analysis with Updated ETFs
Validates the systematic trading engine works with new ETF data
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_china_sector_analysis():
    """Test China sector analysis with updated ETFs"""
    
    print("🧪 Testing China Sector Analysis")
    print("=" * 40)
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import the systematic trading engine
        from app.systematic_trading import systematic_trading_engine
        
        print("✅ Systematic trading engine imported successfully")
        
        # Test with different lookback periods
        test_periods = [30, 60, 90]
        
        for period in test_periods:
            print(f"\n🔍 Testing {period}-day analysis...")
            
            start_time = time.time()
            
            try:
                # Run sector analysis
                sector_scores = systematic_trading_engine.calculate_sector_scores("China", period)
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"✅ {period}-day analysis completed in {duration:.2f} seconds")
                print(f"📊 Analyzed {len(sector_scores)} sectors")
                
                if sector_scores:
                    print(f"🏆 Top 3 ETFs:")
                    for i, score in enumerate(sector_scores[:3]):
                        print(f"   {i+1}. {score.symbol}: {score.sector[:30]}...")
                        print(f"      Conviction: {score.conviction_score:.3f}")
                        print(f"      Weight: {score.recommended_weight*100:.1f}%")
                
                # Performance check
                if duration > 60:
                    print(f"⚠️  Analysis took {duration:.1f}s - consider optimizing")
                elif duration > 30:
                    print(f"🟡 Analysis took {duration:.1f}s - acceptable but could be faster")
                else:
                    print(f"🟢 Analysis performance: Excellent ({duration:.1f}s)")
                
            except Exception as e:
                print(f"❌ {period}-day analysis failed: {e}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the GridTrader Pro root directory")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_etf_data_integrity():
    """Test the integrity of ETF data structure"""
    
    print("\n🔍 Testing ETF Data Integrity")
    print("=" * 40)
    
    try:
        from app.systematic_trading import systematic_trading_engine
        
        etfs = systematic_trading_engine.china_sector_etfs
        
        print(f"📊 Total China ETFs: {len(etfs)}")
        
        # Check symbol formats
        valid_symbols = 0
        invalid_symbols = []
        
        for symbol in etfs.keys():
            if re.match(r'^[0-9]{6}\.(SS|SZ)$', symbol):
                valid_symbols += 1
            else:
                invalid_symbols.append(symbol)
        
        print(f"✅ Valid symbol format: {valid_symbols}/{len(etfs)}")
        
        if invalid_symbols:
            print(f"❌ Invalid symbol formats:")
            for symbol in invalid_symbols:
                print(f"   {symbol}")
        
        # Check exchange distribution
        ss_count = sum(1 for symbol in etfs.keys() if symbol.endswith('.SS'))
        sz_count = sum(1 for symbol in etfs.keys() if symbol.endswith('.SZ'))
        
        print(f"📈 Exchange distribution:")
        print(f"   Shanghai (.SS): {ss_count} ETFs")
        print(f"   Shenzhen (.SZ): {sz_count} ETFs")
        
        # Check for duplicates
        symbols = list(etfs.keys())
        unique_symbols = set(symbols)
        
        if len(symbols) == len(unique_symbols):
            print("✅ No duplicate symbols found")
        else:
            duplicates = len(symbols) - len(unique_symbols)
            print(f"❌ Found {duplicates} duplicate symbols")
        
        return len(invalid_symbols) == 0
        
    except Exception as e:
        print(f"❌ Data integrity test failed: {e}")
        return False

def test_market_regime_detection():
    """Test market regime detection with updated data"""
    
    print("\n🔍 Testing Market Regime Detection")
    print("=" * 40)
    
    try:
        from app.systematic_trading import systematic_trading_engine
        
        # Test market regime detection
        regime = systematic_trading_engine.detect_market_regime(60)
        
        print(f"📊 Current Market Regime: {regime.value}")
        print(f"✅ Market regime detection working")
        
        return True
        
    except Exception as e:
        print(f"❌ Market regime test failed: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    
    print("\n" + "=" * 50)
    print("📋 CHINA ETFS UPDATE TEST REPORT")
    print("=" * 50)
    
    tests = [
        ("Sector Analysis", test_china_sector_analysis),
        ("Data Integrity", test_etf_data_integrity),
        ("Market Regime", test_market_regime_detection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed - ETF update successful!")
        print("\n📋 Ready for deployment:")
        print("   git add app/systematic_trading.py")
        print("   git commit -m 'Update China ETFs with 50+ most traded from cn.investing.com'")
        print("   git push origin main")
    else:
        print("⚠️  Some tests failed - review before deploying")
    
    return passed == total

def main():
    """Main testing process"""
    
    print("🇨🇳 China ETFs Update Testing Tool")
    print("=" * 45)
    
    # Check if we're in the right directory
    if not os.path.exists("app/systematic_trading.py"):
        print("❌ Please run this script from the GridTrader Pro root directory")
        print("Current directory:", os.getcwd())
        return False
    
    # Run comprehensive tests
    success = generate_test_report()
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
