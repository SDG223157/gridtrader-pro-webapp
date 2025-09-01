# GridTrader Pro MCP Trading Commands Guide

## 💰 Execute Trades Directly Through Cursor with Natural Language

This guide covers the new buy and sell transaction tools that allow you to execute trades directly through Cursor using natural language commands.

---

## 🚀 New Trading Tools

### 1. `buy_stock` - Execute Buy Transactions
**Description**: Purchase stocks or ETFs in your portfolios
**Natural Language**: "Buy 10 shares of AAPL in my growth portfolio"

### 2. `sell_stock` - Execute Sell Transactions  
**Description**: Sell stocks or ETFs from your portfolios
**Natural Language**: "Sell 20 shares of TSLA from my tech portfolio"

---

## 💬 Natural Language Buy Commands

### Basic Buy Commands
```
Buy 10 shares of AAPL in my growth portfolio
```

```
Purchase 50 shares of SPY in portfolio [portfolio-id]
```

```
Buy 100 shares of QQQ for my tech portfolio
```

```
Purchase 25 shares of Tesla in my aggressive portfolio
```

### Buy with Specific Price
```
Buy 15 shares of NVDA at $800 in my growth portfolio
```

```
Purchase 20 shares of Microsoft at $350 in my conservative portfolio
```

```
Buy 30 shares of AAPL at $175 with note "Dollar cost averaging"
```

### Buy Chinese ETFs
```
Buy 1000 shares of 513130.SS in my China portfolio
```

```
Purchase 500 shares of 159892.SZ in my healthcare portfolio
```

```
Buy 2000 shares of the top China tech ETF in my growth portfolio
```

### Dollar-Amount Purchases
```
Buy $5,000 worth of SPY in my retirement portfolio
```

```
Purchase $10,000 of QQQ in my tech portfolio at current price
```

```
Invest $2,500 in AAPL for my growth portfolio
```

---

## 💸 Natural Language Sell Commands

### Basic Sell Commands
```
Sell 10 shares of AAPL from my growth portfolio
```

```
Sell 25 shares of SPY from portfolio [portfolio-id]
```

```
Liquidate 50 shares of QQQ from my tech portfolio
```

```
Sell 15 shares of Tesla from my aggressive portfolio
```

### Sell with Specific Price
```
Sell 20 shares of NVDA at $850 from my growth portfolio
```

```
Sell 30 shares of Microsoft at $380 from my conservative portfolio
```

```
Liquidate 40 shares of AAPL at $180 with note "Taking profits"
```

### Partial Position Sales
```
Sell half my Tesla position from my tech portfolio
```

```
Liquidate 25% of my SPY holdings from my retirement portfolio
```

```
Sell 100 shares of my QQQ position from my growth portfolio
```

### Chinese ETF Sales
```
Sell 500 shares of 513130.SS from my China portfolio
```

```
Liquidate 1000 shares of 159892.SZ from my healthcare portfolio
```

```
Sell my entire position in the China tech ETF
```

---

## 📊 Expected Response Format

### Successful Buy Transaction:
```
✅ Buy Transaction Successful!

Trade Details:
• Symbol: AAPL
• Quantity: 10 shares
• Price: $175.50 per share
• Total Cost: $1,755.00
• Portfolio: growth-portfolio-123
• Transaction ID: txn-456789

💰 Portfolio Impact:
• Cash reduced by $1,755.00
• Added 10 shares of AAPL
• Position value: $1,755.00

📋 Next Steps:
• Check updated portfolio: "Show me portfolio details"
• Monitor position: "What's the current price of AAPL?"
• Set up grid trading: "Create a grid for AAPL"

🎉 Trade executed successfully!
```

### Successful Sell Transaction:
```
✅ Sell Transaction Successful!

Trade Details:
• Symbol: TSLA
• Quantity: 20 shares
• Price: $245.75 per share
• Total Proceeds: $4,915.00
• Portfolio: tech-portfolio-789
• Transaction ID: txn-987654

💰 Portfolio Impact:
• Cash increased by $4,915.00
• Reduced 20 shares of TSLA
• Realized P&L will be calculated

📋 Next Steps:
• Check updated portfolio: "Show me portfolio details"
• Review cash balance: "Show me my cash balances"
• Monitor remaining position: "What holdings do I have?"

🎉 Trade executed successfully!
```

---

## 🔧 Advanced Trading Commands

### Research-to-Trade Workflow
```
Show me US sector analysis, then buy the top tech ETF in my portfolio
```

```
What's AAPL's current price? Buy 15 shares in my growth portfolio
```

```
Run China sector analysis and buy the top healthcare ETF
```

### Portfolio Rebalancing
```
Sell my overweight tech positions and buy defensive sectors
```

```
Liquidate 50% of my growth stocks and buy dividend ETFs
```

```
Rebalance my portfolio by selling winners and buying dips
```

### Systematic Trading
```
Buy 10 shares of each top 5 US sector ETFs in my diversified portfolio
```

```
Sell all my China positions and reinvest in US tech
```

```
Execute dollar-cost averaging: buy $1000 SPY monthly
```

---

## 🎯 Smart Trading Features

### Automatic Price Discovery
- **No price specified**: Uses current market price automatically
- **Price validation**: Confirms reasonable price ranges
- **Market hours**: Handles after-hours pricing appropriately

### Portfolio Integration
- **Cash validation**: Checks available cash before buy orders
- **Position validation**: Verifies holdings before sell orders
- **Portfolio updates**: Automatically updates portfolio values
- **Transaction history**: Creates complete audit trail

### Error Handling
- **Insufficient funds**: Clear error messages with cash balance info
- **Invalid symbols**: Symbol validation with search suggestions
- **Missing portfolios**: Portfolio verification with list of available portfolios
- **Insufficient shares**: Position size validation for sell orders

---

## 💡 Best Practices for Trading Commands

### Be Specific
❌ **Vague**: "Buy some Apple"
✅ **Specific**: "Buy 10 shares of AAPL in my growth portfolio"

❌ **Unclear**: "Sell Tesla"
✅ **Clear**: "Sell 20 shares of TSLA from my tech portfolio"

### Include Context
✅ **"Buy 15 shares of NVDA at current price in my growth portfolio"**
✅ **"Sell 25 shares of SPY at $455 from my retirement portfolio"**
✅ **"Purchase 100 shares of QQQ with note 'Monthly investment'"**

### Portfolio Management
✅ **"Show me my portfolios first, then buy AAPL in the growth one"**
✅ **"Check my cash balance, then buy $5000 worth of SPY"**
✅ **"What's my Tesla position? Sell half of it"**

---

## 🚨 Risk Management Commands

### Position Sizing
```
Buy a 2% position in AAPL for my $50,000 portfolio
```

```
Purchase $2,500 worth of QQQ to maintain 5% allocation
```

```
Buy enough SPY to reach 10% portfolio weight
```

### Stop-Loss and Take-Profit
```
Sell my TSLA position if it hits $200 (stop-loss)
```

```
Take profits on NVDA - sell 50% at current price
```

```
Liquidate my overperforming tech positions
```

### Diversification
```
Sell concentrated tech positions and buy sector ETFs
```

```
Reduce single-stock risk by selling individual stocks and buying ETFs
```

```
Rebalance by selling overweight positions
```

---

## 🔄 Integration with Other Tools

### Research → Trade Workflow
```
1. "Show me US sector analysis"
2. "Buy 10 shares of the top momentum ETF"
3. "Set up grid trading for systematic entries"
4. "Monitor the position performance"
```

### Update → Analyze → Trade
```
1. "Update China ETFs with latest data"
2. "Show me China sector analysis"
3. "Buy the top 3 China healthcare ETFs"
4. "Check my portfolio allocation"
```

### Monitor → Adjust → Execute
```
1. "Show me my trading alerts"
2. "Check portfolio risk levels"
3. "Sell overweight positions"
4. "Buy underweight sectors"
```

---

## 🎯 Transaction Command Patterns

### By Portfolio Strategy
**Growth Portfolio:**
```
"Buy growth stocks like NVDA, TSLA, ARKK in my growth portfolio"
```

**Conservative Portfolio:**
```
"Buy dividend ETFs like VYM, SCHD in my conservative portfolio"
```

**Tech Portfolio:**
```
"Buy tech leaders AAPL, MSFT, GOOGL in my tech portfolio"
```

### By Market
**US Stocks:**
```
"Buy 10 shares of AAPL, 20 shares of SPY, 15 shares of QQQ"
```

**China ETFs:**
```
"Buy 1000 shares each of 513130.SS and 159892.SZ"
```

**International:**
```
"Buy international exposure with VEA and VWO ETFs"
```

---

## ⚠️ Important Notes

### Portfolio IDs
- **Get Portfolio ID**: Use "Show me my portfolios" to get exact portfolio IDs
- **Portfolio Names**: You can reference by name if unique (e.g., "growth portfolio")
- **Case Sensitivity**: Portfolio names are case-insensitive

### Symbol Formats
- **US Stocks**: AAPL, MSFT, GOOGL, TSLA
- **US ETFs**: SPY, QQQ, VTI, VEA
- **China ETFs**: 513130.SS, 159892.SZ (include exchange suffix)
- **Crypto**: BTC-USD, ETH-USD

### Price Handling
- **Market Price**: Leave price blank for current market price
- **Specific Price**: Include "at $150.00" for limit orders
- **After Hours**: System handles extended hours pricing

### Transaction Validation
- **Cash Check**: System verifies sufficient cash for buys
- **Holdings Check**: System verifies sufficient shares for sells
- **Symbol Validation**: System validates symbol exists
- **Portfolio Access**: System verifies portfolio ownership

---

## 🎉 Benefits of MCP Trading

### Speed & Efficiency
- **Instant Execution**: Trade directly from research
- **No Context Switching**: Stay in Cursor for everything
- **Natural Language**: No need to remember API syntax
- **Integrated Workflow**: Research → Decide → Execute → Monitor

### Risk Management
- **Automatic Validation**: Cash and position checks
- **Transaction History**: Complete audit trail
- **Portfolio Integration**: Real-time portfolio updates
- **Error Prevention**: Clear validation and error messages

### User Experience
- **Conversational**: Use natural language for trades
- **Contextual**: Reference previous research and analysis
- **Flexible**: Support for various order types and sizes
- **Integrated**: Works with all other MCP tools

---

## 🚀 Ready to Trade!

You can now execute trades directly through Cursor with commands like:

```
"Buy 10 shares of AAPL in my growth portfolio"
"Sell 20 shares of TSLA from my tech portfolio"
"Purchase the top China healthcare ETF"
"Liquidate my overweight tech positions"
```

**Complete AI-powered trading workflow**: Research → Analyze → Execute → Monitor - all through natural language in Cursor! 🎯📈
