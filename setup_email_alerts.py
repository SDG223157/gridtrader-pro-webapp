#!/usr/bin/env python3
"""
Setup Email Alerts for isky999@gmail.com
Configure and test email alerts for grid trading
"""

import os
import json
from datetime import datetime

def setup_email_config():
    """Setup email configuration for isky999@gmail.com"""
    
    print("📧 EMAIL ALERT SETUP FOR isky999@gmail.com")
    print("=" * 60)
    
    # Email configuration template
    email_config = {
        "target_email": "isky999@gmail.com",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "from_name": "GridTrader Pro",
        "alert_types": {
            "grid_order_filled": {
                "enabled": True,
                "frequency": "immediate",
                "subject": "🎯 Grid Order Filled - {symbol}",
                "priority": "medium"
            },
            "price_boundary": {
                "enabled": True,
                "frequency": "immediate", 
                "subject": "⚠️ Price Boundary Alert - {symbol}",
                "priority": "high"
            },
            "profit_target": {
                "enabled": True,
                "thresholds": [5000, 15000, 30000],
                "subject": "🎉 Profit Target Reached - {symbol}",
                "priority": "high"
            },
            "risk_warning": {
                "enabled": True,
                "frequency": "immediate",
                "subject": "🚨 RISK WARNING - {symbol}", 
                "priority": "critical"
            }
        },
        "grids": {
            "600298.SS": {
                "grid_id": "9d26f827-4605-4cce-ac42-8dbcf173433d",
                "grid_name": "600298.SS Conservative Grid",
                "portfolio_name": "Yang's Investment Portfolio",
                "price_range": {"lower": 36.32, "upper": 42.94},
                "investment": 1000000,
                "boundary_buffer": 0.50
            }
        }
    }
    
    # Save configuration
    config_file = "email_alert_config.json"
    with open(config_file, 'w') as f:
        json.dump(email_config, f, indent=2)
    
    print(f"✅ Email configuration saved to: {config_file}")
    print(f"📧 Target email: {email_config['target_email']}")
    print(f"🎯 Grid configured: 600298.SS")
    
    return email_config

def create_sample_email_content():
    """Create sample email content for different alert types"""
    
    alerts = {
        "grid_order_filled": {
            "subject": "🎯 Grid Order Filled - 600298.SS",
            "content": """
Dear Grid Trader,

Your grid order has been executed successfully!

📊 Trade Details:
• Symbol: 600298.SS
• Order Type: BUY
• Price: $38.53
• Quantity: 2,000 shares
• Total Amount: $77,060.00
• Profit: $220.00

🎯 Grid Information:
• Grid: 600298.SS Conservative Grid
• Portfolio: Yang's Investment Portfolio
• Range: $36.32 - $42.94

This automated trade was executed as part of your grid trading strategy.

Best regards,
GridTrader Pro Team

View Portfolio: https://gridsai.app/portfolios/8a4a6edd-200d-4d65-8041-b76de959cd45
            """
        },
        "profit_target": {
            "subject": "🎉 Profit Target Reached - 600298.SS",
            "content": """
Congratulations! Your grid has reached a profit milestone!

💰 Performance Summary:
• Symbol: 600298.SS
• Total Profit: $8,500.00
• Return: 8.5%
• Investment: $100,000
• Duration: 15 days

🎯 Grid: 600298.SS Conservative Grid
📈 Excellent performance!

Consider taking profits or expanding your grid range.

Best regards,
GridTrader Pro Team
            """
        }
    }
    
    return alerts

def main():
    """Main setup function"""
    print("🚀 SETTING UP EMAIL ALERTS FOR GRID TRADING")
    print("=" * 70)
    
    # Setup configuration
    config = setup_email_config()
    
    # Create sample content
    samples = create_sample_email_content()
    
    print("\n📧 EMAIL ALERT TYPES CONFIGURED:")
    for alert_type, settings in config["alert_types"].items():
        if settings["enabled"]:
            status = "✅" if settings["enabled"] else "❌"
            print(f"{status} {alert_type.replace('_', ' ').title()} - {settings['priority']} priority")
    
    print(f"\n🎯 CONFIGURED FOR GRID:")
    grid_info = config["grids"]["600298.SS"]
    print(f"• Grid: {grid_info['grid_name']}")
    print(f"• Range: ${grid_info['price_range']['lower']:.2f} - ${grid_info['price_range']['upper']:.2f}")
    print(f"• Investment: ${grid_info['investment']:,}")
    
    print(f"\n📧 EMAIL DESTINATION:")
    print(f"• Target: {config['target_email']}")
    print(f"• SMTP: {config['smtp_server']}:{config['smtp_port']}")
    
    print(f"\n🔧 NEXT STEPS:")
    print("1. Set SMTP environment variables (see EMAIL_ALERT_SETUP_GUIDE.md)")
    print("2. Test with: POST /api/grids/{grid_id}/alerts/test-email")
    print("3. Configure alert preferences via API")
    print("4. Monitor grid trading with email notifications!")

if __name__ == "__main__":
    main()
