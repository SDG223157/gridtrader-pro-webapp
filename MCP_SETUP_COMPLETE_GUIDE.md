# 🚀 GridTrader Pro MCP Integration - Complete Setup Guide

This guide will help you set up the GridTrader Pro MCP server to work with Cursor, enabling AI-powered trading and portfolio management.

## 📋 What You'll Get

After setup, you can use Cursor to:
- **Manage Portfolios**: "Show me all my portfolios", "Create a new tech portfolio with $10,000"
- **Grid Trading**: "Set up a grid for AAPL with price range $150-200", "Show my grid performance"
- **Market Data**: "What's the current price of TSLA?", "Search for Apple symbols"
- **Analytics**: "Show my dashboard summary", "Calculate metrics for my Growth portfolio"

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    GridTrader Pro MCP Setup                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                  Cursor AI                              │ │
│  │              (Your AI Assistant)                        │ │
│  └─────────────────┬───────────────────────────────────────┘ │
│                    │ MCP Protocol                            │
│  ┌─────────────────▼───────────────────────────────────────┐ │
│  │              MCP Server                                 │ │
│  │           (gridtrader-pro-mcp)                         │ │
│  │                                                         │ │
│  │  • Portfolio Management Tools                           │ │
│  │  • Grid Trading Tools                                   │ │
│  │  • Market Data Tools                                    │ │
│  │  • Analytics Tools                                      │ │
│  └─────────────────┬───────────────────────────────────────┘ │
│                    │ HTTP API Calls                          │
│  ┌─────────────────▼───────────────────────────────────────┐ │
│  │         GridTrader Pro WebApp                           │ │
│  │            (FastAPI Backend)                            │ │
│  │                                                         │ │
│  │  • /api/portfolios                                      │ │
│  │  • /api/grids                                           │ │
│  │  • /api/market/{symbol}                                 │ │
│  │  • Authentication & Database                            │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Step-by-Step Setup

### Step 1: Verify GridTrader Pro is Running

First, make sure your GridTrader Pro application is running:

```bash
cd /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp
python main.py
```

You should see:
```
🌐 Starting server on 0.0.0.0:3000
INFO:     Uvicorn running on http://0.0.0.0:3000
```

Test it: http://localhost:3000/health

### Step 2: Build the MCP Server

The MCP server is already built, but you can rebuild if needed:

```bash
cd /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server
npm run build
```

### Step 3: Test MCP Server Locally

Test the MCP server works:

```bash
cd /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | node dist/index.js
```

You should see a list of available tools.

### Step 4: Configure Cursor

#### Option A: Using Cursor UI (Recommended)

1. Open **Cursor Settings** (Cmd/Ctrl + ,)
2. Go to **Extensions** → **MCP Servers**
3. Click **"Add Server"**
4. Fill in:
   - **Name**: `gridtrader-pro`
   - **Command**: `node`
   - **Arguments**: `/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/index.js`
   - **Environment Variables**:
     - `GRIDTRADER_API_URL`: `http://localhost:3000`
     - `GRIDTRADER_ACCESS_TOKEN`: `gridtrader_dev_token_123`

#### Option B: Manual Configuration File

1. Find your Cursor MCP config file:
   - **macOS**: `~/.cursor/mcp_servers.json`
   - **Windows**: `%APPDATA%\Cursor\User\mcp_servers.json`
   - **Linux**: `~/.config/Cursor/User/mcp_servers.json`

2. Add this configuration:
```json
{
  "mcpServers": {
    "gridtrader-pro": {
      "command": "node",
      "args": ["/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/index.js"],
      "env": {
        "GRIDTRADER_API_URL": "http://localhost:3000",
        "GRIDTRADER_ACCESS_TOKEN": "gridtrader_dev_token_123"
      }
    }
  }
}
```

### Step 5: Restart Cursor

Close and reopen Cursor completely to load the MCP server.

### Step 6: Test the Integration

Open Cursor and try these commands in a chat:

1. **"Show me all my portfolios"**
2. **"What's the current price of AAPL?"**
3. **"Create a new balanced portfolio called 'Tech Fund' with $15,000 initial capital"**

## 🎯 Available Tools & Commands

### Portfolio Management
- `get_portfolio_list` - **"Show me all my portfolios"**
- `get_portfolio_details` - **"Get details for portfolio [id]"**
- `create_portfolio` - **"Create a growth portfolio with $20,000"**
- `calculate_portfolio_metrics` - **"Calculate metrics for my Tech portfolio"**

### Grid Trading
- `get_grid_list` - **"Show me all my grid strategies"**
- `create_grid` - **"Create a grid for TSLA with range $200-300 and $8000 investment"**
- `analyze_grid_performance` - **"Analyze performance of grid [id]"**

### Market Data
- `get_market_data` - **"What's the current price of MSFT?"**
- `search_symbols` - **"Find symbols for Microsoft"**
- `validate_symbol` - **"Is NVDA a valid symbol?"**

### Analytics
- `get_dashboard_summary` - **"Show my dashboard summary"**
- `get_trading_alerts` - **"Show my recent trading alerts"**

## 🔐 Authentication Details

The system uses a simple development token: `gridtrader_dev_token_123`

This token is handled by the middleware in `main.py`:
- Creates a mock user for development: `dev_user_123`
- Allows full access to all MCP tools
- Perfect for testing and development

For production, you can:
1. Replace with JWT tokens
2. Implement proper user authentication
3. Add role-based access control

## 🐛 Troubleshooting

### "MCP server not found" in Cursor
1. Check the file path is correct: `/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/index.js`
2. Verify the file exists: `ls -la /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/`
3. Test manually: `node /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/index.js`

### "Failed to connect to API" errors
1. Ensure GridTrader Pro is running: http://localhost:3000/health
2. Check the API URL in config: `GRIDTRADER_API_URL=http://localhost:3000`
3. Verify no firewall blocking localhost:3000

### "Unauthorized" errors
1. Check the token is set: `GRIDTRADER_ACCESS_TOKEN=gridtrader_dev_token_123`
2. Verify the middleware is working by testing: `curl -H "Authorization: Bearer gridtrader_dev_token_123" http://localhost:3000/api/portfolios`

### "No portfolios found" messages
This is normal if you haven't created any portfolios yet. Try:
**"Create a new balanced portfolio called 'My First Portfolio' with $10000"**

### MCP Tools not appearing in Cursor
1. Restart Cursor completely
2. Check Cursor logs for MCP errors
3. Verify the MCP server config syntax is correct

## 🧪 Testing Commands

Try these commands in Cursor to test everything works:

### Basic Tests
```
"Show me all my portfolios"
"What's the current price of AAPL?"
"Show my dashboard summary"
```

### Create Portfolio
```
"Create a new tech portfolio called 'Growth Fund' with $25,000 initial capital"
```

### Grid Trading
```
"Show me all my grid strategies"
"Create a grid for AAPL in my Growth Fund portfolio with price range $150-200 and $5000 investment"
```

### Market Data
```
"Search for Tesla symbols"
"Get historical data for SPY over 1 month"
"Validate symbol MSFT"
```

## 📊 Expected Responses

When working correctly, you should see responses like:

```
📊 Portfolio Overview

Found 2 portfolios:

1. Growth Fund
   ID: portfolio_123
   Strategy: growth
   Value: $25,450
   Return: 📈 2.18%
   Created: 2024/01/15

2. Tech Portfolio  
   ID: portfolio_456
   Strategy: balanced
   Value: $18,900
   Return: 📉 -0.55%
   Created: 2024/01/10
```

## 🎉 Success Indicators

You know everything is working when:

1. ✅ **GridTrader Pro** responds at http://localhost:3000/health
2. ✅ **MCP Server** builds without errors
3. ✅ **Cursor** shows MCP tools in settings
4. ✅ **API calls** work: `curl -H "Authorization: Bearer gridtrader_dev_token_123" http://localhost:3000/api/portfolios`
5. ✅ **Chat commands** return portfolio/market data

## 🚀 Next Steps

Once everything is working:

1. **Create some portfolios** to see real data
2. **Set up grid trading strategies** for your favorite stocks
3. **Explore advanced commands** like performance metrics
4. **Customize the MCP server** for your specific needs

## 📞 Support

If you run into issues:

1. **Check the logs**: Both GridTrader Pro and Cursor console
2. **Test components individually**: API → MCP Server → Cursor
3. **Verify paths and tokens**: Double-check all file paths and authentication
4. **Review the setup**: Follow this guide step-by-step

---

**🎊 Congratulations! You now have AI-powered trading and portfolio management in Cursor!**

Try saying: **"Show me my dashboard summary and create a new portfolio for tech stocks with $20,000"**
