"""
Volatility Breakout Strategy
Implements a strategy that capitalizes on volatility breakouts.
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from typing import Dict, Any


class VolatilityBreakoutStrategy(BaseStrategy):
    """
    Volatility Breakout Strategy using ATR and Donchian Channels.
    
    This strategy identifies periods of low volatility followed by
    breakouts, entering positions when price breaks out of a range.
    
    Best suited for: Volatile markets with clear breakout patterns
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize the Volatility Breakout Strategy.
        
        Args:
            params: Strategy parameters including:
                - atr_period: Period for ATR calculation (default: 14)
                - donchian_period: Period for Donchian Channels (default: 20)
                - volatility_threshold: Multiplier for volatility (default: 1.5)
                - breakout_confirmation: Bars to confirm breakout (default: 2)
        """
        default_params = {
            'atr_period': 14,
            'donchian_period': 20,
            'volatility_threshold': 1.5,
            'breakout_confirmation': 2
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(name="Volatility Breakout", params=default_params)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate volatility and breakout indicators.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
        """
        df = data.copy()
        
        # Calculate ATR (Average True Range)
        df['atr'] = self._calculate_atr(df, self.params['atr_period'])
        
        # Calculate Donchian Channels (price channels)
        period = self.params['donchian_period']
        df['donchian_high'] = df['high'].rolling(window=period).max()
        df['donchian_low'] = df['low'].rolling(window=period).min()
        df['donchian_mid'] = (df['donchian_high'] + df['donchian_low']) / 2
        
        # Calculate channel width (as proxy for volatility)
        df['channel_width'] = df['donchian_high'] - df['donchian_low']
        df['channel_width_pct'] = df['channel_width'] / df['close']
        
        # Historical volatility (standard deviation of returns)
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(window=20).std()
        
        # Normalized volatility (current vs historical average)
        df['volatility_ratio'] = df['volatility'] / df['volatility'].rolling(window=50).mean()
        
        # Price position within channel
        df['channel_position'] = (
            (df['close'] - df['donchian_low']) / 
            (df['donchian_high'] - df['donchian_low'])
        )
        
        return df
    
    @staticmethod
    def _calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range.
        
        Args:
            data: DataFrame with OHLCV data
            period: ATR period
        
        Returns:
            Series with ATR values
        """
        high = data['high']
        low = data['low']
        close = data['close']
        
        # True Range calculation
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on volatility breakouts.
        
        Args:
            data: DataFrame with OHLCV data and indicators
        
        Returns:
            Series with trading signals (1=Buy, -1=Sell, 0=Hold)
        """
        # Ensure indicators are calculated
        if 'atr' not in data.columns or 'donchian_high' not in data.columns:
            data = self.calculate_indicators(data)
        
        signals = pd.Series(0, index=data.index)
        
        # Ensure we have enough data
        if len(data) < max(self.params['atr_period'], self.params['donchian_period']):
            return signals
        
        # Identify volatility contraction (squeeze)
        # When channel width is narrow relative to historical average
        avg_width = data['channel_width'].rolling(window=50).mean()
        volatility_squeeze = data['channel_width'] < avg_width * 0.8
        
        # Upside breakout conditions:
        # 1. Price closes above upper Donchian channel
        # 2. Increased volume (optional enhancement)
        # 3. ATR is expanding (volatility increasing)
        
        breakout_up = (
            (data['close'] > data['donchian_high'].shift(1)) &
            (data['atr'] > data['atr'].shift(self.params['breakout_confirmation']))
        )
        
        # Downside breakout conditions:
        # 1. Price closes below lower Donchian channel
        # 2. ATR is expanding
        
        breakout_down = (
            (data['close'] < data['donchian_low'].shift(1)) &
            (data['atr'] > data['atr'].shift(self.params['breakout_confirmation']))
        )
        
        # Enhanced signals: Only take breakouts after volatility squeeze
        # This increases probability of meaningful moves
        squeeze_threshold = self.params.get('require_squeeze', False)
        
        if squeeze_threshold:
            # Only signal after recent squeeze
            recent_squeeze = volatility_squeeze.rolling(window=10).sum() > 0
            breakout_up = breakout_up & recent_squeeze
            breakout_down = breakout_down & recent_squeeze
        
        # Generate signals
        signals[breakout_up] = 1
        signals[breakout_down] = -1
        
        # Exit conditions: Price returns to middle channel
        # This represents a failed breakout or profit-taking opportunity
        exit_condition = (
            (abs(data['close'] - data['donchian_mid']) < data['atr'] * 0.5)
        )
        
        # Apply exits (but don't override new breakout signals)
        signals[exit_condition & (signals == 0)] = 0
        
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
            'TREND': 0.6,      # Good for trends following breakouts
            'SIDEWAYS': 0.4,   # Moderate for sideways (many false breakouts)
            'VOLATILE': 0.9    # Excellent for volatile markets
        }
        
        return suitability.get(regime.upper(), 0.5)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("🥝 Volatility Breakout Strategy Test")
    print("=" * 60)
    
    # Create sample data with volatility and breakouts
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Generate price data with periods of low and high volatility
    prices = [100]
    volatility_regime = np.sin(np.linspace(0, 4*np.pi, len(dates))) * 0.015 + 0.02
    
    for i in range(1, len(dates)):
        ret = np.random.normal(0.001, volatility_regime[i])
        new_price = prices[-1] * (1 + ret)
        prices.append(new_price)
    
    data = pd.DataFrame({
        'close': prices,
        'open': np.array(prices) * 0.998,
        'high': np.array(prices) * 1.015,
        'low': np.array(prices) * 0.985,
        'volume': np.random.randint(1e6, 1e7, len(dates))
    }, index=dates)
    
    # Test the strategy
    strategy = VolatilityBreakoutStrategy()
    print(f"\n✅ Created strategy: {strategy}")
    print(f"📊 Parameters: {strategy.params}")
    
    # Calculate indicators
    data_with_indicators = strategy.calculate_indicators(data)
    print(f"\n📈 Calculated indicators:")
    indicators_to_show = ['close', 'atr', 'donchian_high', 'donchian_low', 'volatility']
    print(data_with_indicators[indicators_to_show].tail())
    
    # Generate signals
    signals = strategy.generate_signals(data_with_indicators)
    print(f"\n🎯 Generated {(signals != 0).sum()} trading signals")
    print(f"   - Buy signals (breakout up): {(signals == 1).sum()}")
    print(f"   - Sell signals (breakout down): {(signals == -1).sum()}")
    
    # Show some signal examples
    signal_dates = data_with_indicators[signals != 0].head(10)
    if len(signal_dates) > 0:
        print(f"\n📅 First few signals:")
        for date, row in signal_dates.iterrows():
            signal = signals.loc[date]
            signal_type = "BREAKOUT UP" if signal == 1 else "BREAKOUT DOWN"
            print(f"   {date.date()}: {signal_type} at ${row['close']:.2f} (ATR: {row['atr']:.2f})")
    
    # Test regime suitability
    print(f"\n🎭 Regime Suitability:")
    for regime in ['TREND', 'SIDEWAYS', 'VOLATILE']:
        score = strategy.get_regime_suitability(regime)
        print(f"   {regime}: {score*100:.0f}%")
    
    print("\n✅ Volatility Breakout Strategy test completed!")
