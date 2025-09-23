# 🚀 Celery Deployment Guide for Grid Alert System

## ❌ Why Alerts Aren't Working

The alert system requires **Celery worker** and **Celery beat scheduler** to be running in production. Currently, these are likely not running in your Coolify deployment.

## 🔧 Required Services

### **1. Main Application**
- FastAPI web server (already running)

### **2. Celery Worker** ⚠️ **MISSING**
- Processes background tasks (price monitoring, alert generation)
- Command: `celery -A tasks worker --loglevel=info`

### **3. Celery Beat Scheduler** ⚠️ **MISSING** 
- Schedules periodic tasks (runs every 2 minutes during market hours)
- Command: `celery -A tasks beat --loglevel=info`

### **4. Redis Service** ⚠️ **MIGHT BE MISSING**
- Message broker for Celery
- Required for task queuing

## 🐳 Docker Configuration Update

Your current `Dockerfile` likely only runs the FastAPI app. You need to run multiple services.

### **Option 1: Multi-Service Dockerfile (Recommended)**

Update your `Dockerfile` to use supervisor to run multiple services:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Install supervisor
RUN apt-get update && apt-get install -y supervisor

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 8000

# Start supervisor (manages all services)
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

### **Option 2: Separate Coolify Services**

Deploy 3 separate services in Coolify:
1. **Web Service**: FastAPI app
2. **Worker Service**: Celery worker  
3. **Beat Service**: Celery beat scheduler

## 📝 Supervisor Configuration

Create/update `supervisord.conf`:

```ini
[supervisord]
nodaemon=true
user=root

[program:web]
command=uvicorn main:app --host 0.0.0.0 --port 8000
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/web.err.log
stdout_logfile=/var/log/web.out.log

[program:celery_worker]
command=celery -A tasks worker --loglevel=info
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/celery_worker.err.log
stdout_logfile=/var/log/celery_worker.out.log

[program:celery_beat]
command=celery -A tasks beat --loglevel=info
directory=/app
autostart=true
autorestart=true
stderr_logfile=/var/log/celery_beat.err.log
stdout_logfile=/var/log/celery_beat.out.log
```

## 🔴 Redis Configuration in Coolify

### **Add Redis Service:**
1. In Coolify, add a new **Redis** service to your project
2. Note the Redis connection URL (usually `redis://redis:6379/0`)
3. Add to environment variables: `REDIS_URL=redis://redis:6379/0`

## 📧 Environment Variables Checklist

Ensure these are set in Coolify:

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=GridTrader Pro

# Redis Configuration  
REDIS_URL=redis://redis:6379/0

# Database Configuration
DATABASE_URL=mysql+mysqlconnector://user:pass@host:port/db
```

## 🚀 Quick Fix - Test Deployment

### **1. Update Dockerfile to use existing supervisord.conf:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Install supervisor
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

# Copy supervisor configuration (you already have this file)
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directory
RUN mkdir -p /var/log

# Expose port
EXPOSE 8000

# Start supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
```

### **2. Redeploy in Coolify**
- Push changes to GitHub
- Trigger rebuild in Coolify
- Check logs for all 3 services (web, celery_worker, celery_beat)

## 🔍 Verification Steps

After deployment, check logs for:

1. **Web Service**: `✅ FastAPI server started`
2. **Celery Worker**: `✅ celery@hostname ready`
3. **Celery Beat**: `✅ Scheduler: Sending due task`
4. **Alert System**: `🔍 Monitored X grids, created Y alerts`

## 🎯 Expected Behavior

Once properly deployed:
- Every 2 minutes during market hours (9:30 AM - 3:00 PM Beijing)
- Price $38.61 near buy level $38.64 will trigger email alert
- Email sent to isky999@gmail.com

## 🆘 Troubleshooting

### **Check Coolify Logs:**
1. Go to your application in Coolify
2. Check "Logs" tab
3. Look for Celery worker/beat startup messages
4. Check for any Redis connection errors

### **Test Manually:**
```bash
# In Coolify container terminal
celery -A tasks worker --loglevel=info  # Should start worker
celery -A tasks beat --loglevel=info    # Should start scheduler
```

### **Common Issues:**
- ❌ Redis not running: `Connection refused to redis:6379`
- ❌ Database not accessible: `MySQL connection error`
- ❌ SMTP not configured: `Email service not configured`
