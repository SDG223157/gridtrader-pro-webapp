# GridTrader Pro - Systematic Investment Management Platform

A comprehensive investment management platform featuring grid trading algorithms, portfolio rebalancing, and real-time market data integration. Built with Python FastAPI and HTML templates for deployment with Docker.

## 🚀 Features

- **Grid Trading Algorithms** with dynamic spacing and risk management
- **Portfolio Management** with automated rebalancing and performance tracking
- **Real-time Market Data** via yfinance integration with technical indicators
- **Google OAuth Authentication** with JWT tokens for secure access
- **Background Data Processing** with Celery for automated updates
- **Responsive Web Interface** with modern HTML/CSS/JavaScript
- **Production-Ready Docker Deployment** with single container architecture
- **🤖 AI Integration** with MCP (Model Context Protocol) for Cursor IDE
- **Natural Language Trading** - Control your portfolios with plain English commands

## 📋 Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: MySQL 8.0+ with SQLAlchemy ORM
- **Authentication**: Google OAuth 2.0 + JWT
- **Data Source**: yfinance (Yahoo Finance) - FREE
- **Frontend**: HTML5 + TailwindCSS + Alpine.js
- **Background Tasks**: Celery + Redis
- **Deployment**: Docker + Nginx + Supervisor
- **Charts**: Chart.js + Plotly.js

## 🏗️ Architecture

```
GridTrader Pro WebApp/
├── main.py                 # FastAPI application
├── database.py             # Database models and connection
├── auth.py                 # Authentication system
├── data_provider.py        # yfinance integration
├── tasks.py                # Celery background tasks
├── app/
│   └── algorithms/
│       └── grid_trading.py # Trading algorithms
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   ├── dashboard.html     # Main dashboard
│   ├── portfolios.html    # Portfolio management
│   ├── grids.html         # Grid trading interface
│   └── partials/          # Template components
├── static/                # Static assets (CSS, JS, images)
├── docker/                # Docker configuration
│   ├── start.sh           # Startup script
│   ├── supervisord.conf   # Process management
│   └── nginx.conf         # Web server config
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration
└── README.md
```

## 🛠️ Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd gridtrader-pro-webapp
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your configuration:

```bash
# Database
DB_HOST=your-mysql-host
DB_PASSWORD=your-mysql-password
DB_NAME=gridtrader_db

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Security
SECRET_KEY=your-super-secret-key-32-chars-minimum

# Redis
REDIS_HOST=your-redis-host
REDIS_PASSWORD=your-redis-password
```

### 3. Build and Run

```bash
# Build Docker image
docker build -t gridtrader-pro .

# Run with environment file
docker run -d \
  --name gridtrader-pro \
  --env-file .env \
  -p 3000:3000 \
  gridtrader-pro
```

### 4. Access Application

- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:3000/docs
- **Health Check**: http://localhost:3000/health

## 🔧 Development Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (required for background tasks)
redis-server

# Run database migrations
python -c "from database import create_tables; create_tables()"

# Start the application
python main.py

# In another terminal, start Celery worker
celery -A tasks worker --loglevel=info

# In another terminal, start Celery beat (scheduler)
celery -A tasks beat --loglevel=info
```

### Docker Compose (Recommended for Development)

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
    depends_on:
      - mysql
      - redis
    
  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_DATABASE=gridtrader_db
      - MYSQL_ROOT_PASSWORD=rootpassword
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
```

## 📊 Key Features

### Grid Trading
- **Dynamic Grid Spacing**: Automatically adjusts based on market volatility
- **Risk Management**: Built-in stop-loss and position sizing
- **Backtesting**: Historical performance analysis
- **Multiple Strategies**: Standard, Dynamic, and Martingale grids

### Portfolio Management
- **Real-time Tracking**: Live portfolio values and P&L
- **Auto-rebalancing**: Maintains target allocations
- **Performance Analytics**: Returns, Sharpe ratio, drawdown analysis
- **Multi-strategy Support**: Grid trading, core-satellite, balanced growth

### Market Data
- **Real-time Prices**: Live data from Yahoo Finance
- **Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Historical Data**: Complete price history with OHLCV
- **Symbol Search**: Find and validate trading symbols

### Background Processing
- **Market Data Updates**: Every 5 minutes during market hours
- **Portfolio Revaluation**: Every 10 minutes
- **Grid Order Processing**: Every 3 minutes
- **Alert Generation**: Price movements and portfolio changes
- **Data Cleanup**: Automatic cleanup of old data

## 🔐 Security Features

- **Google OAuth 2.0**: Secure authentication with JWT tokens
- **HTTPS/SSL**: Required for production deployment
- **CORS Protection**: Configurable allowed origins
- **Rate Limiting**: API endpoint protection
- **Secure Sessions**: HTTP-only cookies with proper expiration
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries with SQLAlchemy

## 📈 API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /api/auth/login` - Email/password login
- `GET /api/auth/google` - Google OAuth login
- `POST /logout` - Logout

### Portfolios
- `GET /portfolios` - List portfolios
- `POST /api/portfolios` - Create portfolio
- `GET /api/portfolios/{id}` - Get portfolio details
- `PUT /api/portfolios/{id}` - Update portfolio
- `DELETE /api/portfolios/{id}` - Delete portfolio

### Grid Trading
- `GET /grids` - List grids
- `POST /api/grids` - Create grid
- `GET /api/grids/{id}` - Get grid details
- `PUT /api/grids/{id}` - Update grid
- `DELETE /api/grids/{id}` - Delete grid

### Market Data
- `GET /api/market/{symbol}` - Get symbol data
- `GET /api/search/symbols?q={query}` - Search symbols

## 🚀 Deployment

### Coolify Deployment (Recommended)

1. **Create new service** in Coolify
2. **Set repository**: Point to your Git repository
3. **Configure build**: Use the provided `Dockerfile`
4. **Set environment variables**: Copy from `.env.example`
5. **Deploy**: Coolify handles the rest automatically

### Manual Docker Deployment

```bash
# Build and tag image
docker build -t gridtrader-pro:latest .

# Run with proper environment
docker run -d \
  --name gridtrader-pro \
  --restart unless-stopped \
  --env-file .env \
  -p 3000:3000 \
  gridtrader-pro:latest
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_HOST` | MySQL host | ✅ |
| `DB_PASSWORD` | MySQL password | ✅ |
| `DB_NAME` | Database name | ✅ |
| `GOOGLE_CLIENT_ID` | OAuth client ID | ✅ |
| `GOOGLE_CLIENT_SECRET` | OAuth secret | ✅ |
| `SECRET_KEY` | JWT secret key | ✅ |
| `REDIS_HOST` | Redis host | ✅ |
| `FRONTEND_URL` | Application URL | ✅ |
| `LOG_LEVEL` | Logging level | ❌ |

## 📊 Monitoring

### Health Checks
- **Application**: `GET /health`
- **Database**: Connection test in health endpoint
- **Redis**: Connection test in health endpoint
- **Docker**: Built-in healthcheck with curl

### Logging
- **Application Logs**: `/app/logs/app.log`
- **Celery Worker**: `/app/logs/celery.log`
- **Celery Beat**: `/app/logs/celery-beat.log`
- **Nginx Access**: `/var/log/nginx/access.log`
- **Nginx Error**: `/var/log/nginx/error.log`

### Metrics
- Portfolio performance tracking
- Grid trading success rates
- API response times
- Background task execution times

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤖 AI Integration (MCP)

GridTrader Pro supports AI-powered portfolio management through Cursor IDE:

### Quick Setup
```bash
# Install MCP server globally
./install-mcp-global.sh

# Or manually:
npm install -g gridtrader-pro-mcp
```

### Configuration
1. Create API token at: `https://your-domain.com/tokens`
2. Add MCP config to Cursor settings
3. Restart Cursor
4. Use natural language: "Show me my portfolios"

**📖 Complete Guide**: See [GLOBAL_MCP_SETUP_GUIDE.md](./GLOBAL_MCP_SETUP_GUIDE.md)

### Example AI Commands
- "Show me my cash balances"
- "Create a growth portfolio with $25,000"
- "Set up a grid for AAPL between $150-200"
- "What's my portfolio performance?"
- "Update my cash balance to reflect interest earned"

## 🆘 Support

For deployment issues:

1. Check the **logs** in `/app/logs/`
2. Verify **environment variables** are set correctly
3. Test the **health endpoint**: `/health`
4. Ensure **database and Redis connectivity**
5. Review **Docker container logs**

For MCP integration issues:
1. Check **API token validity**: `/tokens` page
2. Verify **MCP server installation**: `gridtrader-pro-mcp --version`
3. Test **API connectivity**: `curl -H "Authorization: Bearer TOKEN" https://your-domain.com/api/portfolios`
4. Review **Cursor MCP logs**: Cursor Developer Tools

## 🎯 Roadmap

- [ ] WebSocket real-time updates
- [ ] Advanced backtesting interface
- [ ] More trading strategies
- [ ] Mobile-responsive improvements
- [ ] API rate limiting
- [ ] Advanced charting features
- [ ] Export/import functionality
- [ ] Multi-language support

---

**Ready for production deployment with Docker! 🚀**