#!/bin/bash

# GridTrader Pro Git Setup Script
echo "📦 GridTrader Pro - Git Setup"
echo "============================="

# Initialize git repository if not already initialized
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local
.env.production

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite3
*.sql

# Docker
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
tmp/
temp/
*.tmp
*.temp

# Backup files
backups/
*.bak
*.backup

# Redis dump
dump.rdb

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/
EOF
    echo "✅ .gitignore created"
fi

# Add all files
echo "📁 Adding files to Git..."
git add .

# Check if there are any changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Initial commit: GridTrader Pro - Systematic Investment Management Platform

Features:
- FastAPI backend with HTML templates
- Grid trading algorithms with multiple strategies
- Portfolio management with auto-rebalancing
- Real-time market data via yfinance
- Google OAuth authentication + JWT
- Background tasks with Celery + Redis
- MySQL database with complete schema
- Docker deployment with Nginx + Supervisor
- Responsive web interface with TailwindCSS
- Production-ready single container architecture"
    echo "✅ Changes committed"
fi

# Check if remote origin exists
if git remote | grep -q "origin"; then
    echo "🔗 Remote 'origin' already exists"
    git remote -v
else
    echo "🔗 No remote repository configured"
    echo "To add a remote repository, run:"
    echo "   git remote add origin https://github.com/yourusername/gridtrader-pro.git"
fi

echo ""
echo "🎉 Git setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a new repository on GitHub/GitLab"
echo "2. Add remote: git remote add origin <your-repo-url>"
echo "3. Push code: git push -u origin main"
echo ""
echo "Or use the push script: ./git-push.sh"