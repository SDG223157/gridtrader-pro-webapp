# China ETFs Update Guide - cn.investing.com Integration

## 🎯 Complete Guide for Updating 50+ Most Traded China ETFs

This guide provides a systematic approach to update the China sector analysis with the most actively traded ETFs from cn.investing.com, ensuring your systematic trading engine has the latest and most liquid investment options.

---

## 📋 Prerequisites

- ✅ Access to cn.investing.com
- ✅ Understanding of Chinese market structure (Shanghai/Shenzhen exchanges)
- ✅ Python environment for data processing
- ✅ GridTrader Pro codebase access
- ✅ Basic knowledge of ETF symbols and sectors

---

## 🔍 Step 1: Data Collection from cn.investing.com

### 1.1 Navigate to ETF Data

1. **Visit**: [cn.investing.com/etfs](https://cn.investing.com/etfs)
2. **Filter Settings**:
   - Market: China
   - Exchange: Shanghai Stock Exchange (SSE), Shenzhen Stock Exchange (SZSE)
   - Sort by: Trading Volume (Highest first)
   - Time period: Last 30 days

### 1.2 Data Points to Collect

For each ETF, gather:
```
Required Fields:
- Symbol (e.g., 513090.SS, 159892.SZ)
- Chinese Name (e.g., 易方达中证香港证券投资ETF)
- English Name (if available)
- Trading Volume (30-day average)
- Sector/Category
- Exchange (SS for Shanghai, SZ for Shenzhen)
- Assets Under Management (AUM)
- Expense Ratio (if available)
```

### 1.3 Manual Collection Template

Create a spreadsheet with these columns:
```csv
Symbol,Chinese_Name,English_Name,Volume_30d,Sector,Exchange,AUM,Expense_Ratio,Notes
513090.SS,易方达中证香港证券投资ETF,E Fund CSI HK Securities Investment ETF,9.23B,Hong Kong Securities,SS,15.2B,0.50%,High volume
159892.SZ,华夏恒生香港上市生物科技ETF,ChinaAMC Hang Seng HK Biotech ETF,8.76B,Biotech,SZ,3.8B,0.75%,Healthcare focus
```

---

## 🤖 Step 2: Automated Data Collection (Optional)

### 2.1 Web Scraping Script Template

```python
#!/usr/bin/env python3
"""
China ETFs Data Collector from cn.investing.com
Customize this script for automated data collection
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from typing import List, Dict

class ChinaETFCollector:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def collect_etf_data(self, max_etfs: int = 50) -> List[Dict]:
        """
        Collect ETF data from cn.investing.com
        
        Note: This is a template - you'll need to adapt the selectors
        based on the actual website structure
        """
        etfs = []
        
        try:
            # Example URL - adjust based on actual site structure
            url = "https://cn.investing.com/etfs/china"
            response = self.session.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example selectors - adapt based on actual HTML structure
            etf_rows = soup.find_all('tr', class_='etf-row')[:max_etfs]
            
            for row in etf_rows:
                try:
                    # Adapt these selectors based on actual HTML
                    symbol = row.find('td', class_='symbol').text.strip()
                    name = row.find('td', class_='name').text.strip()
                    volume = row.find('td', class_='volume').text.strip()
                    sector = row.find('td', class_='sector').text.strip()
                    
                    # Determine exchange from symbol
                    exchange = 'SS' if '.SS' in symbol else 'SZ' if '.SZ' in symbol else 'Unknown'
                    
                    etfs.append({
                        'symbol': symbol,
                        'chinese_name': name,
                        'volume': volume,
                        'sector': sector,
                        'exchange': exchange
                    })
                    
                except Exception as e:
                    print(f"Error parsing row: {e}")
                    continue
                    
                # Be respectful - add delay between requests
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error collecting data: {e}")
            
        return etfs
    
    def save_to_csv(self, etfs: List[Dict], filename: str = 'china_etfs_update.csv'):
        """Save collected data to CSV for review"""
        df = pd.DataFrame(etfs)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ Saved {len(etfs)} ETFs to {filename}")
        
    def generate_python_dict(self, etfs: List[Dict]) -> str:
        """Generate Python dictionary code for systematic_trading.py"""
        
        code_lines = ["# Updated China Sector ETFs - From cn.investing.com"]
        code_lines.append("self.china_sector_etfs = {")
        
        # Group by sector for better organization
        sectors = {}
        for etf in etfs:
            sector = etf.get('sector', 'Other')
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(etf)
        
        for sector, sector_etfs in sectors.items():
            code_lines.append(f"    # {sector}")
            for etf in sector_etfs:
                symbol = etf['symbol']
                name = etf['chinese_name']
                volume = etf.get('volume', 'N/A')
                code_lines.append(f"    '{symbol}': '{name}',  # Volume: {volume}")
            code_lines.append("")
        
        code_lines.append("}")
        
        return "\n".join(code_lines)

# Usage example
if __name__ == "__main__":
    collector = ChinaETFCollector()
    etfs = collector.collect_etf_data(50)
    
    if etfs:
        collector.save_to_csv(etfs)
        python_code = collector.generate_python_dict(etfs)
        
        with open('china_etfs_code.py', 'w', encoding='utf-8') as f:
            f.write(python_code)
        
        print(f"✅ Generated code for {len(etfs)} ETFs")
        print("📁 Files created:")
        print("   - china_etfs_update.csv (for review)")
        print("   - china_etfs_code.py (for systematic_trading.py)")
    else:
        print("❌ No ETF data collected")
```

### 2.2 Manual Verification Script

```python
#!/usr/bin/env python3
"""
Verify ETF symbols with yfinance before updating
"""

import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time

def verify_etf_symbol(symbol: str) -> Dict:
    """Verify if ETF symbol is valid with yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Try to get recent price data
        hist = ticker.history(period="5d")
        
        if not hist.empty and info:
            return {
                'symbol': symbol,
                'valid': True,
                'name': info.get('longName', 'Unknown'),
                'currency': info.get('currency', 'CNY'),
                'exchange': info.get('exchange', 'Unknown'),
                'volume': hist['Volume'].iloc[-1] if not hist.empty else 0,
                'last_price': hist['Close'].iloc[-1] if not hist.empty else 0
            }
        else:
            return {'symbol': symbol, 'valid': False, 'error': 'No data available'}
            
    except Exception as e:
        return {'symbol': symbol, 'valid': False, 'error': str(e)}

def verify_etf_list(symbols: List[str]) -> pd.DataFrame:
    """Verify multiple ETF symbols in parallel"""
    
    print(f"🔍 Verifying {len(symbols)} ETF symbols with yfinance...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(verify_etf_symbol, symbols))
    
    df = pd.DataFrame(results)
    
    valid_count = df['valid'].sum()
    invalid_count = len(df) - valid_count
    
    print(f"✅ Valid ETFs: {valid_count}")
    print(f"❌ Invalid ETFs: {invalid_count}")
    
    if invalid_count > 0:
        print("\n❌ Invalid symbols:")
        invalid_symbols = df[~df['valid']]['symbol'].tolist()
        for symbol in invalid_symbols:
            error = df[df['symbol'] == symbol]['error'].iloc[0]
            print(f"   {symbol}: {error}")
    
    return df

# Usage
if __name__ == "__main__":
    # Test with current symbols first
    current_symbols = [
        '513090.SS', '159892.SZ', '513060.SS', '513120.SS', 
        '512660.SS', '512670.SS', '588000.SS', '515050.SS'
    ]
    
    results_df = verify_etf_list(current_symbols)
    results_df.to_csv('etf_verification_results.csv', index=False)
    
    print("\n📊 Verification complete - see etf_verification_results.csv")
```

---

## 📝 Step 3: Manual Data Collection Process

### 3.1 cn.investing.com Navigation

1. **Go to**: https://cn.investing.com/etfs
2. **Sort by**: Volume (highest first)
3. **Filter by**: 
   - Chinese ETFs only
   - Active trading status
   - Minimum AUM threshold

### 3.2 Data Collection Spreadsheet

Create this template and fill manually:

```csv
Rank,Symbol,Chinese_Name,English_Name,Volume_30d,Sector,Exchange,AUM,Notes
1,513090.SS,易方达中证香港证券投资ETF,E Fund CSI HK Securities Investment ETF,9.23B,Hong Kong Securities,SS,15.2B,Highest volume
2,159892.SZ,华夏恒生香港上市生物科技ETF,ChinaAMC Hang Seng HK Biotech ETF,8.76B,Biotech,SZ,3.8B,Healthcare focus
3,513060.SS,博时恒生医疗保健QDII-ETF,Bosera Hang Seng Healthcare QDII ETF,4.35B,Healthcare,SS,2.1B,Medical sector
...
```

### 3.3 Sector Classification

Organize ETFs by these categories:

```
Technology & Innovation:
- 5G Communication (515050.SS)
- Semiconductors (512480.SS)
- Artificial Intelligence
- Internet Technology

Healthcare & Biotech:
- Medical Devices
- Pharmaceuticals
- Biotechnology
- Healthcare Services

Financial Services:
- Banking
- Insurance
- Securities
- Fintech

Consumer & Retail:
- Consumer Discretionary
- Consumer Staples
- E-commerce
- Brand Names

Infrastructure & Resources:
- Military/Defense
- Energy
- Materials
- Real Estate

Hong Kong & International:
- Hong Kong Securities
- Hong Kong Tech
- International Exposure
- Cross-border ETFs
```

---

## 🔧 Step 4: Code Implementation

### 4.1 Locate Target File

The China ETFs are defined in:
```
app/systematic_trading.py
Lines: ~104-197 (china_sector_etfs dictionary)
```

### 4.2 Current Structure Analysis

```python
# Current structure in systematic_trading.py
self.china_sector_etfs = {
    # Hong Kong & Tech ETFs (Highest Volume) - Shanghai Stock Exchange
    '513090.SS': '易方达中证香港证券投资ETF',                    # 9.23B volume
    '513130.SS': 'Huatai-PB CSOP HS Tech Id(QDII)',       # 8.76B volume
    # ... more ETFs
}
```

### 4.3 Update Script Template

```python
#!/usr/bin/env python3
"""
China ETFs Update Script for GridTrader Pro
Updates the china_sector_etfs dictionary with fresh data
"""

import re
from typing import Dict, List

def create_updated_etfs_dict(csv_file: str = 'china_etfs_update.csv') -> str:
    """
    Generate updated china_sector_etfs dictionary from CSV data
    """
    
    import pandas as pd
    
    # Read the collected data
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # Sort by volume (highest first)
    df['Volume_Numeric'] = df['Volume_30d'].str.replace('B', '').str.replace('M', '').astype(float)
    df = df.sort_values('Volume_Numeric', ascending=False)
    
    # Generate Python dictionary code
    code_lines = []
    code_lines.append("        # Chinese Market ETFs - Updated from cn.investing.com")
    code_lines.append("        # Top 50+ most actively traded ETFs")
    code_lines.append("        self.china_sector_etfs = {")
    
    # Group by sector
    sectors = df.groupby('Sector')
    
    for sector_name, sector_etfs in sectors:
        code_lines.append(f"            # {sector_name}")
        
        for _, etf in sector_etfs.iterrows():
            symbol = etf['Symbol']
            chinese_name = etf['Chinese_Name']
            volume = etf['Volume_30d']
            
            # Clean the name for Python string
            cleaned_name = chinese_name.replace("'", "\\'")
            
            code_lines.append(f"            '{symbol}': '{cleaned_name}',  # {volume} volume")
        
        code_lines.append("")
    
    code_lines.append("        }")
    
    return "\n".join(code_lines)

def backup_current_etfs():
    """Backup current ETFs configuration"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"app/systematic_trading_backup_{timestamp}.py"
    
    shutil.copy("app/systematic_trading.py", backup_file)
    print(f"✅ Backup created: {backup_file}")

def update_systematic_trading_file(new_etfs_code: str):
    """Update the systematic_trading.py file with new ETFs"""
    
    with open("app/systematic_trading.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Find the china_sector_etfs section
    pattern = r"(# Chinese Market ETFs.*?self\.china_sector_etfs = {.*?})"
    
    if re.search(pattern, content, re.DOTALL):
        # Replace the existing section
        updated_content = re.sub(pattern, new_etfs_code, content, flags=re.DOTALL)
        
        with open("app/systematic_trading.py", "w", encoding="utf-8") as f:
            f.write(updated_content)
        
        print("✅ systematic_trading.py updated with new ETFs")
    else:
        print("❌ Could not find china_sector_etfs section to replace")
        print("Manual update required")

# Usage
if __name__ == "__main__":
    print("🔄 China ETFs Update Process")
    print("=" * 40)
    
    # Step 1: Backup current configuration
    backup_current_etfs()
    
    # Step 2: Generate new code from CSV
    try:
        new_code = create_updated_etfs_dict('china_etfs_update.csv')
        
        # Step 3: Save generated code for review
        with open('new_china_etfs_code.py', 'w', encoding='utf-8') as f:
            f.write(new_code)
        
        print("✅ Generated new ETFs code - saved to new_china_etfs_code.py")
        print("📋 Please review the generated code before applying")
        
        # Step 4: Ask for confirmation
        confirm = input("Apply changes to systematic_trading.py? (y/N): ")
        
        if confirm.lower() == 'y':
            update_systematic_trading_file(new_code)
            print("🎉 Update complete!")
        else:
            print("📝 Update cancelled - review new_china_etfs_code.py manually")
            
    except FileNotFoundError:
        print("❌ china_etfs_update.csv not found")
        print("Please create the CSV file with ETF data first")
    except Exception as e:
        print(f"❌ Error during update: {e}")
```

---

## 📊 Step 5: Data Validation & Testing

### 5.1 Symbol Validation Script

```python
#!/usr/bin/env python3
"""
Validate new China ETF symbols with yfinance
"""

import yfinance as yf
import sys

def validate_new_etfs():
    """Test all new ETF symbols"""
    
    # Read symbols from the updated file
    symbols = []
    
    # Extract symbols from systematic_trading.py
    with open("app/systematic_trading.py", "r") as f:
        content = f.read()
        
    # Find all symbols in the china_sector_etfs section
    import re
    pattern = r"'([^']+\.S[SZ])'"
    symbols = re.findall(pattern, content)
    
    print(f"🧪 Testing {len(symbols)} China ETF symbols...")
    
    valid_symbols = []
    invalid_symbols = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                valid_symbols.append(symbol)
                print(f"✅ {symbol}: Valid")
            else:
                invalid_symbols.append(symbol)
                print(f"❌ {symbol}: No data")
                
        except Exception as e:
            invalid_symbols.append(symbol)
            print(f"❌ {symbol}: Error - {e}")
    
    print(f"\n📊 Validation Results:")
    print(f"✅ Valid: {len(valid_symbols)}/{len(symbols)}")
    print(f"❌ Invalid: {len(invalid_symbols)}/{len(symbols)}")
    
    if invalid_symbols:
        print(f"\n❌ Invalid symbols to review:")
        for symbol in invalid_symbols:
            print(f"   {symbol}")
    
    return len(invalid_symbols) == 0

if __name__ == "__main__":
    success = validate_new_etfs()
    sys.exit(0 if success else 1)
```

### 5.2 Sector Analysis Test

```python
#!/usr/bin/env python3
"""
Test the updated sector analysis with new ETFs
"""

from app.systematic_trading import systematic_trading_engine

def test_china_sector_analysis():
    """Test China sector analysis with updated ETFs"""
    
    print("🧪 Testing China Sector Analysis with Updated ETFs")
    print("=" * 55)
    
    try:
        # Run sector analysis
        sector_scores = systematic_trading_engine.calculate_sector_scores("China", 90)
        
        print(f"✅ Analysis completed successfully")
        print(f"📊 Analyzed {len(sector_scores)} sectors")
        print(f"🏆 Top 5 ETFs:")
        
        for i, score in enumerate(sector_scores[:5]):
            print(f"   {i+1}. {score.symbol}: {score.sector}")
            print(f"      Conviction: {score.conviction_score:.3f}")
            print(f"      Weight: {score.recommended_weight*100:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

if __name__ == "__main__":
    test_china_sector_analysis()
```

---

## 🔄 Step 6: Implementation Workflow

### 6.1 Complete Update Process

```bash
# 1. Backup current configuration
cp app/systematic_trading.py app/systematic_trading_backup_$(date +%Y%m%d).py

# 2. Collect new data (manual or automated)
python collect_china_etfs.py

# 3. Verify symbols
python validate_etfs.py

# 4. Generate new code
python update_etfs.py

# 5. Review generated code
cat new_china_etfs_code.py

# 6. Apply changes (manual copy-paste or automated)
# Replace the china_sector_etfs section in app/systematic_trading.py

# 7. Test the changes
python test_sector_analysis.py

# 8. Commit changes
git add app/systematic_trading.py
git commit -m "Update China ETFs with 50+ most traded from cn.investing.com"
git push origin main
```

### 6.2 Manual Update Process

1. **Open**: `app/systematic_trading.py`
2. **Find**: Line ~104 `self.china_sector_etfs = {`
3. **Replace**: The entire dictionary with new data
4. **Format**: Maintain the existing structure and comments
5. **Test**: Run sector analysis to verify

---

## 📋 Step 7: Quality Assurance

### 7.1 Pre-Update Checklist

- [ ] Backup current `systematic_trading.py`
- [ ] Collect fresh data from cn.investing.com
- [ ] Verify all symbols with yfinance
- [ ] Review sector classifications
- [ ] Check volume data accuracy
- [ ] Validate exchange suffixes (.SS/.SZ)

### 7.2 Post-Update Checklist

- [ ] Run China sector analysis successfully
- [ ] Verify top ETFs make sense
- [ ] Check conviction scores are reasonable
- [ ] Test web interface displays correctly
- [ ] Confirm MCP commands work
- [ ] Monitor for any errors in logs

### 7.3 Performance Validation

```python
# Quick performance test
def performance_test():
    start_time = time.time()
    
    # Run analysis
    scores = systematic_trading_engine.calculate_sector_scores("China", 90)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"⏱️  Analysis completed in {duration:.2f} seconds")
    print(f"📊 Analyzed {len(scores)} ETFs")
    print(f"🎯 Performance: {'✅ Good' if duration < 30 else '⚠️ Slow'}")
    
    return duration < 30

performance_test()
```

---

## 🔄 Step 8: Maintenance Schedule

### 8.1 Regular Updates

**Monthly**: Quick volume check
- Check top 10 ETFs still have high volume
- Verify no major delisting events

**Quarterly**: Comprehensive update
- Full 50+ ETF refresh from cn.investing.com
- Add new high-volume ETFs
- Remove low-volume or delisted ETFs

**Annually**: Complete review
- Sector classification updates
- New ETF categories
- Performance analysis of selections

### 8.2 Monitoring Alerts

Set up monitoring for:
- ETFs with consistently low volume
- Failed yfinance data retrieval
- Sector analysis errors
- Performance degradation

---

## 🎯 Expected Outcomes

### After Update:
- ✅ **50+ most liquid China ETFs** in analysis
- ✅ **Current market representation** 
- ✅ **Improved sector coverage**
- ✅ **Better conviction scores**
- ✅ **Enhanced diversification options**

### Performance Metrics:
- Analysis completion time: < 30 seconds
- Valid symbols: > 95%
- Sector coverage: 8-12 major sectors
- Volume threshold: > 100M daily average

---

## 📞 Troubleshooting

### Common Issues:

**Symbol Format Errors**
```python
# Correct format examples:
'513090.SS'  # Shanghai Stock Exchange
'159892.SZ'  # Shenzhen Stock Exchange

# Incorrect formats:
'513090'     # Missing exchange suffix
'513090.SHA' # Wrong exchange code
```

**yfinance Validation Failures**
- Some symbols may not be available in yfinance
- Use alternative data sources for verification
- Cross-reference with official exchange listings

**Volume Data Inconsistencies**
- cn.investing.com may use different volume metrics
- Verify units (millions vs billions)
- Check time periods (daily vs monthly)

---

## 🚀 Quick Reference Commands

```bash
# Complete update in one session:
python collect_china_etfs.py    # Collect data
python validate_etfs.py         # Verify symbols  
python update_etfs.py           # Generate code
# Manual review and copy-paste
python test_sector_analysis.py  # Test changes
git add app/systematic_trading.py && git commit -m "Update China ETFs" && git push
```

---

## 📈 Success Metrics

### Validation Criteria:
- [ ] All symbols valid in yfinance
- [ ] Volume data accurate and recent
- [ ] Sector analysis runs without errors
- [ ] Top ETFs show reasonable conviction scores
- [ ] Web interface displays updated data
- [ ] MCP commands return fresh results

### Performance Targets:
- Symbol validation: 100% success rate
- Analysis speed: < 30 seconds for 50+ ETFs
- Data freshness: < 7 days old
- Coverage: All major China market sectors

This guide ensures you can efficiently update your China ETF universe with the most current and liquid options from cn.investing.com! 🚀
