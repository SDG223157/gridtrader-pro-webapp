"""
Systematic Trading & Rebalancing Framework
Based on momentum-mean reversion strategy with sector rotation
"""
import logging
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import yfinance as yf
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    LEVEL_1 = "daily_monitoring"      # Daily monitoring
    LEVEL_2 = "immediate_action"      # Immediate action required
    LEVEL_3 = "strategy_review"       # Strategy review needed

class MarketRegime(Enum):
    BULL_MOMENTUM = "bull_momentum"
    BEAR_MOMENTUM = "bear_momentum"
    SIDEWAYS_MEAN_REVERSION = "sideways_mean_reversion"
    HIGH_VOLATILITY = "high_volatility"

@dataclass
class SectorScore:
    sector: str
    symbol: str
    momentum_score: float      # 0-1 scale
    mean_reversion_score: float # 0-1 scale
    fundamental_score: float   # 0-1 scale
    technical_score: float     # 0-1 scale
    sentiment_score: float     # 0-1 scale
    macro_score: float         # 0-1 scale
    conviction_score: float    # Final 0-2 scale
    recommended_weight: float  # Position size %
    risk_adjustment: float     # 0.8-1.2 volatility adjustment

@dataclass
class PortfolioAlert:
    level: AlertLevel
    title: str
    message: str
    symbol: Optional[str]
    current_value: float
    target_value: float
    deviation_pct: float
    action_required: str
    created_at: datetime

class SystematicTradingEngine:
    """
    Advanced systematic trading engine implementing momentum-mean reversion
    with sector rotation, risk management, and automated rebalancing
    """
    
    def __init__(self):
        self.sector_etfs = {
            # Technology & Growth
            'XLK': 'Technology Select Sector SPDR',
            'QQQ': 'Invesco QQQ Trust',
            'ARKK': 'ARK Innovation ETF',
            'SOXX': 'iShares Semiconductor ETF',
            
            # Financial Services
            'XLF': 'Financial Select Sector SPDR',
            'KRE': 'SPDR S&P Regional Banking',
            'KIE': 'SPDR S&P Insurance',
            
            # Healthcare & Biotech
            'XLV': 'Health Care Select Sector SPDR',
            'IBB': 'iShares Biotechnology ETF',
            'XBI': 'SPDR S&P Biotech ETF',
            
            # Energy & Materials
            'XLE': 'Energy Select Sector SPDR',
            'XLB': 'Materials Select Sector SPDR',
            'XME': 'SPDR S&P Metals & Mining',
            
            # Consumer & Retail
            'XLY': 'Consumer Discretionary SPDR',
            'XLP': 'Consumer Staples SPDR',
            'XRT': 'SPDR S&P Retail ETF',
            
            # Infrastructure & REITs
            'XLI': 'Industrial Select Sector SPDR',
            'XLU': 'Utilities Select Sector SPDR',
            'XLRE': 'Real Estate Select Sector SPDR',
            
            # International & Emerging
            'EFA': 'iShares MSCI EAFE ETF',
            'EEM': 'iShares MSCI Emerging Markets',
            'VEA': 'Vanguard FTSE Developed Markets',
            
            # Fixed Income & Alternatives
            'TLT': 'iShares 20+ Year Treasury Bond',
            'HYG': 'iShares iBoxx High Yield Corporate',
            'GLD': 'SPDR Gold Shares',
            'SLV': 'iShares Silver Trust'
        }
        
        # Risk management parameters
        self.risk_limits = {
            'max_sector_concentration': 0.15,    # 15%
            'max_single_position': 0.05,         # 5%
            'min_cash_buffer': 0.05,             # 5%
            'max_monthly_turnover': 0.25,        # 25%
            'daily_var_limit': 0.02,             # 2%
            'max_drawdown_trigger': 0.15         # 15%
        }
        
        # Performance thresholds
        self.alert_thresholds = {
            'level_1': {
                'position_deviation': 0.07,      # ±7% from target
                'min_cash_pct': 0.03,            # Portfolio cash < 3%
                'daily_loss_limit': 0.015       # Daily loss > 1.5%
            },
            'level_2': {
                'position_deviation': 0.10,      # ±10% from target
                'sector_correlation': 0.8,       # Correlation > 0.8
                'weekly_loss_limit': 0.03        # Weekly loss > 3%
            },
            'level_3': {
                'monthly_underperformance': 0.02, # Monthly underperformance > 2%
                'max_drawdown': 0.10,             # Maximum drawdown > 10%
                'min_win_rate': 0.45              # Win rate < 45% over 3 months
            }
        }
    
    def calculate_sector_scores(self, lookback_days: int = 90) -> List[SectorScore]:
        """
        Calculate comprehensive sector scores for rotation decisions
        Based on momentum, mean reversion, fundamental, technical factors
        """
        sector_scores = []
        
        try:
            # Get market benchmark (S&P 500) for relative performance
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period=f"{lookback_days}d")
            spy_return = (spy_data['Close'].iloc[-1] / spy_data['Close'].iloc[0] - 1) if not spy_data.empty else 0
            
            for symbol, name in self.sector_etfs.items():
                try:
                    score = self._analyze_sector_etf(symbol, name, spy_return, lookback_days)
                    if score:
                        sector_scores.append(score)
                        logger.info(f"📊 {symbol}: Conviction {score.conviction_score:.2f}, Weight {score.recommended_weight:.1%}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error analyzing {symbol}: {e}")
                    continue
            
            # Sort by conviction score (highest first)
            sector_scores.sort(key=lambda x: x.conviction_score, reverse=True)
            
            logger.info(f"✅ Analyzed {len(sector_scores)} sectors for rotation")
            return sector_scores
            
        except Exception as e:
            logger.error(f"❌ Error calculating sector scores: {e}")
            return []
    
    def _analyze_sector_etf(self, symbol: str, name: str, market_return: float, lookback_days: int) -> Optional[SectorScore]:
        """Analyze individual sector ETF for scoring"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get price data
            price_data = ticker.history(period=f"{lookback_days}d")
            if price_data.empty:
                return None
            
            # Get fundamental data
            info = ticker.info
            
            # Calculate momentum score (3-month relative strength)
            sector_return = (price_data['Close'].iloc[-1] / price_data['Close'].iloc[0] - 1)
            relative_strength = sector_return - market_return
            momentum_score = min(1.0, max(0.0, (relative_strength + 0.1) / 0.2))  # Normalize to 0-1
            
            # Calculate mean reversion score (oversold opportunities)
            # Using RSI and price vs moving average
            close_prices = price_data['Close']
            rsi = self._calculate_rsi(close_prices, 14)
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # Price vs 50-day MA
            ma_50 = close_prices.rolling(50).mean()
            price_vs_ma = (close_prices.iloc[-1] / ma_50.iloc[-1] - 1) if not ma_50.empty else 0
            
            # Mean reversion score (higher when oversold)
            rsi_score = (70 - current_rsi) / 40 if current_rsi < 70 else 0  # Higher score when RSI < 30
            ma_score = (-price_vs_ma + 0.05) / 0.1 if price_vs_ma < 0 else 0  # Higher when below MA
            mean_reversion_score = min(1.0, max(0.0, (rsi_score + ma_score) / 2))
            
            # Fundamental score (basic metrics from yfinance)
            pe_ratio = info.get('trailingPE', 0)
            pb_ratio = info.get('priceToBook', 0)
            roe = info.get('returnOnEquity', 0)
            
            fundamental_score = 0.5  # Default neutral
            if pe_ratio > 0 and pe_ratio < 25:  # Reasonable valuation
                fundamental_score += 0.2
            if pb_ratio > 0 and pb_ratio < 3:   # Not overvalued
                fundamental_score += 0.2
            if roe > 0.08:  # ROE > 8%
                fundamental_score += 0.1
            
            # Technical score (volume and price action)
            volume_trend = price_data['Volume'].rolling(20).mean()
            recent_volume = price_data['Volume'].tail(5).mean()
            volume_score = min(1.0, recent_volume / volume_trend.iloc[-1]) if not volume_trend.empty else 0.5
            
            # Price momentum (20-day vs 50-day trend)
            ma_20 = close_prices.rolling(20).mean()
            momentum_signal = (ma_20.iloc[-1] / ma_50.iloc[-1] - 1) if not ma_20.empty and not ma_50.empty else 0
            momentum_technical = min(1.0, max(0.0, (momentum_signal + 0.05) / 0.1))
            
            technical_score = (volume_score + momentum_technical) / 2
            
            # Sentiment and macro scores (simplified for now)
            sentiment_score = 0.5  # Neutral - could be enhanced with sentiment data
            macro_score = 0.5      # Neutral - could be enhanced with economic indicators
            
            # Calculate conviction score (0-2 scale)
            conviction_score = (
                fundamental_score * 0.25 +
                technical_score * 0.25 +
                momentum_score * 0.25 +
                mean_reversion_score * 0.25
            ) * 2  # Scale to 0-2
            
            # Calculate risk adjustment based on volatility
            volatility = close_prices.pct_change().std() * np.sqrt(252)  # Annualized volatility
            risk_adjustment = min(1.2, max(0.8, 1.0 - (volatility - 0.15) / 0.3))
            
            # Calculate recommended weight
            base_weight = 0.025  # 2.5% base allocation
            recommended_weight = base_weight * conviction_score * risk_adjustment
            recommended_weight = min(0.05, max(0.01, recommended_weight))  # Cap between 1-5%
            
            return SectorScore(
                sector=name,
                symbol=symbol,
                momentum_score=momentum_score,
                mean_reversion_score=mean_reversion_score,
                fundamental_score=fundamental_score,
                technical_score=technical_score,
                sentiment_score=sentiment_score,
                macro_score=macro_score,
                conviction_score=conviction_score,
                recommended_weight=recommended_weight,
                risk_adjustment=risk_adjustment
            )
            
        except Exception as e:
            logger.error(f"❌ Error analyzing {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception:
            return pd.Series([50] * len(prices), index=prices.index)
    
    def generate_rebalancing_signals(self, current_positions: Dict[str, float], 
                                   target_weights: Dict[str, float]) -> List[Dict]:
        """
        Generate rebalancing signals based on decision tree logic
        """
        signals = []
        
        try:
            for symbol, current_weight in current_positions.items():
                target_weight = target_weights.get(symbol, 0)
                deviation = abs(current_weight - target_weight)
                deviation_pct = deviation / target_weight if target_weight > 0 else deviation
                
                # Decision tree logic
                action = None
                urgency = None
                
                if deviation_pct > 0.10:  # >10% deviation
                    action = "REBALANCE_IMMEDIATE"
                    urgency = AlertLevel.LEVEL_2
                elif deviation_pct > 0.07:  # >7% deviation
                    action = "REBALANCE_SOON"
                    urgency = AlertLevel.LEVEL_1
                elif deviation_pct > 0.05:  # >5% deviation
                    action = "MONITOR"
                    urgency = AlertLevel.LEVEL_1
                
                if action:
                    signals.append({
                        'symbol': symbol,
                        'current_weight': current_weight,
                        'target_weight': target_weight,
                        'deviation_pct': deviation_pct,
                        'action': action,
                        'urgency': urgency,
                        'recommended_trade': 'BUY' if current_weight < target_weight else 'SELL',
                        'trade_amount': abs(current_weight - target_weight)
                    })
            
            logger.info(f"📊 Generated {len(signals)} rebalancing signals")
            return signals
            
        except Exception as e:
            logger.error(f"❌ Error generating rebalancing signals: {e}")
            return []
    
    def check_risk_limits(self, portfolio_data: Dict) -> List[PortfolioAlert]:
        """
        Check portfolio against risk management limits
        """
        alerts = []
        
        try:
            total_value = portfolio_data.get('total_value', 0)
            cash_balance = portfolio_data.get('cash_balance', 0)
            positions = portfolio_data.get('positions', {})
            
            # Check cash buffer
            cash_pct = cash_balance / total_value if total_value > 0 else 0
            if cash_pct < self.risk_limits['min_cash_buffer']:
                alerts.append(PortfolioAlert(
                    level=AlertLevel.LEVEL_1,
                    title="Low Cash Buffer",
                    message=f"Cash balance {cash_pct:.1%} below minimum {self.risk_limits['min_cash_buffer']:.1%}",
                    symbol=None,
                    current_value=cash_pct,
                    target_value=self.risk_limits['min_cash_buffer'],
                    deviation_pct=(self.risk_limits['min_cash_buffer'] - cash_pct) / self.risk_limits['min_cash_buffer'],
                    action_required="Consider reducing positions to increase cash buffer",
                    created_at=datetime.now()
                ))
            
            # Check position concentration
            for symbol, position_value in positions.items():
                position_pct = position_value / total_value if total_value > 0 else 0
                
                if position_pct > self.risk_limits['max_single_position']:
                    alerts.append(PortfolioAlert(
                        level=AlertLevel.LEVEL_2,
                        title="Position Concentration Risk",
                        message=f"{symbol} position {position_pct:.1%} exceeds limit {self.risk_limits['max_single_position']:.1%}",
                        symbol=symbol,
                        current_value=position_pct,
                        target_value=self.risk_limits['max_single_position'],
                        deviation_pct=(position_pct - self.risk_limits['max_single_position']) / self.risk_limits['max_single_position'],
                        action_required=f"Consider reducing {symbol} position",
                        created_at=datetime.now()
                    ))
            
            logger.info(f"🛡️ Risk check complete: {len(alerts)} alerts generated")
            return alerts
            
        except Exception as e:
            logger.error(f"❌ Error checking risk limits: {e}")
            return []
    
    def calculate_performance_metrics(self, portfolio_history: List[Dict]) -> Dict:
        """
        Calculate comprehensive performance metrics
        """
        try:
            if len(portfolio_history) < 2:
                return {}
            
            # Convert to pandas for easier calculation
            df = pd.DataFrame(portfolio_history)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            
            # Calculate returns
            df['daily_return'] = df['total_value'].pct_change()
            df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
            
            # Performance metrics
            total_return = df['cumulative_return'].iloc[-1]
            annualized_return = (1 + total_return) ** (252 / len(df)) - 1
            
            # Risk metrics
            daily_vol = df['daily_return'].std()
            annualized_vol = daily_vol * np.sqrt(252)
            sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0
            
            # Drawdown analysis
            rolling_max = df['total_value'].expanding().max()
            drawdown = (df['total_value'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min()
            
            # Win rate (positive return days)
            positive_days = (df['daily_return'] > 0).sum()
            win_rate = positive_days / len(df['daily_return'].dropna())
            
            return {
                'total_return': total_return,
                'annualized_return': annualized_return,
                'annualized_volatility': annualized_vol,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': win_rate,
                'total_trades': len(df),
                'current_value': df['total_value'].iloc[-1],
                'peak_value': rolling_max.iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"❌ Error calculating performance metrics: {e}")
            return {}
    
    def detect_market_regime(self, lookback_days: int = 60) -> MarketRegime:
        """
        Detect current market regime for strategy adaptation
        """
        try:
            # Use VIX for volatility regime detection
            vix = yf.Ticker("^VIX")
            vix_data = vix.history(period=f"{lookback_days}d")
            
            # Use SPY for trend detection
            spy = yf.Ticker("SPY")
            spy_data = spy.history(period=f"{lookback_days}d")
            
            if vix_data.empty or spy_data.empty:
                return MarketRegime.SIDEWAYS_MEAN_REVERSION
            
            # Current VIX level
            current_vix = vix_data['Close'].iloc[-1]
            avg_vix = vix_data['Close'].mean()
            
            # SPY trend analysis
            spy_ma_20 = spy_data['Close'].rolling(20).mean()
            spy_ma_50 = spy_data['Close'].rolling(50).mean()
            
            current_price = spy_data['Close'].iloc[-1]
            ma_20_current = spy_ma_20.iloc[-1]
            ma_50_current = spy_ma_50.iloc[-1]
            
            # Regime detection logic
            if current_vix > avg_vix * 1.5:
                return MarketRegime.HIGH_VOLATILITY
            elif current_price > ma_20_current > ma_50_current:
                return MarketRegime.BULL_MOMENTUM
            elif current_price < ma_20_current < ma_50_current:
                return MarketRegime.BEAR_MOMENTUM
            else:
                return MarketRegime.SIDEWAYS_MEAN_REVERSION
                
        except Exception as e:
            logger.error(f"❌ Error detecting market regime: {e}")
            return MarketRegime.SIDEWAYS_MEAN_REVERSION

# Global instance
systematic_trading_engine = SystematicTradingEngine()
