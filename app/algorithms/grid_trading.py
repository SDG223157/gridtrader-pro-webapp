import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GridTradingStrategy:
    """Grid Trading Strategy Implementation"""
    
    def __init__(self, symbol: str, upper_price: float, lower_price: float, 
                 grid_count: int, investment_amount: float):
        self.symbol = symbol
        self.upper_price = float(upper_price)
        self.lower_price = float(lower_price)
        self.grid_count = grid_count
        self.investment_amount = float(investment_amount)
        
        # Calculate grid spacing
        self.price_range = self.upper_price - self.lower_price
        self.grid_spacing = self.price_range / (self.grid_count - 1)
        
        # Calculate quantity per grid
        self.quantity_per_grid = self.investment_amount / (self.grid_count * self.upper_price)
        
        logger.info(f"Grid strategy initialized for {symbol}: {grid_count} grids, "
                   f"${lower_price:.2f}-${upper_price:.2f}, spacing: ${self.grid_spacing:.4f}")
    
    def generate_grid_levels(self) -> List[Dict]:
        """Generate all grid levels with buy/sell prices"""
        grid_levels = []
        
        for i in range(self.grid_count):
            price = self.lower_price + (i * self.grid_spacing)
            
            # Buy orders are placed below current grid level
            # Sell orders are placed above current grid level
            buy_price = round(price - (self.grid_spacing / 2), 4) if i > 0 else None
            sell_price = round(price + (self.grid_spacing / 2), 4) if i < self.grid_count - 1 else None
            
            grid_level = {
                'level': i + 1,
                'grid_price': round(price, 4),
                'buy_price': buy_price,
                'sell_price': sell_price,
                'quantity': round(self.quantity_per_grid, 6),
                'status': 'active'
            }
            
            grid_levels.append(grid_level)
        
        return grid_levels
    
    def calculate_initial_orders(self, current_price: float) -> List[Dict]:
        """Calculate initial orders based on current price"""
        orders = []
        grid_levels = self.generate_grid_levels()
        
        for level in grid_levels:
            # Place buy orders below current price
            if level['buy_price'] and level['buy_price'] < current_price:
                orders.append({
                    'type': 'buy',
                    'price': level['buy_price'],
                    'quantity': level['quantity'],
                    'level': level['level'],
                    'status': 'pending'
                })
            
            # Place sell orders above current price (if we have inventory)
            if level['sell_price'] and level['sell_price'] > current_price:
                orders.append({
                    'type': 'sell',
                    'price': level['sell_price'],
                    'quantity': level['quantity'],
                    'level': level['level'],
                    'status': 'pending'
                })
        
        logger.info(f"Generated {len(orders)} initial orders for {self.symbol}")
        return orders
    
    def should_place_order(self, current_price: float, order: Dict) -> bool:
        """Determine if an order should be placed"""
        if order['type'] == 'buy':
            return current_price <= order['price']
        elif order['type'] == 'sell':
            return current_price >= order['price']
        return False
    
    def calculate_profit_per_cycle(self) -> float:
        """Calculate expected profit per complete buy-sell cycle"""
        # Profit per cycle = sell_price - buy_price - fees
        profit_per_cycle = self.grid_spacing * self.quantity_per_grid
        return round(profit_per_cycle, 4)
    
    def get_strategy_metrics(self) -> Dict:
        """Get strategy performance metrics"""
        return {
            'symbol': self.symbol,
            'upper_price': self.upper_price,
            'lower_price': self.lower_price,
            'grid_count': self.grid_count,
            'grid_spacing': round(self.grid_spacing, 4),
            'investment_amount': self.investment_amount,
            'quantity_per_grid': round(self.quantity_per_grid, 6),
            'expected_profit_per_cycle': self.calculate_profit_per_cycle(),
            'price_range_percent': round((self.price_range / self.lower_price) * 100, 2)
        }
    
    def rebalance_grid(self, current_price: float, filled_orders: List[Dict]) -> List[Dict]:
        """Rebalance grid after orders are filled"""
        new_orders = []
        
        for order in filled_orders:
            level = order['level']
            
            if order['type'] == 'buy':
                # After buy order fills, place corresponding sell order
                sell_price = order['price'] + self.grid_spacing
                if sell_price <= self.upper_price:
                    new_orders.append({
                        'type': 'sell',
                        'price': round(sell_price, 4),
                        'quantity': order['quantity'],
                        'level': level,
                        'status': 'pending'
                    })
            
            elif order['type'] == 'sell':
                # After sell order fills, place corresponding buy order
                buy_price = order['price'] - self.grid_spacing
                if buy_price >= self.lower_price:
                    new_orders.append({
                        'type': 'buy',
                        'price': round(buy_price, 4),
                        'quantity': order['quantity'],
                        'level': level,
                        'status': 'pending'
                    })
        
        logger.info(f"Rebalanced grid: generated {len(new_orders)} new orders")
        return new_orders

class DynamicGridStrategy(GridTradingStrategy):
    """Dynamic Grid Strategy that adjusts to market volatility"""
    
    def __init__(self, symbol: str, center_price: float, volatility: float,
                 grid_count: int, investment_amount: float, volatility_multiplier: float = 2.0):
        
        # Calculate upper and lower bounds based on volatility
        price_deviation = center_price * volatility * volatility_multiplier
        upper_price = center_price + price_deviation
        lower_price = center_price - price_deviation
        
        super().__init__(symbol, upper_price, lower_price, grid_count, investment_amount)
        
        self.center_price = center_price
        self.volatility = volatility
        self.volatility_multiplier = volatility_multiplier
        
        logger.info(f"Dynamic grid initialized: center=${center_price:.2f}, "
                   f"volatility={volatility:.2%}, bounds=${lower_price:.2f}-${upper_price:.2f}")
    
    def adjust_grid_bounds(self, new_center_price: float, new_volatility: float):
        """Adjust grid bounds based on new market conditions"""
        old_upper, old_lower = self.upper_price, self.lower_price
        
        # Calculate new bounds
        price_deviation = new_center_price * new_volatility * self.volatility_multiplier
        self.upper_price = new_center_price + price_deviation
        self.lower_price = new_center_price - price_deviation
        
        # Recalculate grid parameters
        self.center_price = new_center_price
        self.volatility = new_volatility
        self.price_range = self.upper_price - self.lower_price
        self.grid_spacing = self.price_range / (self.grid_count - 1)
        self.quantity_per_grid = self.investment_amount / (self.grid_count * self.upper_price)
        
        logger.info(f"Grid bounds adjusted: ${old_lower:.2f}-${old_upper:.2f} -> "
                   f"${self.lower_price:.2f}-${self.upper_price:.2f}")
    
    def should_rebalance_bounds(self, current_price: float, price_history: List[float],
                               threshold: float = 0.8) -> bool:
        """Determine if grid bounds should be rebalanced"""
        # Check if price is approaching bounds
        upper_distance = (self.upper_price - current_price) / self.price_range
        lower_distance = (current_price - self.lower_price) / self.price_range
        
        # Rebalance if price is too close to either bound
        if upper_distance < (1 - threshold) or lower_distance < (1 - threshold):
            return True
        
        # Calculate recent volatility and compare with initial volatility
        if len(price_history) >= 20:
            recent_returns = np.diff(np.log(price_history[-20:]))
            recent_volatility = np.std(recent_returns) * np.sqrt(252)  # Annualized
            
            # Rebalance if volatility has changed significantly
            if abs(recent_volatility - self.volatility) / self.volatility > 0.5:
                return True
        
        return False

class MartingaleGridStrategy(GridTradingStrategy):
    """Martingale Grid Strategy - increases position size after losses"""
    
    def __init__(self, symbol: str, upper_price: float, lower_price: float,
                 grid_count: int, investment_amount: float, martingale_multiplier: float = 1.5):
        
        super().__init__(symbol, upper_price, lower_price, grid_count, investment_amount)
        self.martingale_multiplier = martingale_multiplier
        self.loss_streak = 0
        self.base_quantity = self.quantity_per_grid
        
        logger.info(f"Martingale grid initialized with multiplier: {martingale_multiplier}")
    
    def calculate_martingale_quantity(self, loss_streak: int) -> float:
        """Calculate quantity based on loss streak"""
        multiplier = self.martingale_multiplier ** loss_streak
        return round(self.base_quantity * multiplier, 6)
    
    def update_loss_streak(self, trade_result: str):
        """Update loss streak based on trade result"""
        if trade_result == 'loss':
            self.loss_streak += 1
        elif trade_result == 'profit':
            self.loss_streak = 0  # Reset on profit
        
        logger.info(f"Loss streak updated: {self.loss_streak}")
    
    def generate_adaptive_orders(self, current_price: float) -> List[Dict]:
        """Generate orders with adaptive quantities"""
        orders = self.calculate_initial_orders(current_price)
        
        # Adjust quantities based on loss streak
        for order in orders:
            order['quantity'] = self.calculate_martingale_quantity(self.loss_streak)
        
        return orders

class GridBacktester:
    """Backtest grid trading strategies"""
    
    def __init__(self, strategy: GridTradingStrategy, price_data: pd.DataFrame):
        self.strategy = strategy
        self.price_data = price_data
        self.trades = []
        self.portfolio_value = []
        self.cash = strategy.investment_amount
        self.position = 0.0
        
    def run_backtest(self) -> Dict:
        """Run backtest simulation"""
        logger.info(f"Starting backtest for {self.strategy.symbol}")
        
        # Initialize orders
        initial_price = float(self.price_data['Close'].iloc[0])
        active_orders = self.strategy.calculate_initial_orders(initial_price)
        
        for i, (date, row) in enumerate(self.price_data.iterrows()):
            current_price = float(row['Close'])
            
            # Check for filled orders
            filled_orders = []
            remaining_orders = []
            
            for order in active_orders:
                if self.strategy.should_place_order(current_price, order):
                    # Execute order
                    self.execute_order(order, current_price, date)
                    filled_orders.append(order)
                else:
                    remaining_orders.append(order)
            
            # Generate new orders from filled ones
            new_orders = self.strategy.rebalance_grid(current_price, filled_orders)
            active_orders = remaining_orders + new_orders
            
            # Calculate portfolio value
            portfolio_value = self.cash + (self.position * current_price)
            self.portfolio_value.append({
                'date': date,
                'price': current_price,
                'cash': self.cash,
                'position': self.position,
                'portfolio_value': portfolio_value
            })
        
        return self.calculate_performance_metrics()
    
    def execute_order(self, order: Dict, execution_price: float, date):
        """Execute an order"""
        quantity = order['quantity']
        cost = quantity * execution_price
        
        if order['type'] == 'buy':
            if self.cash >= cost:
                self.cash -= cost
                self.position += quantity
                
                trade = {
                    'date': date,
                    'type': 'buy',
                    'quantity': quantity,
                    'price': execution_price,
                    'cost': cost,
                    'level': order['level']
                }
                self.trades.append(trade)
                
        elif order['type'] == 'sell':
            if self.position >= quantity:
                self.cash += cost
                self.position -= quantity
                
                trade = {
                    'date': date,
                    'type': 'sell',
                    'quantity': quantity,
                    'price': execution_price,
                    'proceeds': cost,
                    'level': order['level']
                }
                self.trades.append(trade)
    
    def calculate_performance_metrics(self) -> Dict:
        """Calculate backtest performance metrics"""
        if not self.portfolio_value:
            return {}
        
        initial_value = self.strategy.investment_amount
        final_value = self.portfolio_value[-1]['portfolio_value']
        
        # Calculate returns
        total_return = (final_value - initial_value) / initial_value
        
        # Calculate daily returns
        values = [pv['portfolio_value'] for pv in self.portfolio_value]
        daily_returns = np.diff(values) / values[:-1]
        
        # Risk metrics
        volatility = np.std(daily_returns) * np.sqrt(252)  # Annualized
        sharpe_ratio = (total_return / volatility) if volatility > 0 else 0
        
        # Drawdown analysis
        cumulative_values = np.array(values)
        running_max = np.maximum.accumulate(cumulative_values)
        drawdowns = (cumulative_values - running_max) / running_max
        max_drawdown = np.min(drawdowns)
        
        # Trade statistics
        total_trades = len(self.trades)
        profitable_trades = sum(1 for trade in self.trades if trade['type'] == 'sell' and 
                              trade['proceeds'] > trade['quantity'] * self.get_avg_buy_price())
        
        return {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return': round(total_return * 100, 2),
            'volatility': round(volatility * 100, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown * 100, 2),
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'win_rate': round(profitable_trades / max(total_trades, 1) * 100, 2),
            'trades': self.trades[-10:],  # Last 10 trades
            'portfolio_values': self.portfolio_value[-30:]  # Last 30 days
        }
    
    def get_avg_buy_price(self) -> float:
        """Calculate average buy price from trades"""
        buy_trades = [t for t in self.trades if t['type'] == 'buy']
        if not buy_trades:
            return 0
        
        total_cost = sum(t['cost'] for t in buy_trades)
        total_quantity = sum(t['quantity'] for t in buy_trades)
        
        return total_cost / total_quantity if total_quantity > 0 else 0