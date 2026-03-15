#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro Production..."

# Remove stale SSL client certificates that cause Permission denied errors
rm -rf /root/.postgresql 2>/dev/null || true
export PGSSLCERT=/tmp/.postgresql/nonexistent.crt
export PGSSLKEY=/tmp/.postgresql/nonexistent.key

# Optional: disable Redis entirely (no Celery worker/beat, no Redis wait)
if [ "$DISABLE_REDIS" = "1" ] || [ "$DISABLE_REDIS" = "true" ] || [ "$DISABLE_REDIS" = "yes" ]; then
    echo "📌 Redis disabled (DISABLE_REDIS) - running web app only, no background tasks"
    export DISABLE_REDIS=1
    unset REDIS_URL REDIS_HOST REDIS_PORT
    SUPERVISORD_CONF="/etc/supervisor/conf.d/supervisord-no-redis.conf"
else
    # Wait for external Redis (use REDIS_HOST or parse from REDIS_URL)
    REDIS_HOST="${REDIS_HOST:-}"
    REDIS_PORT="${REDIS_PORT:-6379}"
    if [ -z "$REDIS_HOST" ] && [ -n "$REDIS_URL" ]; then
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
    SUPERVISORD_CONF="/etc/supervisor/conf.d/supervisord.conf"
fi

# Create database tables
echo "🔧 Setting up database..."
python init_database.py

# Start supervisor
echo "🎬 Starting services..."
exec /usr/bin/supervisord -c "$SUPERVISORD_CONF"