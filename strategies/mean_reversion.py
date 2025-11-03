"""
Mean Reversion Strategy
Implements a mean reversion strategy using RSI and Bollinger Bands.
"""

import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy
from typing import Dict, Any


class MeanReversionStrategy(BaseStrategy):
    """
    Mean Reversion Strategy using RSI and Bollinger Bands.
    
    This strategy assumes that prices will revert to their mean after
    extreme movements. It buys when the price is oversold and sells
    when the price is overbought.
    
    Best suited for: Sideways/ranging markets
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize the Mean Reversion Strategy.
        
        Args:
            params: Strategy parameters including:
                - rsi_period: Period for RSI calculation (default: 14)
                - rsi_oversold: RSI level for oversold (default: 30)
                - rsi_overbought: RSI level for overbought (default: 70)
                - bb_period: Period for Bollinger Bands (default: 20)
                - bb_std: Standard deviations for BB (default: 2)
        """
        default_params = {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'bb_period': 20,
            'bb_std': 2.0
        }
        
        if params:
            default_params.update(params)
        
        super().__init__(name="Mean Reversion", params=default_params)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI and Bollinger Bands indicators.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
        """
        df = data.copy()
        
        # Calculate RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.params['rsi_period'])
        
        # Calculate Bollinger Bands
        bb_period = self.params['bb_period']
        bb_std = self.params['bb_std']
        
        df['bb_middle'] = df['close'].rolling(window=bb_period).mean()
        rolling_std = df['close'].rolling(window=bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (rolling_std * bb_std)
        df['bb_lower'] = df['bb_middle'] - (rolling_std * bb_std)
        
        # Calculate position relative to Bollinger Bands
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Calculate distance from mean
        df['distance_from_mean'] = (df['close'] - df['bb_middle']) / df['bb_middle']
        
        return df
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            prices: Series of prices
            period: RSI period
        
        Returns:
            Series with RSI values
        """
        delta = prices.diff()
        
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on mean reversion logic.
        
        Args:
            data: DataFrame with OHLCV data and indicators
        
        Returns:
            Series with trading signals (1=Buy, -1=Sell, 0=Hold)
        """
        # Ensure indicators are calculated
        if 'rsi' not in data.columns or 'bb_lower' not in data.columns:
            data = self.calculate_indicators(data)
        
        signals = pd.Series(0, index=data.index)
        
        # Ensure we have enough data
        if len(data) < max(self.params['rsi_period'], self.params['bb_period']):
            return signals
        
        rsi_oversold = self.params['rsi_oversold']
        rsi_overbought = self.params['rsi_overbought']
        
        # Buy conditions (oversold):
        # 1. RSI is below oversold threshold
        # 2. Price is near or below lower Bollinger Band
        buy_condition = (
            (data['rsi'] < rsi_oversold) &
            (data['close'] <= data['bb_lower'] * 1.02)  # Within 2% of lower band
        )
        
        # Sell conditions (overbought):
        # 1. RSI is above overbought threshold
        # 2. Price is near or above upper Bollinger Band
        sell_condition = (
            (data['rsi'] > rsi_overbought) &
            (data['close'] >= data['bb_upper'] * 0.98)  # Within 2% of upper band
        )
        
        # Alternative exit: Price crosses back to middle band
        # This is a mean reversion exit
        exit_long_condition = (
            (data['close'] > data['bb_middle']) &
            (data['close'].shift(1) <= data['bb_middle'].shift(1))
        )
        
        exit_short_condition = (
            (data['close'] < data['bb_middle']) &
            (data['close'].shift(1) >= data['bb_middle'].shift(1))
        )
        
        # Generate signals
        signals[buy_condition] = 1
        signals[sell_condition] = -1
        
        # Add exit signals (prioritize exits over new positions)
        signals[exit_long_condition] = -1
        signals[exit_short_condition] = 1
        
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
            'TREND': 0.3,      # Poor for trending markets (fighting the trend)
            'SIDEWAYS': 0.9,   # Excellent for sideways/ranging markets
            'VOLATILE': 0.6    # Good for volatile markets with mean reversion
        }
        
        return suitability.get(regime.upper(), 0.5)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("🥝 Mean Reversion Strategy Test")
    print("=" * 60)
    
    # Create sample data with mean-reverting behavior
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    # Generate mean-reverting price data (oscillating around 100)
    mean_price = 100
    prices = [mean_price]
    
    for i in range(1, len(dates)):
        # Mean reversion with random walk
        reversion = (mean_price - prices[-1]) * 0.1  # Pull towards mean
        noise = np.random.normal(0, 2)
        new_price = prices[-1] + reversion + noise
        prices.append(new_price)
    
    data = pd.DataFrame({
        'close': prices,
        'open': np.array(prices) * 0.99,
        'high': np.array(prices) * 1.02,
        'low': np.array(prices) * 0.98,
        'volume': np.random.randint(1e6, 1e7, len(dates))
    }, index=dates)
    
    # Test the strategy
    strategy = MeanReversionStrategy()
    print(f"\n✅ Created strategy: {strategy}")
    print(f"📊 Parameters: {strategy.params}")
    
    # Calculate indicators
    data_with_indicators = strategy.calculate_indicators(data)
    print(f"\n📈 Calculated indicators:")
    print(data_with_indicators[['close', 'rsi', 'bb_upper', 'bb_middle', 'bb_lower']].tail())
    
    # Generate signals
    signals = strategy.generate_signals(data_with_indicators)
    print(f"\n🎯 Generated {(signals != 0).sum()} trading signals")
    print(f"   - Buy signals: {(signals == 1).sum()}")
    print(f"   - Sell signals: {(signals == -1).sum()}")
    
    # Show some signal examples
    signal_dates = data_with_indicators[signals != 0].head(10)
    if len(signal_dates) > 0:
        print(f"\n📅 First few signals:")
        for date, row in signal_dates.iterrows():
            signal = signals.loc[date]
            signal_type = "BUY" if signal == 1 else "SELL"
            print(f"   {date.date()}: {signal_type} at ${row['close']:.2f} (RSI: {row['rsi']:.1f})")
    
    # Test regime suitability
    print(f"\n🎭 Regime Suitability:")
    for regime in ['TREND', 'SIDEWAYS', 'VOLATILE']:
        score = strategy.get_regime_suitability(regime)
        print(f"   {regime}: {score*100:.0f}%")
    
    print("\n✅ Mean Reversion Strategy test completed!")
