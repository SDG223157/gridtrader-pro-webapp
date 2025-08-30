#!/bin/bash

# GridTrader Pro Git Push Script
echo "🚀 GridTrader Pro - Git Push"
echo "============================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git repository not initialized. Run ./git-setup.sh first"
    exit 1
fi

# Check if remote origin exists
if ! git remote | grep -q "origin"; then
    echo "🔗 No remote repository configured."
    echo "Please add a remote repository first:"
    echo ""
    read -p "Enter your repository URL: " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✅ Remote repository added"
    else
        echo "❌ No repository URL provided. Exiting."
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff --staged --quiet || ! git diff --quiet; then
    echo "📝 Uncommitted changes detected. Committing..."
    git add .
    
    # Get commit message
    echo "Enter commit message (or press Enter for default):"
    read -p "> " commit_message
    
    if [ -z "$commit_message" ]; then
        commit_message="Update GridTrader Pro - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    git commit -m "$commit_message"
    echo "✅ Changes committed"
fi

# Get current branch
current_branch=$(git branch --show-current)
if [ -z "$current_branch" ]; then
    current_branch="main"
    git branch -M main
fi

echo "📤 Pushing to remote repository..."
echo "Branch: $current_branch"

# Push to remote
if git push -u origin "$current_branch"; then
    echo "✅ Code pushed successfully!"
    echo ""
    echo "🎉 Your GridTrader Pro is now on GitHub!"
    echo ""
    echo "Repository URL:"
    git remote get-url origin
    echo ""
    echo "Next steps:"
    echo "1. Set up your production environment variables"
    echo "2. Deploy to Coolify or your preferred platform"
    echo "3. Configure Google OAuth credentials"
    echo "4. Set up your MySQL and Redis instances"
else
    echo "❌ Failed to push to remote repository"
    echo "Please check your repository URL and permissions"
    exit 1
fi