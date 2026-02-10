# GridTrader Pro - Production Deployment (Neon + Gunicorn)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies (PostgreSQL client libs instead of MySQL)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    pkg-config \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/static /app/templates

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting GridTrader Pro..."\n\
\n\
# Create database tables\n\
echo "Setting up database..."\n\
python -c "from database import create_tables; create_tables()"\n\
\n\
# Start with gunicorn + uvicorn workers\n\
echo "Starting Gunicorn with Uvicorn workers..."\n\
exec gunicorn main:app \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT:-3000} \
  --workers 4 \
  --timeout 120 \
  --graceful-timeout 30 \
  --access-logfile -' > /start.sh && chmod +x /start.sh

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-3000}/health || exit 1

# Start the application
CMD ["/start.sh"]
