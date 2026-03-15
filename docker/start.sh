#!/bin/bash
set -e

echo "🚀 Starting GridTrader Pro Production..."

# Remove stale SSL client certificates that cause Permission denied errors
rm -rf /root/.postgresql 2>/dev/null || true
export PGSSLCERT=/tmp/.postgresql/nonexistent.crt
export PGSSLKEY=/tmp/.postgresql/nonexistent.key

# Create database tables
echo "🔧 Setting up database..."
python init_database.py

# Start supervisor (web app only)
echo "🎬 Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
