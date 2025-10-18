"""
Data Handler Module
Responsible for fetching historical and live market data from various sources.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
import config


class DataHandler:
    """
    Handles data fetching, caching, and preprocessing for the trading system.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the DataHandler.
        
        Args:
            data_dir: Directory to store cached market data
        """
        self.data_dir = data_dir or config.DATA_DIRECTORY
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = '1D',
        use_cache: bool = True
    ) -> pd.DataFrame:
        """
        Fetch historical market data for a given symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'SPY', 'AAPL')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            timeframe: Data timeframe ('1D', '1H', '5Min', etc.)
            use_cache: Whether to use cached data if available
        
        Returns:
            DataFrame with OHLCV data
        """
        cache_file = self._get_cache_filename(symbol, start_date, end_date, timeframe)
        
        # Check cache first
        if use_cache and os.path.exists(cache_file):
            print(f"📂 Loading {symbol} data from cache...")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        print(f"🌐 Fetching {symbol} data from API...")
        
        try:
            # Import here to avoid issues if alpaca-py is not installed
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
            
            # Initialize Alpaca client
            client = StockHistoricalDataClient(
                config.ALPACA_KEY,
                config.ALPACA_SECRET
            )
            
            # Parse timeframe
            timeframe_map = {
                '1Min': TimeFrame(1, TimeFrameUnit.Minute),
                '5Min': TimeFrame(5, TimeFrameUnit.Minute),
                '15Min': TimeFrame(15, TimeFrameUnit.Minute),
                '1H': TimeFrame(1, TimeFrameUnit.Hour),
                '1D': TimeFrame(1, TimeFrameUnit.Day),
            }
            
            tf = timeframe_map.get(timeframe, TimeFrame(1, TimeFrameUnit.Day))
            
            # Create request
            request_params = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=pd.Timestamp(start_date, tz='UTC'),
                end=pd.Timestamp(end_date, tz='UTC')
            )
            
            # Fetch data
            bars = client.get_stock_bars(request_params)
            df = bars.df
            
            # If multi-index (symbol, timestamp), reset to get symbol column
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)
            
            # Ensure standard column names
            df.columns = [col.lower() for col in df.columns]
            
            # Cache the data
            df.to_csv(cache_file)
            print(f"✅ Fetched {len(df)} bars for {symbol}")
            
            return df
            
        except ImportError:
            print("⚠️  Alpaca SDK not available, using mock data...")
            return self._generate_mock_data(symbol, start_date, end_date)
        
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            print("⚠️  Falling back to mock data...")
            return self._generate_mock_data(symbol, start_date, end_date)
    
    def _get_cache_filename(self, symbol: str, start: str, end: str, timeframe: str) -> str:
        """Generate a cache filename based on parameters."""
        filename = f"{symbol}_{start}_{end}_{timeframe}.csv"
        return os.path.join(self.data_dir, filename)
    
    def _generate_mock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_price: float = 100.0
    ) -> pd.DataFrame:
        """
        Generate realistic mock market data for testing purposes.
        
        Args:
            symbol: Stock symbol
            start_date: Start date
            end_date: End date
            initial_price: Starting price
        
        Returns:
            DataFrame with synthetic OHLCV data
        """
        print(f"🎲 Generating mock data for {symbol}...")
        
        # Create date range
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n = len(dates)
        
        # Generate realistic price movements
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, n)  # Mean return 0.05%, std 2%
        prices = initial_price * np.exp(np.cumsum(returns))
        
        # Generate OHLC data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Simulate intraday volatility
            high = close * (1 + abs(np.random.normal(0, 0.01)))
            low = close * (1 - abs(np.random.normal(0, 0.01)))
            open_price = prices[i-1] if i > 0 else close
            volume = int(np.random.uniform(1e6, 1e8))
            
            data.append({
                'open': open_price,
                'high': max(open_price, close, high),
                'low': min(open_price, close, low),
                'close': close,
                'volume': volume
            })
        
        df = pd.DataFrame(data, index=dates)
        df.index.name = 'timestamp'
        
        return df
    
    def get_latest_price(self, symbol: str) -> float:
        """
        Get the most recent price for a symbol.
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Latest close price
        """
        # Fetch last 5 days of data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        df = self.fetch_historical_data(symbol, start_date, end_date, use_cache=False)
        
        if df is not None and len(df) > 0:
            return float(df['close'].iloc[-1])
        else:
            raise ValueError(f"Could not fetch price for {symbol}")
    
    def calculate_returns(self, df: pd.DataFrame, period: int = 1) -> pd.Series:
        """
        Calculate returns from price data.
        
        Args:
            df: DataFrame with 'close' column
            period: Number of periods for return calculation
        
        Returns:
            Series of returns
        """
        return df['close'].pct_change(period)
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add common technical indicators to the data.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added technical indicators
        """
        df = df.copy()
        
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        
        # Returns and Volatility
        df['returns'] = df['close'].pct_change()
        df['volatility_20'] = df['returns'].rolling(window=20).std()
        
        # RSI (Relative Strength Index)
        df['rsi_14'] = self._calculate_rsi(df['close'], period=14)
        
        return df
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🥝 Kiwi_AI Data Handler Test")
    print("=" * 60)
    
    handler = DataHandler()
    
    # Test fetching data
    symbol = "SPY"
    start = "2023-01-01"
    end = "2023-12-31"
    
    df = handler.fetch_historical_data(symbol, start, end)
    
    print(f"\n📊 Fetched {len(df)} bars for {symbol}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    print(f"\nLast 5 rows:")
    print(df.tail())
    
    # Add technical indicators
    df_with_indicators = handler.add_technical_indicators(df)
    print(f"\n📈 Added technical indicators:")
    print(df_with_indicators[['close', 'sma_20', 'sma_50', 'rsi_14']].tail())
    
    print("\n✅ Data Handler test completed!")
