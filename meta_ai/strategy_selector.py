"""
Strategy Selector Module
The "brain" that decides which strategy to activate based on regime and performance.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

# When run as script, import from parent modules
if __name__ == "__main__":
    from meta_ai.regime_detector import RegimeDetector
    from meta_ai.performance_monitor import PerformanceMonitor
    from strategies.base_strategy import BaseStrategy
    from utils.logger import get_logger
else:
    from .regime_detector import RegimeDetector
    from .performance_monitor import PerformanceMonitor
    from strategies import BaseStrategy
    from utils.logger import get_logger


class StrategySelector:
    """
    Meta-strategy that dynamically selects the best strategy based on:
    1. Current market regime
    2. Strategy performance
    3. Regime-strategy suitability matrix
    """
    
    def __init__(
        self,
        strategies: List[BaseStrategy],
        regime_detector: RegimeDetector,
        performance_monitor: PerformanceMonitor = None
    ):
        """
        Initialize the Strategy Selector.
        
        Args:
            strategies: List of available trading strategies
            regime_detector: RegimeDetector instance
            performance_monitor: PerformanceMonitor instance (optional)
        """
        self.strategies = {s.name: s for s in strategies}
        self.regime_detector = regime_detector
        self.performance_monitor = performance_monitor or PerformanceMonitor()
        
        self.current_strategy = None
        self.current_regime = None
        self.strategy_history = []
        
        self.logger = get_logger("kiwi_ai.selector")
        
        # Performance thresholds for strategy switching
        self.min_sharpe = 0.5
        self.max_drawdown = -15.0
        self.min_bars_before_switch = 20  # Minimum bars to evaluate a strategy
        
        self.bars_with_current_strategy = 0
    
    def select_strategy(
        self,
        data: pd.DataFrame,
        force_evaluation: bool = False
    ) -> Tuple[BaseStrategy, str]:
        """
        Select the best strategy based on current conditions.
        
        Args:
            data: Recent market data
            force_evaluation: Force strategy re-evaluation even if recent
        
        Returns:
            Tuple of (selected_strategy, reason_for_selection)
        """
        # Detect current regime
        self.current_regime = self.regime_detector.predict_regime(data)
        regime_confidence = self.regime_detector.get_regime_confidence(data)
        
        self.logger.info(f"Current Regime: {self.current_regime}")
        
        # First time selection
        if self.current_strategy is None:
            strategy = self._select_by_regime(self.current_regime)
            reason = f"Initial selection for {self.current_regime} regime"
            self.current_strategy = strategy
            self.bars_with_current_strategy = 0
            self._log_selection(strategy, reason)
            return strategy, reason
        
        # Increment counter
        self.bars_with_current_strategy += 1
        
        # Don't switch too frequently (let strategy stabilize)
        if not force_evaluation and self.bars_with_current_strategy < self.min_bars_before_switch:
            return self.current_strategy, "Maintaining current strategy (evaluation period)"
        
        # Check if current strategy is performing poorly
        if self.performance_monitor.is_performance_degrading(
            sharpe_threshold=self.min_sharpe,
            drawdown_threshold=self.max_drawdown
        ):
            self.logger.warning("Current strategy performance is degrading")
            strategy = self._select_by_regime(self.current_regime)
            
            if strategy.name != self.current_strategy.name:
                reason = "Performance degradation detected"
                self.current_strategy = strategy
                self.bars_with_current_strategy = 0
                self._log_selection(strategy, reason)
                return strategy, reason
        
        # Check if regime has changed significantly
        if self._regime_changed():
            self.logger.info(f"Regime change detected: {self.current_regime}")
            strategy = self._select_by_regime(self.current_regime)
            
            if strategy.name != self.current_strategy.name:
                reason = f"Regime changed to {self.current_regime}"
                self.current_strategy = strategy
                self.bars_with_current_strategy = 0
                self._log_selection(strategy, reason)
                return strategy, reason
        
        # No reason to switch
        return self.current_strategy, "Maintaining current strategy (performing well)"
    
    def _select_by_regime(self, regime: str) -> BaseStrategy:
        """
        Select the most suitable strategy for a given regime.
        
        Args:
            regime: Market regime ('TREND', 'SIDEWAYS', 'VOLATILE')
        
        Returns:
            Best strategy for the regime
        """
        # Get suitability scores for all strategies
        scores = {}
        for strategy_name, strategy in self.strategies.items():
            if hasattr(strategy, 'get_regime_suitability'):
                scores[strategy_name] = strategy.get_regime_suitability(regime)
            else:
                scores[strategy_name] = 0.5  # Default neutral score
        
        # Select strategy with highest suitability
        best_strategy_name = max(scores, key=scores.get)
        best_score = scores[best_strategy_name]
        
        self.logger.info(f"Strategy suitability scores for {regime}: {scores}")
        self.logger.info(f"Selected: {best_strategy_name} (score: {best_score:.2f})")
        
        return self.strategies[best_strategy_name]
    
    def _regime_changed(self) -> bool:
        """
        Check if regime has changed significantly.
        
        Returns:
            True if regime has changed
        """
        if len(self.strategy_history) == 0:
            return True
        
        last_regime = self.strategy_history[-1]['regime']
        return last_regime != self.current_regime
    
    def _log_selection(self, strategy: BaseStrategy, reason: str):
        """
        Log strategy selection for tracking.
        
        Args:
            strategy: Selected strategy
            reason: Reason for selection
        """
        selection_record = {
            'strategy': strategy.name,
            'regime': self.current_regime,
            'reason': reason,
            'performance': self.performance_monitor.get_performance_summary()
        }
        
        self.strategy_history.append(selection_record)
        
        self.logger.info(f"Strategy Selected: {strategy.name}")
        self.logger.info(f"Reason: {reason}")
    
    def get_current_strategy(self) -> Optional[BaseStrategy]:
        """
        Get the currently active strategy.
        
        Returns:
            Current strategy or None
        """
        return self.current_strategy
    
    def get_selection_history(self) -> List[Dict]:
        """
        Get the history of strategy selections.
        
        Returns:
            List of selection records
        """
        return self.strategy_history
    
    def evaluate_all_strategies(
        self,
        data: pd.DataFrame
    ) -> Dict[str, Dict]:
        """
        Evaluate all strategies on current data.
        
        Args:
            data: Market data for evaluation
        
        Returns:
            Dictionary with strategy evaluations
        """
        evaluations = {}
        
        for strategy_name, strategy in self.strategies.items():
            # Calculate indicators
            data_with_indicators = strategy.calculate_indicators(data.copy())
            
            # Generate signals
            signals = strategy.generate_signals(data_with_indicators)
            
            # Count signals
            num_signals = (signals != 0).sum()
            
            # Get regime suitability
            suitability = strategy.get_regime_suitability(self.current_regime)
            
            evaluations[strategy_name] = {
                'signals_generated': num_signals,
                'regime_suitability': suitability,
                'is_current': strategy_name == (self.current_strategy.name if self.current_strategy else None)
            }
        
        return evaluations
    
    def get_recommendation(
        self,
        data: pd.DataFrame
    ) -> Dict:
        """
        Get a comprehensive recommendation for strategy selection.
        
        Args:
            data: Current market data
        
        Returns:
            Dictionary with recommendation details
        """
        # Detect regime
        regime = self.regime_detector.predict_regime(data)
        regime_confidence = self.regime_detector.get_regime_confidence(data)
        
        # Evaluate strategies
        evaluations = self.evaluate_all_strategies(data)
        
        # Get performance summary
        performance = self.performance_monitor.get_performance_summary()
        
        # Select best strategy
        best_strategy = self._select_by_regime(regime)
        
        recommendation = {
            'regime': regime,
            'regime_confidence': regime_confidence,
            'recommended_strategy': best_strategy.name,
            'current_strategy': self.current_strategy.name if self.current_strategy else None,
            'should_switch': best_strategy.name != (self.current_strategy.name if self.current_strategy else None),
            'strategy_evaluations': evaluations,
            'current_performance': performance
        }
        
        return recommendation


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("🧠 Strategy Selector Test")
    print("=" * 70)
    
    # Import required modules
    from data.data_handler import DataHandler
    from strategies import (
        TrendFollowingStrategy,
        MeanReversionStrategy,
        VolatilityBreakoutStrategy
    )
    from datetime import datetime, timedelta
    
    # Fetch data
    handler = DataHandler()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print("\nFetching market data...")
    data = handler.fetch_historical_data("SPY", start_date, end_date)
    
    # Initialize components
    print("\nInitializing components...")
    
    # Strategies
    strategies = [
        TrendFollowingStrategy(),
        MeanReversionStrategy(),
        VolatilityBreakoutStrategy()
    ]
    
    # Regime detector
    regime_detector = RegimeDetector()
    
    # Performance monitor
    performance_monitor = PerformanceMonitor()
    
    # Strategy selector
    selector = StrategySelector(
        strategies=strategies,
        regime_detector=regime_detector,
        performance_monitor=performance_monitor
    )
    
    # Test strategy selection
    print("\n" + "=" * 70)
    print("Testing Strategy Selection")
    print("=" * 70)
    
    # Test on different periods
    test_periods = [
        ("Recent 30 days", -30),
        ("Recent 60 days", -60),
        ("Recent 90 days", -90)
    ]
    
    for period_name, days in test_periods:
        print(f"\n{period_name}:")
        test_data = data.iloc[days:]
        
        strategy, reason = selector.select_strategy(test_data)
        
        print(f"  Selected Strategy: {strategy.name}")
        print(f"  Reason: {reason}")
        print(f"  Current Regime: {selector.current_regime}")
    
    # Get comprehensive recommendation
    print("\n" + "=" * 70)
    print("Strategy Recommendation Report")
    print("=" * 70)
    
    recommendation = selector.get_recommendation(data)
    
    print(f"\nCurrent Regime: {recommendation['regime']}")
    print(f"Regime Confidence:")
    for regime, conf in recommendation['regime_confidence'].items():
        print(f"  {regime}: {conf:.2%}")
    
    print(f"\nRecommended Strategy: {recommendation['recommended_strategy']}")
    print(f"Should Switch: {recommendation['should_switch']}")
    
    print(f"\nStrategy Evaluations:")
    for strat_name, eval_data in recommendation['strategy_evaluations'].items():
        current_marker = " ⭐" if eval_data['is_current'] else ""
        print(f"  {strat_name}{current_marker}:")
        print(f"    Regime Suitability: {eval_data['regime_suitability']:.2%}")
        print(f"    Signals Generated: {eval_data['signals_generated']}")
    
    print("\n✅ Strategy Selector test completed!")
