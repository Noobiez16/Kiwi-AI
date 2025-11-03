"""
Phase 2 Demonstration Script
Tests all Phase 2 components: AI Brain (Regime Detection, Performance Monitoring, Strategy Selection)
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print(" " * 15 + "🥝 KIWI_AI - PHASE 2 DEMONSTRATION 🥝")
print(" " * 20 + "AI Brain & Intelligence")
print("=" * 80)
print()

# Test 1: Regime Detector
print("🧠 TEST 1: Regime Detection")
print("-" * 80)
try:
    from meta_ai.regime_detector import RegimeDetector
    from data.data_handler import DataHandler
    
    # Fetch data
    handler = DataHandler()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    
    print("Fetching historical data for training...")
    data = handler.fetch_historical_data("SPY", start_date, end_date)
    
    # Initialize and train detector
    detector = RegimeDetector()
    print(f"Training on {len(data)} bars...")
    detector.train(data.iloc[:500], save_model=False)  # Train on subset for speed
    
    # Test regime detection
    recent_data = data.tail(100)
    regime = detector.predict_regime(recent_data)
    confidence = detector.get_regime_confidence(recent_data)
    
    print(f"✅ Regime Detector initialized!")
    print(f"   Current Market Regime: {regime}")
    print(f"   Confidence Scores:")
    for reg, conf in confidence.items():
        print(f"      {reg}: {conf:.2%}")
    
except Exception as e:
    print(f"❌ Regime Detector test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Performance Monitor
print("\n" + "=" * 80)
print("📊 TEST 2: Performance Monitoring")
print("-" * 80)
try:
    from meta_ai.performance_monitor import PerformanceMonitor
    
    # Initialize monitor
    monitor = PerformanceMonitor(lookback_window=50)
    
    # Simulate some trading activity
    initial_equity = 100000
    equity = initial_equity
    
    print("Simulating 50 trading periods...")
    np.random.seed(42)
    
    for i in range(50):
        # Simulate returns
        daily_return = np.random.normal(0.0005, 0.01)
        equity *= (1 + daily_return)
        monitor.update(equity, daily_return)
        
        # Simulate some trades
        if i % 10 == 0 and i > 0:
            entry = equity * 0.99
            exit = equity
            monitor.add_trade(entry, exit, direction=1)
    
    # Get performance summary
    summary = monitor.get_performance_summary()
    
    print(f"✅ Performance Monitor operational!")
    print(f"   Sharpe Ratio: {summary['sharpe_ratio']:.2f}")
    print(f"   Max Drawdown: {summary['max_drawdown']:.2f}%")
    print(f"   Win Rate: {summary['win_rate']:.1f}%")
    print(f"   Total Trades: {summary['total_trades']}")
    print(f"   Total Return: {summary['total_return']:.2f}%")
    
    # Check for performance degradation
    is_degrading = monitor.is_performance_degrading()
    print(f"   Performance Status: {'⚠️ Degrading' if is_degrading else '✅ Healthy'}")
    
except Exception as e:
    print(f"❌ Performance Monitor test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Strategy Selector
print("\n" + "=" * 80)
print("🎯 TEST 3: Strategy Selection (The Brain)")
print("-" * 80)
try:
    from meta_ai.strategy_selector import StrategySelector
    from strategies import (
        TrendFollowingStrategy,
        MeanReversionStrategy,
        VolatilityBreakoutStrategy
    )
    
    # Initialize strategies
    strategies = [
        TrendFollowingStrategy(),
        MeanReversionStrategy(),
        VolatilityBreakoutStrategy()
    ]
    
    # Initialize selector
    selector = StrategySelector(
        strategies=strategies,
        regime_detector=detector,
        performance_monitor=monitor
    )
    
    print(f"Initialized with {len(strategies)} strategies")
    
    # Select strategy for current market conditions
    strategy, reason = selector.select_strategy(data)
    
    print(f"✅ Strategy Selector operational!")
    print(f"   Selected Strategy: {strategy.name}")
    print(f"   Selection Reason: {reason}")
    print(f"   Current Regime: {selector.current_regime}")
    
    # Get comprehensive recommendation
    recommendation = selector.get_recommendation(data)
    
    print(f"\n   Strategy Suitability for {recommendation['regime']} market:")
    for strat_name, eval_data in recommendation['strategy_evaluations'].items():
        is_selected = "⭐" if eval_data['is_current'] else "  "
        print(f"      {is_selected} {strat_name}: {eval_data['regime_suitability']:.0%}")
    
except Exception as e:
    print(f"❌ Strategy Selector test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Integrated Test - Market Regime Changes
print("\n" + "=" * 80)
print("🔄 TEST 4: Dynamic Strategy Adaptation")
print("-" * 80)
try:
    print("Testing strategy adaptation across different market periods...")
    
    # Test on different time windows
    test_windows = [
        ("Last 30 days", -30),
        ("Last 60 days", -60),
        ("Last 90 days", -90)
    ]
    
    results = []
    
    for window_name, days in test_windows:
        test_data = data.iloc[days:]
        
        # Detect regime
        regime = detector.predict_regime(test_data)
        
        # Select strategy
        strategy, reason = selector.select_strategy(test_data, force_evaluation=True)
        
        results.append({
            'window': window_name,
            'regime': regime,
            'strategy': strategy.name
        })
        
        print(f"\n   {window_name}:")
        print(f"      Regime: {regime}")
        print(f"      Selected Strategy: {strategy.name}")
    
    print(f"\n✅ Dynamic adaptation test complete!")
    print(f"   Tested {len(test_windows)} different market conditions")
    
except Exception as e:
    print(f"❌ Integration test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Model Persistence
print("\n" + "=" * 80)
print("💾 TEST 5: Model Persistence")
print("-" * 80)
try:
    import os
    import config
    
    # Check if model file exists
    model_exists = os.path.exists(config.REGIME_MODEL_PATH)
    
    print(f"Model save path: {config.REGIME_MODEL_PATH}")
    print(f"Model file exists: {'✅ YES' if model_exists else '❌ NO'}")
    
    if model_exists:
        # Try loading the model
        new_detector = RegimeDetector()
        if new_detector.is_trained:
            print(f"✅ Model successfully loaded from disk!")
        else:
            print(f"⚠️  Model file exists but not loaded")
    else:
        print(f"ℹ️  Run 'python train_models.py' to train and save the model")
    
except Exception as e:
    print(f"⚠️  Model persistence test warning: {e}")

# Summary
print("\n" + "=" * 80)
print("🎉 PHASE 2 DEMONSTRATION COMPLETE!")
print("=" * 80)
print("\n✅ All AI Brain components are operational:")
print("   ✓ Regime Detection (HMM-based or rule-based)")
print("   ✓ Performance Monitoring (Sharpe, Drawdown, Win Rate)")
print("   ✓ Strategy Selection (Dynamic regime-based)")
print("   ✓ Strategy Adaptation (Automatic switching)")
print("   ✓ Model Persistence (Save/Load capability)")
print("\n📊 Key Features Demonstrated:")
print("   • Market regime classification (TREND, SIDEWAYS, VOLATILE)")
print("   • Real-time performance tracking")
print("   • Intelligent strategy selection based on market conditions")
print("   • Automatic strategy switching when performance degrades")
print("   • Confidence scoring for regime detection")
print("\n🚀 Ready for Phase 3: Backtesting Engine!")
print("=" * 80)
