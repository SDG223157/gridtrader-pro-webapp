# 📊 Mandatory Portfolio Building Workflow with yfinance Price Validation

## 🚨 CRITICAL REQUIREMENT

**ALWAYS fetch current prices with yfinance BEFORE using MCP tools for portfolio building.**

This prevents pricing errors and ensures zero P&L when purchasing stocks at current market prices.

---

## 🔄 Standardized Workflow

### **STEP 1: Price Validation (MANDATORY)**
```bash
# Run yfinance price validation FIRST
source venv/bin/activate
python validate_stock_prices.py
```

**What this does:**
- ✅ Fetches real-time prices for all stocks
- ✅ Calculates exact quantities for target allocation
- ✅ Creates CSV file with validated data
- ✅ Provides summary of capital utilization
- ✅ Timestamps the price fetch for validation

### **STEP 2: Create Portfolio**
```python
# Use MCP tool to create portfolio
mcp_gridtrader-pro_create_portfolio(
    name="Your Portfolio Name",
    initial_capital=10000000,
    description="Portfolio with yfinance validated prices",
    strategy_type="growth"
)
```

### **STEP 3: Execute Purchases with Validated Prices**
```python
# Use EXACT prices from yfinance validation
# Example for each stock:
mcp_gridtrader-pro_buy_stock(
    portfolio_id="your_portfolio_id",
    symbol="300857.SZ",
    quantity=1529,  # From yfinance calculation
    price=163.43,   # From yfinance current price
    notes="协创数据 - yfinance validated price"
)
```

### **STEP 4: Verify Results**
- ✅ Check that all stocks show 0% P&L
- ✅ Verify Purchase Price = Current Price for all holdings
- ✅ Confirm proper allocation (~250K per stock)

---

## 🛠️ Helper Scripts Available

### **1. validate_stock_prices.py**
- **Purpose**: Quick price validation for any stock list
- **Usage**: `python validate_stock_prices.py`
- **Output**: CSV file with current prices and quantities

### **2. build_portfolio_with_yfinance.py**
- **Purpose**: Complete portfolio building workflow
- **Usage**: Advanced portfolio construction with validation
- **Output**: Execution plan and MCP commands

### **3. get_current_prices.py**
- **Purpose**: Batch price fetching for 40 Chinese stocks
- **Usage**: `python get_current_prices.py`
- **Output**: Comprehensive price report

---

## ⚠️ Common Mistakes to Avoid

### **❌ DON'T DO THIS:**
- Using estimated prices without yfinance validation
- Using outdated prices from previous sessions
- Assuming MCP API prices are current
- Skipping price validation step

### **✅ ALWAYS DO THIS:**
1. Run yfinance price validation FIRST
2. Use exact prices from validation output
3. Verify zero P&L after purchases
4. Save validation files for reference

---

## 🎯 Why This Workflow is Critical

### **The 601717.SS Lesson:**
- **Problem**: Bought at $28.90, current price was $24.26
- **Loss**: -16.1% P&L due to incorrect pricing
- **Solution**: yfinance validation would have caught this

### **Benefits of yfinance Validation:**
- ✅ **Accurate Pricing**: Real-time market data
- ✅ **Zero P&L**: Purchase price = current price
- ✅ **Error Prevention**: Catches pricing discrepancies
- ✅ **Perfect Allocation**: Precise quantity calculations
- ✅ **Audit Trail**: Timestamped validation records

---

## 📋 Quick Reference Commands

### **For 40 Chinese Stocks Portfolio:**
```bash
# 1. Validate prices (MANDATORY)
python validate_stock_prices.py

# 2. Create portfolio (use MCP)
# mcp_gridtrader-pro_create_portfolio(...)

# 3. Use validated prices from CSV file
# Follow exact prices and quantities from validation output

# 4. Verify results
# Check that all holdings show 0% P&L
```

### **For Custom Stock Lists:**
```python
# Modify validate_stock_prices.py with your symbols
custom_stocks = ["AAPL", "MSFT", "GOOGL"]
validated_df = validate_and_get_prices(custom_stocks)
```

---

## 🚀 Automation Options

### **Option 1: Manual Execution (Recommended)**
- Run validation script
- Copy prices to MCP commands
- Execute purchases manually
- Maximum control and verification

### **Option 2: Semi-Automated**
- Use `build_portfolio_with_yfinance.py`
- Generate MCP command list
- Execute commands in batches
- Good for large portfolios

### **Option 3: Full Automation (Advanced)**
- Integrate yfinance validation into MCP server
- Automatic price validation before purchases
- Requires MCP server modifications

---

## 📚 Best Practices

1. **Always validate prices first** - No exceptions
2. **Save validation files** - For audit and reference
3. **Check timestamps** - Ensure prices are recent (<30 min)
4. **Verify zero P&L** - After all purchases complete
5. **Document the process** - Keep records of price validation

**Remember: Price accuracy is critical for portfolio success!** 🎯
