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
        # Separate US and Chinese ETFs for independent analysis
        self.us_sector_etfs = {
            # US Technology & Growth
            'XLK': 'Technology Select Sector SPDR',
            'QQQ': 'Invesco QQQ Trust',
            'ARKK': 'ARK Innovation ETF',
            'SOXX': 'iShares Semiconductor ETF',
            'VGT': 'Vanguard Information Technology ETF',
            'SMH': 'VanEck Semiconductor ETF',
            
            # US Financial Services
            'XLF': 'Financial Select Sector SPDR',
            'KRE': 'SPDR S&P Regional Banking',
            'KIE': 'SPDR S&P Insurance',
            'KBE': 'SPDR S&P Bank ETF',
            
            # US Healthcare & Biotech
            'XLV': 'Health Care Select Sector SPDR',
            'IBB': 'iShares Biotechnology ETF',
            'XBI': 'SPDR S&P Biotech ETF',
            'IHI': 'iShares U.S. Medical Devices ETF',
            
            # US Energy & Materials
            'XLE': 'Energy Select Sector SPDR',
            'XLB': 'Materials Select Sector SPDR',
            'XME': 'SPDR S&P Metals & Mining',
            'UNG': 'United States Natural Gas Fund',
            
            # US Consumer & Retail
            'XLY': 'Consumer Discretionary SPDR',
            'XLP': 'Consumer Staples SPDR',
            'XRT': 'SPDR S&P Retail ETF',
            'VCR': 'Vanguard Consumer Discretionary ETF',
            
            # US Infrastructure & REITs
            'XLI': 'Industrial Select Sector SPDR',
            'XLU': 'Utilities Select Sector SPDR',
            'XLRE': 'Real Estate Select Sector SPDR',
            'VNQ': 'Vanguard Real Estate ETF',
            
        }
        
        # Chinese Market ETFs - From cn.investing.com actual data (40 most active traded)
        self.china_sector_etfs = {
            # Hong Kong & Tech ETFs (Highest Volume) - Shanghai Stock Exchange
            '513090.SS': '易方达中证香港证券投资ETF',                    # 9.23B volume - Hong Kong securities
            '513130.SS': 'Huatai-PB CSOP HS Tech Id(QDII)',       # 8.76B volume - Hang Seng Tech
            '513180.SS': 'ChinaAMC Hangsheng Tech (QDII)',        # 8.67B volume - Hang Seng Tech
            '513330.SS': '华夏恒生互联网科技业ETF(QDII)',              # 7.95B volume - Internet tech
            '513120.SS': 'GF CSI Hong Kong Brand Name Drug(QDII)', # 7.85B volume - HK pharma
            
            # Broad Market & Large Cap - Shanghai Stock Exchange
            '512050.SS': 'ChinaAMC CSI A500',                     # 5.54B volume - A500 index
            '588000.SS': '华夏科创50场内联接基金',                      # 5.36B volume - STAR 50
            '512880.SS': '国泰中证全指证券公司',                        # 3.70B volume - Securities
            '510300.SS': '华泰柏瑞沪深300',                         # 1.36B volume - CSI 300
            '510050.SS': '华夏上证50',                             # 1.24B volume - SSE 50
            '510500.SS': '南方中证500',                            # 349.46M volume - CSI 500
            '510310.SS': '易方达沪深300',                          # 279.45M volume - CSI 300
            '510330.SS': '华夏沪深300',                           # 124.07M volume - CSI 300
            
            # Healthcare & Biotech - Shanghai Stock Exchange
            '513060.SS': '博时恒生医疗保健QDII-ETF',                  # 4.35B volume - Healthcare
            '512170.SS': '华宝中证医疗',                             # 2.40B volume - Medical
            '512010.SS': '易方达沪深300医药卫生',                     # 2.22B volume - Pharma
            
            # Consumer & Alcohol - Shanghai Stock Exchange
            '512690.SS': '鹏华中证酒',                              # 3.24B volume - Alcohol/liquor
            '510150.SS': '招商上证消费80',                           # 323.76M volume - Consumer
            
            # Technology & AI - Shanghai Stock Exchange
            '513980.SS': 'IGW CSI HK Connect Technology',         # 2.67B volume - HK tech
            '515050.SS': '华夏中证5G通信主题',                        # 327.16M volume - 5G
            '588200.SS': 'Harvest SSE STAR Chip Index',           # 2.73B volume - STAR chip
            
            # Defense & Military - Shanghai Stock Exchange
            '512710.SS': 'Fullgoal CSI National Defense Industry', # 2.06B volume - Defense
            '512660.SS': '国泰中证军工',                            # 1.26B volume - Military
            '512670.SS': '鹏华中证国防',                            # 528.31M volume - Defense
            
            # Materials & Chemicals - Shanghai Stock Exchange
            '512480.SS': '国联安中证全指半导体产品与设备',               # 1.79B volume - Semiconductors
            '512400.SS': '南方中证申万有色金属',                      # 324.12M volume - Metals
            
            # Energy & New Energy - Shenzhen Stock Exchange
            '159755.SZ': '广发国证新能源车电池ETF',                   # 1.33B volume - EV battery
            '159840.SZ': '工银瑞信国证新能源车电池ETF',                # 340.73M volume - EV battery
            '515030.SS': '华夏中证新能源汽车',                        # 170.33M volume - New energy auto
            '159875.SZ': '嘉实中证新能源ETF',                       # 223.39M volume - New energy
            
            # Growth & ChiNext - Shenzhen Stock Exchange
            '159915.SZ': '易方达创业板',                             # 2.48B volume - ChiNext/Growth
            '159949.SZ': '华安创业板50ETF',                         # 2.36B volume - ChiNext 50
            '159780.SZ': '双创ETF',                               # 1.56B volume - Innovation
            '159792.SZ': '港股通互联网ETF',                           # 3.72B volume - HK internet
            '159740.SZ': '大成恒生科技ETF（QDII）',                    # 3.65B volume - Hang Seng tech
            '159797.SZ': 'HuaTai-PineBridge CSI Medical Devices',  # Medical devices
            '159892.SZ': '华夏恒生香港上市生物科技ETF',                 # 1.79B volume - Biotech
            '159819.SZ': '易方达中证人工智能主题ETF',                   # 1.51B volume - AI theme
            '159851.SZ': '华宝中证金融科技主题ETF',                    # 1.74B volume - Fintech
            '159870.SZ': '鹏华中证细分化工产业ETF',                   # 1.94B volume - Chemicals
            
            # Financial Services - Shanghai Stock Exchange
            '512000.SS': '华宝中证全指证券公司',                      # 3.24B volume - Securities
            '512800.SS': '华宝中证银行',                           # 1.35B volume - Banking
            '512700.SS': '南方中证银行',                           # 124.04M volume - Banking
        
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
    
    def calculate_sector_scores(self, market: str = "US", lookback_days: int = 90) -> List[SectorScore]:
        """
        Calculate comprehensive sector scores for rotation decisions
        Based on momentum, mean reversion, fundamental, technical factors
        
        Args:
            market: "US" for US market ETFs, "China" for Chinese market ETFs
            lookback_days: Number of days for analysis
        """
        sector_scores = []
        
        try:
            # Select appropriate ETF dictionary
            if market.upper() == "CHINA":
                sector_etfs = self.china_sector_etfs
                # Use CSI 300 Index (000300.SS) as benchmark for Chinese market
                benchmark_ticker = "000300.SS"
                logger.info(f"🇨🇳 Analyzing Chinese market ETFs with CSI 300 benchmark")
            else:
                sector_etfs = self.us_sector_etfs
                # Use S&P 500 as benchmark for US market
                benchmark_ticker = "SPY"
                logger.info(f"🇺🇸 Analyzing US market ETFs with S&P 500 benchmark")
            
            # Get market benchmark for relative performance
            benchmark = yf.Ticker(benchmark_ticker)
            benchmark_data = benchmark.history(period=f"{lookback_days}d")
            benchmark_return = (benchmark_data['Close'].iloc[-1] / benchmark_data['Close'].iloc[0] - 1) if not benchmark_data.empty else 0
            
            logger.info(f"📈 {benchmark_ticker} benchmark return: {benchmark_return:.2%} over {lookback_days} days")
            
            for symbol, name in sector_etfs.items():
                try:
                    score = self._analyze_sector_etf(symbol, name, benchmark_return, lookback_days)
                    if score:
                        sector_scores.append(score)
                        logger.info(f"📊 {symbol}: Conviction {score.conviction_score:.2f}, Weight {score.recommended_weight:.1%}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error analyzing {symbol}: {e}")
                    continue
            
            # Sort by conviction score (highest first)
            sector_scores.sort(key=lambda x: x.conviction_score, reverse=True)
            
            logger.info(f"✅ Analyzed {len(sector_scores)} {market} market sectors for rotation")
            return sector_scores
            
        except Exception as e:
            logger.error(f"❌ Error calculating {market} sector scores: {e}")
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
