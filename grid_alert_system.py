#!/usr/bin/env python3
"""
Grid Trading Alert System Design
Comprehensive alert system for monitoring grid trading activities
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

class AlertType(Enum):
    """Types of grid trading alerts"""
    GRID_ORDER_FILLED = "grid_order_filled"
    PRICE_BOUNDARY = "price_boundary"
    GRID_REBALANCE = "grid_rebalance"
    PROFIT_TARGET = "profit_target"
    RISK_WARNING = "risk_warning"
    GRID_COMPLETION = "grid_completion"
    VOLUME_ANOMALY = "volume_anomaly"
    VOLATILITY_SPIKE = "volatility_spike"

class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertChannel(Enum):
    """Alert delivery channels"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"
    PUSH = "push"

@dataclass
class GridAlert:
    """Grid trading alert data structure"""
    id: str
    alert_type: AlertType
    priority: AlertPriority
    title: str
    message: str
    symbol: str
    grid_id: str
    portfolio_id: str
    user_id: str
    data: Dict
    channels: List[AlertChannel]
    created_at: datetime
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None

class GridAlertSystem:
    """Comprehensive grid trading alert system"""
    
    def __init__(self):
        self.alerts = []
        self.user_preferences = {}
        self.alert_rules = self._setup_default_rules()
    
    def _setup_default_rules(self) -> Dict:
        """Setup default alert rules for grid trading"""
        return {
            "grid_order_filled": {
                "enabled": True,
                "priority": AlertPriority.MEDIUM,
                "channels": [AlertChannel.IN_APP, AlertChannel.EMAIL],
                "frequency": "immediate"
            },
            "price_boundary": {
                "enabled": True,
                "priority": AlertPriority.HIGH,
                "channels": [AlertChannel.IN_APP, AlertChannel.SMS],
                "frequency": "immediate"
            },
            "profit_target": {
                "enabled": True,
                "priority": AlertPriority.HIGH,
                "channels": [AlertChannel.IN_APP, AlertChannel.EMAIL],
                "min_profit": 1000  # Minimum profit to trigger alert
            },
            "grid_rebalance": {
                "enabled": True,
                "priority": AlertPriority.MEDIUM,
                "channels": [AlertChannel.IN_APP],
                "frequency": "daily"
            },
            "risk_warning": {
                "enabled": True,
                "priority": AlertPriority.CRITICAL,
                "channels": [AlertChannel.IN_APP, AlertChannel.SMS, AlertChannel.EMAIL],
                "frequency": "immediate"
            }
        }
    
    def create_grid_order_alert(self, grid_id: str, symbol: str, order_type: str, 
                               price: float, quantity: int, profit: float) -> GridAlert:
        """Create alert when grid order is filled"""
        return GridAlert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{grid_id[:8]}",
            alert_type=AlertType.GRID_ORDER_FILLED,
            priority=AlertPriority.MEDIUM,
            title=f"Grid Order Filled - {symbol}",
            message=f"🎯 {order_type.upper()} order filled for {symbol}\n"
                   f"💰 Price: ${price:.2f}\n"
                   f"📊 Quantity: {quantity:,} shares\n"
                   f"💵 Profit: ${profit:.2f}",
            symbol=symbol,
            grid_id=grid_id,
            portfolio_id="",  # To be filled by caller
            user_id="",       # To be filled by caller
            data={
                "order_type": order_type,
                "price": price,
                "quantity": quantity,
                "profit": profit,
                "timestamp": datetime.now().isoformat()
            },
            channels=[AlertChannel.IN_APP, AlertChannel.EMAIL],
            created_at=datetime.now()
        )
    
    def create_boundary_alert(self, grid_id: str, symbol: str, current_price: float,
                             boundary_type: str, boundary_price: float) -> GridAlert:
        """Create alert when price hits grid boundaries"""
        priority = AlertPriority.HIGH if boundary_type == "outside" else AlertPriority.MEDIUM
        
        return GridAlert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{grid_id[:8]}",
            alert_type=AlertType.PRICE_BOUNDARY,
            priority=priority,
            title=f"Price Boundary Alert - {symbol}",
            message=f"⚠️ {symbol} price {boundary_type} grid boundary\n"
                   f"💰 Current Price: ${current_price:.2f}\n"
                   f"🚧 Boundary: ${boundary_price:.2f}\n"
                   f"📊 Consider grid adjustment",
            symbol=symbol,
            grid_id=grid_id,
            portfolio_id="",
            user_id="",
            data={
                "current_price": current_price,
                "boundary_price": boundary_price,
                "boundary_type": boundary_type,
                "timestamp": datetime.now().isoformat()
            },
            channels=[AlertChannel.IN_APP, AlertChannel.SMS],
            created_at=datetime.now()
        )
    
    def create_profit_alert(self, grid_id: str, symbol: str, total_profit: float,
                           profit_percentage: float) -> GridAlert:
        """Create alert when grid reaches profit targets"""
        return GridAlert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{grid_id[:8]}",
            alert_type=AlertType.PROFIT_TARGET,
            priority=AlertPriority.HIGH,
            title=f"Profit Target Reached - {symbol}",
            message=f"🎉 Grid strategy profitable!\n"
                   f"💰 Total Profit: ${total_profit:.2f}\n"
                   f"📈 Return: {profit_percentage:.2f}%\n"
                   f"🎯 Consider taking profits or expanding grid",
            symbol=symbol,
            grid_id=grid_id,
            portfolio_id="",
            user_id="",
            data={
                "total_profit": total_profit,
                "profit_percentage": profit_percentage,
                "timestamp": datetime.now().isoformat()
            },
            channels=[AlertChannel.IN_APP, AlertChannel.EMAIL],
            created_at=datetime.now()
        )
    
    def create_rebalance_alert(self, grid_id: str, symbol: str, current_price: float,
                              suggested_lower: float, suggested_upper: float) -> GridAlert:
        """Create alert suggesting grid rebalancing"""
        return GridAlert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{grid_id[:8]}",
            alert_type=AlertType.GRID_REBALANCE,
            priority=AlertPriority.MEDIUM,
            title=f"Grid Rebalance Suggestion - {symbol}",
            message=f"🔄 Consider rebalancing grid for {symbol}\n"
                   f"💰 Current Price: ${current_price:.2f}\n"
                   f"📊 Suggested Range: ${suggested_lower:.2f} - ${suggested_upper:.2f}\n"
                   f"🎯 Optimize for current market conditions",
            symbol=symbol,
            grid_id=grid_id,
            portfolio_id="",
            user_id="",
            data={
                "current_price": current_price,
                "suggested_lower": suggested_lower,
                "suggested_upper": suggested_upper,
                "timestamp": datetime.now().isoformat()
            },
            channels=[AlertChannel.IN_APP],
            created_at=datetime.now()
        )
    
    def create_risk_alert(self, grid_id: str, symbol: str, risk_type: str,
                         current_price: float, risk_data: Dict) -> GridAlert:
        """Create risk warning alerts"""
        return GridAlert(
            id=f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{grid_id[:8]}",
            alert_type=AlertType.RISK_WARNING,
            priority=AlertPriority.CRITICAL,
            title=f"Risk Warning - {symbol}",
            message=f"🚨 {risk_type} detected for {symbol}\n"
                   f"💰 Current Price: ${current_price:.2f}\n"
                   f"⚠️ Risk Level: {risk_data.get('level', 'Unknown')}\n"
                   f"🛡️ Consider risk management actions",
            symbol=symbol,
            grid_id=grid_id,
            portfolio_id="",
            user_id="",
            data={
                "risk_type": risk_type,
                "current_price": current_price,
                "risk_level": risk_data.get('level'),
                "timestamp": datetime.now().isoformat(),
                **risk_data
            },
            channels=[AlertChannel.IN_APP, AlertChannel.SMS, AlertChannel.EMAIL],
            created_at=datetime.now()
        )

# Alert configuration for 600298.SS grid
GRID_600298_ALERT_CONFIG = {
    "symbol": "600298.SS",
    "current_price": 39.63,
    "grid_range": {"lower": 36.32, "upper": 42.94},
    "alert_rules": {
        "order_filled": {
            "enabled": True,
            "min_profit": 100,  # Alert if profit > $100
            "channels": ["in_app", "email"]
        },
        "boundary_breach": {
            "enabled": True,
            "buffer": 0.5,  # Alert if price within $0.50 of boundary
            "channels": ["in_app", "sms"]
        },
        "profit_targets": [
            {"amount": 5000, "channels": ["in_app", "email"]},
            {"amount": 10000, "channels": ["in_app", "sms", "email"]},
            {"amount": 25000, "channels": ["all"]}
        ],
        "rebalance_triggers": {
            "price_outside_range_hours": 24,  # If price outside range for 24h
            "low_activity_days": 7,           # If no trades for 7 days
            "volatility_change": 50           # If volatility changes >50%
        },
        "risk_warnings": {
            "max_drawdown": 15,     # Alert if grid down >15%
            "volume_spike": 300,    # Alert if volume >300% normal
            "price_gap": 5          # Alert if gap >5%
        }
    }
}

def generate_alert_examples():
    """Generate example alerts for 600298.SS grid"""
    alert_system = GridAlertSystem()
    
    examples = [
        alert_system.create_grid_order_alert(
            "9d26f827-4605-4cce-ac42-8dbcf173433d",
            "600298.SS", "buy", 38.53, 2000, 220.00
        ),
        alert_system.create_boundary_alert(
            "9d26f827-4605-4cce-ac42-8dbcf173433d", 
            "600298.SS", 36.20, "approaching", 36.32
        ),
        alert_system.create_profit_alert(
            "9d26f827-4605-4cce-ac42-8dbcf173433d",
            "600298.SS", 8500.00, 8.5
        )
    ]
    
    return examples

if __name__ == "__main__":
    print("🔔 GRID TRADING ALERT SYSTEM DESIGN")
    print("=" * 60)
    
    # Show configuration
    config = GRID_600298_ALERT_CONFIG
    print(f"📊 Symbol: {config['symbol']}")
    print(f"💰 Current Price: ${config['current_price']:.2f}")
    print(f"📈 Grid Range: ${config['grid_range']['lower']:.2f} - ${config['grid_range']['upper']:.2f}")
    
    print("\n🔔 Alert Types Configured:")
    for alert_type, settings in config['alert_rules'].items():
        if isinstance(settings, dict) and settings.get('enabled'):
            print(f"✅ {alert_type.replace('_', ' ').title()}")
    
    # Generate example alerts
    examples = generate_alert_examples()
    print(f"\n📨 Generated {len(examples)} example alerts")
    
    print("\n🎯 Alert system ready for grid trading!")
