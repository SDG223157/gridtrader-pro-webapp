# 🏠 GridTrader Pro - Cursor MCP Setup Guide

## 📋 Quick Setup (Copy & Paste)

### Step 1: Install MCP Server
Run this command in your terminal:

```bash
# Method 1: One-line install script (recommended)
curl -fsSL https://raw.githubusercontent.com/SDG223157/gridtrader-pro-webapp/main/install-mcp.sh | bash

# Method 2: Manual installation
git clone https://github.com/SDG223157/gridtrader-pro-webapp.git
cd gridtrader-pro-webapp/mcp-server
npm install
npm run build
sudo npm install -g .
```

### Step 2: Access GridTrader Pro Application
Your GridTrader Pro application is running at:
**https://gridsai.app**

### Step 3: Get Your Access Token
1. Visit: **https://gridsai.app/tokens**
2. Login with your GridTrader Pro account
3. Create a new API token for MCP integration

### Step 4: Configure Cursor
Add this configuration to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "gridtrader-pro": {
      "command": "gridtrader-pro-mcp",
      "env": {
        "GRIDTRADER_API_URL": "https://gridsai.app",
        "GRIDTRADER_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

**🔑 Important:** Replace `your_access_token_here` with your actual access token!

### Step 5: Restart Cursor
Restart Cursor to load the MCP server.

---

## 🎯 Available Commands

Once configured, you can use these commands in Cursor:

### Portfolio Management
- **"Show me all my portfolios"** - Get portfolio overview
- **"Create a balanced portfolio called 'Tech Fund' with $25,000"** - Create new portfolio
- **"Get details for portfolio [id]"** - View specific portfolio
- **"Calculate metrics for my Growth portfolio"** - Get performance metrics

### Grid Trading
- **"Show me all my grid strategies"** - List all grids
- **"Create a grid for AAPL with price range $150-200 and $5000 investment"** - Set up grid
- **"Analyze performance of grid [id]"** - Get grid analysis
- **"Show grids for TSLA"** - Filter grids by symbol

### Market Data
- **"What's the current price of AAPL?"** - Get real-time price
- **"Get historical data for SPY over 1 month"** - Historical data
- **"Search for Tesla symbols"** - Find trading symbols
- **"Validate symbol MSFT"** - Check if symbol is supported

### Analytics & Monitoring
- **"Show my dashboard summary"** - Portfolio and market overview
- **"Get my recent trading alerts"** - View notifications
- **"Show market data for popular stocks"** - Market overview

---

## 🔧 Configuration Locations

### macOS
- **Via UI**: Cursor Settings → Extensions → MCP Servers
- **File**: `~/.cursor/mcp_servers.json`

### Windows  
- **Via UI**: Cursor Settings → Extensions → MCP Servers
- **File**: `%APPDATA%\Cursor\User\mcp_servers.json`

### Linux
- **Via UI**: Cursor Settings → Extensions → MCP Servers  
- **File**: `~/.config/Cursor/User/mcp_servers.json`

---

## 🔐 Authentication Setup

### Option 1: Simple Token (Development)
For development, you can use a simple token approach:

1. Add to your `main.py`:
```python
# Simple token validation
SIMPLE_TOKEN = "gridtrader_dev_token_123"

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        token = auth_header.replace("Bearer ", "")
        if token != SIMPLE_TOKEN:
            return JSONResponse({"error": "Invalid token"}, status_code=401)
    
    response = await call_next(request)
    return response
```

2. Use this token in your MCP configuration:
```json
"GRIDTRADER_ACCESS_TOKEN": "gridtrader_dev_token_123"
```

### Option 2: JWT Token (Production)
For production, implement proper JWT token authentication using your existing auth system.

---

## 🛠️ API Endpoints Integration

Make sure these endpoints are available in your GridTrader Pro application:

### Required Endpoints
```python
# Portfolio endpoints
@app.get("/api/portfolios")
@app.post("/api/portfolios") 
@app.get("/api/portfolios/{id}")

# Grid endpoints
@app.get("/api/grids")
@app.post("/api/grids")
@app.get("/api/grids/{id}")

# Market data endpoints
@app.get("/api/market/{symbol}")
@app.get("/api/search/symbols")

# Optional endpoints
@app.get("/api/alerts")
@app.get("/api/portfolios/{id}/metrics")
```

### Example Implementation
Add to your `main.py`:

```python
@app.get("/api/portfolios")
async def api_get_portfolios(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
    return {"portfolios": [p.__dict__ for p in portfolios]}

@app.get("/api/grids")  
async def api_get_grids(user: User = Depends(require_auth), db: Session = Depends(get_db)):
    grids = db.query(Grid).join(Portfolio).filter(Portfolio.user_id == user.id).all()
    return {"grids": [g.__dict__ for g in grids]}
```

---

## ❓ Troubleshooting

### "Command not found: gridtrader-pro-mcp"
```bash
# Reinstall globally
npm install -g gridtrader-pro-mcp

# Check installation
which gridtrader-pro-mcp
```

### "Failed to connect to API"
1. Make sure GridTrader Pro is running on http://localhost:3000
2. Check if the port is correct
3. Verify firewall settings

### "Unauthorized" error
1. Check your access token is correct
2. Implement authentication middleware
3. Verify token permissions

### "API endpoint not found"
1. Make sure you've added the required API endpoints
2. Check the endpoint paths match exactly
3. Verify authentication is working

---

## 🔧 Development Mode

For development and testing:

```bash
# Run MCP server in development mode
cd mcp-server
npm run dev

# Test MCP server directly
echo '{"method": "tools/list"}' | node dist/index.js
```

---

## 🆘 Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Available in the repository
- **Local Development**: http://localhost:3000

---

## 🎉 Example Usage Session

Once everything is set up, try this in Cursor:

```
User: "Show me my portfolio overview"
AI: Uses get_portfolio_list tool to show all portfolios

User: "Create a new growth portfolio with $10,000"  
AI: Uses create_portfolio tool to create the portfolio

User: "Set up a grid for AAPL in my new portfolio"
AI: Uses create_grid tool to set up grid trading

User: "What's the current price of AAPL?"
AI: Uses get_market_data tool to get real-time price

User: "Show my dashboard summary"
AI: Uses get_dashboard_summary to show overview
```

**Happy trading with AI! 🚀**
