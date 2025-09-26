#!/usr/bin/env python3
"""
Email Alert Service for Grid Trading
Sends alerts to users' email addresses for grid trading events
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class EmailAlertService:
    """Email service for sending grid trading alerts"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "GridTrader Pro")
        
        # Validate configuration
        self.is_configured = bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("⚠️ Email service not configured - missing SMTP credentials")
    
    def send_grid_order_alert(self, user_email: str, user_name: str, grid_data: Dict[str, Any]) -> bool:
        """Send alert when grid order is filled"""
        if not self.is_configured:
            logger.warning("Email service not configured")
            return False
            
        subject = f"🎯 Grid Order Filled - {grid_data['symbol']}"
        
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #28a745; margin-top: 0;">🎯 Grid Order Executed</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Trade Details</h3>
                    <p><strong>Symbol:</strong> {grid_data['symbol']}</p>
                    <p><strong>Order Type:</strong> {grid_data['order_type'].upper()}</p>
                    <p><strong>Price:</strong> ${grid_data['price']:.2f}</p>
                    <p><strong>Quantity:</strong> {grid_data['quantity']:,} shares</p>
                    <p><strong>Total Amount:</strong> ${grid_data['quantity'] * grid_data['price']:,.2f}</p>
                    <p><strong>Profit:</strong> <span style="color: {'green' if grid_data['profit'] >= 0 else 'red'};">${grid_data['profit']:.2f}</span></p>
                </div>
                
                <div style="background-color: #e9ecef; padding: 10px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #666;">
                        <strong>Grid:</strong> {grid_data['grid_name']}<br>
                        <strong>Portfolio:</strong> {grid_data['portfolio_name']}<br>
                        <strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    This is an automated alert from GridTrader Pro. 
                    <a href="https://gridsai.app/portfolios/{grid_data['portfolio_id']}">View Portfolio</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_boundary_alert(self, user_email: str, user_name: str, boundary_data: Dict[str, Any]) -> bool:
        """Send alert when price approaches grid boundaries"""
        if not self.is_configured:
            return False
            
        subject = f"⚠️ Price Boundary Alert - {boundary_data['symbol']}"
        
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                <h2 style="color: #856404; margin-top: 0;">⚠️ Price Boundary Alert</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Price Movement</h3>
                    <p><strong>Symbol:</strong> {boundary_data['symbol']}</p>
                    <p><strong>Current Price:</strong> ${boundary_data['current_price']:.2f}</p>
                    <p><strong>Boundary:</strong> ${boundary_data['boundary_price']:.2f} ({boundary_data['boundary_type']})</p>
                    <p><strong>Distance:</strong> ${abs(boundary_data['current_price'] - boundary_data['boundary_price']):.2f}</p>
                </div>
                
                <div style="background-color: #f8d7da; padding: 10px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #721c24;">
                        <strong>Action Required:</strong> Consider adjusting grid parameters or manual intervention
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    Grid: {boundary_data['grid_name']} | 
                    <a href="https://gridsai.app/grids/{boundary_data['grid_id']}">Manage Grid</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_profit_alert(self, user_email: str, user_name: str, profit_data: Dict[str, Any]) -> bool:
        """Send alert when profit targets are reached"""
        if not self.is_configured:
            return False
            
        subject = f"🎉 Profit Target Reached - {profit_data['symbol']}"
        
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
                <h2 style="color: #155724; margin-top: 0;">🎉 Profit Target Achieved!</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Performance Summary</h3>
                    <p><strong>Symbol:</strong> {profit_data['symbol']}</p>
                    <p><strong>Total Profit:</strong> <span style="color: #28a745; font-size: 18px; font-weight: bold;">${profit_data['total_profit']:,.2f}</span></p>
                    <p><strong>Return:</strong> {profit_data['profit_percentage']:.2f}%</p>
                    <p><strong>Investment:</strong> ${profit_data['investment_amount']:,.2f}</p>
                    <p><strong>Duration:</strong> {profit_data.get('duration_days', 'N/A')} days</p>
                </div>
                
                <div style="background-color: #cce5ff; padding: 10px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #004085;">
                        <strong>Suggestion:</strong> Consider taking profits or expanding grid range
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    Grid: {profit_data['grid_name']} | 
                    <a href="https://gridsai.app/grids/{profit_data['grid_id']}">View Details</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_risk_alert(self, user_email: str, user_name: str, risk_data: Dict[str, Any]) -> bool:
        """Send critical risk warning alerts"""
        if not self.is_configured:
            return False
            
        subject = f"🚨 RISK WARNING - {risk_data['symbol']}"
        
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                <h2 style="color: #721c24; margin-top: 0;">🚨 URGENT: Risk Warning</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Risk Details</h3>
                    <p><strong>Symbol:</strong> {risk_data['symbol']}</p>
                    <p><strong>Risk Type:</strong> {risk_data['risk_type']}</p>
                    <p><strong>Current Price:</strong> ${risk_data['current_price']:.2f}</p>
                    <p><strong>Risk Level:</strong> <span style="color: #dc3545; font-weight: bold;">{risk_data['risk_level']}</span></p>
                    <p><strong>Impact:</strong> {risk_data.get('impact_description', 'Potential grid performance impact')}</p>
                </div>
                
                <div style="background-color: #721c24; color: white; padding: 15px; border-radius: 6px;">
                    <p style="margin: 0; font-weight: bold;">
                        ⚡ IMMEDIATE ACTION RECOMMENDED
                    </p>
                    <p style="margin: 5px 0 0 0; font-size: 14px;">
                        Review grid parameters and consider risk management measures
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    Grid: {risk_data['grid_name']} | 
                    <a href="https://gridsai.app/grids/{risk_data['grid_id']}">MANAGE NOW</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_buy_level_alert(self, user_email: str, user_name: str, buy_data: Dict[str, Any]) -> bool:
        """Send alert when price approaches a buy level"""
        if not self.is_configured:
            return False
            
        subject = f"🎯 Buy Level Alert - {buy_data['symbol']}"
        
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #cce5ff; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff;">
                <h2 style="color: #004085; margin-top: 0;">🎯 Buy Level Opportunity</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Price Alert</h3>
                    <p><strong>Symbol:</strong> {buy_data['symbol']}</p>
                    <p><strong>Current Price:</strong> ${buy_data['current_price']:.2f}</p>
                    <p><strong>Buy Level:</strong> ${buy_data['buy_level']:.2f}</p>
                    <p><strong>Distance:</strong> ${abs(buy_data['current_price'] - buy_data['buy_level']):.2f}</p>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 10px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #0c5460;">
                        <strong>Action:</strong> Price is near your grid buy level - consider executing buy order
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    Grid: {buy_data['grid_name']} | 
                    <a href="https://gridsai.app/grids/{buy_data['grid_id']}">View Grid</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def send_sell_level_alert(self, user_email: str, user_name: str, sell_data: Dict[str, Any]) -> bool:
        """Send alert when price approaches a sell level"""
        if not self.is_configured:
            return False
            
        subject = f"💰 Sell Level Alert - {sell_data['symbol']}"
        
        html_content = f"""
        <html>
        <head></head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #d4edda; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
                <h2 style="color: #155724; margin-top: 0;">💰 Sell Level Opportunity</h2>
                
                <div style="background-color: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <h3 style="color: #333; margin-top: 0;">Price Alert</h3>
                    <p><strong>Symbol:</strong> {sell_data['symbol']}</p>
                    <p><strong>Current Price:</strong> ${sell_data['current_price']:.2f}</p>
                    <p><strong>Sell Level:</strong> ${sell_data['sell_level']:.2f}</p>
                    <p><strong>Distance:</strong> ${abs(sell_data['current_price'] - sell_data['sell_level']):.2f}</p>
                </div>
                
                <div style="background-color: #d1ecf1; padding: 10px; border-radius: 6px;">
                    <p style="margin: 0; font-size: 14px; color: #0c5460;">
                        <strong>Action:</strong> Price is near your grid sell level - consider taking profits or selling shares
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #999; margin-top: 20px;">
                    Grid: {sell_data['grid_name']} | 
                    <a href="https://gridsai.app/grids/{sell_data['grid_id']}">View Grid</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(user_email, subject, html_content)
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email alert sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

# Integration with existing user system
def send_grid_alert_to_user(user_id: str, alert_type: str, alert_data: Dict[str, Any], db_session) -> bool:
    """Send grid alert to user's email address"""
    try:
        # Get user from database
        from database import User
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if not user or not user.email:
            logger.error(f"User {user_id} not found or no email address")
            return False
        
        # Get user's display name
        user_name = user.profile.display_name if user.profile else user.email.split('@')[0]
        
        # Initialize email service
        email_service = EmailAlertService()
        
        # Send appropriate alert type
        if alert_type == "grid_order_filled":
            return email_service.send_grid_order_alert(user.email, user_name, alert_data)
        elif alert_type == "price_boundary":
            return email_service.send_boundary_alert(user.email, user_name, alert_data)
        elif alert_type == "profit_target":
            return email_service.send_profit_alert(user.email, user_name, alert_data)
        elif alert_type == "risk_warning":
            return email_service.send_risk_alert(user.email, user_name, alert_data)
        elif alert_type == "buy_level":
            return email_service.send_buy_level_alert(user.email, user_name, alert_data)
        elif alert_type == "sell_level":
            return email_service.send_sell_level_alert(user.email, user_name, alert_data)
        else:
            logger.warning(f"Unknown alert type: {alert_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending alert to user {user_id}: {e}")
        return False

# Example usage and testing
def test_email_alerts():
    """Test email alert system with sample data"""
    print("📧 TESTING EMAIL ALERT SYSTEM")
    print("=" * 50)
    
    # Sample alert data for 600298.SS grid
    sample_alerts = {
        "grid_order_filled": {
            "symbol": "600298.SS",
            "order_type": "buy",
            "price": 38.53,
            "quantity": 2000,
            "profit": 220.00,
            "grid_name": "600298.SS Conservative Grid",
            "portfolio_name": "Yang's Investment Portfolio",
            "portfolio_id": "8a4a6edd-200d-4d65-8041-b76de959cd45",
            "grid_id": "9d26f827-4605-4cce-ac42-8dbcf173433d"
        },
        "profit_target": {
            "symbol": "600298.SS",
            "total_profit": 8500.00,
            "profit_percentage": 8.5,
            "investment_amount": 100000,
            "duration_days": 15,
            "grid_name": "600298.SS Conservative Grid",
            "grid_id": "9d26f827-4605-4cce-ac42-8dbcf173433d"
        },
        "price_boundary": {
            "symbol": "600298.SS",
            "current_price": 36.45,
            "boundary_price": 36.32,
            "boundary_type": "approaching lower",
            "grid_name": "600298.SS Conservative Grid",
            "grid_id": "9d26f827-4605-4cce-ac42-8dbcf173433d"
        }
    }
    
    email_service = EmailAlertService()
    
    if email_service.is_configured:
        print("✅ Email service configured")
        print("📧 Test emails would be sent for:")
        for alert_type in sample_alerts.keys():
            print(f"  - {alert_type.replace('_', ' ').title()}")
    else:
        print("⚠️ Email service not configured")
        print("📝 To configure, set environment variables:")
        print("   - SMTP_SERVER (default: smtp.gmail.com)")
        print("   - SMTP_PORT (default: 587)")
        print("   - SMTP_USERNAME (your email)")
        print("   - SMTP_PASSWORD (your app password)")
        print("   - FROM_EMAIL (sender email)")
        print("   - FROM_NAME (sender name)")

if __name__ == "__main__":
    test_email_alerts()
