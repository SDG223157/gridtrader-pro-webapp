# 🚀 GridTrader Pro - Deployment Guide

## 📋 Complete Environment Configuration

### 1. Copy Environment File

```bash
# The .env file is already created with these settings:
# - Database: MySQL with local/Docker settings
# - Redis: Local/Docker Redis instance  
# - Google OAuth: Placeholder for your credentials
# - Security: Generated secret key
# - Application: Development settings
```

### 2. Required Environment Variables to Update

**MUST UPDATE for production:**

```bash
# Google OAuth (Required for authentication)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Production URLs
FRONTEND_URL=https://yourdomain.com
GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback

# Production Database (if using external DB)
DB_HOST=your-production-mysql-host
DB_PASSWORD=your-secure-mysql-password

# Production Redis (if using external Redis)
REDIS_HOST=your-production-redis-host
REDIS_PASSWORD=your-redis-password

# Security (Generate new secret)
SECRET_KEY=your-production-secret-key-32-chars-minimum
```

## 🐳 Quick Start (Local Development)

```bash
# 1. Quick start with Docker Compose
./quickstart.sh

# 2. Or manual steps
docker-compose up -d
```

**Access Points:**
- Web Interface: http://localhost:3000
- API Documentation: http://localhost:3000/docs
- Health Check: http://localhost:3000/health

## 🛠️ Deployment Commands

```bash
# Build and start
./deploy.sh build
./deploy.sh up

# View logs
./deploy.sh logs

# Check status  
./deploy.sh status

# Stop services
./deploy.sh down

# Create backup
./deploy.sh backup

# Clean everything
./deploy.sh clean
```

## 📦 Git Setup and Push

```bash
# 1. Initialize Git and commit
./git-setup.sh

# 2. Push to your repository
./git-push.sh
```

## ☁️ Coolify Deployment

### Method 1: Docker Compose (Recommended)

1. **Create new service** in Coolify
2. **Select "Docker Compose"** as deployment type
3. **Connect your Git repository**
4. **Set environment variables** in Coolify:
   ```
   GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   SECRET_KEY=your-production-secret-key-32-chars-minimum
   ENVIRONMENT=production
   FRONTEND_URL=https://yourdomain.com
   GOOGLE_REDIRECT_URI=https://yourdomain.com/api/auth/google/callback
   ```
5. **Deploy** - Coolify will use docker-compose.yml automatically

### Method 2: Single Dockerfile

1. **Create new service** in Coolify  
2. **Select "Dockerfile"** as deployment type
3. **Set Dockerfile path**: `Dockerfile`
4. **Set port**: `3000`
5. **Add environment variables** (same as above)
6. **Add external services**:
   - MySQL database
   - Redis cache
7. **Deploy**

## 🗄️ Database Setup

### Option 1: Docker Compose (Included)
- MySQL 8.0 with persistent volume
- Automatic initialization
- User and permissions setup

### Option 2: External Database
Update `.env` with your database credentials:
```bash
DB_HOST=your-mysql-host.com
DB_PORT=3306
DB_NAME=gridtrader_db
DB_USER=your-username
DB_PASSWORD=your-password
```

## 🔐 Google OAuth Setup

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create new project** or select existing
3. **Enable Google+ API**
4. **Create OAuth 2.0 credentials**:
   - Application type: Web application
   - Authorized redirect URIs: `https://yourdomain.com/api/auth/google/callback`
5. **Copy credentials** to your `.env` file
6. **Update environment** in Coolify

## 📊 Production Checklist

### Before Deployment:
- [ ] Update Google OAuth credentials
- [ ] Set production SECRET_KEY
- [ ] Configure production database
- [ ] Set correct FRONTEND_URL
- [ ] Update GOOGLE_REDIRECT_URI
- [ ] Test local deployment with `./quickstart.sh`

### After Deployment:
- [ ] Verify health endpoint: `/health`
- [ ] Test Google OAuth login
- [ ] Check database connection
- [ ] Verify Redis connection
- [ ] Test API endpoints: `/docs`
- [ ] Monitor application logs

## 🔍 Troubleshooting

### Common Issues:

**Database Connection Failed:**
```bash
# Check database credentials in .env
# Verify database is running
docker-compose logs mysql
```

**Google OAuth Error:**
```bash
# Verify OAuth credentials are correct
# Check redirect URI matches exactly
# Ensure Google+ API is enabled
```

**Redis Connection Failed:**
```bash
# Check Redis is running
docker-compose logs redis
# Verify Redis URL in .env
```

**Port Already in Use:**
```bash
# Stop existing services
./deploy.sh down
# Or change port in docker-compose.yml
```

### Log Files:
- Application: `/app/logs/app.log`
- Celery Worker: `/app/logs/celery.log`
- Celery Beat: `/app/logs/celery-beat.log`
- Nginx: `/var/log/nginx/`

## 🎯 Production Optimization

### Performance:
- Enable Redis caching
- Configure Nginx gzip compression
- Set up CDN for static files
- Monitor resource usage

### Security:
- Use strong SECRET_KEY
- Enable HTTPS/SSL
- Configure CORS properly
- Regular security updates

### Monitoring:
- Set up health checks
- Monitor database performance
- Track API response times
- Set up alerts for failures

## 📈 Scaling

### Horizontal Scaling:
- Multiple app containers behind load balancer
- Separate database server
- Redis cluster for caching
- Celery worker scaling

### Vertical Scaling:
- Increase container resources
- Optimize database queries
- Redis memory optimization
- Background task optimization

---

## 🎉 You're Ready to Deploy!

Your GridTrader Pro application is now ready for production deployment with:

✅ **Complete FastAPI backend** with all trading features  
✅ **Modern responsive frontend** with HTML templates  
✅ **Docker containerization** for easy deployment  
✅ **Database integration** with MySQL  
✅ **Authentication system** with Google OAuth  
✅ **Background processing** with Celery  
✅ **Production configuration** with Nginx + Supervisor  
✅ **Deployment scripts** for easy management  

**Next Step**: Update your Google OAuth credentials and deploy! 🚀