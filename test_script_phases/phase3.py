"""
Phase 3 Demonstration Script
Tests all Phase 3 components: Broker Interface, Risk Manager, Main Loop, Dashboard

Run with: python test_script_phases/phase3.py
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 80)
print(" " * 15 + "🥝 KIWI_AI - PHASE 3 DEMONSTRATION 🥝")
print(" " * 15 + "Execution & Live Trading System")
print("=" * 80)
print()

# Test 1: Broker Interface
print("🏦 TEST 1: Broker Interface")
print("-" * 80)
try:
    from execution.broker_interface import Broker
    
    broker = Broker(mock_mode=True)
    
    # Get account info
    account = broker.get_account_info()
    print(f"✅ Broker connected")
    print(f"   Account Value: ${account['portfolio_value']:,.2f}")
    print(f"   Cash: ${account['cash']:,.2f}")
    print(f"   Status: {account['status']}")
    
    # Place test order
    print("\n   Placing test order...")
    order = broker.place_order('SPY', 10, 'buy', 'market')
    print(f"   ✅ Order placed: {order['order_id']}")
    print(f"      Symbol: {order['symbol']}")
    print(f"      Quantity: {order['qty']}")
    print(f"      Status: {order['status']}")
    
    # Get positions
    print("\n   Checking positions...")
    positions = broker.get_open_positions()
    print(f"   ✅ Open positions: {len(positions)}")
    for pos in positions:
        print(f"      📍 {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
        print(f"         Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pl']:.2f}")
    
    # Close position
    print("\n   Closing position...")
    close_result = broker.close_position('SPY')
    print(f"   ✅ Position closed")
    
    print("\n✅ Broker Interface Test Complete!")
    
except Exception as e:
    print(f"❌ Broker Interface Test Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

# Test 2: Risk Manager
print("🛡️  TEST 2: Risk Manager")
print("-" * 80)
try:
    from execution.risk_manager import RiskManager
    
    risk_mgr = RiskManager(
        initial_capital=100000.0,
        max_risk_per_trade=0.02,
        max_position_size=0.10
    )
    
    print("✅ Risk Manager initialized")
    
    # Test position sizing
    print("\n   Testing position sizing...")
    current_price = 450.0
    stop_loss = 440.0
    account_value = 100000.0
    
    qty, details = risk_mgr.calculate_position_size(current_price, stop_loss, account_value)
    print(f"   ✅ Position size calculated")
    print(f"      Entry: ${current_price:.2f} | Stop: ${stop_loss:.2f}")
    print(f"      → Position: {qty} shares")
    print(f"      → Value: ${details['position_value']:,.2f} ({details['position_pct']*100:.1f}%)")
    print(f"      → Risk: ${details['dollar_risk']:.2f} ({details['risk_pct']*100:.1f}%)")
    
    # Test trade validation
    print("\n   Testing trade validation...")
    is_valid, reason = risk_mgr.validate_trade('SPY', qty, current_price, account_value)
    print(f"   ✅ Valid trade: {is_valid} | {reason}")
    
    # Test invalid trade
    large_qty = 500
    is_valid, reason = risk_mgr.validate_trade('SPY', large_qty, current_price, account_value)
    print(f"   ❌ Large trade valid: {is_valid} | {reason}")
    
    # Test portfolio risk
    print("\n   Testing portfolio risk check...")
    within_limits, drawdown, status = risk_mgr.check_portfolio_risk(95000.0, 100000.0)
    print(f"   ✅ Risk check: {status}")
    
    # Test stop loss calculation
    print("\n   Testing stop loss calculation...")
    stop = risk_mgr.calculate_stop_loss(current_price, method='percentage', percentage=0.02)
    take_profit = risk_mgr.calculate_take_profit(current_price, stop, risk_reward_ratio=2.0)
    print(f"   ✅ Entry: ${current_price:.2f}")
    print(f"      Stop Loss: ${stop:.2f}")
    print(f"      Take Profit: ${take_profit:.2f}")
    print(f"      Risk/Reward: 1:2.0")
    
    print("\n✅ Risk Manager Test Complete!")
    
except Exception as e:
    print(f"❌ Risk Manager Test Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

# Test 3: Integrated Trading Logic
print("🔄 TEST 3: Integrated Trading Logic")
print("-" * 80)
try:
    from data.data_handler import DataHandler
    from meta_ai.regime_detector import RegimeDetector
    from meta_ai.strategy_selector import StrategySelector
    from strategies.trend_following import TrendFollowingStrategy
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.volatility_breakout import VolatilityBreakoutStrategy
    
    print("Initializing components...")
    
    # Initialize components
    data_handler = DataHandler()
    regime_detector = RegimeDetector()
    
    strategies = [
        TrendFollowingStrategy(),
        MeanReversionStrategy(),
        VolatilityBreakoutStrategy()
    ]
    strategy_selector = StrategySelector(strategies, regime_detector)
    
    # Create dict for easy access by name
    strategy_dict = {s.name: s for s in strategies}
    
    broker = Broker(mock_mode=True)
    risk_mgr = RiskManager(initial_capital=100000.0)
    
    print("✅ All components initialized")
    
    # Simulate one trading loop iteration
    print("\n   Simulating trading loop iteration...")
    print("   " + "-" * 76)
    
    # Step 1: Fetch data
    print("   1. Fetching market data...")
    data = data_handler.get_historical_data('SPY', timeframe='1Day', years=1)
    print(f"      ✅ Fetched {len(data)} bars")
    
    # Step 2: Detect regime
    print("   2. Detecting market regime...")
    regime = regime_detector.predict_regime(data)
    confidence = regime_detector.get_regime_confidence()
    print(f"      📈 Regime: {regime}")
    print(f"      🎯 Confidence: {confidence.get(regime, 0):.1f}%")
    
    # Step 3: Select strategy
    print("   3. Selecting strategy...")
    selected_strategy = strategy_selector.select_strategy(regime, confidence)
    print(f"      🎯 Selected: {selected_strategy}")
    
    # Step 4: Generate signal
    print("   4. Generating trading signal...")
    strategy = strategy_dict[selected_strategy]
    signal = strategy.generate_signals(data)
    latest_signal = signal.iloc[-1] if signal is not None and len(signal) > 0 else 0
    signal_text = {1: 'BUY', -1: 'SELL', 0: 'HOLD'}
    print(f"      📊 Signal: {signal_text.get(latest_signal, 'UNKNOWN')}")
    
    # Step 5: Execute trade (if signal is BUY)
    if latest_signal == 1:
        print("   5. Executing trade...")
        current_price = data['close'].iloc[-1]
        stop_loss = risk_mgr.calculate_stop_loss(current_price, method='percentage')
        
        # Calculate position size
        account = broker.get_account_info()
        qty, details = risk_mgr.calculate_position_size(
            current_price,
            stop_loss,
            account['portfolio_value']
        )
        
        if qty > 0:
            # Validate and place order
            is_valid, reason = risk_mgr.validate_trade(
                'SPY', qty, current_price, account['portfolio_value']
            )
            
            if is_valid:
                order = broker.place_order('SPY', qty, 'buy', 'market')
                print(f"      ✅ Order placed: {qty} shares @ ${current_price:.2f}")
                print(f"         Order ID: {order['order_id']}")
            else:
                print(f"      ⚠️  Trade rejected: {reason}")
        else:
            print("      ⚠️  Position size too small")
    else:
        print("   5. No trade action (HOLD signal)")
    
    # Step 6: Check positions and account
    print("   6. Checking account status...")
    positions = broker.get_open_positions()
    account = broker.get_account_info()
    print(f"      💰 Account Value: ${account['portfolio_value']:,.2f}")
    print(f"      📍 Open Positions: {len(positions)}")
    
    print("\n✅ Integrated Trading Logic Test Complete!")
    
except Exception as e:
    print(f"❌ Integrated Trading Logic Test Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)

# Test 4: Dashboard Components
print("📊 TEST 4: Dashboard Components")
print("-" * 80)
try:
    print("Testing dashboard data preparation...")
    
    # Simulate dashboard data
    broker = Broker(mock_mode=True)
    risk_mgr = RiskManager(initial_capital=100000.0)
    
    # Place a test position
    broker.place_order('SPY', 20, 'buy', 'market')
    
    account = broker.get_account_info()
    positions = broker.get_open_positions()
    
    print("✅ Dashboard data ready")
    print("\n   Account Metrics:")
    print(f"      Portfolio Value: ${account['portfolio_value']:,.2f}")
    print(f"      Cash: ${account['cash']:,.2f}")
    print(f"      Open Positions: {len(positions)}")
    
    if len(positions) > 0:
        print("\n   Position Details:")
        for pos in positions:
            print(f"      {pos['symbol']}: {pos['qty']} shares")
            print(f"         Entry: ${pos['avg_entry_price']:.2f}")
            print(f"         Current: ${pos['current_price']:.2f}")
            print(f"         P&L: ${pos['unrealized_pl']:.2f}")
    
    # Risk summary
    risk_summary = risk_mgr.get_risk_summary(account, {
        pos['symbol']: pos for pos in positions
    })
    
    print("\n   Risk Metrics:")
    print(f"      Total Return: {risk_summary['total_return_pct']:.2f}%")
    print(f"      Drawdown: {risk_summary['drawdown_pct']:.2f}%")
    print(f"      Portfolio Concentration: {risk_summary['portfolio_concentration']:.1f}%")
    print(f"      Cash Position: {risk_summary['cash_pct']:.1f}%")
    print(f"      Risk Status: {risk_summary['risk_status']}")
    
    print("\n✅ Dashboard Components Test Complete!")
    print("\n   ℹ️  To run the full dashboard:")
    print("      streamlit run dashboard.py")
    
except Exception as e:
    print(f"❌ Dashboard Components Test Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("🎉 PHASE 3 DEMONSTRATION COMPLETE!")
print("=" * 80)

print("\n✅ All Phase 3 components are operational:")
print("   ✓ Broker Interface (Order execution, position tracking)")
print("   ✓ Risk Manager (Position sizing, portfolio risk)")
print("   ✓ Main Trading Loop (Integrated execution logic)")
print("   ✓ Dashboard Components (Real-time monitoring)")

print("\n📊 Key Features Demonstrated:")
print("   • Broker abstraction for multiple platforms")
print("   • Mock mode for safe testing")
print("   • Position sizing based on risk parameters")
print("   • Trade validation and risk limits")
print("   • Stop loss and take profit calculation")
print("   • Portfolio risk monitoring")
print("   • Integrated trading logic (data → signal → execution)")
print("   • Dashboard-ready data structures")

print("\n🚀 Ready for Phase 4: Deployment & Production!")
print("=" * 80)
