#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro Production..."

# Remove stale SSL client certificates that cause Permission denied errors
rm -rf /root/.postgresql 2>/dev/null || true
export PGSSLCERT=/dev/null
export PGSSLKEY=/dev/null

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