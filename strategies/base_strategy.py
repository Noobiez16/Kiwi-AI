"""
Base Strategy Class
Defines the interface that all trading strategies must implement.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.
    All concrete strategies must inherit from this class and implement its methods.
    """
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        """
        Initialize the strategy.
        
        Args:
            name: Name of the strategy
            params: Dictionary of strategy parameters
        """
        self.name = name
        self.params = params or {}
        self.position = 0  # Current position: 1 (long), -1 (short), 0 (flat)
        self.trades = []   # List of executed trades
        self.equity_curve = []  # Track equity over time
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on market data.
        
        This is the core method that each strategy must implement.
        
        Args:
            data: DataFrame with OHLCV data and any additional indicators
        
        Returns:
            Series with trading signals:
                1  = Buy signal (go long)
                -1 = Sell signal (go short or close long)
                0  = Hold (no action)
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators required for the strategy.
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
        """
        pass
    
    def get_position_size(
        self,
        signal: int,
        capital: float,
        current_price: float,
        risk_per_trade: float = 0.02
    ) -> int:
        """
        Calculate position size based on signal and risk parameters.
        
        Args:
            signal: Trading signal (1, -1, or 0)
            capital: Available capital
            current_price: Current market price
            risk_per_trade: Risk percentage per trade (default 2%)
        
        Returns:
            Number of shares to trade (positive for long, negative for short)
        """
        if signal == 0:
            return 0
        
        # Simple position sizing: risk a fixed percentage of capital
        risk_amount = capital * risk_per_trade
        position_value = capital * 0.95  # Use 95% of capital
        shares = int(position_value / current_price)
        
        return shares if signal == 1 else -shares
    
    def update_position(self, signal: int, price: float, timestamp: pd.Timestamp):
        """
        Update the current position based on a signal.
        
        Args:
            signal: Trading signal
            price: Execution price
            timestamp: Time of trade
        """
        if signal != 0 and signal != self.position:
            trade = {
                'timestamp': timestamp,
                'action': 'BUY' if signal == 1 else 'SELL',
                'price': price,
                'position': signal
            }
            self.trades.append(trade)
            self.position = signal
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate basic performance metrics for the strategy.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.equity_curve:
            return {}
        
        equity = pd.Series(self.equity_curve)
        returns = equity.pct_change().dropna()
        
        metrics = {
            'total_return': (equity.iloc[-1] / equity.iloc[0] - 1) * 100,
            'num_trades': len(self.trades),
            'sharpe_ratio': self._calculate_sharpe(returns) if len(returns) > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(equity),
        }
        
        return metrics
    
    @staticmethod
    def _calculate_sharpe(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) == 0 or returns.std() == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252  # Daily risk-free rate
        return float((excess_returns.mean() / excess_returns.std()) * (252 ** 0.5))
    
    @staticmethod
    def _calculate_max_drawdown(equity: pd.Series) -> float:
        """Calculate maximum drawdown as a percentage."""
        if len(equity) == 0:
            return 0.0
        
        cummax = equity.expanding().max()
        drawdown = (equity - cummax) / cummax
        return float(drawdown.min() * 100)
    
    def reset(self):
        """Reset strategy state."""
        self.position = 0
        self.trades = []
        self.equity_curve = []
    
    def __str__(self) -> str:
        """String representation of the strategy."""
        return f"{self.name} (Position: {self.position}, Trades: {len(self.trades)})"
    
    def __repr__(self) -> str:
        """Detailed representation of the strategy."""
        return f"<{self.__class__.__name__}: {self.name}>"


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("🥝 Base Strategy Test")
    print("=" * 60)
    
    # Create a simple test strategy
    class TestStrategy(BaseStrategy):
        """Simple test strategy for demonstration."""
        
        def generate_signals(self, data: pd.DataFrame) -> pd.Series:
            # Simple moving average crossover
            signals = pd.Series(0, index=data.index)
            if 'sma_short' in data and 'sma_long' in data:
                signals[data['sma_short'] > data['sma_long']] = 1
                signals[data['sma_short'] < data['sma_long']] = -1
            return signals
        
        def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
            data = data.copy()
            data['sma_short'] = data['close'].rolling(window=20).mean()
            data['sma_long'] = data['close'].rolling(window=50).mean()
            return data
    
    # Test the strategy
    strategy = TestStrategy("Test SMA Crossover")
    print(f"\n✅ Created strategy: {strategy}")
    print(f"📊 Strategy class: {strategy.__class__.__name__}")
    print(f"🎯 Strategy name: {strategy.name}")
    
    print("\n✅ Base Strategy test completed!")
