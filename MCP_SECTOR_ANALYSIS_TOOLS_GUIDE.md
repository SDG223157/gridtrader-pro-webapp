# MCP Sector Analysis Tools Guide

## 🎯 US & China Market Sector Analysis via Natural Language Commands

This guide shows how to use the new MCP tools to get comprehensive sector analysis for both US and China markets directly through Cursor.

---

## 🚀 New MCP Tools Added

### 1. `get_us_sector_analysis`
**Description**: Get US market sector analysis with ETF recommendations
**Natural Language**: "Show me US sector analysis" or "What are the best US sector ETFs?"

### 2. `get_china_sector_analysis`  
**Description**: Get China market sector analysis with ETF recommendations
**Natural Language**: "Show me China sector analysis" or "What are the best China sector ETFs?"

---

## 💬 Natural Language Commands

### US Market Analysis

**Basic Commands:**
```
Show me US sector analysis
```

```
What are the best US sector ETFs right now?
```

```
Run US market sector analysis for 60 days
```

```
Give me US sector recommendations for this week
```

**Advanced Commands:**
```
Analyze US technology and healthcare sectors
```

```
What US sectors have the highest conviction scores?
```

```
Show me US sector momentum and mean reversion opportunities
```

### China Market Analysis

**Basic Commands:**
```
Show me China sector analysis
```

```
What are the best China sector ETFs?
```

```
Run China market sector analysis for 90 days
```

```
Give me China sector recommendations
```

**Advanced Commands:**
```
Analyze Chinese healthcare and tech ETFs
```

```
What China sectors are showing strong momentum?
```

```
Show me Hong Kong and mainland China ETF opportunities
```

---

## 📊 Expected Response Format

### US Sector Analysis Response:
```
🇺🇸 US Market Sector Analysis

Market: United States
Benchmark: S&P 500 (SPY)
Market Regime: BULL MOMENTUM
Analysis Period: 90 days
Sectors Analyzed: 25

📊 Top 10 US Sector ETFs:

1. **XLK**: Technology Select Sector SPDR...
   Conviction: 1.45 | Weight: 2.8% | Risk Adj: 0.985
   Recommendation: BUY

2. **QQQ**: Invesco QQQ Trust...
   Conviction: 1.42 | Weight: 2.7% | Risk Adj: 0.978
   Recommendation: BUY

3. **ARKK**: ARK Innovation ETF...
   Conviction: 1.38 | Weight: 2.6% | Risk Adj: 0.921
   Recommendation: BUY

🏆 Key Highlights:
• Strongest Momentum: XLK
• Best Value: XLV
• Highest Conviction: QQQ

💡 Investment Ideas:
• Consider overweighting sectors with conviction > 1.2
• Monitor risk adjustment for position sizing
• Focus on BUY recommendations for new positions

🔄 Updated: 9/1/2025, 12:45:30 PM
```

### China Sector Analysis Response:
```
🇨🇳 China Market Sector Analysis

Market: China
Benchmark: CSI 300 Index (000300.SS)
Market Regime: BULL MOMENTUM
Analysis Period: 90 days
Sectors Analyzed: 43

📊 Top 10 China Sector ETFs:

1. **159892.SZ**: 华夏恒生香港上市生物科技ETF...
   Conviction: 1.33 | Weight: 2.7% | Risk Adj: 0.950
   Recommendation: BUY

2. **513060.SS**: 博时恒生医疗保健QDII-ETF...
   Conviction: 1.32 | Weight: 2.6% | Risk Adj: 0.960
   Recommendation: BUY

🏆 Key Highlights:
• Strongest Momentum: 159892.SZ
• Best Value: 513060.SS
• Highest Conviction: 513090.SS

💡 Investment Ideas:
• Focus on high-conviction healthcare and tech ETFs
• Consider Hong Kong exposure for diversification
• Monitor military/defense sectors for geopolitical plays

🔄 Updated: 9/1/2025, 12:45:30 PM
```

---

## 🎯 Key Features

### Comprehensive Analysis
- **Momentum scoring** vs market benchmarks
- **Mean reversion** opportunities identification
- **Risk adjustment** factors for position sizing
- **Conviction scores** for investment confidence
- **Sector recommendations** (BUY/HOLD/AVOID)

### Market Context
- **Market regime detection** (Bull/Bear/Sideways/High Volatility)
- **Benchmark comparison** (S&P 500 for US, CSI 300 for China)
- **Customizable timeframes** (30, 60, 90, 120 days)
- **Real-time data** from yfinance

### Investment Insights
- **Top performers** by conviction score
- **Risk-adjusted weights** for portfolio allocation
- **Sector rotation** opportunities
- **Value vs momentum** trade-offs

---

## 🔧 Technical Details

### US Market Coverage
**Sectors Analyzed**: ~25 sector ETFs
- Technology (XLK, QQQ, ARKK, SOXX, VGT, SMH)
- Healthcare (XLV, IBB, XBI, IHI)
- Financial (XLF, KRE, KIE, KBE)
- Energy (XLE, XLB, XME, UNG)
- Consumer (XLY, XLP, XRT, VCR)
- Infrastructure (XLI, XLU, XLRE, VNQ)

### China Market Coverage
**Sectors Analyzed**: ~43 sector ETFs
- Technology & Innovation (Hong Kong Tech, 5G, AI, Semiconductors)
- Healthcare & Biotech (Medical devices, Pharmaceuticals)
- Financial Services (Banks, Securities, Insurance)
- Energy & Materials (New energy, Batteries, Solar)
- Infrastructure & Defense (Military, Construction)
- Hong Kong & International (QDII funds)

### Analysis Parameters
- **Lookback Period**: 30-120 days (default: 90)
- **Benchmark Comparison**: Relative strength calculation
- **Risk Metrics**: Volatility-adjusted position sizing
- **Technical Indicators**: RSI, Moving averages, Volume analysis

---

## 💡 Usage Examples

### Portfolio Construction
```
Show me US sector analysis for building a growth portfolio
```

```
What China sectors should I focus on for defensive positioning?
```

### Market Timing
```
Run 30-day US sector analysis to identify short-term opportunities
```

```
Analyze China sectors over 120 days for long-term trends
```

### Sector Rotation
```
Compare US and China sector momentum for rotation strategy
```

```
What sectors are showing mean reversion opportunities?
```

### Risk Management
```
Show me sector ETFs with the best risk-adjusted returns
```

```
What's the current market regime and sector allocation strategy?
```

---

## 🎯 Investment Decision Support

### For US Market:
- **Bull Market**: Focus on momentum (XLK, QQQ)
- **Bear Market**: Defensive sectors (XLU, XLP)
- **Sideways Market**: Mean reversion plays
- **High Volatility**: Lower risk adjustment sectors

### For China Market:
- **Growth Focus**: Technology and healthcare ETFs
- **Value Focus**: Financial and infrastructure sectors
- **International Exposure**: Hong Kong QDII funds
- **Thematic Plays**: Military, new energy, AI

### Risk Considerations:
- **Risk Adjustment**: 0.8-1.2 range for position sizing
- **Conviction Threshold**: >1.0 for BUY recommendations
- **Diversification**: Spread across multiple sectors
- **Rebalancing**: Monitor for >5% weight deviations

---

## 🔄 Regular Usage Patterns

### Daily Market Check
```
Quick US and China sector update for today
```

### Weekly Review
```
Show me this week's top sector performers in US and China
```

### Monthly Rebalancing
```
Run comprehensive sector analysis for portfolio rebalancing
```

### Quarterly Strategy Review
```
Analyze 90-day sector trends for strategic allocation changes
```

---

## 📈 Integration with Portfolio Management

### Combine with Other MCP Tools:
```
1. "Show me China sector analysis"
2. "Create a growth portfolio with $25,000"  
3. "Set up grids for the top 3 China tech ETFs"
4. "Monitor my portfolio risk with new sector allocations"
```

### Workflow Example:
```
"Run China sector analysis, then create a tech-focused portfolio 
with the top 3 ETFs and set up grid trading for each"
```

---

## 🎉 Benefits

### Before:
- Manual sector analysis through web interface
- Static reports without real-time insights
- Separate tools for different markets
- Time-consuming research process

### After:
- **Natural language queries** for instant analysis
- **Real-time insights** with current market data
- **Unified interface** for both US and China markets
- **Actionable recommendations** with specific ETFs
- **Investment-ready insights** with conviction scores

### Time Savings:
- **Sector Research**: 30 minutes → 30 seconds
- **Market Analysis**: Multiple tabs → Single command
- **Decision Making**: Faster with clear recommendations
- **Portfolio Updates**: Immediate actionable insights

This completes your AI-powered sector analysis toolkit, enabling instant market insights through natural language commands in Cursor! 🚀📈

<function_calls>
<invoke name="todo_write">
<parameter name="merge">true
