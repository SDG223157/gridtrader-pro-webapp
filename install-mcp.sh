#!/bin/bash

# GridTrader Pro MCP Server Installation Script
# This script installs the GridTrader Pro MCP server globally

set -e

echo "🚀 Installing GridTrader Pro MCP Server..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2)
MAJOR_VERSION=$(echo $NODE_VERSION | cut -d'.' -f1)

if [ "$MAJOR_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ is required. Current version: v$NODE_VERSION"
    echo "Please upgrade Node.js: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js v$NODE_VERSION detected"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📦 Downloading GridTrader Pro MCP Server..."

# Clone the repository
if command -v git &> /dev/null; then
    git clone https://github.com/SDG223157/gridtrader-pro-webapp.git
    cd gridtrader-pro-webapp/mcp-server
else
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

echo "🔧 Building MCP Server..."

# Install dependencies
npm install

# Build TypeScript
npm run build

echo "📦 Installing globally..."

# Install globally
npm install -g .

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo "✅ GridTrader Pro MCP Server installed successfully!"
echo ""
echo "🔧 Next Steps:"
echo "1. Set up your GridTrader Pro application"
echo "2. Configure your access token"
echo "3. Add the MCP configuration to Cursor"
echo ""
echo "📖 Configuration Example:"
echo '{'
echo '  "mcpServers": {'
echo '    "gridtrader-pro": {'
echo '      "command": "gridtrader-pro-mcp",'
echo '      "env": {'
echo '        "GRIDTRADER_API_URL": "http://localhost:3000",'
echo '        "GRIDTRADER_ACCESS_TOKEN": "your_access_token_here"'
echo '      }'
echo '    }'
echo '  }'
echo '}'
echo ""
echo "🎉 Ready to use GridTrader Pro with AI!"
