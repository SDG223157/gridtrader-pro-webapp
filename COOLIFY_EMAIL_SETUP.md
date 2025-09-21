# 📧 Coolify Email Alert Configuration for isky999@gmail.com

## 🚀 Coolify Deployment Configuration

Since you deploy the GridTrader Pro app on Coolify, you need to add the SMTP environment variables in your Coolify project settings.

---

## ⚙️ Coolify Environment Variables

### **Add These Variables in Coolify Dashboard:**

Go to your Coolify project → **Environment Variables** section and add:

```bash
# Email Alert Configuration
SMTP_USERNAME=isky999@gmail.com
SMTP_PASSWORD=oxqy ktcn dyot vljy
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FROM_EMAIL=isky999@gmail.com
FROM_NAME=GridTrader Pro Alerts

# Enable Email Alerts
ENABLE_EMAIL_ALERTS=true
DEFAULT_ALERT_EMAIL=isky999@gmail.com
```

---

## 📋 Coolify Configuration Steps

### **STEP 1: Access Coolify Dashboard**
1. Log into your Coolify instance
2. Navigate to your GridTrader Pro project
3. Go to **"Environment Variables"** or **"Configuration"** section

### **STEP 2: Add Environment Variables**
For each variable, click **"Add Environment Variable"** and enter:

| **Variable Name** | **Value** | **Description** |
|-------------------|-----------|-----------------|
| `SMTP_USERNAME` | `isky999@gmail.com` | Gmail account for sending |
| `SMTP_PASSWORD` | `oxqy ktcn dyot vljy` | Gmail app password |
| `SMTP_SERVER` | `smtp.gmail.com` | Gmail SMTP server |
| `SMTP_PORT` | `587` | TLS port for Gmail |
| `FROM_EMAIL` | `isky999@gmail.com` | Sender email address |
| `FROM_NAME` | `GridTrader Pro Alerts` | Sender display name |
| `ENABLE_EMAIL_ALERTS` | `true` | Enable email functionality |
| `DEFAULT_ALERT_EMAIL` | `isky999@gmail.com` | Default alert recipient |

### **STEP 3: Deploy/Restart Application**
1. Save the environment variables
2. Restart or redeploy your application
3. Coolify will inject these variables into your container

---

## 🔧 Coolify-Specific Configuration

### **Update Existing Coolify JSON:**
If you have a `coolify.json` or similar configuration file, add:

```json
{
  "name": "gridtrader-pro",
  "environment": {
    "SMTP_USERNAME": "isky999@gmail.com",
    "SMTP_PASSWORD": "oxqy ktcn dyot vljy", 
    "SMTP_SERVER": "smtp.gmail.com",
    "SMTP_PORT": "587",
    "FROM_EMAIL": "isky999@gmail.com",
    "FROM_NAME": "GridTrader Pro Alerts",
    "ENABLE_EMAIL_ALERTS": "true",
    "DEFAULT_ALERT_EMAIL": "isky999@gmail.com"
  }
}
```

### **Docker Environment Variables:**
Coolify will pass these as Docker environment variables:
```bash
docker run \
  -e SMTP_USERNAME="isky999@gmail.com" \
  -e SMTP_PASSWORD="oxqy ktcn dyot vljy" \
  -e SMTP_SERVER="smtp.gmail.com" \
  -e SMTP_PORT="587" \
  -e FROM_EMAIL="isky999@gmail.com" \
  -e FROM_NAME="GridTrader Pro Alerts" \
  your-gridtrader-image
```

---

## 🧪 Testing After Coolify Deployment

### **Verify Environment Variables:**
```bash
# SSH into your Coolify container or check logs
echo $SMTP_USERNAME
echo $SMTP_SERVER
# Password should be set but not echoed for security
```

### **Test Email Functionality:**
```bash
# Test API endpoint after deployment
curl -X POST "https://gridsai.app/api/grids/9d26f827-4605-4cce-ac42-8dbcf173433d/alerts/test-email?alert_type=grid_order_filled" \
  -H "Authorization: Bearer FG08bkU8TcGzqQJWy0QuoXqANJT2EuJwP2a6nLZlKoU"
```

### **Check Application Logs:**
Look for these log messages in Coolify:
```
✅ Email alert sent to isky999@gmail.com: 🎯 Grid Order Filled - 600298.SS
📧 Email service configured and ready
```

---

## 🔒 Security Considerations

### **Environment Variable Security in Coolify:**
- ✅ **Encrypted Storage**: Coolify encrypts environment variables
- ✅ **No Git Exposure**: Variables not stored in repository
- ✅ **Container Isolation**: Variables only available to your app
- ✅ **Access Control**: Only you can view/edit variables

### **Best Practices:**
- ✅ Use Gmail app password (not regular password)
- ✅ Store variables in Coolify (not in code)
- ✅ Monitor email delivery in application logs
- ✅ Regenerate app password if compromised

---

## 🎯 For Your 600298.SS Grid

### **Grid Configuration:**
- **Grid ID**: 9d26f827-4605-4cce-ac42-8dbcf173433d
- **Symbol**: 600298.SS
- **Range**: $36.32 - $42.94
- **Investment**: $1,000,000

### **Email Alerts Configured:**
- **Target**: isky999@gmail.com
- **Order Alerts**: ✅ Every trade execution
- **Boundary Alerts**: ✅ Price near $36.32 or $42.94
- **Profit Alerts**: ✅ $5K, $15K, $30K milestones
- **Risk Alerts**: ✅ Critical market warnings

---

## 🚀 Deployment Checklist

- [ ] Add environment variables in Coolify dashboard
- [ ] Save configuration changes
- [ ] Restart/redeploy application
- [ ] Test email delivery via API
- [ ] Verify alerts in application logs
- [ ] Check email delivery to isky999@gmail.com

**Once deployed on Coolify with these environment variables, your grid trading email alerts will be fully operational!** 📧🎯
