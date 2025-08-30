#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro Production..."

# Wait for external database
if [ "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ]; then
    echo "⏳ Waiting for database at $DB_HOST:${DB_PORT:-3306}..."
    timeout=60
    while ! nc -z "$DB_HOST" "${DB_PORT:-3306}" && [ $timeout -gt 0 ]; do
        sleep 2
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Database connection timeout"
        exit 1
    fi
    echo "✅ Database connection established"
fi

# Wait for external Redis
if [ "$REDIS_HOST" ] && [ "$REDIS_HOST" != "localhost" ]; then
    echo "⏳ Waiting for Redis at $REDIS_HOST:${REDIS_PORT:-6379}..."
    timeout=30
    while ! nc -z "$REDIS_HOST" "${REDIS_PORT:-6379}" && [ $timeout -gt 0 ]; do
        sleep 2
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        echo "❌ Redis connection timeout - continuing without background tasks"
    else
        echo "✅ Redis connection established"
    fi
fi

# Create database tables
echo "🔧 Setting up database..."
python init_database.py

# Start supervisor
echo "🎬 Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf