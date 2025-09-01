# MCP Integration Templates

This directory contains **reusable templates** for adding MCP (Model Context Protocol) integration to any web application deployed on Coolify with Docker.

## 📁 Template Files

### Core Implementation
- **`api-endpoints-template.py`** - FastAPI endpoints for token management and data access
- **`authentication-middleware-template.py`** - Universal Bearer token authentication middleware
- **`mcp-server-template.ts`** - TypeScript MCP server implementation
- **`package.json.template`** - npm package configuration for MCP server

### Setup & Deployment
- **`install-script-template.sh`** - Automated installation script template
- **`quick-start-checklist.md`** - 2-hour implementation checklist

## 🚀 Quick Usage

### 1. Copy Templates
```bash
# Copy the templates to your new project
cp templates/mcp-integration/* /path/to/your-new-app/
```

### 2. Customize for Your App
```bash
# Replace placeholders in all files:
# - "your-app" → your actual app name
# - "your-domain.com" → your actual domain
# - "YourEntity" → your database models
# - "YourAppMCPServer" → your server class name
```

### 3. Implement
```bash
# Follow the quick-start-checklist.md
# Estimated time: 2-3 hours for complete integration
```

## 🎯 What Each Template Provides

### `api-endpoints-template.py`
- ✅ Token CRUD operations
- ✅ Core data access endpoints
- ✅ Dashboard summary endpoint
- ✅ Debug and health check endpoints
- ✅ Proper error handling

### `authentication-middleware-template.py`
- ✅ Bearer token validation
- ✅ Session-based auth fallback
- ✅ Request state management
- ✅ Token expiration checking
- ✅ Usage tracking

### `mcp-server-template.ts`
- ✅ MCP protocol implementation
- ✅ Tool definitions and handlers
- ✅ API communication layer
- ✅ Error handling and logging
- ✅ Natural language response formatting

### `install-script-template.sh`
- ✅ Node.js version checking
- ✅ Global npm installation
- ✅ Source fallback installation
- ✅ Installation verification
- ✅ Setup instructions

## 📋 Customization Checklist

When adapting these templates for your app:

### Replace These Placeholders:
- [ ] `your-app` → Your app name (lowercase, hyphenated)
- [ ] `Your App` → Your app name (title case)
- [ ] `your-domain.com` → Your actual domain
- [ ] `YourEntity` → Your database model names
- [ ] `YourAppMCPServer` → Your MCP server class name
- [ ] `YOUR_APP_API_URL` → Your API URL environment variable
- [ ] `YOUR_APP_ACCESS_TOKEN` → Your token environment variable

### Customize These Functions:
- [ ] `get_data_list` → Your main data retrieval
- [ ] `get_items` → Your entity listing
- [ ] `create_item` → Your entity creation
- [ ] Tool descriptions and schemas
- [ ] API endpoint paths
- [ ] Database queries

### Update These Configurations:
- [ ] MCP server name and version
- [ ] npm package name and details
- [ ] Repository URLs
- [ ] Domain and API URLs
- [ ] Environment variable names

## 🎯 Expected Results

After implementing these templates, users should be able to:

### Natural Language Commands
- "Show me my [entities]"
- "Create a new [entity] called '[name]'"
- "What's my [app] summary?"
- "Get details for [specific item]"

### Technical Integration
- ✅ Global MCP server installation
- ✅ Secure API token authentication
- ✅ Cursor IDE integration
- ✅ Real-time data access
- ✅ Error handling and feedback

## 📚 Additional Resources

- [Main Guide](../GENERAL_MCP_INTEGRATION_GUIDE.md) - Complete implementation guide
- [GridTrader Pro Example](../) - Real-world implementation reference
- [MCP Protocol Docs](https://modelcontextprotocol.io) - Official MCP documentation
- [Cursor MCP Setup](https://cursor.sh/docs/mcp) - Cursor-specific setup guide

## 🤝 Contributing

If you improve these templates or create new ones:

1. Test with a real application
2. Document any changes or improvements
3. Submit a pull request with examples
4. Update this README with new features

## 📞 Support

For template-related questions:
- Create an issue in the repository
- Reference the specific template file
- Include your customization details
- Provide error logs if applicable

---

**These templates provide a proven foundation for adding AI integration to any web application! 🚀**
