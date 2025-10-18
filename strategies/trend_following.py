"""
Trend Following Strategy
Implements a moving average crossover strategy for trending markets.
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from typing import Dict, Any


class TrendFollowingStrategy(BaseStrategy):
    """
    Trend Following Strategy using Moving Average Crossover.
    
    This strategy generates buy signals when a faster moving average crosses
    above a slower moving average, and sell signals on the opposite crossover.
    
    Best suited for: Trending markets
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize the Trend Following Strategy.
        
        Args:
            params: Strategy parameters including:
                - fast_period: Period for fast moving average (default: 20)
                - slow_period: Period for slow moving average (default: 50)
                - ma_type: Type of MA ('SMA' or 'EMA', default: 'SMA')
        """
        default_params = {
            'fast_period': 20,
            'slow_period': 50,
            'ma_type': 'SMA'  # Simple Moving Average
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(name="Trend Following", params=default_params)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate moving averages and trend indicators.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
        """
        df = data.copy()
        
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        ma_type = self.params['ma_type']
        
        # Calculate moving averages
        if ma_type == 'SMA':
            df['ma_fast'] = df['close'].rolling(window=fast_period).mean()
            df['ma_slow'] = df['close'].rolling(window=slow_period).mean()
        elif ma_type == 'EMA':
            df['ma_fast'] = df['close'].ewm(span=fast_period, adjust=False).mean()
            df['ma_slow'] = df['close'].ewm(span=slow_period, adjust=False).mean()
        else:
            raise ValueError(f"Unknown MA type: {ma_type}")
        
        # Calculate the difference between MAs (momentum indicator)
        df['ma_diff'] = df['ma_fast'] - df['ma_slow']
        
        # Calculate trend strength using ADX concept (simplified)
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # Trend direction
        df['trend'] = np.where(df['ma_fast'] > df['ma_slow'], 1, -1)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on moving average crossovers.
        
        Args:
            data: DataFrame with OHLCV data and indicators
        
        Returns:
            Series with trading signals (1=Buy, -1=Sell, 0=Hold)
        """
        # First ensure indicators are calculated
        if 'ma_fast' not in data.columns or 'ma_slow' not in data.columns:
            data = self.calculate_indicators(data)
        
        signals = pd.Series(0, index=data.index)
        
        # Ensure we have enough data
        if len(data) < self.params['slow_period']:
            return signals
        
        # Detect crossovers
        # Buy signal: fast MA crosses above slow MA
        crossover_up = (
            (data['ma_fast'] > data['ma_slow']) & 
            (data['ma_fast'].shift(1) <= data['ma_slow'].shift(1))
        )
        
        # Sell signal: fast MA crosses below slow MA
        crossover_down = (
            (data['ma_fast'] < data['ma_slow']) & 
            (data['ma_fast'].shift(1) >= data['ma_slow'].shift(1))
        )
        
        # Generate signals
        signals[crossover_up] = 1
        signals[crossover_down] = -1
        
        # Optional: Filter signals by trend strength
        # Only take signals when volatility is reasonable (not too low, not too high)
        if 'volatility' in data.columns:
            vol_median = data['volatility'].median()
            # Filter out signals in very low volatility (sideways market)
            low_vol_mask = data['volatility'] < vol_median * 0.5
            signals[low_vol_mask] = 0
        
        return signals
    
    def get_regime_suitability(self, regime: str) -> float:
        """
        Return a score (0-1) indicating how suitable this strategy is for a given regime.
        
        Args:
            regime: Market regime ('TREND', 'SIDEWAYS', 'VOLATILE')
        
        Returns:
            Suitability score (0-1)
        """
        suitability = {
            'TREND': 0.9,      # Excellent for trending markets
            'SIDEWAYS': 0.3,   # Poor for sideways markets (many false signals)
            'VOLATILE': 0.5    # Moderate for volatile markets
        }
        
        return suitability.get(regime.upper(), 0.5)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("🥝 Trend Following Strategy Test")
    print("=" * 60)
    
    # Create sample data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Generate trending price data
    trend = np.linspace(100, 150, len(dates))
    noise = np.random.normal(0, 2, len(dates))
    prices = trend + noise
    
    data = pd.DataFrame({
        'close': prices,
        'open': prices * 0.99,
        'high': prices * 1.01,
        'low': prices * 0.98,
        'volume': np.random.randint(1e6, 1e7, len(dates))
    }, index=dates)
    
    # Test the strategy
    strategy = TrendFollowingStrategy()
    print(f"\n✅ Created strategy: {strategy}")
    print(f"📊 Parameters: {strategy.params}")
    
    # Calculate indicators
    data_with_indicators = strategy.calculate_indicators(data)
    print(f"\n📈 Calculated indicators:")
    print(data_with_indicators[['close', 'ma_fast', 'ma_slow', 'trend']].tail())
    
    # Generate signals
    signals = strategy.generate_signals(data_with_indicators)
    print(f"\n🎯 Generated {(signals != 0).sum()} trading signals")
    print(f"   - Buy signals: {(signals == 1).sum()}")
    print(f"   - Sell signals: {(signals == -1).sum()}")
    
    # Show some signal examples
    signal_dates = data_with_indicators[signals != 0].head()
    if len(signal_dates) > 0:
        print(f"\n📅 First few signals:")
        for date, row in signal_dates.iterrows():
            signal = signals.loc[date]
            signal_type = "BUY" if signal == 1 else "SELL"
            print(f"   {date.date()}: {signal_type} at ${row['close']:.2f}")
    
    # Test regime suitability
    print(f"\n🎭 Regime Suitability:")
    for regime in ['TREND', 'SIDEWAYS', 'VOLATILE']:
        score = strategy.get_regime_suitability(regime)
        print(f"   {regime}: {score*100:.0f}%")
    
    print("\n✅ Trend Following Strategy test completed!")
