#!/bin/bash

# Universal MCP Server Installation Script Template
# Customize this script for your application

set -e

echo "🚀 Your App - Global MCP Server Installation"
echo "============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration (Customize these variables)
APP_NAME="Your App"
MCP_PACKAGE_NAME="your-app-mcp"
MCP_COMMAND_NAME="your-app-mcp"
APP_DOMAIN="https://your-domain.com"
GITHUB_REPO="yourusername/your-app"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2)
REQUIRED_VERSION="18.0.0"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$NODE_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Node.js version $NODE_VERSION is too old. Please install Node.js 18+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js version $NODE_VERSION detected${NC}"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Please install npm first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ npm detected${NC}"
echo ""

# Install the MCP server globally
echo -e "${BLUE}📦 Installing $APP_NAME MCP Server globally...${NC}"

if npm install -g $MCP_PACKAGE_NAME; then
    echo -e "${GREEN}✅ MCP Server installed successfully!${NC}"
else
    echo -e "${YELLOW}⚠️  Global installation failed. Trying alternative method...${NC}"
    
    # Alternative: Install from source
    if [ -d "mcp-server" ]; then
        echo -e "${BLUE}📦 Installing from source...${NC}"
        cd mcp-server
        
        if npm install && npm run build && npm install -g .; then
            echo -e "${GREEN}✅ MCP Server installed from source!${NC}"
            cd ..
        else
            echo -e "${RED}❌ Installation failed. Please check the error messages above.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Installation failed and no source directory found.${NC}"
        echo "Try cloning the repository first:"
        echo "git clone https://github.com/$GITHUB_REPO.git"
        exit 1
    fi
fi

# Verify installation
echo ""
echo -e "${BLUE}🔍 Verifying installation...${NC}"

if command -v $MCP_COMMAND_NAME &> /dev/null; then
    echo -e "${GREEN}✅ MCP Server command is available${NC}"
    
    # Try to get version
    if $MCP_COMMAND_NAME --version &> /dev/null; then
        VERSION=$($MCP_COMMAND_NAME --version 2>/dev/null || echo "unknown")
        echo -e "${GREEN}✅ Version: $VERSION${NC}"
    fi
else
    echo -e "${RED}❌ MCP Server command not found. Installation may have failed.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Installation Complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. 🔑 Create an API token at: $APP_DOMAIN/tokens"
echo "2. ⚙️  Configure Cursor MCP settings with:"
echo ""
echo -e "${BLUE}   {${NC}"
echo -e "${BLUE}     \"mcpServers\": {${NC}"
echo -e "${BLUE}       \"your-app\": {${NC}"
echo -e "${BLUE}         \"command\": \"$MCP_COMMAND_NAME\",${NC}"
echo -e "${BLUE}         \"env\": {${NC}"
echo -e "${BLUE}           \"YOUR_APP_API_URL\": \"$APP_DOMAIN\",${NC}"
echo -e "${BLUE}           \"YOUR_APP_ACCESS_TOKEN\": \"your_api_token_here\"${NC}"
echo -e "${BLUE}         }${NC}"
echo -e "${BLUE}       }${NC}"
echo -e "${BLUE}     }${NC}"
echo -e "${BLUE}   }${NC}"
echo ""
echo "3. 🔄 Restart Cursor IDE"
echo "4. 🧪 Test with: \"Show me my data\""
echo ""
echo -e "${GREEN}📖 For detailed instructions, see: GENERAL_MCP_INTEGRATION_GUIDE.md${NC}"
echo ""
echo -e "${YELLOW}🆘 Need help? Visit: https://github.com/$GITHUB_REPO/issues${NC}"
