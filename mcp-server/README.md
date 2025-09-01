# GridTrader Pro MCP Server

A Model Context Protocol (MCP) server for GridTrader Pro, enabling AI assistants like Cursor to interact with your trading and portfolio management system.

## 🚀 Features

- **Portfolio Management**: Create, view, and manage investment portfolios
- **Grid Trading**: Set up and monitor grid trading strategies
- **Market Data**: Get real-time and historical market data
- **Performance Analytics**: Analyze portfolio and grid performance
- **Symbol Search**: Find and validate trading symbols
- **Trading Alerts**: Monitor alerts and notifications

## 📦 Installation

### Global Installation (Recommended)

```bash
# Install globally via npm
npm install -g gridtrader-pro-mcp

# Or install from source
git clone https://github.com/SDG223157/gridtrader-pro-webapp.git
cd gridtrader-pro-webapp/mcp-server
npm install
npm run build
npm install -g .
```

### Development Installation

```bash
cd mcp-server
npm install
npm run build
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# GridTrader Pro API Configuration
GRIDTRADER_API_URL=http://localhost:3000
GRIDTRADER_ACCESS_TOKEN=your_access_token_here
```

### Cursor MCP Configuration

Add this to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "gridtrader-pro": {
      "command": "gridtrader-pro-mcp",
      "env": {
        "GRIDTRADER_API_URL": "http://localhost:3000",
        "GRIDTRADER_ACCESS_TOKEN": "your_access_token_here"
      }
    }
  }
}
```

## 🛠️ Available Tools

### Portfolio Management
- `get_portfolio_list` - Get all portfolios with performance metrics
- `get_portfolio_details` - Get detailed portfolio information
- `create_portfolio` - Create a new investment portfolio
- `calculate_portfolio_metrics` - Calculate performance metrics

### Grid Trading
- `get_grid_list` - Get all grid trading strategies
- `create_grid` - Create a new grid trading strategy
- `analyze_grid_performance` - Analyze grid performance

### Market Data
- `get_market_data` - Get current/historical market data
- `search_symbols` - Search for trading symbols
- `validate_symbol` - Validate if a symbol is supported

### Analytics & Monitoring
- `get_dashboard_summary` - Get portfolio and market overview
- `get_trading_alerts` - Get recent alerts and notifications

## 💡 Usage Examples

### In Cursor Chat

```
# Get portfolio overview
"Show me all my portfolios"

# Create a new portfolio
"Create a balanced portfolio called 'Growth Fund' with $10,000 initial capital"

# Set up a grid trading strategy
"Create a grid for AAPL in my Growth Fund portfolio with price range $150-200 and $5000 investment"

# Get market data
"What's the current price of AAPL?"

# Search for symbols
"Find symbols for Tesla"

# Get dashboard summary
"Show me my dashboard summary with market data"
```

### API Integration

The MCP server communicates with your GridTrader Pro application running on `http://localhost:3000` by default.

## 🔧 Development

### Build

```bash
npm run build
```

### Development Mode

```bash
npm run dev
```

### Testing

```bash
npm test
```

## 📊 API Endpoints Used

The MCP server expects these endpoints from your GridTrader Pro application:

- `GET /api/portfolios` - List portfolios
- `POST /api/portfolios` - Create portfolio
- `GET /api/portfolios/{id}` - Get portfolio details
- `GET /api/grids` - List grid strategies
- `POST /api/grids` - Create grid strategy
- `GET /api/grids/{id}` - Get grid details
- `GET /api/market/{symbol}` - Get market data
- `GET /api/search/symbols` - Search symbols
- `GET /api/alerts` - Get trading alerts

## 🔐 Authentication

The MCP server uses Bearer token authentication. Set your `GRIDTRADER_ACCESS_TOKEN` environment variable to authenticate with your GridTrader Pro application.

## 🐛 Troubleshooting

### Common Issues

1. **"Command not found: gridtrader-pro-mcp"**
   ```bash
   # Reinstall globally
   npm install -g gridtrader-pro-mcp
   ```

2. **"Failed to connect to API"**
   - Check if GridTrader Pro is running on the configured URL
   - Verify your access token is correct
   - Check network connectivity

3. **"Unauthorized" errors**
   - Verify your `GRIDTRADER_ACCESS_TOKEN` is set correctly
   - Check if the token has the required permissions

### Debug Mode

Set `DEBUG=1` environment variable for verbose logging:

```bash
DEBUG=1 gridtrader-pro-mcp
```

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Available in the main GridTrader Pro repository
- **Website**: http://localhost:3000 (your GridTrader Pro instance)

---

**Ready to supercharge your trading with AI! 🚀**
