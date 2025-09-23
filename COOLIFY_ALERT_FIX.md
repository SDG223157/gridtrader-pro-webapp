# 🚨 Coolify Alert System Fix - Step by Step

## 🔍 **Current Issue**
- Price $38.61 is $0.03 from buy level $38.64 ✅ **SHOULD trigger alert**
- Alert system code is correct ✅
- **Problem**: Celery worker/beat not running in production ❌

## 🛠️ **Required Coolify Configuration**

### **1. Add Redis Service**
In your Coolify project:
1. Click **"+ Add Resource"**
2. Select **"Redis"**
3. Deploy Redis service
4. Note the internal URL (usually `redis://redis:6379/0`)

### **2. Update Environment Variables**
In your app's **Environment** tab, add/verify:

```bash
# Email Configuration (you said you added these)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=GridTrader Pro

# Redis Configuration (ADD THIS)
REDIS_URL=redis://redis:6379/0

# Database (should already exist)
DATABASE_URL=mysql+mysqlconnector://user:pass@host:port/database
```

### **3. Use Correct Dockerfile**
In Coolify, ensure you're using:
- **Dockerfile**: `Dockerfile.production` 
- **OR** verify main `Dockerfile` uses supervisor correctly

### **4. Verify Port Configuration**
- Coolify should expose port **3000** (matches supervisord.conf)
- Internal FastAPI runs on port 3000

## 🚀 **Deploy and Test**

### **Step 1: Commit Changes**
```bash
git add .
git commit -m "🔧 Fix Celery supervisor configuration for alerts"
git push origin main
```

### **Step 2: Redeploy in Coolify**
1. Go to your app in Coolify
2. Click **"Deploy"** to trigger rebuild
3. Wait for deployment to complete

### **Step 3: Check Logs**
In Coolify logs, you should see:
```
🚀 Starting GridTrader Pro Production...
✅ Database connection established
✅ Redis connection established  
🔧 Setting up database...
🎬 Starting services...
[INFO] Starting supervisor...
[INFO] Starting gridtrader...
[INFO] Starting celery-worker...
[INFO] Starting celery-beat...
```

### **Step 4: Verify Services Running**
Look for these log entries:
```
# Celery Worker Started
celery@hostname ready.

# Celery Beat Started  
Scheduler: Sending due task monitor-grid-prices-realtime

# Alert System Working
🔍 Monitored 1 grids, created 1 alerts
📧 Email alert sent for buy level 38.64
```

## 🔍 **Troubleshooting**

### **If Redis Connection Fails:**
```
❌ Redis connection timeout - continuing without background tasks
```
**Fix**: Ensure Redis service is running and `REDIS_URL` is correct

### **If Celery Worker Fails:**
```
[CRITICAL] Worker failed to start
```
**Fix**: Check `/app/logs/celery-error.log` for specific errors

### **If No Alerts Triggered:**
```
📴 Skipping grid price monitoring - China market closed
```
**Fix**: This is normal outside market hours (9:30 AM - 3:00 PM Beijing)

### **If Email Fails:**
```
❌ Failed to send email: Authentication failed
```
**Fix**: Verify SMTP credentials, use Gmail app password

## 🎯 **Expected Result**

Once properly deployed, within 2 minutes during market hours:

1. **Celery beat** triggers `monitor_grid_prices_realtime`
2. **Task detects** price $38.61 near buy level $38.64  
3. **Alert created** in database
4. **Email sent** to isky999@gmail.com with subject:
   ```
   🎯 Buy Level Alert - 600298.SS
   ```

## 📧 **Test Email Manually**

To test email service immediately:

1. **SSH into Coolify container** (if available)
2. **Run test script**:
   ```bash
   cd /app
   python3 diagnose_alert_system.py
   ```

## 🆘 **If Still Not Working**

### **Check Specific Logs:**
- `/app/logs/celery.log` - Worker status
- `/app/logs/celery-beat.log` - Scheduler status  
- `/app/logs/app.log` - Main application
- `/var/log/supervisor/supervisord.log` - Service management

### **Manual Celery Test:**
```bash
# In container terminal
celery -A tasks worker --loglevel=debug
celery -A tasks beat --loglevel=debug
```

### **Force Alert Test:**
```bash
# In container, create test alert
python3 -c "
from tasks import monitor_grid_prices_realtime
result = monitor_grid_prices_realtime()
print(result)
"
```

## 📞 **Next Steps**
1. ✅ Add Redis service to Coolify
2. ✅ Verify REDIS_URL environment variable  
3. ✅ Redeploy application
4. ✅ Check logs for Celery worker/beat startup
5. ✅ Wait for next market hours to test alerts

The alert system **will work** once Celery services are running properly! 🎯
