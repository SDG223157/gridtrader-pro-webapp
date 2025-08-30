#!/bin/bash

# GridTrader Pro Deployment Script
set -e

echo "🚀 GridTrader Pro Deployment Script"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p logs

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration before continuing."
    print_warning "Especially set your GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET"
    exit 1
fi

# Parse command line arguments
ACTION=${1:-"up"}

case $ACTION in
    "build")
        print_status "Building GridTrader Pro..."
        docker-compose build --no-cache
        ;;
    "up")
        print_status "Starting GridTrader Pro..."
        docker-compose up -d
        print_status "Waiting for services to start..."
        sleep 10
        print_status "Checking service health..."
        docker-compose ps
        ;;
    "down")
        print_status "Stopping GridTrader Pro..."
        docker-compose down
        ;;
    "restart")
        print_status "Restarting GridTrader Pro..."
        docker-compose down
        docker-compose up -d
        ;;
    "logs")
        print_status "Showing logs..."
        docker-compose logs -f
        ;;
    "status")
        print_status "Service status:"
        docker-compose ps
        ;;
    "clean")
        print_warning "This will remove all containers, volumes, and images. Are you sure? (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            print_status "Cleaning up..."
            docker-compose down -v
            docker system prune -f
            docker volume prune -f
        else
            print_status "Cleanup cancelled."
        fi
        ;;
    "backup")
        print_status "Creating database backup..."
        mkdir -p backups
        docker-compose exec mysql mysqldump -u root -proot_secure_password gridtrader_db > "backups/gridtrader_backup_$(date +%Y%m%d_%H%M%S).sql"
        print_status "Backup created in backups/ directory"
        ;;
    "restore")
        if [ -z "$2" ]; then
            print_error "Please specify backup file: ./deploy.sh restore <backup_file>"
            exit 1
        fi
        print_status "Restoring database from $2..."
        docker-compose exec -T mysql mysql -u root -proot_secure_password gridtrader_db < "$2"
        print_status "Database restored successfully"
        ;;
    "update")
        print_status "Updating GridTrader Pro..."
        git pull origin main
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    *)
        echo "Usage: $0 {build|up|down|restart|logs|status|clean|backup|restore|update}"
        echo ""
        echo "Commands:"
        echo "  build    - Build the Docker images"
        echo "  up       - Start all services"
        echo "  down     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  logs     - Show service logs"
        echo "  status   - Show service status"
        echo "  clean    - Remove all containers and volumes"
        echo "  backup   - Create database backup"
        echo "  restore  - Restore database from backup"
        echo "  update   - Pull latest code and rebuild"
        exit 1
        ;;
esac

# Show final status
if [ "$ACTION" = "up" ]; then
    echo ""
    print_status "GridTrader Pro is starting up!"
    print_status "Web Interface: http://localhost:3000"
    print_status "API Documentation: http://localhost:3000/docs"
    print_status "Health Check: http://localhost:3000/health"
    echo ""
    print_warning "Make sure to configure your Google OAuth credentials in .env"
    print_warning "Database and Redis data will persist in Docker volumes"
fi

echo ""
print_status "Deployment script completed!"