#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro..."

# Wait for database
if [ "$DB_HOST" ]; then
    echo "⏳ Waiting for database at $DB_HOST:${DB_PORT:-3306}..."
    timeout=30
    while ! nc -z "$DB_HOST" "${DB_PORT:-3306}" && [ $timeout -gt 0 ]; do
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Database connection timeout"
        exit 1
    fi
    echo "✅ Database connection established"
fi

# Wait for Redis
if [ "$REDIS_HOST" ]; then
    echo "⏳ Waiting for Redis at $REDIS_HOST:${REDIS_PORT:-6379}..."
    timeout=30
    while ! nc -z "$REDIS_HOST" "${REDIS_PORT:-6379}" && [ $timeout -gt 0 ]; do
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Redis connection timeout"
        exit 1
    fi
    echo "✅ Redis connection established"
fi

# Create database tables
echo "🔧 Setting up database..."
python -c "from database import create_tables; create_tables()"

# Start supervisor
echo "🎬 Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf