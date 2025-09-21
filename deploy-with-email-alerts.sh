#!/bin/bash
# Deploy GridTrader Pro to Coolify with Email Alerts Configured

echo "🚀 DEPLOYING GRIDTRADER PRO TO COOLIFY"
echo "📧 Email alerts configured for: isky999@gmail.com"
echo "=" * 60

# Check if Coolify configuration exists
if [ -f "coolify-production.json" ]; then
    echo "✅ Found coolify-production.json"
else
    echo "❌ coolify-production.json not found"
    exit 1
fi

# Verify email configuration in Coolify JSON
echo "🔍 Verifying email configuration..."
if grep -q "SMTP_USERNAME" coolify-production.json; then
    echo "✅ SMTP_USERNAME configured"
else
    echo "❌ SMTP_USERNAME missing"
fi

if grep -q "isky999@gmail.com" coolify-production.json; then
    echo "✅ Email address configured: isky999@gmail.com"
else
    echo "❌ Email address not configured"
fi

echo ""
echo "📋 COOLIFY ENVIRONMENT VARIABLES TO SET:"
echo "SMTP_USERNAME=isky999@gmail.com"
echo "SMTP_PASSWORD=oxqy ktcn dyot vljy"
echo "SMTP_SERVER=smtp.gmail.com"
echo "SMTP_PORT=587"
echo "FROM_EMAIL=isky999@gmail.com"
echo "FROM_NAME=GridTrader Pro Alerts"
echo "ENABLE_EMAIL_ALERTS=true"
echo "DEFAULT_ALERT_EMAIL=isky999@gmail.com"

echo ""
echo "🎯 GRID ALERT CONFIGURATION:"
echo "• 600298.SS Conservative Grid: Email alerts enabled"
echo "• Grid ID: 9d26f827-4605-4cce-ac42-8dbcf173433d"
echo "• Price range: $36.32 - $42.94"
echo "• Alert types: Order filled, Boundary, Profit, Risk"

echo ""
echo "📧 AFTER DEPLOYMENT:"
echo "1. Verify environment variables in Coolify dashboard"
echo "2. Check application logs for email service status"
echo "3. Test email alerts via API endpoint"
echo "4. Monitor grid trading alerts in isky999@gmail.com inbox"

echo ""
echo "🧪 TEST COMMAND AFTER DEPLOYMENT:"
echo "curl -X POST \"https://gridsai.app/api/grids/9d26f827-4605-4cce-ac42-8dbcf173433d/alerts/test-email\" \\"
echo "  -H \"Authorization: Bearer FG08bkU8TcGzqQJWy0QuoXqANJT2EuJwP2a6nLZlKoU\""

echo ""
echo "🚀 Ready for Coolify deployment with email alerts!"
