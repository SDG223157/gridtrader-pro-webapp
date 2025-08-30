#!/bin/bash

# GridTrader Pro Production Deployment Script for gridsai.app
set -e

echo "🚀 GridTrader Pro Production Deployment"
echo "======================================="
echo "Domain: https://gridsai.app"
echo "Database: External MySQL"
echo "Redis: External Redis"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# Verify environment configuration
print_status "Verifying production configuration..."

if [ ! -f .env ]; then
    print_error ".env file not found!"
    exit 1
fi

# Check critical environment variables
source .env

if [ -z "$GOOGLE_CLIENT_ID" ] || [[ "$GOOGLE_CLIENT_ID" == *"your-google"* ]]; then
    print_error "GOOGLE_CLIENT_ID not configured in .env"
    exit 1
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ] || [[ "$GOOGLE_CLIENT_SECRET" == *"your-google"* ]]; then
    print_error "GOOGLE_CLIENT_SECRET not configured in .env"
    exit 1
fi

if [ -z "$DB_HOST" ] || [[ "$DB_HOST" == "localhost" ]]; then
    print_error "External DB_HOST not configured in .env"
    exit 1
fi

if [ -z "$REDIS_URL" ] || [[ "$REDIS_URL" == *"localhost"* ]]; then
    print_error "External REDIS_URL not configured in .env"
    exit 1
fi

print_status "✅ Configuration verified"

# Parse command line arguments
ACTION=${1:-"deploy"}

case $ACTION in
    "build")
        print_status "Building GridTrader Pro production image..."
        docker build -f Dockerfile.production -t gridtrader-pro:production .
        ;;
    "deploy")
        print_status "Deploying GridTrader Pro to production..."
        
        # Build the image
        print_status "Building production image..."
        docker build -f Dockerfile.production -t gridtrader-pro:production .
        
        # Stop existing container if running
        if docker ps -a | grep -q gridtrader-pro-production; then
            print_status "Stopping existing container..."
            docker stop gridtrader-pro-production || true
            docker rm gridtrader-pro-production || true
        fi
        
        # Start new container
        print_status "Starting production container..."
        docker run -d \
            --name gridtrader-pro-production \
            --restart unless-stopped \
            --env-file .env \
            -p 3000:3000 \
            -v "$(pwd)/logs:/app/logs" \
            gridtrader-pro:production
        
        print_status "Waiting for container to start..."
        sleep 10
        
        # Check container status
        if docker ps | grep -q gridtrader-pro-production; then
            print_status "✅ Container started successfully"
        else
            print_error "❌ Container failed to start"
            docker logs gridtrader-pro-production
            exit 1
        fi
        ;;
    "stop")
        print_status "Stopping GridTrader Pro production..."
        docker stop gridtrader-pro-production || true
        docker rm gridtrader-pro-production || true
        ;;
    "restart")
        print_status "Restarting GridTrader Pro production..."
        docker stop gridtrader-pro-production || true
        docker rm gridtrader-pro-production || true
        docker run -d \
            --name gridtrader-pro-production \
            --restart unless-stopped \
            --env-file .env \
            -p 3000:3000 \
            -v "$(pwd)/logs:/app/logs" \
            gridtrader-pro:production
        ;;
    "logs")
        print_status "Showing production logs..."
        docker logs -f gridtrader-pro-production
        ;;
    "status")
        print_status "Production service status:"
        docker ps | grep gridtrader-pro-production || echo "Container not running"
        ;;
    "shell")
        print_status "Opening shell in production container..."
        docker exec -it gridtrader-pro-production /bin/bash
        ;;
    "health")
        print_status "Checking application health..."
        if curl -f http://localhost:3000/health > /dev/null 2>&1; then
            print_status "✅ Application is healthy"
        else
            print_error "❌ Application health check failed"
            exit 1
        fi
        ;;
    "test-db")
        print_status "Testing database connection..."
        docker exec gridtrader-pro-production python -c "
from database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
        ;;
    "test-redis")
        print_status "Testing Redis connection..."
        docker exec gridtrader-pro-production python -c "
import redis
import os
try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
"
        ;;
    *)
        echo "Usage: $0 {build|deploy|stop|restart|logs|status|shell|health|test-db|test-redis}"
        echo ""
        echo "Commands:"
        echo "  build     - Build production Docker image"
        echo "  deploy    - Deploy to production (build + run)"
        echo "  stop      - Stop production container"
        echo "  restart   - Restart production container"
        echo "  logs      - Show container logs"
        echo "  status    - Show container status"
        echo "  shell     - Open shell in container"
        echo "  health    - Check application health"
        echo "  test-db   - Test database connection"
        echo "  test-redis - Test Redis connection"
        exit 1
        ;;
esac

# Show final status for deploy action
if [ "$ACTION" = "deploy" ]; then
    echo ""
    print_status "🎉 GridTrader Pro deployed to production!"
    print_status "🌐 Application URL: https://gridsai.app"
    print_status "📊 Health Check: https://gridsai.app/health"
    print_status "📚 API Documentation: https://gridsai.app/docs"
    echo ""
    print_status "📋 Next steps:"
    print_status "1. Configure your reverse proxy/load balancer to point to port 3000"
    print_status "2. Set up SSL certificate for https://gridsai.app"
    print_status "3. Test the application at https://gridsai.app"
    print_status "4. Monitor logs with: ./deploy-production.sh logs"
    echo ""
    print_warning "🔧 Container is running on port 3000"
    print_warning "📝 Make sure your reverse proxy forwards traffic to localhost:3000"
fi

echo ""
print_status "Production deployment script completed!"