"""
Performance Monitor Module
Monitors and evaluates strategy performance in real-time.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
from collections import deque


class PerformanceMonitor:
    """
    Monitors trading strategy performance metrics in real-time.
    
    Tracks:
    - Rolling Sharpe Ratio
    - Maximum Drawdown
    - Win Rate
    - Profit Factor
    - Recent Returns
    """
    
    def __init__(self, lookback_window: int = 50, risk_free_rate: float = 0.02):
        """
        Initialize the Performance Monitor.
        
        Args:
            lookback_window: Number of periods to look back for metrics
            risk_free_rate: Annual risk-free rate for Sharpe calculation
        """
        self.lookback_window = lookback_window
        self.risk_free_rate = risk_free_rate
        
        # Store recent performance data
        self.returns_history = deque(maxlen=lookback_window)
        self.equity_history = deque(maxlen=lookback_window)
        self.trades_history = []
    
    def update(self, equity: float, returns: float = None):
        """
        Update performance metrics with new data point.
        
        Args:
            equity: Current portfolio equity
            returns: Period return (if None, calculated from equity)
        """
        self.equity_history.append(equity)
        
        if returns is None and len(self.equity_history) > 1:
            prev_equity = list(self.equity_history)[-2]
            returns = (equity - prev_equity) / prev_equity
        
        if returns is not None:
            self.returns_history.append(returns)
    
    def add_trade(self, entry_price: float, exit_price: float, direction: int = 1):
        """
        Record a completed trade.
        
        Args:
            entry_price: Entry price
            exit_price: Exit price
            direction: 1 for long, -1 for short
        """
        pnl = (exit_price - entry_price) * direction
        pnl_pct = pnl / entry_price
        
        trade = {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'direction': direction,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'win': pnl > 0
        }
        
        self.trades_history.append(trade)
    
    def calculate_rolling_sharpe(self, window: int = None) -> float:
        """
        Calculate rolling Sharpe ratio.
        
        Args:
            window: Lookback window (if None, uses self.lookback_window)
        
        Returns:
            Annualized Sharpe ratio
        """
        if len(self.returns_history) < 10:
            return 0.0
        
        window = window or min(len(self.returns_history), self.lookback_window)
        recent_returns = list(self.returns_history)[-window:]
        
        # Convert to pandas Series for easier calculation
        returns_series = pd.Series(recent_returns)
        
        # Calculate excess returns
        daily_rf = self.risk_free_rate / 252
        excess_returns = returns_series - daily_rf
        
        # Sharpe ratio
        if excess_returns.std() == 0:
            return 0.0
        
        sharpe = excess_returns.mean() / excess_returns.std()
        
        # Annualize (assuming daily data)
        annualized_sharpe = sharpe * np.sqrt(252)
        
        return float(annualized_sharpe)
    
    def calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown from equity curve.
        
        Returns:
            Maximum drawdown as a percentage (negative value)
        """
        if len(self.equity_history) < 2:
            return 0.0
        
        equity_array = np.array(self.equity_history)
        
        # Calculate running maximum
        running_max = np.maximum.accumulate(equity_array)
        
        # Calculate drawdown at each point
        drawdowns = (equity_array - running_max) / running_max
        
        # Maximum drawdown (most negative)
        max_dd = float(drawdowns.min())
        
        return max_dd * 100  # Convert to percentage
    
    def calculate_win_rate(self, recent_n: int = None) -> float:
        """
        Calculate win rate from recent trades.
        
        Args:
            recent_n: Number of recent trades to consider (if None, uses all)
        
        Returns:
            Win rate as a percentage
        """
        if not self.trades_history:
            return 0.0
        
        recent_trades = self.trades_history[-recent_n:] if recent_n else self.trades_history
        
        if not recent_trades:
            return 0.0
        
        wins = sum(1 for trade in recent_trades if trade['win'])
        win_rate = (wins / len(recent_trades)) * 100
        
        return float(win_rate)
    
    def calculate_profit_factor(self, recent_n: int = None) -> float:
        """
        Calculate profit factor (gross profit / gross loss).
        
        Args:
            recent_n: Number of recent trades to consider
        
        Returns:
            Profit factor (values > 1 indicate profitability)
        """
        if not self.trades_history:
            return 0.0
        
        recent_trades = self.trades_history[-recent_n:] if recent_n else self.trades_history
        
        if not recent_trades:
            return 0.0
        
        gross_profit = sum(trade['pnl'] for trade in recent_trades if trade['pnl'] > 0)
        gross_loss = abs(sum(trade['pnl'] for trade in recent_trades if trade['pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return float(gross_profit / gross_loss)
    
    def get_performance_summary(self, recent_window: int = None) -> Dict[str, float]:
        """
        Get a comprehensive performance summary.
        
        Args:
            recent_window: Window for recent metrics (if None, uses lookback_window)
        
        Returns:
            Dictionary with performance metrics
        """
        window = recent_window or self.lookback_window
        
        summary = {
            'sharpe_ratio': self.calculate_rolling_sharpe(window),
            'max_drawdown': self.calculate_max_drawdown(),
            'win_rate': self.calculate_win_rate(window),
            'profit_factor': self.calculate_profit_factor(window),
            'total_trades': len(self.trades_history),
            'current_equity': self.equity_history[-1] if self.equity_history else 0.0,
            'total_return': self._calculate_total_return(),
            'avg_return': self._calculate_avg_return(window),
            'volatility': self._calculate_volatility(window)
        }
        
        return summary
    
    def is_performance_degrading(
        self,
        sharpe_threshold: float = 0.5,
        drawdown_threshold: float = -15.0,
        lookback: int = 20
    ) -> bool:
        """
        Determine if strategy performance is degrading.
        
        Args:
            sharpe_threshold: Minimum acceptable Sharpe ratio
            drawdown_threshold: Maximum acceptable drawdown (%)
            lookback: Recent period to evaluate
        
        Returns:
            True if performance is degrading
        """
        if len(self.returns_history) < lookback:
            return False
        
        recent_sharpe = self.calculate_rolling_sharpe(lookback)
        current_drawdown = self.calculate_max_drawdown()
        
        # Check if performance is below thresholds
        is_degrading = (
            recent_sharpe < sharpe_threshold or
            current_drawdown < drawdown_threshold
        )
        
        return is_degrading
    
    def _calculate_total_return(self) -> float:
        """Calculate total return from equity curve."""
        if len(self.equity_history) < 2:
            return 0.0
        
        initial_equity = list(self.equity_history)[0]
        current_equity = list(self.equity_history)[-1]
        
        return ((current_equity - initial_equity) / initial_equity) * 100
    
    def _calculate_avg_return(self, window: int = None) -> float:
        """Calculate average return over window."""
        if not self.returns_history:
            return 0.0
        
        window = window or len(self.returns_history)
        recent_returns = list(self.returns_history)[-window:]
        
        return float(np.mean(recent_returns) * 100)
    
    def _calculate_volatility(self, window: int = None) -> float:
        """Calculate return volatility over window."""
        if len(self.returns_history) < 2:
            return 0.0
        
        window = window or len(self.returns_history)
        recent_returns = list(self.returns_history)[-window:]
        
        # Annualized volatility
        daily_vol = np.std(recent_returns)
        annual_vol = daily_vol * np.sqrt(252)
        
        return float(annual_vol * 100)
    
    def reset(self):
        """Reset all performance data."""
        self.returns_history.clear()
        self.equity_history.clear()
        self.trades_history.clear()
    
    def __str__(self) -> str:
        """String representation of current performance."""
        summary = self.get_performance_summary()
        return (
            f"Performance(Sharpe: {summary['sharpe_ratio']:.2f}, "
            f"Drawdown: {summary['max_drawdown']:.1f}%, "
            f"Win Rate: {summary['win_rate']:.1f}%)"
        )


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("📊 Performance Monitor Test")
    print("=" * 70)
    
    # Initialize monitor
    monitor = PerformanceMonitor(lookback_window=50)
    
    # Simulate trading performance
    print("\nSimulating trading performance...")
    
    initial_equity = 100000
    equity = initial_equity
    
    # Simulate 100 periods with varying returns
    np.random.seed(42)
    
    for i in range(100):
        # Simulate returns (mix of winning and losing periods)
        if i < 30:
            # Good performance period
            daily_return = np.random.normal(0.001, 0.01)
        elif i < 60:
            # Sideways period
            daily_return = np.random.normal(0, 0.008)
        else:
            # Declining performance
            daily_return = np.random.normal(-0.0005, 0.015)
        
        equity *= (1 + daily_return)
        monitor.update(equity, daily_return)
        
        # Simulate some trades
        if i % 10 == 0 and i > 0:
            entry = equity * 0.99
            exit = equity
            monitor.add_trade(entry, exit, direction=1)
    
    # Get performance summary
    print("\n" + "=" * 70)
    print("Performance Summary")
    print("=" * 70)
    
    summary = monitor.get_performance_summary()
    
    for metric, value in summary.items():
        if isinstance(value, float):
            if 'rate' in metric or 'return' in metric:
                print(f"  {metric.replace('_', ' ').title()}: {value:.2f}%")
            else:
                print(f"  {metric.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"  {metric.replace('_', ' ').title()}: {value}")
    
    # Test performance degradation detection
    print("\n" + "=" * 70)
    print("Performance Degradation Check")
    print("=" * 70)
    
    is_degrading = monitor.is_performance_degrading()
    print(f"  Performance Degrading: {'YES ⚠️' if is_degrading else 'NO ✅'}")
    
    print(f"\n  {monitor}")
    
    print("\n✅ Performance Monitor test completed!")
