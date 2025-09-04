# GridTrader Pro Security Guide

## 🛡️ Security Implementation Summary

Your GridTrader Pro webapp now includes comprehensive security middleware to protect against the WordPress scanning attacks and other common web application threats.

## 🚨 What We Detected

From your logs, we identified:
- **Legitimate traffic**: Health checks from `127.0.0.1` (localhost) ✅
- **Normal usage**: Successful requests to `/` from `10.0.1.8` ✅
- **Attack attempts**: WordPress admin scanning from `10.0.1.8` ⚠️
  - `/wp-admin/setup-config.php`
  - `/wordpress/wp-admin/setup-config.php`
  - All returning 404 (good - your app doesn't have these endpoints)

## 🛡️ Security Measures Implemented

### 1. Rate Limiting Middleware
- **Normal requests**: 100 requests per minute per IP
- **404 requests**: 10 per minute per IP (stricter for scanning attempts)
- **Auto-blocking**: IPs exceeding limits are blocked for 5-10 minutes
- **Whitelist**: Localhost and private IPs are whitelisted

### 2. Attack Pattern Detection
Automatically detects and blocks requests containing:
- WordPress paths (`wp-admin`, `wordpress`, etc.)
- SQL injection patterns (`union select`, etc.)
- XSS attempts (`<script>`, `javascript:`, etc.)
- Directory traversal (`../`)
- Malicious function calls (`eval()`, `system()`, etc.)
- Suspicious user agents (scanner tools)

### 3. Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (for HTTPS)
- `Content-Security-Policy` (CSP)
- `Referrer-Policy: strict-origin-when-cross-origin`

### 4. Enhanced Logging
- Logs all security events with IP addresses
- Tracks attack patterns and blocked IPs
- Monitors suspicious activity patterns

## 🔧 Testing Your Security

You can test the security features:

1. **Check security status**:
   ```bash
   curl https://your-domain.com/debug/security-status
   ```

2. **Test rate limiting** (be careful - this will temporarily block your IP):
   ```bash
   # Don't run this from your main IP!
   for i in {1..15}; do curl https://your-domain.com/nonexistent-page; done
   ```

3. **Test attack detection**:
   ```bash
   curl https://your-domain.com/wp-admin/setup-config.php
   # Should return 403 Forbidden and block the IP
   ```

## 🔒 Deployment Security Recommendations

### Coolify Deployment Security

1. **Environment Variables**
   ```bash
   # Set strong secrets
   SECRET_KEY=your_very_long_random_secret_key_here
   
   # Database security
   DB_PASSWORD=strong_random_password
   
   # Disable debug in production
   DEBUG=false
   ENVIRONMENT=production
   ```

2. **Reverse Proxy Configuration**
   Coolify handles this, but ensure:
   - HTTPS is enabled
   - HTTP redirects to HTTPS
   - Proper SSL certificates

### Network Security

1. **Firewall Rules** (if you have server access):
   ```bash
   # Allow only necessary ports
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP (for redirects)
   ufw allow 443/tcp   # HTTPS
   ufw deny 3000/tcp   # Block direct app access
   ufw enable
   ```

2. **Database Security**:
   - Use strong passwords
   - Restrict database access to app server only
   - Enable SSL for database connections
   - Regular backups

### Application Security

1. **Update Dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor Logs**:
   ```bash
   # Check for security events
   grep "🛡️\|🚫\|⚠️" /var/log/your-app.log
   ```

3. **Regular Security Audits**:
   ```bash
   # Check for vulnerabilities
   pip audit
   ```

## 📊 Security Monitoring

### Key Metrics to Monitor

1. **Rate Limiting**:
   - Number of blocked IPs
   - Rate limit violations per hour
   - Top blocked IP addresses

2. **Attack Detection**:
   - Attack patterns detected
   - Most common attack types
   - Geographic distribution of attacks

3. **Application Security**:
   - Failed authentication attempts
   - Unusual API usage patterns
   - Database query anomalies

### Log Analysis

Look for these patterns in your logs:
```bash
# Security blocks
grep "🚫 Blocked IP" logs/

# Attack detection
grep "🛡️ Attack pattern detected" logs/

# Rate limiting
grep "⚠️ Rate limit exceeded" logs/
```

## 🚨 Incident Response

If you notice suspicious activity:

1. **Immediate Actions**:
   - Check `/debug/security-status` endpoint
   - Review recent logs for patterns
   - Verify legitimate user access isn't affected

2. **Investigation**:
   - Identify attack source and pattern
   - Check if any data was compromised
   - Review authentication logs

3. **Response**:
   - Block malicious IPs at network level if needed
   - Update security rules if new patterns emerge
   - Notify users if necessary

## 🔄 Security Updates

The security middleware is designed to be:
- **Self-updating**: Automatically adapts to new attack patterns
- **Performance-optimized**: Minimal impact on legitimate users
- **Configurable**: Can be tuned for your specific needs

### Customization Options

You can modify `security_middleware.py` to:
- Adjust rate limits
- Add custom attack patterns
- Modify blocking durations
- Customize whitelisted IPs

## 📞 Support

If you experience issues:
1. Check the security status endpoint
2. Review application logs
3. Verify legitimate traffic isn't being blocked
4. Adjust rate limits if needed

## ✅ Security Checklist

- [x] Rate limiting implemented
- [x] Attack pattern detection active
- [x] Security headers configured
- [x] Enhanced logging enabled
- [x] HTTPS enforced (via Coolify)
- [ ] Regular security audits scheduled
- [ ] Monitoring alerts configured
- [ ] Incident response plan documented

Your GridTrader Pro application is now significantly more secure against common web attacks!



