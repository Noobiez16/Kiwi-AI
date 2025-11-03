"""
Phase 1 Demonstration Script
Tests all Phase 1 components of the Kiwi_AI system.
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print(" " * 20 + "🥝 KIWI_AI - PHASE 1 DEMONSTRATION 🥝")
print("=" * 80)
print()

# Test 1: Configuration
print("📋 TEST 1: Configuration Module")
print("-" * 80)
try:
    import config
    from utils.config_loader import print_config_summary, create_directories
    
    # Create required directories
    create_directories()
    
    print("\n✅ Configuration loaded successfully!")
    print(f"   - Paper Trading: {config.IS_PAPER_TRADING}")
    print(f"   - Initial Capital: ${config.INITIAL_CAPITAL:,.2f}")
    print(f"   - Max Risk: {config.MAX_RISK_PER_TRADE*100:.1f}%")
    
except Exception as e:
    print(f"❌ Configuration test failed: {e}")
    sys.exit(1)

# Test 2: Logger
print("\n" + "=" * 80)
print("📝 TEST 2: Logging System")
print("-" * 80)
try:
    from utils.logger import setup_logger, TradingLogger
    
    logger = setup_logger("demo", level="INFO")
    trade_logger = TradingLogger("demo.trading")
    
    logger.info("Logger initialized successfully")
    trade_logger.log_signal("Test Strategy", 1, 0.85)
    
    print("✅ Logging system operational!")
    
except Exception as e:
    print(f"❌ Logger test failed: {e}")
    sys.exit(1)

# Test 3: Data Handler
print("\n" + "=" * 80)
print("📊 TEST 3: Data Handler")
print("-" * 80)
try:
    from data.data_handler import DataHandler
    
    handler = DataHandler()
    
    # Fetch sample data
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"Fetching data for SPY from {start_date} to {end_date}...")
    df = handler.fetch_historical_data("SPY", start_date, end_date)
    
    print(f"✅ Fetched {len(df)} bars successfully!")
    print(f"   - Date range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"   - Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    
    # Add technical indicators
    df_with_indicators = handler.add_technical_indicators(df)
    print(f"✅ Added technical indicators")
    print(f"   - SMA_20, SMA_50, SMA_200")
    print(f"   - RSI_14, Volatility, Returns")
    
except Exception as e:
    print(f"❌ Data handler test failed: {e}")
    sys.exit(1)

# Test 4: Strategies
print("\n" + "=" * 80)
print("🎯 TEST 4: Trading Strategies")
print("-" * 80)

try:
    from strategies import (
        TrendFollowingStrategy,
        MeanReversionStrategy,
        VolatilityBreakoutStrategy
    )
    
    # Initialize strategies
    trend_strategy = TrendFollowingStrategy()
    mean_rev_strategy = MeanReversionStrategy()
    vol_breakout_strategy = VolatilityBreakoutStrategy()
    
    strategies = [trend_strategy, mean_rev_strategy, vol_breakout_strategy]
    
    print(f"Initialized {len(strategies)} strategies:")
    for strategy in strategies:
        print(f"   ✅ {strategy.name}")
    
    # Test signal generation
    print("\nTesting signal generation on real data...")
    
    for strategy in strategies:
        # Calculate indicators
        df_strat = strategy.calculate_indicators(df.copy())
        
        # Generate signals
        signals = strategy.generate_signals(df_strat)
        
        num_signals = (signals != 0).sum()
        num_buys = (signals == 1).sum()
        num_sells = (signals == -1).sum()
        
        print(f"\n   {strategy.name}:")
        print(f"      - Total signals: {num_signals}")
        print(f"      - Buy signals: {num_buys}")
        print(f"      - Sell signals: {num_sells}")
        
        # Show regime suitability
        print(f"      - Best for: ", end="")
        max_regime = max(['TREND', 'SIDEWAYS', 'VOLATILE'], 
                        key=lambda r: strategy.get_regime_suitability(r))
        print(f"{max_regime} markets")
    
    print("\n✅ All strategies operational!")
    
except Exception as e:
    print(f"❌ Strategy test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Strategy Comparison
print("\n" + "=" * 80)
print("📈 TEST 5: Strategy Performance Comparison")
print("-" * 80)

try:
    # Simple backtest simulation
    print("Running simple comparison on recent data...")
    
    results = []
    
    for strategy in strategies:
        df_test = strategy.calculate_indicators(df.copy())
        signals = strategy.generate_signals(df_test)
        
        # Simple simulation: Buy on signal=1, sell on signal=-1
        position = 0
        entry_price = 0
        trades = []
        
        for i, (date, row) in enumerate(df_test.iterrows()):
            signal = signals.iloc[i]
            price = row['close']
            
            if signal == 1 and position == 0:
                # Buy
                position = 1
                entry_price = price
            elif signal == -1 and position == 1:
                # Sell
                pnl = (price - entry_price) / entry_price
                trades.append(pnl)
                position = 0
        
        if len(trades) > 0:
            avg_return = np.mean(trades) * 100
            win_rate = sum(1 for t in trades if t > 0) / len(trades) * 100
        else:
            avg_return = 0
            win_rate = 0
        
        results.append({
            'strategy': strategy.name,
            'num_trades': len(trades),
            'avg_return': avg_return,
            'win_rate': win_rate
        })
    
    print("\nResults:")
    print("-" * 80)
    for result in results:
        print(f"   {result['strategy']}:")
        print(f"      - Trades: {result['num_trades']}")
        print(f"      - Avg Return: {result['avg_return']:.2f}%")
        print(f"      - Win Rate: {result['win_rate']:.1f}%")
    
    print("\n✅ Performance comparison complete!")
    
except Exception as e:
    print(f"❌ Performance comparison failed: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 80)
print("🎉 PHASE 1 DEMONSTRATION COMPLETE!")
print("=" * 80)
print("\n✅ All core components are operational:")
print("   ✓ Configuration management")
print("   ✓ Logging system")
print("   ✓ Data handling and caching")
print("   ✓ Technical indicator calculation")
print("   ✓ Three trading strategies implemented")
print("   ✓ Signal generation working")
print("\n🚀 Ready to proceed to Phase 2: AI Brain & Backtesting Engine!")
print("=" * 80)
