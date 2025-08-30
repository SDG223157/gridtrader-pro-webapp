#!/bin/bash

# GridTrader Pro Quick Start Script
echo "🚀 GridTrader Pro - Quick Start"
echo "================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Setting up environment configuration..."
    cp .env.example .env
    echo "✅ .env file created"
fi

# Check for required environment variables
echo "🔍 Checking configuration..."

# Check if Google OAuth is configured
if grep -q "your-google-client-id" .env; then
    echo "⚠️  WARNING: Please configure your Google OAuth credentials in .env file"
    echo "   1. Go to https://console.cloud.google.com/"
    echo "   2. Create OAuth 2.0 credentials"
    echo "   3. Update GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env"
    echo ""
    read -p "Press Enter when you've updated the .env file..."
fi

# Create logs directory
mkdir -p logs

# Start the application
echo "🐳 Starting GridTrader Pro with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for services to initialize..."
sleep 15

# Check if services are running
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 GridTrader Pro is ready!"
echo "🌐 Web Interface: http://localhost:3000"
echo "📚 API Documentation: http://localhost:3000/docs"
echo "❤️  Health Check: http://localhost:3000/health"
echo ""
echo "💡 Useful commands:"
echo "   ./deploy.sh logs     - View application logs"
echo "   ./deploy.sh status   - Check service status"
echo "   ./deploy.sh down     - Stop all services"
echo "   ./deploy.sh backup   - Create database backup"
echo ""
echo "🔧 To stop: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"