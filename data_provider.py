import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from database import MarketData
import logging

logger = logging.getLogger(__name__)

class YFinanceDataProvider:
    """Yahoo Finance data provider for market data"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
            
            current_price = float(data['Close'].iloc[-1])
            logger.info(f"Current price for {symbol}: ${current_price:.2f}")
            return current_price
        
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Get historical data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval, timeout=self.timeout)
            
            if data.empty:
                logger.warning(f"No historical data available for {symbol}")
                return None
            
            # Clean and format data
            data = data.round(4)
            data.index = pd.to_datetime(data.index).date
            
            logger.info(f"Fetched {len(data)} records for {symbol} ({period})")
            return data
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get current prices for multiple symbols"""
        prices = {}
        
        try:
            # Use yfinance to get multiple tickers at once for efficiency
            tickers = yf.Tickers(' '.join(symbols))
            
            for symbol in symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    data = ticker.history(period="1d", interval="1m")
                    
                    if not data.empty:
                        prices[symbol] = float(data['Close'].iloc[-1])
                    else:
                        logger.warning(f"No data for {symbol}")
                        prices[symbol] = None
                
                except Exception as e:
                    logger.error(f"Error fetching price for {symbol}: {e}")
                    prices[symbol] = None
            
            logger.info(f"Fetched prices for {len([p for p in prices.values() if p is not None])}/{len(symbols)} symbols")
            return prices
        
        except Exception as e:
            logger.error(f"Error fetching multiple prices: {e}")
            return {symbol: None for symbol in symbols}
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """Get detailed stock information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key information
            stock_info = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                '52_week_high': info.get('fiftyTwoWeekHigh'),
                '52_week_low': info.get('fiftyTwoWeekLow'),
                'volume': info.get('volume'),
                'avg_volume': info.get('averageVolume'),
                'description': info.get('longBusinessSummary', '')[:500] + '...' if info.get('longBusinessSummary') else ''
            }
            
            logger.info(f"Fetched info for {symbol}: {stock_info.get('name')}")
            return stock_info
        
        except Exception as e:
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return None
    
    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            if data.empty:
                return data
            
            # Simple Moving Averages
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            data['SMA_50'] = data['Close'].rolling(window=50).mean()
            data['SMA_200'] = data['Close'].rolling(window=200).mean()
            
            # Exponential Moving Averages
            data['EMA_12'] = data['Close'].ewm(span=12).mean()
            data['EMA_26'] = data['Close'].ewm(span=26).mean()
            
            # MACD
            data['MACD'] = data['EMA_12'] - data['EMA_26']
            data['MACD_Signal'] = data['MACD'].ewm(span=9).mean()
            data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            data['BB_Middle'] = data['Close'].rolling(window=20).mean()
            bb_std = data['Close'].rolling(window=20).std()
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * 2)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * 2)
            
            # Volume indicators
            data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
            
            logger.info(f"Calculated technical indicators for {len(data)} records")
            return data
        
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return data
    
    def update_market_data(self, db: Session, symbols: List[str], period: str = "5d") -> Dict[str, int]:
        """Update market data in database"""
        results = {"success": 0, "failed": 0}
        
        for symbol in symbols:
            try:
                # Get historical data
                data = self.get_historical_data(symbol, period=period)
                if data is None or data.empty:
                    results["failed"] += 1
                    continue
                
                # Update database
                for date, row in data.iterrows():
                    # Check if record exists
                    existing = db.query(MarketData).filter(
                        MarketData.symbol == symbol,
                        MarketData.date == date
                    ).first()
                    
                    if existing:
                        # Update existing record
                        existing.open_price = float(row['Open'])
                        existing.high_price = float(row['High'])
                        existing.low_price = float(row['Low'])
                        existing.close_price = float(row['Close'])
                        existing.volume = int(row['Volume']) if pd.notna(row['Volume']) else None
                        existing.adjusted_close = float(row['Close'])  # yfinance returns adjusted close as 'Close'
                    else:
                        # Create new record
                        market_data = MarketData(
                            symbol=symbol,
                            date=date,
                            open_price=float(row['Open']),
                            high_price=float(row['High']),
                            low_price=float(row['Low']),
                            close_price=float(row['Close']),
                            volume=int(row['Volume']) if pd.notna(row['Volume']) else None,
                            adjusted_close=float(row['Close'])
                        )
                        db.add(market_data)
                
                db.commit()
                results["success"] += 1
                logger.info(f"Updated market data for {symbol}")
                
            except Exception as e:
                db.rollback()
                logger.error(f"Error updating market data for {symbol}: {e}")
                results["failed"] += 1
        
        logger.info(f"Market data update completed: {results['success']} success, {results['failed']} failed")
        return results
    
    def get_portfolio_performance(self, holdings: List[Dict]) -> Dict:
        """Calculate portfolio performance metrics"""
        try:
            if not holdings:
                return {
                    'total_value': 0.0,
                    'total_cost': 0.0,
                    'total_pnl': 0.0,
                    'total_pnl_percent': 0.0,
                    'day_change': 0.0,
                    'day_change_percent': 0.0
                }
            
            symbols = [h['symbol'] for h in holdings]
            current_prices = self.get_multiple_prices(symbols)
            
            total_value = 0.0
            total_cost = 0.0
            day_change = 0.0
            
            for holding in holdings:
                symbol = holding['symbol']
                quantity = float(holding['quantity'])
                avg_cost = float(holding['average_cost'])
                
                current_price = current_prices.get(symbol)
                if current_price is None:
                    continue
                
                market_value = quantity * current_price
                cost_basis = quantity * avg_cost
                
                total_value += market_value
                total_cost += cost_basis
                
                # Get previous day's price for day change calculation
                prev_data = self.get_historical_data(symbol, period="2d")
                if prev_data is not None and len(prev_data) >= 2:
                    prev_price = float(prev_data['Close'].iloc[-2])
                    day_change += quantity * (current_price - prev_price)
            
            total_pnl = total_value - total_cost
            total_pnl_percent = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0
            day_change_percent = (day_change / (total_value - day_change) * 100) if (total_value - day_change) > 0 else 0.0
            
            return {
                'total_value': round(total_value, 2),
                'total_cost': round(total_cost, 2),
                'total_pnl': round(total_pnl, 2),
                'total_pnl_percent': round(total_pnl_percent, 2),
                'day_change': round(day_change, 2),
                'day_change_percent': round(day_change_percent, 2)
            }
        
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {e}")
            return {
                'total_value': 0.0,
                'total_cost': 0.0,
                'total_pnl': 0.0,
                'total_pnl_percent': 0.0,
                'day_change': 0.0,
                'day_change_percent': 0.0
            }
    
    def validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol exists and has data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid info
            if 'symbol' in info or 'shortName' in info or 'longName' in info:
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error validating symbol {symbol}: {e}")
            return False
    
    def search_symbols(self, query: str) -> List[Dict]:
        """Search for symbols (limited functionality with yfinance)"""
        try:
            # This is a basic implementation - in production you might want to use
            # a dedicated symbol search API or maintain a symbols database
            common_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX',
                'SPY', 'QQQ', 'VTI', 'VOO', 'BTC-USD', 'ETH-USD'
            ]
            
            query = query.upper()
            matches = []
            
            for symbol in common_symbols:
                if query in symbol:
                    info = self.get_stock_info(symbol)
                    if info:
                        matches.append({
                            'symbol': symbol,
                            'name': info.get('name', symbol),
                            'sector': info.get('sector', 'Unknown')
                        })
            
            return matches[:10]  # Limit to 10 results
        
        except Exception as e:
            logger.error(f"Error searching symbols: {e}")
            return []