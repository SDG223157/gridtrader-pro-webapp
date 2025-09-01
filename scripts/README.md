# China ETFs Update Scripts

This directory contains tools for updating the China ETFs list in GridTrader Pro's systematic trading engine with the most traded ETFs from cn.investing.com.

## 📁 Files

### Core Scripts
- **`validate_china_etfs.py`** - Validates current ETF symbols with yfinance
- **`update_china_etfs.py`** - Updates systematic_trading.py with new ETF data
- **`test_china_sector_analysis.py`** - Tests sector analysis after updates

### Data Files
- **`china_etfs_template.csv`** - Template CSV format for ETF data collection

## 🚀 Quick Usage

### Option 1: Complete Update Process

```bash
# 1. Collect data from cn.investing.com (manual)
# Fill in china_etfs_update.csv with new data

# 2. Validate current ETFs
python scripts/validate_china_etfs.py

# 3. Update with new data
python scripts/update_china_etfs.py

# 4. Test the changes
python scripts/test_china_sector_analysis.py

# 5. Commit if successful
git add app/systematic_trading.py
git commit -m "Update China ETFs with 50+ most traded from cn.investing.com"
git push origin main
```

### Option 2: Validation Only

```bash
# Just check current ETFs status
python scripts/validate_china_etfs.py
```

## 📊 Data Collection Process

### 1. Manual Collection from cn.investing.com

1. Visit: https://cn.investing.com/etfs
2. Sort by trading volume (highest first)
3. Collect top 50+ ETFs
4. Fill in the CSV template

### 2. Required CSV Format

```csv
Symbol,Chinese_Name,English_Name,Volume_30d,Sector,Exchange,AUM,Expense_Ratio,Notes
513090.SS,易方达中证香港证券投资ETF,E Fund CSI HK Securities,9.23B,Hong Kong Securities,SS,15.2B,0.50%,High volume
```

### 3. Symbol Format Requirements

- **Shanghai**: `XXXXXX.SS` (e.g., 513090.SS)
- **Shenzhen**: `XXXXXX.SZ` (e.g., 159892.SZ)
- **6-digit code** + exchange suffix

## 🔧 Script Details

### validate_china_etfs.py

**Purpose**: Validate ETF symbols with yfinance
**Output**: 
- Console validation results
- CSV report with detailed data
- Performance metrics

**Usage**:
```bash
python scripts/validate_china_etfs.py
```

**Output Files**:
- `china_etfs_validation_report_YYYYMMDD_HHMMSS.csv`

### update_china_etfs.py

**Purpose**: Update systematic_trading.py with new ETF data
**Input**: CSV file with new ETF data
**Output**: Updated Python code

**Usage**:
```bash
python scripts/update_china_etfs.py
# Will prompt for CSV file path (default: china_etfs_update.csv)
```

**Features**:
- Automatic backup creation
- Code generation with comments
- Preview before applying changes
- Sector-based organization

### test_china_sector_analysis.py

**Purpose**: Test sector analysis functionality
**Tests**:
- Sector analysis execution
- Data integrity checks
- Market regime detection
- Performance validation

**Usage**:
```bash
python scripts/test_china_sector_analysis.py
```

## 📋 Update Workflow

### Step-by-Step Process

1. **Preparation**
   ```bash
   cd /path/to/gridtrader-pro-webapp
   cp scripts/china_etfs_template.csv china_etfs_update.csv
   ```

2. **Data Collection**
   - Open cn.investing.com/etfs
   - Sort by volume
   - Fill in china_etfs_update.csv with top 50+ ETFs

3. **Validation**
   ```bash
   python scripts/validate_china_etfs.py
   ```

4. **Update**
   ```bash
   python scripts/update_china_etfs.py
   ```

5. **Testing**
   ```bash
   python scripts/test_china_sector_analysis.py
   ```

6. **Deployment**
   ```bash
   git add app/systematic_trading.py
   git commit -m "Update China ETFs with latest high-volume ETFs"
   git push origin main
   ```

## 🎯 Success Criteria

### Validation Success
- [ ] 95%+ symbols valid in yfinance
- [ ] All major sectors represented
- [ ] Volume data consistent
- [ ] No duplicate symbols

### Update Success
- [ ] Backup created successfully
- [ ] Code generation completed
- [ ] systematic_trading.py updated
- [ ] No syntax errors

### Testing Success
- [ ] Sector analysis runs < 30 seconds
- [ ] Returns reasonable number of ETFs (40-60)
- [ ] Top ETFs have logical conviction scores
- [ ] No runtime errors or exceptions

## ⚠️ Troubleshooting

### Common Issues

**"No module named 'app'"**
```bash
# Run from GridTrader Pro root directory
cd /path/to/gridtrader-pro-webapp
python scripts/script_name.py
```

**"ETF symbol not found in yfinance"**
- Some cn.investing.com symbols may not be in yfinance
- Cross-reference with official exchange listings
- Consider alternative data sources

**"Analysis takes too long"**
- Reduce number of ETFs (remove lowest volume)
- Optimize yfinance calls
- Check network connectivity

**"Invalid CSV format"**
- Use UTF-8 encoding
- Check column names match exactly
- Ensure no empty rows

## 📈 Performance Optimization

### For Large ETF Lists (100+)

1. **Parallel Processing**
   ```python
   # Use ThreadPoolExecutor for yfinance calls
   with ThreadPoolExecutor(max_workers=20) as executor:
       # Process multiple symbols simultaneously
   ```

2. **Caching**
   ```python
   # Cache yfinance results for repeated runs
   @lru_cache(maxsize=1000)
   def get_etf_data(symbol):
       # Cached ETF data retrieval
   ```

3. **Batch Processing**
   ```python
   # Process ETFs in batches to avoid rate limits
   for batch in chunks(symbols, 10):
       # Process batch with delay
       time.sleep(1)
   ```

## 🔄 Automation Ideas

### Future Enhancements

1. **Automated Collection**: Web scraping script for cn.investing.com
2. **Scheduled Updates**: Cron job for monthly ETF refresh
3. **Performance Tracking**: Monitor ETF performance over time
4. **Alert System**: Notify when ETFs become illiquid
5. **A/B Testing**: Compare old vs new ETF selections

---

**Ready to update your China ETFs with the latest market data! 🚀**
