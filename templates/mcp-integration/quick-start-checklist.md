# MCP Integration Quick Start Checklist

## ⚡ 2-Hour Implementation Checklist

### Phase 1: Database (15 min)
- [ ] Add `api_tokens` table to database schema
- [ ] Create ApiToken model in ORM
- [ ] Run database migration
- [ ] Verify table creation

### Phase 2: Backend API (30 min)
- [ ] Add authentication middleware for Bearer tokens
- [ ] Create `/api/tokens` CRUD endpoints
- [ ] Update `require_auth` function for API token support
- [ ] Add core API endpoints for your app data
- [ ] Test API endpoints with curl

### Phase 3: MCP Server (45 min)
- [ ] Create `mcp-server/` directory
- [ ] Set up TypeScript project with package.json
- [ ] Implement MCP server with your app's tools
- [ ] Build and test MCP server locally
- [ ] Create installation script

### Phase 4: Frontend (30 min)
- [ ] Create token management page (`/tokens`)
- [ ] Add token creation form with Alpine.js
- [ ] Implement token listing and management
- [ ] Add MCP setup guide modal
- [ ] Test token creation and deletion

### Phase 5: Integration (20 min)
- [ ] Install MCP server globally: `npm install -g your-app-mcp`
- [ ] Create test API token
- [ ] Configure Cursor MCP settings
- [ ] Restart Cursor IDE
- [ ] Test natural language commands

## 🔧 Environment Variables Needed

```env
# Add to your Coolify deployment
SECRET_KEY=your_secret_key_here
YOUR_APP_API_URL=https://your-domain.com
```

## 📝 Files to Create/Modify

```
your-app/
├── database.py (or models.py)     # Add ApiToken model
├── auth.py                        # Update require_auth function  
├── main.py                        # Add middleware + API endpoints
├── templates/tokens.html          # Token management UI
├── mcp-server/
│   ├── src/index.ts              # MCP server implementation
│   ├── package.json              # Dependencies and scripts
│   └── tsconfig.json             # TypeScript configuration
├── install-mcp.sh                # Installation script
└── your-app-mcp-config.json      # Sample MCP configuration
```

## 🧪 Testing Commands

```bash
# Test API authentication
curl -H "Authorization: Bearer YOUR_TOKEN" https://your-domain.com/api/data

# Test MCP server
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | your-app-mcp

# Test in Cursor
"Show me my data"
"Create a new item called 'Test'"
```

## 🎯 Success Criteria

- [ ] API token authentication working
- [ ] MCP server responds to tool calls
- [ ] Cursor shows MCP server as connected
- [ ] Natural language commands return data
- [ ] Token management UI functional
- [ ] Setup guide accessible to users

## ⚠️ Common Pitfalls

1. **Middleware Order**: Place auth middleware after CORS
2. **Token Format**: Use `Bearer ` prefix (with space)
3. **Request State**: Set `request.state.user` in middleware
4. **Error Handling**: Return proper HTTP status codes
5. **CORS**: Allow Authorization header in CORS config

## 🚀 Go Live Checklist

- [ ] Coolify deployment updated
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] MCP server published to npm (optional)
- [ ] Documentation updated
- [ ] Users notified of new AI features
