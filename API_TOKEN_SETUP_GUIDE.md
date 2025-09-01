# 🔐 GridTrader Pro API Token Setup Guide

Complete guide for setting up API tokens to connect GridTrader Pro with Cursor via MCP server.

## 🎯 What This Adds

Your GridTrader Pro now has a **complete API token management system** similar to prombank_backup:

- **🔑 Token Creation**: Generate secure API tokens from the web interface
- **📊 Token Management**: View, edit, and delete tokens
- **⚙️ MCP Configuration**: Automatic generation of Cursor MCP settings
- **🔒 Security**: Token expiration, permissions, and usage tracking
- **🚀 Easy Setup**: One-click copy-paste configuration for Cursor

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                GridTrader Pro Token System                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Frontend UI (/tokens)                    │ │
│  │                                                         │ │
│  │  • Create API tokens                                    │ │
│  │  • View existing tokens                                 │ │
│  │  • Get MCP configuration                                │ │
│  │  • Copy-paste setup                                     │ │
│  └─────────────────┬───────────────────────────────────────┘ │
│                    │ HTTP API                                │
│  ┌─────────────────▼───────────────────────────────────────┐ │
│  │              Backend API                                │ │
│  │                                                         │ │
│  │  • POST /api/tokens (create)                            │ │
│  │  • GET /api/tokens (list)                               │ │
│  │  • GET /api/tokens/{id}/mcp-config                      │ │
│  │  • PUT /api/tokens/{id} (update)                        │ │
│  │  • DELETE /api/tokens/{id}                              │ │
│  └─────────────────┬───────────────────────────────────────┘ │
│                    │ Database                                │
│  ┌─────────────────▼───────────────────────────────────────┐ │
│  │               api_tokens Table                          │ │
│  │                                                         │ │
│  │  • Secure token storage                                 │ │
│  │  • User association                                     │ │
│  │  • Permissions & expiration                             │ │
│  │  • Usage tracking                                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

                              │
                              ▼ Token Authentication
                              
┌─────────────────────────────────────────────────────────────┐
│                    MCP Server                               │
│                                                             │
│  • Uses API token for authentication                        │
│  • Connects to GridTrader Pro API                          │
│  • Provides trading tools to Cursor                        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Setup

### Step 1: Run Database Migration

```bash
cd /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp
python add_api_tokens_migration.py
```

### Step 2: Start GridTrader Pro

```bash
python main.py
```

### Step 3: Create Your First Token

1. **Visit**: https://gridsai.app/tokens
2. **Login** with your GridTrader Pro account
3. **Click "Create New Token"**
4. **Fill in details**:
   - Name: "Cursor MCP Token"
   - Description: "Token for Cursor AI integration"
   - Permissions: Read + Write
   - Expires: 90 days (or never)
5. **Click "Create Token"**

### Step 4: Copy MCP Configuration

After creating the token, you'll see:
- ✅ **Your secure API token** (save it!)
- 🛠️ **Installation command** (copy & run)
- ⚙️ **Complete MCP configuration** (copy to Cursor)

### Step 5: Configure Cursor

1. **Copy the MCP configuration** from the success modal
2. **Open Cursor Settings** (Cmd/Ctrl + ,)
3. **Go to Extensions → MCP Servers**
4. **Add the configuration**
5. **Restart Cursor**

### Step 6: Test Integration

In Cursor, try:
- **"Show me all my portfolios"**
- **"What's the current price of AAPL?"**
- **"Create a new tech portfolio with $10,000"**

## 📋 Features Added

### 🎨 Frontend Features

#### Token Management Page (`/tokens`)
- **Clean, modern UI** with TailwindCSS
- **Create new tokens** with form validation
- **View existing tokens** in a data table
- **Token status management** (active/inactive)
- **Delete tokens** with confirmation
- **MCP configuration modal** for existing tokens

#### Success Modal
- **Secure token display** (shown only once)
- **Copy-to-clipboard** functionality
- **Installation command** with copy button
- **Complete MCP configuration** with syntax highlighting
- **Step-by-step setup instructions**

### 🔧 Backend Features

#### API Endpoints
```python
# Token management
POST /api/tokens          # Create new token
GET /api/tokens           # List user's tokens
PUT /api/tokens/{id}      # Update token
DELETE /api/tokens/{id}   # Delete token

# MCP integration
GET /api/tokens/{id}/mcp-config  # Get MCP configuration
```

#### Database Model
```python
class ApiToken(Base):
    id = Column(VARCHAR(36), primary_key=True)
    user_id = Column(VARCHAR(36), ForeignKey("users.id"))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    token = Column(VARCHAR(64), unique=True)  # Secure token
    permissions = Column(JSON)  # ["read", "write"]
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
```

#### Authentication Middleware
- **Token validation** from database
- **Expiration checking**
- **Usage tracking** (last_used_at)
- **Permission enforcement**
- **Fallback to JWT tokens**

### 🔒 Security Features

#### Token Generation
- **Cryptographically secure** using `secrets.token_urlsafe(32)`
- **Unique tokens** with database constraint
- **URL-safe encoding** for easy copying

#### Token Management
- **Expiration dates** (optional)
- **Active/inactive status**
- **Usage tracking** for monitoring
- **Secure storage** (tokens never shown again)

#### Permission System
- **Read permissions**: View portfolios, grids, market data
- **Write permissions**: Create/modify portfolios and grids
- **Granular control** ready for future expansion

## 🛠️ Configuration Examples

### Basic MCP Configuration
```json
{
  "mcpServers": {
    "gridtrader-pro": {
      "command": "gridtrader-pro-mcp",
      "env": {
        "GRIDTRADER_API_URL": "https://gridsai.app",
        "GRIDTRADER_ACCESS_TOKEN": "your_secure_token_here"
      }
    }
  }
}
```

### Advanced Configuration (Production)
```json
{
  "mcpServers": {
    "gridtrader-pro": {
      "command": "gridtrader-pro-mcp",
      "env": {
        "GRIDTRADER_API_URL": "https://your-domain.com",
        "GRIDTRADER_ACCESS_TOKEN": "your_secure_token_here"
      }
    }
  }
}
```

## 🧪 Testing

### Automated Testing
```bash
# Run comprehensive integration test
python test_token_integration.py
```

This test will:
1. ✅ **Check API connection**
2. ✅ **Create test user**
3. ✅ **Login and get session**
4. ✅ **Create API token**
5. ✅ **Test token authentication**
6. ✅ **Test MCP configuration**
7. ✅ **Test MCP server with token**

### Manual Testing
```bash
# Test token authentication directly
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://gridsai.app/api/portfolios

# Test MCP server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | \
GRIDTRADER_ACCESS_TOKEN=YOUR_TOKEN \
node mcp-server/dist/index.js
```

## 📊 Usage Analytics

### Token Usage Tracking
- **last_used_at**: Updated on every API call
- **Usage patterns**: Track which tokens are actively used
- **Security monitoring**: Detect unusual usage patterns

### Dashboard Integration
Future enhancement: Add token usage statistics to the main dashboard.

## 🔧 Troubleshooting

### Common Issues

#### "Table 'api_tokens' doesn't exist"
```bash
python add_api_tokens_migration.py
```

#### "Token not found" errors
1. Check token is active in `/tokens` page
2. Verify token hasn't expired
3. Confirm correct API URL in MCP config

#### "Authorization header required"
1. Check MCP configuration has correct token
2. Verify GRIDTRADER_ACCESS_TOKEN is set
3. Restart Cursor after config changes

#### MCP server connection issues
1. Ensure GridTrader Pro is running
2. Check API URL is accessible
3. Verify token permissions include required access

### Debug Commands

```bash
# Check database migration
mysql -u root -p -e "DESCRIBE gridtrader_db.api_tokens;"

# Test API endpoint directly
curl -X POST https://gridsai.app/api/tokens \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Test token"}'

# Check MCP server installation
which gridtrader-pro-mcp
```

## 🎉 Success Indicators

You know everything is working when:

1. ✅ **Token page loads**: https://gridsai.app/tokens
2. ✅ **Token creation works**: Success modal appears
3. ✅ **API authentication works**: `curl` with token succeeds
4. ✅ **MCP server responds**: Tools list returns successfully
5. ✅ **Cursor integration works**: AI commands return data

## 🚀 What's Next

### Immediate Use
- **Create portfolios**: "Create a balanced portfolio with $15,000"
- **Grid trading**: "Set up a grid for TSLA with range $200-300"
- **Market data**: "What's the current price of AAPL?"
- **Analytics**: "Show my portfolio performance metrics"

### Future Enhancements
- **Webhook support**: Real-time notifications
- **API rate limiting**: Per-token rate limits
- **Advanced permissions**: Granular endpoint access
- **Token analytics**: Usage dashboards
- **Multi-tenant support**: Organization-level tokens

## 📞 Support

### Getting Help
1. **Check the logs**: Both GridTrader Pro and MCP server
2. **Run the test script**: `python test_token_integration.py`
3. **Verify configuration**: Double-check token and URLs
4. **Test components individually**: API → Token → MCP → Cursor

### Common Commands
```bash
# View application logs
tail -f logs/app.log

# Test token creation
python test_token_integration.py

# Check MCP server
node mcp-server/dist/index.js < test_input.json

# Restart services
python main.py  # GridTrader Pro
# Restart Cursor completely
```

---

**🎊 Congratulations! You now have a complete API token system for GridTrader Pro!**

**Ready to trade with AI using secure, manageable API tokens! 🚀📈🔐**
