# 📧 Gmail SMTP Setup Guide for isky999@gmail.com

## 🎯 Overview
Configure Gmail SMTP to send grid trading alerts to your email address: **isky999@gmail.com**

---

## 📋 Step-by-Step Setup

### **STEP 1: Enable 2-Factor Authentication**

1. **Go to Google Account Settings**:
   - Visit: https://myaccount.google.com/
   - Sign in with: isky999@gmail.com

2. **Navigate to Security**:
   - Click "Security" in the left sidebar
   - Find "2-Step Verification" section

3. **Enable 2-Step Verification**:
   - Click "2-Step Verification"
   - Follow the setup wizard
   - Use your phone number for verification
   - **IMPORTANT**: This is required for app passwords

### **STEP 2: Generate App Password**

1. **Access App Passwords**:
   - Go to: https://myaccount.google.com/apppasswords
   - Or: Security → 2-Step Verification → App passwords

2. **Create App Password**:
   - Click "Select app" → Choose "Other (Custom name)"
   - Enter name: **"GridTrader Pro Alerts"**
   - Click "Generate"

3. **Save the App Password**:
   - Google will show a 16-character password (e.g., `abcd efgh ijkl mnop`)
   - **COPY THIS PASSWORD** - you won't see it again
   - This is NOT your regular Gmail password

### **STEP 3: Configure Environment Variables**

#### **Option A: Terminal/Shell Setup**
```bash
# Set environment variables (replace with your actual app password)
export SMTP_USERNAME="isky999@gmail.com"
export SMTP_PASSWORD="your-16-char-app-password"
export FROM_EMAIL="isky999@gmail.com"
export FROM_NAME="GridTrader Pro Alerts"

# Optional: Add to your shell profile for persistence
echo 'export SMTP_USERNAME="isky999@gmail.com"' >> ~/.zshrc
echo 'export SMTP_PASSWORD="your-app-password"' >> ~/.zshrc
echo 'export FROM_EMAIL="isky999@gmail.com"' >> ~/.zshrc
echo 'export FROM_NAME="GridTrader Pro Alerts"' >> ~/.zshrc
```

#### **Option B: Docker/Production Setup**
```bash
# For Docker deployment
docker run -e SMTP_USERNAME="isky999@gmail.com" \
           -e SMTP_PASSWORD="your-app-password" \
           -e FROM_EMAIL="isky999@gmail.com" \
           -e FROM_NAME="GridTrader Pro Alerts" \
           your-app
```

#### **Option C: .env File (Development)**
```bash
# Create .env file in project root
cat > .env << EOF
SMTP_USERNAME=isky999@gmail.com
SMTP_PASSWORD=your-16-char-app-password
FROM_EMAIL=isky999@gmail.com
FROM_NAME=GridTrader Pro Alerts
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EOF
```

---

## 🧪 Testing

### **STEP 4: Test Email Configuration**

```bash
# Test the email service
source venv/bin/activate
python3 -c "
from email_alert_service import EmailAlertService

email_service = EmailAlertService()
print(f'✅ Configured: {email_service.is_configured}')
print(f'📧 Username: {email_service.smtp_username}')
print(f'🔒 Password: {\"*\" * len(email_service.smtp_password) if email_service.smtp_password else \"Not set\"}')
"
```

### **STEP 5: Send Test Alert**

```bash
# Test with Yang's 600298.SS grid
curl -X POST "https://gridsai.app/api/grids/9d26f827-4605-4cce-ac42-8dbcf173433d/alerts/test-email?alert_type=grid_order_filled" \
  -H "Authorization: Bearer FG08bkU8TcGzqQJWy0QuoXqANJT2EuJwP2a6nLZlKoU"
```

---

## 🔧 Configuration Details

### **Gmail SMTP Settings:**
```
SMTP Server: smtp.gmail.com
SMTP Port: 587 (TLS)
Username: isky999@gmail.com
Password: [Your 16-character app password]
Security: STARTTLS
```

### **Environment Variables:**
```bash
SMTP_USERNAME=isky999@gmail.com          # Your Gmail address
SMTP_PASSWORD=abcd-efgh-ijkl-mnop        # 16-char app password
SMTP_SERVER=smtp.gmail.com               # Gmail SMTP server
SMTP_PORT=587                            # TLS port
FROM_EMAIL=isky999@gmail.com             # Sender email
FROM_NAME=GridTrader Pro Alerts         # Sender name
```

---

## 📧 Email Alert Examples

### **Grid Order Filled Alert:**
```
To: isky999@gmail.com
Subject: 🎯 Grid Order Filled - 600298.SS
Content:
  BUY order filled for 600298.SS
  Price: $38.53
  Quantity: 2,000 shares
  Profit: $220.00
  Grid: 600298.SS Conservative Grid
```

### **Profit Target Alert:**
```
To: isky999@gmail.com
Subject: 🎉 Profit Target Reached - 600298.SS
Content:
  Grid profit reached $8,500!
  Return: 8.5%
  Duration: 15 days
  Investment: $1,000,000
```

### **Boundary Alert:**
```
To: isky999@gmail.com
Subject: ⚠️ Price Boundary Alert - 600298.SS
Content:
  Price $36.45 approaching lower boundary $36.32
  Distance: $0.13
  Consider grid adjustment
```

---

## 🛡️ Security Best Practices

### **✅ DO:**
- Use Gmail App Password (not regular password)
- Enable 2-Factor Authentication
- Store app password securely
- Use environment variables (not hardcoded)
- Test in development first

### **❌ DON'T:**
- Use your regular Gmail password
- Share app passwords
- Commit passwords to git
- Disable 2-Factor Authentication
- Use unsecured SMTP

---

## 🚨 Troubleshooting

### **Common Issues:**

**"Authentication Failed"**
- ✅ Verify 2-Factor Authentication is enabled
- ✅ Use app password, not regular password
- ✅ Check username is exactly: isky999@gmail.com

**"Connection Refused"**
- ✅ Verify SMTP server: smtp.gmail.com
- ✅ Verify port: 587
- ✅ Check firewall/network settings

**"App Password Not Working"**
- ✅ Generate new app password
- ✅ Remove spaces from password
- ✅ Verify 2FA is still enabled

### **Test Commands:**
```bash
# Test SMTP connection
python3 -c "
import smtplib
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print('✅ SMTP connection successful')
    server.quit()
except Exception as e:
    print(f'❌ SMTP error: {e}')
"
```

---

## 🎯 For Your 600298.SS Grid

### **Current Grid Configuration:**
- **Grid ID**: 9d26f827-4605-4cce-ac42-8dbcf173433d
- **Symbol**: 600298.SS
- **Range**: $36.32 - $42.94
- **Investment**: $1,000,000
- **Portfolio**: Yang's Investment Portfolio

### **Alert Configuration:**
- **Email**: isky999@gmail.com
- **Order Alerts**: ✅ Enabled (immediate)
- **Boundary Alerts**: ✅ Enabled (within $0.50)
- **Profit Alerts**: ✅ Enabled ($5K, $15K, $30K)
- **Risk Alerts**: ✅ Enabled (critical priority)

---

## 🚀 Quick Setup Summary

1. **Enable 2FA**: https://myaccount.google.com/security
2. **Generate App Password**: https://myaccount.google.com/apppasswords
3. **Set Environment Variables**: Use the 16-character app password
4. **Test Configuration**: Run email service test
5. **Send Test Alert**: Use API endpoint to verify delivery

**Once configured, you'll receive professional email alerts for all grid trading activities!** 📧🎯
