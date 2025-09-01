#!/usr/bin/env python3
"""
China ETFs Validation Script
Validates ETF symbols with yfinance and generates reports
"""

import yfinance as yf
import pandas as pd
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import re

def extract_current_etfs():
    """Extract current China ETFs from systematic_trading.py"""
    try:
        with open("app/systematic_trading.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find china_sector_etfs section
        pattern = r"self\.china_sector_etfs\s*=\s*{(.*?)}"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            etfs_section = match.group(1)
            
            # Extract symbol-name pairs
            symbol_pattern = r"'([^']+\.S[SZ])'\s*:\s*'([^']+)'"
            symbols_data = re.findall(symbol_pattern, etfs_section)
            
            return [(symbol, name) for symbol, name in symbols_data]
        else:
            print("❌ Could not find china_sector_etfs section")
            return []
            
    except FileNotFoundError:
        print("❌ app/systematic_trading.py not found")
        return []

def verify_etf_symbol(symbol_data):
    """Verify single ETF symbol with yfinance"""
    symbol, chinese_name = symbol_data
    
    try:
        ticker = yf.Ticker(symbol)
        
        # Get basic info
        info = ticker.info
        
        # Get recent price data
        hist = ticker.history(period="5d")
        
        if not hist.empty:
            last_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            return {
                'symbol': symbol,
                'chinese_name': chinese_name,
                'valid': True,
                'last_price': last_price,
                'avg_volume': avg_volume,
                'currency': info.get('currency', 'CNY'),
                'exchange': info.get('exchange', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'error': None
            }
        else:
            return {
                'symbol': symbol,
                'chinese_name': chinese_name,
                'valid': False,
                'error': 'No price data available'
            }
            
    except Exception as e:
        return {
            'symbol': symbol,
            'chinese_name': chinese_name,
            'valid': False,
            'error': str(e)
        }

def validate_all_etfs(etfs_data, max_workers=10):
    """Validate all ETFs in parallel"""
    
    print(f"🔍 Validating {len(etfs_data)} China ETF symbols...")
    print("=" * 50)
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_symbol = {
            executor.submit(verify_etf_symbol, etf_data): etf_data[0] 
            for etf_data in etfs_data
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                results.append(result)
                
                status = "✅" if result['valid'] else "❌"
                print(f"{status} {result['symbol']}: {result.get('error', 'Valid')}")
                
            except Exception as e:
                print(f"❌ {symbol}: Exception - {e}")
                results.append({
                    'symbol': symbol,
                    'valid': False,
                    'error': f"Exception: {e}"
                })
    
    return results

def generate_validation_report(results):
    """Generate comprehensive validation report"""
    
    df = pd.DataFrame(results)
    
    valid_count = df['valid'].sum() if 'valid' in df.columns else 0
    total_count = len(df)
    invalid_count = total_count - valid_count
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION REPORT")
    print("=" * 50)
    print(f"Total ETFs: {total_count}")
    print(f"✅ Valid: {valid_count} ({valid_count/total_count*100:.1f}%)")
    print(f"❌ Invalid: {invalid_count} ({invalid_count/total_count*100:.1f}%)")
    
    if invalid_count > 0:
        print(f"\n❌ Invalid ETFs requiring attention:")
        invalid_etfs = df[~df['valid']] if 'valid' in df.columns else df
        for _, etf in invalid_etfs.iterrows():
            print(f"   {etf['symbol']}: {etf.get('error', 'Unknown error')}")
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"china_etfs_validation_report_{timestamp}.csv"
    df.to_csv(report_file, index=False, encoding='utf-8-sig')
    
    print(f"\n📄 Detailed report saved: {report_file}")
    
    # Generate summary for top performers
    if valid_count > 0:
        valid_df = df[df['valid'] == True] if 'valid' in df.columns else df
        
        if 'avg_volume' in valid_df.columns:
            top_volume = valid_df.nlargest(10, 'avg_volume')
            print(f"\n🏆 Top 10 by Volume:")
            for _, etf in top_volume.iterrows():
                volume_str = f"{etf['avg_volume']:,.0f}" if pd.notna(etf['avg_volume']) else "N/A"
                print(f"   {etf['symbol']}: {volume_str}")
    
    return valid_count >= total_count * 0.9  # 90% success rate

def main():
    """Main validation process"""
    
    print("🇨🇳 China ETFs Validation Tool")
    print("=" * 40)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extract current ETFs
    etfs_data = extract_current_etfs()
    
    if not etfs_data:
        print("❌ No ETF data found to validate")
        return False
    
    print(f"📋 Found {len(etfs_data)} ETFs to validate")
    
    # Validate all ETFs
    results = validate_all_etfs(etfs_data)
    
    # Generate report
    success = generate_validation_report(results)
    
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 Validation successful - ETFs are ready for production!")
    else:
        print("⚠️  Some ETFs failed validation - review before deploying")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
