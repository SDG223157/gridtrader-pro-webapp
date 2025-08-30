#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro Simple..."

# Wait for database
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

# Initialize database
echo "🔧 Setting up database..."
python init_database.py

# Start application directly (no supervisord)
echo "🎬 Starting GridTrader Pro..."
exec python main_simple.py
