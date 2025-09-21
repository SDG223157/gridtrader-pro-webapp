# 📧 Email Alert Setup Guide for Grid Trading

## 🔔 Overview

The email alert system sends real-time notifications to users' email addresses for grid trading events, including order executions, profit targets, boundary alerts, and risk warnings.

## ⚙️ Configuration

### **Environment Variables Required:**

```bash
# SMTP Server Configuration
export SMTP_SERVER="smtp.gmail.com"          # Gmail SMTP (or your provider)
export SMTP_PORT="587"                       # Standard TLS port
export SMTP_USERNAME="your-email@gmail.com"  # Your email address
export SMTP_PASSWORD="your-app-password"     # Gmail app password (not regular password)
export FROM_EMAIL="alerts@gridsai.app"       # Sender email (optional)
export FROM_NAME="GridTrader Pro"            # Sender name (optional)
```

### **Gmail Setup (Recommended):**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "GridTrader Pro"
   - Use this app password (not your regular Gmail password)

3. **Set Environment Variables**:
   ```bash
   export SMTP_USERNAME="your-email@gmail.com"
   export SMTP_PASSWORD="your-16-char-app-password"
   ```

## 📧 Alert Types

### **1. Grid Order Filled Alerts** 🎯
**Trigger**: When buy/sell orders execute in grid
**Content**:
- Order type (BUY/SELL)
- Execution price
- Quantity traded
- Profit/loss for the trade
- Grid and portfolio context

**Example**: "🎯 BUY order filled for 600298.SS at $38.53 (2,000 shares, $220 profit)"

### **2. Price Boundary Alerts** ⚠️
**Trigger**: Price approaches or breaches grid boundaries
**Content**:
- Current price vs boundary price
- Distance from boundary
- Boundary type (upper/lower)
- Suggested actions

**Example**: "⚠️ 600298.SS approaching lower boundary: $36.45 (boundary: $36.32)"

### **3. Profit Target Alerts** 💰
**Trigger**: Grid reaches profit milestones
**Content**:
- Total profit achieved
- ROI percentage
- Time to achieve target
- Investment performance

**Example**: "🎉 Grid profit reached $8,500 for 600298.SS (8.5% return in 15 days)"

### **4. Risk Warning Alerts** 🚨
**Trigger**: Unusual market conditions or high risk
**Content**:
- Risk type and level
- Current market conditions
- Impact on grid performance
- Recommended actions

**Example**: "🚨 HIGH RISK: 600298.SS dropped 10% below grid range"

## 🔧 API Endpoints

### **Configure Grid Alerts:**
```http
POST /api/grids/{grid_id}/alerts/configure
{
  "order_filled_alerts": true,
  "boundary_alerts": true,
  "profit_alerts": true,
  "risk_alerts": true,
  "channels": ["email", "in_app"],
  "min_profit_threshold": 1000
}
```

### **Send Test Alert:**
```http
POST /api/grids/{grid_id}/alerts/test-email?alert_type=grid_order_filled
```

### **Get Grid Alerts:**
```http
GET /api/grids/{grid_id}/alerts?limit=50
```

## 🎯 For 600298.SS Grid

### **Current Grid Configuration:**
- **Symbol**: 600298.SS
- **Range**: $36.32 - $42.94
- **Investment**: $1,000,000
- **Grid ID**: 9d26f827-4605-4cce-ac42-8dbcf173433d

### **Recommended Alert Settings:**
```json
{
  "order_filled_alerts": true,
  "boundary_alerts": true,
  "profit_alerts": true,
  "profit_thresholds": [5000, 15000, 30000],
  "boundary_buffer": 0.50,
  "risk_alerts": true,
  "channels": ["email", "in_app"]
}
```

## 📱 Testing

### **Test Email Alert:**
```bash
# Test order filled alert
curl -X POST "https://gridsai.app/api/grids/9d26f827-4605-4cce-ac42-8dbcf173433d/alerts/test-email?alert_type=grid_order_filled" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test profit alert
curl -X POST "https://gridsai.app/api/grids/9d26f827-4605-4cce-ac42-8dbcf173433d/alerts/test-email?alert_type=profit_target" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛡️ Security & Privacy

- ✅ **User Email Privacy**: Only sends to verified user email addresses
- ✅ **Authentication Required**: All endpoints require valid user authentication
- ✅ **Grid Ownership**: Users only receive alerts for their own grids
- ✅ **Secure SMTP**: Uses TLS encryption for email transmission
- ✅ **Configurable**: Users can disable/enable alert types

## 🚀 Benefits

### **Proactive Trading:**
- ✅ **Immediate Notifications**: Know when orders execute
- ✅ **Risk Management**: Early warning for boundary breaches
- ✅ **Profit Tracking**: Celebrate milestone achievements
- ✅ **Market Awareness**: Stay informed of unusual conditions

### **User Experience:**
- ✅ **Professional Emails**: Clean HTML formatting
- ✅ **Direct Links**: Click to view portfolio/grid details
- ✅ **Contextual Information**: All relevant trade data included
- ✅ **Mobile Friendly**: Responsive email design

**The email alert system ensures you never miss important grid trading events!** 📧🚀
