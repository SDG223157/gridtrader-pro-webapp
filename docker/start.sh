#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro Production..."

# Remove stale SSL client certificates that cause Permission denied errors
rm -rf /root/.postgresql 2>/dev/null || true
export PGSSLCERT=/tmp/.postgresql/nonexistent.crt
export PGSSLKEY=/tmp/.postgresql/nonexistent.key

# Wait for external Redis (use REDIS_HOST or parse from REDIS_URL)
REDIS_HOST="${REDIS_HOST:-}"
REDIS_PORT="${REDIS_PORT:-6379}"
if [ -z "$REDIS_HOST" ] && [ -n "$REDIS_URL" ]; then
    # Parse host from redis://HOST:PORT/DB or redis://HOST:PORT
    if [[ "$REDIS_URL" =~ redis://([^:/]+)(:([0-9]+))? ]]; then
        REDIS_HOST="${BASH_REMATCH[1]}"
        [ -n "${BASH_REMATCH[3]}" ] && REDIS_PORT="${BASH_REMATCH[3]}"
    fi
fi
if [ -n "$REDIS_HOST" ] && [ "$REDIS_HOST" != "localhost" ] && [ "$REDIS_HOST" != "127.0.0.1" ]; then
    echo "⏳ Waiting for Redis at $REDIS_HOST:${REDIS_PORT}..."
    timeout=30
    while ! nc -z "$REDIS_HOST" "$REDIS_PORT" 2>/dev/null && [ $timeout -gt 0 ]; do
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