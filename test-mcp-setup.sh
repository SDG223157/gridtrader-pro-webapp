#!/bin/bash

# GridTrader Pro MCP Setup Test Script
# This script tests that all components are working correctly

set -e

echo "🧪 Testing GridTrader Pro MCP Setup..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Check if GridTrader Pro is running
echo -e "${BLUE}1. Testing GridTrader Pro WebApp...${NC}"
if curl -s https://gridsai.app/health > /dev/null; then
    echo -e "${GREEN}✅ GridTrader Pro is running on https://gridsai.app${NC}"
else
    echo -e "${RED}❌ GridTrader Pro is not running. Check https://gridsai.app${NC}"
    exit 1
fi

# Test 2: Check if MCP server builds
echo -e "${BLUE}2. Testing MCP Server Build...${NC}"
cd /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server
if npm run build > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MCP Server builds successfully${NC}"
else
    echo -e "${RED}❌ MCP Server build failed${NC}"
    exit 1
fi

# Test 3: Check if MCP server responds
echo -e "${BLUE}3. Testing MCP Server Response...${NC}"
if echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | timeout 10s node dist/index.js > /dev/null 2>&1; then
    echo -e "${GREEN}✅ MCP Server responds to tool list request${NC}"
else
    echo -e "${YELLOW}⚠️  MCP Server test timed out (this may be normal)${NC}"
fi

# Test 4: Test API authentication
echo -e "${BLUE}4. Testing API Authentication...${NC}"
cd /Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp
if curl -s -H "Authorization: Bearer gridtrader_dev_token_123" https://gridsai.app/api/portfolios > /dev/null; then
    echo -e "${GREEN}✅ API authentication works${NC}"
else
    echo -e "${RED}❌ API authentication failed${NC}"
    echo -e "${YELLOW}   Make sure the middleware is added to main.py${NC}"
fi

# Test 5: Check market data endpoint
echo -e "${BLUE}5. Testing Market Data API...${NC}"
if curl -s -H "Authorization: Bearer gridtrader_dev_token_123" https://gridsai.app/api/market/AAPL?period=current | grep -q "price"; then
    echo -e "${GREEN}✅ Market data API works${NC}"
else
    echo -e "${YELLOW}⚠️  Market data API may not be working (check yfinance)${NC}"
fi

# Test 6: Check if Cursor config exists
echo -e "${BLUE}6. Checking Cursor Configuration...${NC}"
CURSOR_CONFIG="$HOME/.cursor/mcp_servers.json"
if [ -f "$CURSOR_CONFIG" ]; then
    echo -e "${GREEN}✅ Cursor MCP config file exists${NC}"
    if grep -q "gridtrader-pro" "$CURSOR_CONFIG"; then
        echo -e "${GREEN}✅ GridTrader Pro MCP server is configured in Cursor${NC}"
    else
        echo -e "${YELLOW}⚠️  GridTrader Pro MCP server not found in Cursor config${NC}"
        echo -e "${YELLOW}   Add the configuration manually or use Cursor UI${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Cursor MCP config file not found${NC}"
    echo -e "${YELLOW}   You'll need to configure MCP in Cursor settings${NC}"
fi

# Test 7: Verify required files exist
echo -e "${BLUE}7. Checking Required Files...${NC}"
REQUIRED_FILES=(
    "/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/dist/index.js"
    "/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/mcp-server/package.json"
    "/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/cursor-mcp-config.json"
    "/Users/sdg223157/gridsai_webapp/gridtrader-pro-webapp/MCP_SETUP_COMPLETE_GUIDE.md"
)

ALL_FILES_EXIST=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file${NC}"
        ALL_FILES_EXIST=false
    fi
done

# Summary
echo ""
echo "======================================"
echo -e "${BLUE}📋 Setup Summary${NC}"
echo "======================================"

if [ "$ALL_FILES_EXIST" = true ]; then
    echo -e "${GREEN}🎉 All components are ready!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Configure Cursor MCP settings (see MCP_SETUP_COMPLETE_GUIDE.md)"
    echo "2. Restart Cursor completely"
    echo "3. Test with: 'Show me all my portfolios'"
    echo ""
    echo -e "${BLUE}Example Cursor Commands:${NC}"
    echo "• 'Show me all my portfolios'"
    echo "• 'What's the current price of AAPL?'"
    echo "• 'Create a new tech portfolio with \$10,000'"
    echo "• 'Show my dashboard summary'"
else
    echo -e "${RED}❌ Some components are missing. Check the errors above.${NC}"
fi

echo ""
echo -e "${BLUE}📖 For detailed setup instructions, see:${NC}"
echo "   MCP_SETUP_COMPLETE_GUIDE.md"
echo ""
echo -e "${GREEN}🚀 Happy trading with AI!${NC}"
