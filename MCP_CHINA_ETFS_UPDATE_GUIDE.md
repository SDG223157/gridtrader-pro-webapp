# MCP China ETFs Update Tool Guide

## 🤖 Update China ETFs Directly Through Cursor with Natural Language

This guide shows how to use the new MCP tool to update China ETFs directly in Cursor by pasting CSV data from cn.investing.com.

---

## 🚀 Quick Usage

### Simple Command in Cursor:
```
Update China ETFs with this CSV data:

名称,代码,最新价,涨跌幅,交易量,时间
Huatai-PB CSOP HS Tech Id(QDII),513130,0.770,+1.32%,5.94B,11:29:59
ChinaAMC Hangsheng Tech (QDII),513180,0.783,+1.29%,5.76B,11:29:59
华夏恒生互联网科技业ETF(QDII),513330,0.540,+1.89%,5.37B,11:29:58
[... paste your full CSV data here ...]
```

---

## 📋 Step-by-Step Process

### Step 1: Collect Data from cn.investing.com

1. **Visit**: https://cn.investing.com/etfs
2. **Sort by**: 交易量 (Trading Volume) - Highest first
3. **Copy the table data** including headers
4. **Ensure format**: 名称,代码,最新价,涨跌幅,交易量,时间

### Step 2: Use MCP Tool in Cursor

**Natural Language Command:**
```
Update China ETFs with the latest data from cn.investing.com:

[paste your CSV data here]
```

**Alternative Commands:**
```
Process this China ETF data and generate code for systematic_trading.py:

[CSV data]
```

```
I have new China ETF data from cn.investing.com, please update the ETF list:

[CSV data]
```

### Step 3: Review Results

The MCP tool will return:
- ✅ **Processing summary** (number of ETFs processed)
- 📊 **Top 10 ETFs** by trading volume
- 📈 **Sector breakdown** (Technology, Healthcare, etc.)
- 🔧 **Generated Python code** ready for systematic_trading.py
- 📋 **Step-by-step instructions** for manual update

### Step 4: Apply Changes

1. **Copy the generated code** from the MCP response
2. **Open**: `app/systematic_trading.py`
3. **Find**: Line ~104 `self.china_sector_etfs = {`
4. **Replace**: The entire dictionary with the generated code
5. **Save** the file

### Step 5: Test and Deploy

```bash
# Validate symbols
python scripts/validate_china_etfs.py

# Test sector analysis
python scripts/test_china_sector_analysis.py

# Deploy changes
git add app/systematic_trading.py
git commit -m "Update China ETFs with latest from cn.investing.com via MCP"
git push origin main
```

---

## 🎯 Expected MCP Response

### Successful Processing:
```
🇨🇳 China ETFs Update Successful!

✅ Processed 50 ETFs from cn.investing.com

📊 Top 10 by Volume:
1. 513130.SS: Huatai-PB CSOP HS Tech Id(QDII)... (5.94B)
2. 513180.SS: ChinaAMC Hangsheng Tech (QDII)... (5.76B)
3. 513330.SS: 华夏恒生互联网科技业ETF(QDII)... (5.37B)
...

📈 Sector Breakdown:
• Technology & Innovation: 23 ETFs
• Healthcare & Biotech: 8 ETFs  
• Financial Services: 6 ETFs
• Hong Kong & International: 5 ETFs
...

🔧 Generated Code:
```python
        # Chinese Market ETFs - Updated from cn.investing.com via MCP
        # Top 50 most actively traded ETFs - Updated 2025-09-01 12:30:15
        self.china_sector_etfs = {
            # Technology & Innovation - 23 ETFs
            '513130.SS': 'Huatai-PB CSOP HS Tech Id(QDII)',  # 5.94B volume
            '513180.SS': 'ChinaAMC Hangsheng Tech (QDII)',  # 5.76B volume
            ...
        }
```

📋 Next Steps:
1. Copy the generated code above
2. Replace china_sector_etfs in app/systematic_trading.py
3. Test: python scripts/validate_china_etfs.py
4. Deploy: git commit and push

🎯 Ready to update your systematic trading engine with the latest China ETFs!
```

---

## 🔧 Technical Details

### API Endpoint
- **URL**: `POST /api/china-etfs/update`
- **Authentication**: Bearer token (automatic via MCP)
- **Input**: CSV data string
- **Output**: Processed ETF data and Python code

### Data Processing
1. **CSV Parsing**: Handles Chinese column names
2. **Symbol Conversion**: 6-digit codes → .SS/.SZ format
3. **Volume Parsing**: B/M suffixes → numeric values
4. **Sector Classification**: Automatic from ETF names
5. **Sorting**: By trading volume (highest first)
6. **Code Generation**: Ready-to-use Python dictionary

### Error Handling
- Invalid CSV format detection
- Missing column handling
- Symbol validation
- Sector classification fallbacks

---

## 💡 Usage Examples

### Example 1: Small Update (5 ETFs)
```
Update China ETFs with this data:

名称,代码,最新价,涨跌幅,交易量,时间
Huatai-PB CSOP HS Tech Id(QDII),513130,0.770,+1.32%,5.94B,11:29:59
ChinaAMC Hangsheng Tech (QDII),513180,0.783,+1.29%,5.76B,11:29:59
华夏恒生互联网科技业ETF(QDII),513330,0.540,+1.89%,5.37B,11:29:58
GF CSI Hong Kong Brand Nm Drug(QDII),513120,1.528,+3.10%,5.17B,11:29:59
ChinaAMC CSI A500,512050,1.125,-0.27%,3.71B,11:29:59
```

### Example 2: Full Update (50+ ETFs)
```
Process the latest China ETF data from cn.investing.com and generate systematic_trading.py code:

[paste full CSV with 50+ rows]
```

### Example 3: Sector-Specific Update
```
Update China technology ETFs with this data from cn.investing.com:

[paste technology ETFs CSV data]
```

---

## ⚠️ Important Notes

### CSV Format Requirements
- **Headers must be**: 名称,代码,最新价,涨跌幅,交易量,时间
- **Encoding**: UTF-8 (Chinese characters supported)
- **Volume format**: Use B for billions, M for millions (e.g., 5.94B, 830M)

### Symbol Conversion Rules
- **Shanghai (.SS)**: 51xxxx, 58xxxx, 56xxxx, 52xxxx, 50xxxx
- **Shenzhen (.SZ)**: 15xxxx, 16xxxx, 17xxxx

### Limitations
- Processes top 50 ETFs by volume
- Requires valid 6-digit ETF codes
- Chinese names must be properly encoded

---

## 🎯 Benefits

### Before (Manual Process):
1. Download CSV from cn.investing.com
2. Run Python scripts locally
3. Process and validate data
4. Generate code manually
5. Update systematic_trading.py
6. Test and deploy

**Time**: ~30-60 minutes

### After (MCP Tool):
1. Copy CSV data from cn.investing.com
2. Paste in Cursor with natural language command
3. Copy generated code to systematic_trading.py
4. Test and deploy

**Time**: ~5-10 minutes

### Key Advantages:
- 🚀 **6x faster** update process
- 🤖 **Natural language** interface
- ✅ **Automatic processing** and validation
- 📋 **Ready-to-use code** generation
- 🔄 **Seamless workflow** in Cursor

---

## 🔄 Workflow Integration

### Regular Update Schedule

**Monthly**: Quick volume check
```
Check current China ETF volumes and update if needed
```

**Quarterly**: Full refresh
```
Update China ETFs with the latest 50 most traded from cn.investing.com:

[paste full CSV data]
```

### Emergency Updates
```
Urgent: Update China ETFs due to market changes:

[paste updated CSV data]
```

---

## 🧪 Testing the Tool

Once your MCP is properly configured, you can test with:

```
Test the China ETF update tool with sample data:

名称,代码,最新价,涨跌幅,交易量,时间
Test ETF,513130,1.00,+1.00%,1.00B,12:00:00
```

Expected response:
- Processing confirmation
- Generated code snippet
- Instructions for next steps

---

## 🎉 Success!

You now have a **seamless AI-powered workflow** for updating China ETFs:

1. **Visit cn.investing.com** → Copy CSV data
2. **Ask Cursor** → "Update China ETFs with this data: [paste]"
3. **Copy generated code** → Update systematic_trading.py
4. **Deploy** → git commit and push

**Total time**: ~5 minutes for complete ETF universe refresh! 🚀

This makes keeping your China ETF data current effortless and enables rapid response to market changes.
