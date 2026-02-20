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

class AdaptiveGridStrategy:
    """
    Adaptive Dual-Zone Grid Strategy with volatility-based optimization.
    A-Zone: Active trading grid with linear position sizing.
    B-Zone: Defense zone (hold, no new buys).
    Includes stop-loss and overflow lines.
    """

    def __init__(self, symbol: str, investment_amount: float,
                 price_data: pd.DataFrame, lot_size: int = 100):
        self.symbol = symbol
        self.investment_amount = float(investment_amount)
        self.lot_size = lot_size
        self.price_data = price_data

        closes = price_data['close'].values.astype(float)
        highs = price_data['high'].values.astype(float)
        lows = price_data['low'].values.astype(float)
        self.current_price = float(closes[-1])

        returns = np.diff(np.log(closes))
        self.annual_vol = float(np.std(returns) * np.sqrt(245) * 100)

        tr_list = []
        for i in range(1, len(closes)):
            tr = max(highs[i] - lows[i],
                     abs(highs[i] - closes[i - 1]),
                     abs(lows[i] - closes[i - 1]))
            tr_list.append(tr)
        atr14 = pd.Series(tr_list).rolling(14).mean().dropna().values
        atr14_pct = atr14 / closes[14:14 + len(atr14)] * 100
        self.atr14_median_pct = float(np.median(atr14_pct))

        self.p5 = float(np.percentile(closes, 5))
        self.p10 = float(np.percentile(closes, 10))
        self.p20 = float(np.percentile(closes, 20))
        self.p50 = float(np.percentile(closes, 50))
        self.p80 = float(np.percentile(closes, 80))
        self.p90 = float(np.percentile(closes, 90))
        self.p95 = float(np.percentile(closes, 95))
        self.close_high = float(np.max(closes))
        self.close_low = float(np.min(closes))

        vol_20d = pd.Series(returns).rolling(20).std().dropna().values * np.sqrt(245) * 100
        self.vol_20d_current = float(vol_20d[-1]) if len(vol_20d) > 0 else self.annual_vol

        self._design()
        self.trend = self._analyze_trend()
        logger.info(f"AdaptiveGrid for {symbol}: A[{self.a_lower:.2f}-{self.a_upper:.2f}] "
                     f"step={self.step:.4f} grids={self.n_grids_a} "
                     f"trend={self.trend['label']}({self.trend['score']})")

    def _analyze_trend(self) -> Dict:
        """
        Score the current trend using MA, RSI, momentum and percentile position.
        Returns trend score (0-100), label, key signals, and recommended
        initial position percentage for generate_orders().
        """
        closes = self.price_data['close'].values.astype(float)
        price = self.current_price
        signals = {}
        score = 0

        # ── Moving averages ───────────────────────────────────────────────────
        ma20 = float(pd.Series(closes).rolling(20).mean().iloc[-1]) if len(closes) >= 20 else price
        ma50 = float(pd.Series(closes).rolling(50).mean().iloc[-1]) if len(closes) >= 50 else price
        ma200 = float(pd.Series(closes).rolling(200).mean().iloc[-1]) if len(closes) >= 200 else None

        above_ma20 = price > ma20
        above_ma50 = price > ma50
        golden_cross = ma20 > ma50  # short MA above long MA

        signals["price_vs_ma20"] = f"${price:.2f} {'>' if above_ma20 else '<'} MA20(${ma20:.2f})"
        signals["price_vs_ma50"] = f"${price:.2f} {'>' if above_ma50 else '<'} MA50(${ma50:.2f})"
        signals["ma20_vs_ma50"] = "Golden Cross ✓" if golden_cross else "Death Cross ✗"

        if above_ma20:  score += 18
        if above_ma50:  score += 18
        if golden_cross: score += 14
        if ma200 is not None:
            above_ma200 = price > ma200
            signals["price_vs_ma200"] = f"${price:.2f} {'>' if above_ma200 else '<'} MA200(${ma200:.2f})"
            if above_ma200: score += 10

        # ── RSI (14-day) ──────────────────────────────────────────────────────
        rsi_n = 14
        if len(closes) >= rsi_n + 1:
            deltas = np.diff(closes[-(rsi_n + 1):])
            gains = np.where(deltas > 0, deltas, 0.0)
            losses = np.where(deltas < 0, -deltas, 0.0)
            avg_gain = np.mean(gains)
            avg_loss = np.mean(losses)
            rsi = 100.0 if avg_loss == 0 else 100.0 - 100.0 / (1.0 + avg_gain / avg_loss)
        else:
            rsi = 50.0
        signals["rsi14"] = f"{rsi:.1f}"
        if 50 <= rsi <= 70:   score += 20   # healthy uptrend
        elif rsi > 70:         score += 12   # strong but possibly overbought
        elif 40 <= rsi < 50:   score += 8
        elif 30 <= rsi < 40:   score += 3

        # ── 20-day momentum ───────────────────────────────────────────────────
        if len(closes) >= 21:
            mom20 = (price / float(closes[-21]) - 1) * 100
        else:
            mom20 = 0.0
        signals["momentum_20d"] = f"{mom20:+.1f}%"
        if mom20 > 5:          score += 20
        elif mom20 > 1:        score += 14
        elif mom20 >= -1:      score += 8
        elif mom20 >= -5:      score += 3

        # ── Percentile position in 250-day range ─────────────────────────────
        price_range = self.close_high - self.close_low
        pct_in_range = (price - self.close_low) / price_range if price_range > 0 else 0.5
        signals["pct_in_range"] = f"{pct_in_range * 100:.0f}th percentile (250-day)"
        if pct_in_range >= 0.75:   score += 10
        elif pct_in_range >= 0.50: score += 7
        elif pct_in_range >= 0.25: score += 3

        # Normalize to 0-100 (max raw = 110 with MA200, 100 without)
        max_raw = 100 if ma200 is None else 110
        score = min(100, int(round(score / max_raw * 100)))

        # ── Trend label ───────────────────────────────────────────────────────
        if score >= 72:
            label, emoji, color = "Strong Uptrend",  "🚀", "green"
        elif score >= 55:
            label, emoji, color = "Uptrend",         "📈", "green"
        elif score >= 40:
            label, emoji, color = "Sideways",        "↔️",  "gray"
        elif score >= 25:
            label, emoji, color = "Downtrend",       "📉", "red"
        else:
            label, emoji, color = "Strong Downtrend","🔻", "red"

        # ── Recommended initial position % ───────────────────────────────────
        # Uptrend → hold more shares (higher initial %).
        # Downtrend → hold fewer, keep cash to buy dips.
        if score >= 72:    init_pct = 60
        elif score >= 60:  init_pct = 50
        elif score >= 50:  init_pct = 42
        elif score >= 40:  init_pct = 35
        elif score >= 28:  init_pct = 25
        elif score >= 15:  init_pct = 18
        else:              init_pct = 12

        return {
            "score": score,
            "label": label,
            "emoji": emoji,
            "color": color,
            "initial_position_pct": init_pct,
            "signals": signals,
            "ma20": round(ma20, 4),
            "ma50": round(ma50, 4),
            "ma200": round(ma200, 4) if ma200 is not None else None,
            "rsi14": round(rsi, 1),
            "momentum_20d": round(mom20, 2),
        }

    def _design(self):
        price = self.current_price

        step_pct_target = max(1.0, min(2.0, self.atr14_median_pct * 1.1))
        step_raw = price * step_pct_target / 100
        tick = 0.01
        step = round(round(step_raw / tick) * tick, 4)
        if step < tick:
            step = tick

        range_factor = self.annual_vol / 100 * 0.8
        half_range = price * range_factor / 2
        raw_upper = price + half_range * 1.2
        raw_lower = price - half_range * 0.8

        a_upper = round(min(raw_upper, self.p80 * 1.02), 4)
        a_lower = round(max(raw_lower, self.p20 * 0.98), 4)

        if a_upper <= price:
            a_upper = round(price * 1.05, 4)
        if a_lower >= price:
            a_lower = round(price * 0.95, 4)
        if a_upper - a_lower < step * 3:
            a_upper = round(price + step * 3, 4)
            a_lower = round(price - step * 2, 4)

        n_a = max(3, min(10, int(round((a_upper - a_lower) / step))))
        step = round((a_upper - a_lower) / n_a, 4)

        n_b = 2
        b_lower = round(a_lower - step * n_b, 4)
        stop_loss = round(b_lower - step * 1.5, 4)
        overflow = round(a_upper + step, 4)

        max_shares = int(self.investment_amount / a_lower)
        if self.lot_size > 1:
            max_shares = (max_shares // self.lot_size) * self.lot_size
        shares_per_grid = int(max_shares / n_a)
        if self.lot_size > 1:
            shares_per_grid = max(self.lot_size, (shares_per_grid // self.lot_size) * self.lot_size)
        max_shares = shares_per_grid * n_a

        self.a_upper = a_upper
        self.a_lower = a_lower
        self.b_lower = b_lower
        self.stop_loss = stop_loss
        self.overflow = overflow
        self.step = step
        self.step_pct = step / price * 100
        self.n_grids_a = n_a
        self.n_grids_b = n_b
        self.max_shares = max_shares
        self.shares_per_grid = shares_per_grid

        self.grid_lines = []
        self.target_positions = []
        self.zone_labels = []

        self.grid_lines.append(overflow)
        self.target_positions.append(0.0)
        self.zone_labels.append("overflow")

        for i in range(n_a + 1):
            p = round(a_upper - i * step, 4)
            pos = i / n_a
            self.grid_lines.append(p)
            self.target_positions.append(pos)
            self.zone_labels.append("a_zone")

        for i in range(1, n_b + 1):
            p = round(a_lower - i * step, 4)
            self.grid_lines.append(p)
            self.target_positions.append(1.0)
            self.zone_labels.append("b_zone")

        self.grid_lines.append(stop_loss)
        self.target_positions.append(-1.0)
        self.zone_labels.append("stop_loss")

    def get_target_position(self, price: float) -> float:
        if price >= self.overflow:
            return 0.0
        if price <= self.stop_loss:
            return -1.0
        for i in range(len(self.grid_lines) - 1):
            if self.grid_lines[i] >= price > self.grid_lines[i + 1]:
                return self.target_positions[i]
        if price > self.grid_lines[0]:
            return 0.0
        return 1.0

    def generate_grid_levels(self) -> List[Dict]:
        levels = []
        for i in range(len(self.grid_lines)):
            p = self.grid_lines[i]
            pos = self.target_positions[i]
            zone = self.zone_labels[i]
            if pos < 0:
                shares = 0
                action = "stop_loss"
            elif pos == 0:
                shares = 0
                action = "sell_all"
            else:
                shares = int(pos * self.max_shares)
                if self.lot_size > 1:
                    shares = (shares // self.lot_size) * self.lot_size
                action = "hold"

            levels.append({
                "level": i,
                "price": round(p, 4),
                "target_position_pct": round(pos * 100, 1) if pos >= 0 else 0,
                "target_shares": shares,
                "zone": zone,
                "action": action,
            })
        return levels

    def generate_orders(self) -> List[Dict]:
        # Use trend-adjusted initial position instead of the pure grid-math target.
        # Clamp to the range implied by the grid so we never buy above overflow
        # or below stop-loss territory.
        grid_target = self.get_target_position(self.current_price)
        if grid_target < 0:
            grid_target = 0.0
        trend_target = self.trend["initial_position_pct"] / 100.0
        # Stay within [grid_target * 0.5, 1.0] so we respect the zone logic
        target = max(min(trend_target, 1.0), 0.0)

        init_shares = int(target * self.max_shares)
        if self.lot_size > 1:
            init_shares = (init_shares // self.lot_size) * self.lot_size
        max_affordable = int(self.investment_amount * 0.99 / self.current_price)
        if self.lot_size > 1:
            max_affordable = (max_affordable // self.lot_size) * self.lot_size
        init_shares = min(init_shares, max_affordable)

        orders = []
        if init_shares > 0:
            orders.append({
                "type": "buy", "price": round(self.current_price, 4),
                "quantity": init_shares, "action": "initial_build",
                "target_pct": round(target * 100, 1),
            })

        # Sell orders: iterate ASCENDING (lowest price first) so each grid level
        # only sells the incremental diff, not everything in one hit.
        # grid_lines is stored descending (overflow first), so we reverse-sort.
        above = sorted(
            [(p, pos, zone) for p, pos, zone
             in zip(self.grid_lines, self.target_positions, self.zone_labels)
             if p > self.current_price and zone in ("a_zone", "overflow")],
            key=lambda x: x[0]  # ascending price
        )
        running_sell = init_shares
        for p, pos, zone in above:
            tgt = max(0, int(pos * self.max_shares))
            if self.lot_size > 1:
                tgt = (tgt // self.lot_size) * self.lot_size
            diff = running_sell - tgt
            if diff > 0:
                orders.append({
                    "type": "sell", "price": round(p, 4),
                    "quantity": diff, "action": "grid_sell",
                    "target_pct": round(pos * 100, 1),
                })
                running_sell = tgt

        # Buy orders: iterate DESCENDING (highest price first = closest to current price)
        # so each grid level only buys the incremental diff.
        below = sorted(
            [(p, pos, zone) for p, pos, zone
             in zip(self.grid_lines, self.target_positions, self.zone_labels)
             if p < self.current_price and zone == "a_zone" and pos > target],
            key=lambda x: -x[0]  # descending price
        )
        running_buy = init_shares
        for p, pos, zone in below:
            tgt = int(pos * self.max_shares)
            if self.lot_size > 1:
                tgt = (tgt // self.lot_size) * self.lot_size
            diff = tgt - running_buy
            if diff > 0:
                orders.append({
                    "type": "buy", "price": round(p, 4),
                    "quantity": diff, "action": "grid_buy",
                    "target_pct": round(pos * 100, 1),
                })
                running_buy = tgt

        return orders

    def get_strategy_config(self) -> Dict:
        return {
            "strategy_type": "adaptive_dual_zone",
            "symbol": self.symbol,
            "current_price": self.current_price,
            "annual_volatility": round(self.annual_vol, 2),
            "atr14_median_pct": round(self.atr14_median_pct, 2),
            "vol_20d_current": round(self.vol_20d_current, 2),
            "a_zone_upper": self.a_upper,
            "a_zone_lower": self.a_lower,
            "b_zone_lower": self.b_lower,
            "stop_loss": self.stop_loss,
            "overflow_line": self.overflow,
            "step": self.step,
            "step_pct": round(self.step_pct, 2),
            "n_grids_a": self.n_grids_a,
            "n_grids_b": self.n_grids_b,
            "max_shares": self.max_shares,
            "shares_per_grid": self.shares_per_grid,
            "lot_size": self.lot_size,
            "investment_amount": self.investment_amount,
            "percentiles": {
                "p5": self.p5, "p20": self.p20, "p50": self.p50,
                "p80": self.p80, "p95": self.p95,
            },
            "price_range": {
                "high": self.close_high, "low": self.close_low,
                "amplitude_pct": round((self.close_high / self.close_low - 1) * 100, 1),
            },
            "trend": self.trend,
            "grid_levels": self.generate_grid_levels(),
            "orders": self.generate_orders(),
            "created_at": datetime.now().isoformat(),
        }

    def get_backtest_summary(self) -> Dict:
        """Quick backtest on the historical data used for design."""
        closes = self.price_data['close'].values.astype(float)
        cash = self.investment_amount
        shares = 0
        n_trades = 0

        for price in closes:
            target = self.get_target_position(price)
            if target < 0:
                if shares > 0:
                    cash += shares * price * 0.999
                    shares = 0
                    n_trades += 1
            elif target >= 0:
                tgt_shares = int(target * self.max_shares)
                if self.lot_size > 1:
                    tgt_shares = (tgt_shares // self.lot_size) * self.lot_size
                diff = tgt_shares - shares
                if abs(diff) >= (self.lot_size if self.lot_size > 1 else 1):
                    if diff > 0:
                        cost = diff * price * 1.0005
                        if cash >= cost:
                            cash -= cost
                            shares += diff
                            n_trades += 1
                    elif diff < 0:
                        cash += abs(diff) * price * 0.999
                        shares += diff
                        n_trades += 1

        final_equity = cash + shares * closes[-1]
        bnh_shares = int(self.investment_amount / closes[0])
        bnh_equity = (self.investment_amount - bnh_shares * closes[0]) + bnh_shares * closes[-1]

        return {
            "grid_return_pct": round((final_equity / self.investment_amount - 1) * 100, 2),
            "bnh_return_pct": round((bnh_equity / self.investment_amount - 1) * 100, 2),
            "n_trades": n_trades,
            "final_equity": round(final_equity, 2),
        }


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