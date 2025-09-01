# cn.investing.com ETF Update Procedure

## 🎯 Step-by-Step Guide for Updating China ETFs from cn.investing.com

Based on the actual data format from cn.investing.com, this guide provides the exact procedure for updating your China ETF universe with the most traded funds.

---

## 📊 Data Format from cn.investing.com

The data comes in this format:
```csv
名称,代码,最新价,涨跌幅,交易量,时间
Huatai-PB CSOP HS Tech Id(QDII),513130,0.770,+1.32%,5.94B,11:29:59
ChinaAMC Hangsheng Tech (QDII),513180,0.783,+1.29%,5.76B,11:29:59
华夏恒生互联网科技业ETF(QDII),513330,0.540,+1.89%,5.37B,11:29:58
```

**Column Meanings:**
- **名称** (Name): ETF name (Chinese + English if available)
- **代码** (Code): 6-digit ETF code (without exchange suffix)
- **最新价** (Latest Price): Current price
- **涨跌幅** (Change %): Daily change percentage
- **交易量** (Volume): Trading volume (B=Billions, M=Millions)
- **时间** (Time): Last update time

---

## 🔄 Complete Update Procedure

### Step 1: Data Collection from cn.investing.com

#### 1.1 Navigate to ETF Data
1. **Visit**: https://cn.investing.com/etfs
2. **Sort by**: 交易量 (Trading Volume) - Highest first
3. **Select timeframe**: Recent data (current day/week)

#### 1.2 Export Data
1. **Copy the table data** from the website
2. **Paste into Excel/Google Sheets**
3. **Save as CSV** with UTF-8 encoding
4. **Name the file**: `cn_investing_raw.csv`

#### 1.3 Data Quality Check
- Ensure all rows have valid 6-digit codes
- Check volume data is present (B/M suffixes)
- Verify Chinese names are properly encoded
- Remove any empty or invalid rows

### Step 2: Process Raw Data

#### 2.1 Run Processing Script
```bash
# Copy your raw data to the scripts directory
cp your_downloaded_file.csv scripts/cn_investing_raw.csv

# Run the parser
python scripts/parse_cn_investing_data.py
```

#### 2.2 Script Processing
The script will:
- ✅ Convert 6-digit codes to proper symbols (513130 → 513130.SS)
- ✅ Determine exchange (SS for Shanghai, SZ for Shenzhen)
- ✅ Parse volume data (5.94B → 5940 million)
- ✅ Classify sectors based on ETF names
- ✅ Extract English names where available
- ✅ Sort by trading volume (highest first)

#### 2.3 Output Files
- `china_etfs_processed.csv` - Clean, processed data
- `china_etfs_systematic_trading_code.py` - Ready-to-use Python code

### Step 3: Symbol Format Conversion

#### 3.1 Exchange Determination Rules
```python
# Shanghai Stock Exchange (.SS)
51xxxx → 51xxxx.SS  # Most ETFs
58xxxx → 58xxxx.SS  # STAR Market ETFs  
56xxxx → 56xxxx.SS  # Some special ETFs
52xxxx → 52xxxx.SS  # Sector ETFs
50xxxx → 50xxxx.SS  # Index ETFs

# Shenzhen Stock Exchange (.SZ)  
15xxxx → 15xxxx.SZ  # Most Shenzhen ETFs
16xxxx → 16xxxx.SZ  # Thematic ETFs
17xxxx → 17xxxx.SZ  # Some special ETFs
```

#### 3.2 Validation Examples
```
Original: 513130 → Converted: 513130.SS ✅
Original: 159892 → Converted: 159892.SZ ✅
Original: 588000 → Converted: 588000.SS ✅
```

### Step 4: Sector Classification

#### 4.1 Automated Sector Detection
The script automatically classifies ETFs based on name keywords:

**Technology & Innovation:**
- Keywords: 科技, 互联网, 人工智能, 5G, 通信, 软件, 芯片, 半导体
- Examples: 华夏恒生互联网科技业ETF, 华夏中证5G通信主题

**Healthcare & Biotech:**
- Keywords: 医疗, 生物, 医药, 保健
- Examples: 博时恒生医疗保健QDII-ETF, 华夏恒生香港上市生物科技ETF

**Financial Services:**
- Keywords: 银行, 证券, 金融, 保险
- Examples: 华宝中证银行, 华宝中证全指证券公司

**Hong Kong & International:**
- Keywords: 香港, 恒生, QDII
- Examples: 易方达中证香港证券投资ETF, GF CSI Hong Kong Brand Nm Drug

### Step 5: Update systematic_trading.py

#### 5.1 Backup Current Configuration
```bash
# Automatic backup is created by the script
cp app/systematic_trading.py app/systematic_trading_backup_$(date +%Y%m%d).py
```

#### 5.2 Apply New ETF Data
```bash
# Use the update script
python scripts/update_china_etfs.py

# When prompted, use: china_etfs_processed.csv
```

#### 5.3 Manual Update (Alternative)
1. **Open**: `app/systematic_trading.py`
2. **Find**: Line ~104 `self.china_sector_etfs = {`
3. **Replace**: With code from `china_etfs_systematic_trading_code.py`
4. **Save**: The file

### Step 6: Validation & Testing

#### 6.1 Validate Symbols
```bash
# Test all symbols with yfinance
python scripts/validate_china_etfs.py
```

Expected output:
```
✅ 513130.SS: Valid
✅ 513180.SS: Valid  
✅ 159892.SZ: Valid
...
📊 Valid: 48/50 (96.0%)
```

#### 6.2 Test Sector Analysis
```bash
# Test the updated sector analysis
python scripts/test_china_sector_analysis.py
```

Expected output:
```
✅ 90-day analysis completed in 25.3 seconds
📊 Analyzed 50 sectors
🏆 Top 3 ETFs:
   1. 513130.SS: Huatai-PB CSOP HS Tech Id(QDII)
      Conviction: 1.45
      Weight: 2.8%
```

### Step 7: Deploy Changes

#### 7.1 Commit to Repository
```bash
git add app/systematic_trading.py
git commit -m "Update China ETFs with 50+ most traded from cn.investing.com

- Updated with latest high-volume ETFs from cn.investing.com
- Included top technology, healthcare, and financial ETFs
- Verified all symbols with yfinance
- Tested sector analysis performance
- Volume range: 5.94B to 491M (top 50 ETFs)"

git push origin main
```

#### 7.2 Verify Deployment
1. **Wait for Coolify deployment** to complete
2. **Test web interface**: Visit https://gridsai.app/analytics
3. **Run China sector analysis**
4. **Verify new ETFs appear** in results

---

## 📋 Real Example Walkthrough

### Example Data Processing

**Input from cn.investing.com:**
```
华夏恒生互联网科技业ETF(QDII),513330,0.540,+1.89%,5.37B,11:29:58
```

**Processed Output:**
```csv
Symbol: 513330.SS
Chinese_Name: 华夏恒生互联网科技业ETF(QDII)
English_Name: (QDII)
Volume_30d: 5.37B
Volume_Numeric: 5370
Sector: Hong Kong & International
Exchange: SS
```

**Generated Code:**
```python
# Hong Kong & International
'513330.SS': '华夏恒生互联网科技业ETF(QDII)',  # 5.37B volume
```

### Top 10 ETFs Example

Based on your data, the top 10 would be:
```
1. 513130.SS: Huatai-PB CSOP HS Tech Id(QDII) - 5.94B volume
2. 513180.SS: ChinaAMC Hangsheng Tech (QDII) - 5.76B volume  
3. 513330.SS: 华夏恒生互联网科技业ETF(QDII) - 5.37B volume
4. 513120.SS: GF CSI Hong Kong Brand Nm Drug(QDII) - 5.17B volume
5. 512050.SS: ChinaAMC CSI A500 - 3.71B volume
6. 159792.SZ: 港股通互联网ETF - 3.65B volume
7. 513060.SS: 博时恒生医疗保健QDII-ETF - 3.31B volume
8. 513090.SS: 易方达中证香港证券投资ETF - 2.96B volume
9. 588000.SS: 华夏科创50场内联接基金 - 2.94B volume
10. 563360.SS: Huatai-PB CSI A500 - 2.36B volume
```

---

## 🛠️ Troubleshooting

### Common Issues

#### "Invalid CSV Format"
- **Problem**: Excel encoding issues
- **Solution**: Save as "CSV UTF-8" format
- **Alternative**: Use Google Sheets and download as CSV

#### "Symbol Not Found in yfinance"
- **Problem**: Some ETFs may not be in yfinance database
- **Solution**: Check official exchange listings
- **Workaround**: Remove problematic symbols from list

#### "Volume Parsing Errors"
- **Problem**: Inconsistent volume formats
- **Solution**: Manually clean volume data
- **Check**: Ensure B/M suffixes are consistent

### Data Quality Checks

```bash
# Check for duplicates
python -c "
import pandas as pd
df = pd.read_csv('china_etfs_processed.csv')
print('Duplicates:', df['Symbol'].duplicated().sum())
"

# Check symbol formats
python -c "
import pandas as pd
import re
df = pd.read_csv('china_etfs_processed.csv')
valid = df['Symbol'].str.match(r'^[0-9]{6}\.(SS|SZ)$')
print('Valid symbols:', valid.sum(), '/', len(df))
"
```

---

## 📈 Expected Results

### After Successful Update

**Sector Analysis Results:**
```
🇨🇳 China Market Sector Analysis

Market: China
Benchmark: CSI 300 Index (000300.SS)  
Market Regime: BULL MOMENTUM
Analyzed 50 sectors over 90 days

Top ETFs:
1. Technology ETFs with high conviction scores
2. Healthcare ETFs with growth momentum
3. Hong Kong ETFs with international exposure
4. Defense ETFs with strategic value
```

**Performance Metrics:**
- Analysis time: < 30 seconds
- Valid symbols: > 95%
- Sector coverage: 8-10 major categories
- Volume threshold: > 500M for top selections

---

## 🔄 Maintenance Schedule

### Regular Updates

**Monthly**: Quick volume check
- Verify top 10 ETFs still have high volume
- Check for any delisted funds

**Quarterly**: Full refresh
- Complete data collection from cn.investing.com
- Update with new high-volume ETFs
- Remove low-volume funds

**Semi-Annually**: Comprehensive review
- Sector classification updates
- Performance analysis of selections
- Strategy optimization

---

## 📞 Quick Reference Commands

```bash
# Complete update process
cp scripts/cn_investing_sample.csv cn_investing_raw.csv
# Edit cn_investing_raw.csv with fresh data from website
python scripts/parse_cn_investing_data.py
python scripts/validate_china_etfs.py
python scripts/update_china_etfs.py
python scripts/test_china_sector_analysis.py
git add app/systematic_trading.py && git commit -m "Update China ETFs" && git push
```

---

## 🎉 Success Validation

### Checklist
- [ ] Raw data collected from cn.investing.com
- [ ] CSV file properly formatted and encoded
- [ ] Processing script completed successfully
- [ ] All symbols validated with yfinance
- [ ] systematic_trading.py updated
- [ ] Sector analysis test passed
- [ ] Changes committed and deployed
- [ ] Web interface shows new ETFs

### Performance Targets
- **Processing time**: < 5 minutes total
- **Symbol validation**: > 95% success rate
- **Analysis speed**: < 30 seconds for 50 ETFs
- **Data freshness**: Same-day data from cn.investing.com

This procedure ensures you can efficiently update your China ETF universe with the most current and liquid options from cn.investing.com! 🚀
