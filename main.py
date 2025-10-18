"""
Main Entry Point for Kiwi_AI Live Trading System

This script runs the main trading loop:
1. Fetches latest market data
2. Runs MetaStrategy logic (regime detection + strategy selection)
3. Calculates position size with risk management
4. Places orders through broker interface
5. Logs all actions

Run with: python main.py
"""

import time
import sys
import signal
from datetime import datetime, timedelta
from typing import Dict, Optional

# Import Kiwi_AI modules
import config
from data.data_handler import DataHandler
from meta_ai.regime_detector import RegimeDetector
from meta_ai.performance_monitor import PerformanceMonitor
from meta_ai.strategy_selector import StrategySelector
from execution.broker_interface import Broker
from execution.risk_manager import RiskManager
from strategies.trend_following import TrendFollowingStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.volatility_breakout import VolatilityBreakoutStrategy
from utils.logger import TradingLogger

# Initialize logger
logger = TradingLogger()

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    global running
    logger.logger.info("🛑 Shutdown signal received. Closing positions...")
    running = False


class KiwiAI:
    """
    Main Kiwi_AI trading system.
    
    Integrates all components:
    - Data fetching
    - Regime detection
    - Strategy selection
    - Risk management
    - Order execution
    """
    
    def __init__(self, symbol: str = "SPY", interval_minutes: int = 60, 
                 paper_trading: bool = True, mock_mode: bool = False):
        """
        Initialize Kiwi_AI trading system.
        
        Args:
            symbol: Trading symbol
            interval_minutes: Loop interval in minutes
            paper_trading: Use paper trading mode
            mock_mode: Use mock broker (no real API calls)
        """
        self.symbol = symbol
        self.interval_minutes = interval_minutes
        self.paper_trading = paper_trading
        self.mock_mode = mock_mode
        
        logger.logger.info("=" * 80)
        logger.logger.info(" " * 25 + "🥝 KIWI_AI STARTING UP 🥝")
        logger.logger.info("=" * 80)
        logger.logger.info(f"Symbol: {symbol} | Interval: {interval_minutes}min | "
                          f"Mode: {'PAPER' if paper_trading else 'LIVE'}")
        
        # Initialize components
        self._initialize_components()
        
        # Track state
        self.current_regime = None
        self.current_strategy_name = None
        self.position = None
        self.last_trade_time = None
        
        logger.logger.info("✅ Kiwi_AI initialized successfully!")
    
    def _initialize_components(self):
        """Initialize all system components."""
        logger.logger.info("Initializing components...")
        
        # Data handler
        self.data_handler = DataHandler()
        
        # AI Brain
        self.regime_detector = RegimeDetector()
        self.performance_monitor = PerformanceMonitor()
        
        # Strategies
        self.strategies = {
            'Trend Following': TrendFollowingStrategy(),
            'Mean Reversion': MeanReversionStrategy(),
            'Volatility Breakout': VolatilityBreakoutStrategy()
        }
        
        # Strategy selector
        self.strategy_selector = StrategySelector(self.strategies)
        
        # Execution
        self.broker = Broker(
            api_key=config.ALPACA_KEY,
            secret_key=config.ALPACA_SECRET,
            paper_trading=self.paper_trading,
            mock_mode=self.mock_mode
        )
        
        self.risk_manager = RiskManager(
            initial_capital=float(config.INITIAL_CAPITAL),
            max_risk_per_trade=float(config.MAX_RISK_PER_TRADE)
        )
    
    def run_trading_loop(self):
        """
        Main trading loop.
        
        Runs continuously at specified intervals.
        """
        global running
        
        logger.logger.info(f"🚀 Starting trading loop (interval: {self.interval_minutes} minutes)")
        
        while running:
            try:
                loop_start = datetime.now()
                
                logger.logger.info("\n" + "=" * 80)
                logger.logger.info(f"📊 Trading Loop | {loop_start.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.logger.info("=" * 80)
                
                # Execute trading logic
                self._execute_trading_logic()
                
                # Calculate sleep time
                loop_duration = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, (self.interval_minutes * 60) - loop_duration)
                
                if running:
                    logger.logger.info(f"💤 Sleeping for {sleep_time/60:.1f} minutes...")
                    time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.logger.info("🛑 Keyboard interrupt received")
                running = False
            except Exception as e:
                logger.log_error(e, "Main trading loop")
                time.sleep(60)  # Sleep 1 minute on error
        
        # Cleanup
        self._shutdown()
    
    def _execute_trading_logic(self):
        """Execute one iteration of trading logic."""
        
        # Step 1: Fetch latest data
        logger.logger.info("1️⃣  Fetching market data...")
        data = self.data_handler.fetch_data(
            self.symbol,
            timeframe="1D",
            period_days=252  # 1 year
        )
        
        if data is None or len(data) < 50:
            logger.logger.warning("⚠️  Insufficient data, skipping this iteration")
            return
        
        logger.logger.info(f"   ✅ Fetched {len(data)} bars")
        
        # Step 2: Detect market regime
        logger.logger.info("2️⃣  Detecting market regime...")
        regime = self.regime_detector.predict_regime(data)
        confidence = self.regime_detector.get_regime_confidence()
        
        if regime != self.current_regime:
            if self.current_regime:
                logger.log_regime_change(self.current_regime, regime)
            self.current_regime = regime
        
        logger.logger.info(f"   📈 Current Regime: {regime}")
        logger.logger.info(f"   🎯 Confidence: {confidence.get(regime, 0):.1f}%")
        
        # Step 3: Select optimal strategy
        logger.logger.info("3️⃣  Selecting strategy...")
        selected_strategy = self.strategy_selector.select_strategy(
            regime,
            confidence,
            self.performance_monitor
        )
        
        if selected_strategy != self.current_strategy_name:
            if self.current_strategy_name:
                logger.log_strategy_switch(
                    self.current_strategy_name,
                    selected_strategy,
                    f"Regime: {regime}"
                )
            self.current_strategy_name = selected_strategy
        
        logger.logger.info(f"   🎯 Selected Strategy: {selected_strategy}")
        
        # Step 4: Generate trading signal
        logger.logger.info("4️⃣  Generating trading signal...")
        strategy = self.strategies[selected_strategy]
        signal = strategy.generate_signals(data)
        
        if signal is None or len(signal) == 0:
            logger.logger.warning("⚠️  No signal generated")
            return
        
        latest_signal = signal.iloc[-1]
        logger.logger.info(f"   📊 Signal: {latest_signal} "
                          f"(1=BUY, -1=SELL, 0=HOLD)")
        
        # Step 5: Execute trading decision
        logger.logger.info("5️⃣  Executing trading decision...")
        self._execute_trade(latest_signal, data, selected_strategy, regime)
        
        # Step 6: Monitor performance
        logger.logger.info("6️⃣  Monitoring performance...")
        positions = self.broker.get_open_positions()
        account = self.broker.get_account_info()
        
        logger.logger.info(f"   💰 Account Value: ${account.get('portfolio_value', 0):,.2f}")
        logger.logger.info(f"   📍 Open Positions: {len(positions)}")
        
        # Update performance monitor
        if len(positions) > 0:
            for pos in positions:
                self.performance_monitor.record_trade(
                    entry_price=pos['avg_entry_price'],
                    exit_price=pos['current_price'],
                    quantity=pos['qty']
                )
        
        performance_status = self.performance_monitor.check_performance_degradation()
        logger.logger.info(f"   📈 Performance: {performance_status}")
        
        # Log risk summary
        risk_summary = self.risk_manager.get_risk_summary(account, {
            pos['symbol']: pos for pos in positions
        })
        logger.logger.info(f"   🛡️  Portfolio Risk: {risk_summary['drawdown_pct']:.2f}% drawdown | "
                          f"{risk_summary['portfolio_concentration']:.1f}% invested")
    
    def _execute_trade(self, signal: int, data, strategy_name: str, regime: str):
        """
        Execute trade based on signal.
        
        Args:
            signal: Trading signal (1=BUY, -1=SELL, 0=HOLD)
            data: Market data DataFrame
            strategy_name: Name of active strategy
            regime: Current market regime
        """
        current_price = data['close'].iloc[-1]
        account = self.broker.get_account_info()
        positions = self.broker.get_open_positions()
        
        # Check if we have a position
        has_position = any(pos['symbol'] == self.symbol for pos in positions)
        
        if signal == 1 and not has_position:  # BUY
            logger.logger.info("   📈 BUY signal detected")
            
            # Calculate stop loss
            stop_loss = self.risk_manager.calculate_stop_loss(
                current_price,
                method='percentage',
                percentage=0.02
            )
            
            # Calculate position size
            qty, details = self.risk_manager.calculate_position_size(
                current_price,
                stop_loss,
                account['portfolio_value']
            )
            
            if qty > 0:
                # Validate trade
                is_valid, reason = self.risk_manager.validate_trade(
                    self.symbol,
                    qty,
                    current_price,
                    account['portfolio_value'],
                    {pos['symbol']: pos for pos in positions}
                )
                
                if is_valid:
                    # Place order
                    order = self.broker.place_order(
                        self.symbol,
                        qty,
                        'buy',
                        'market'
                    )
                    
                    if 'error' not in order:
                        logger.logger.info(f"   ✅ Order placed: {order['order_id']}")
                        self.last_trade_time = datetime.now()
                    else:
                        logger.logger.error(f"   ❌ Order failed: {order['error']}")
                else:
                    logger.logger.warning(f"   ⚠️  Trade rejected: {reason}")
            else:
                logger.logger.warning("   ⚠️  Position size too small, skipping trade")
        
        elif signal == -1 and has_position:  # SELL
            logger.logger.info("   📉 SELL signal detected")
            
            # Close position
            result = self.broker.close_position(self.symbol)
            
            if result.get('success', True):
                logger.logger.info("   ✅ Position closed")
                self.last_trade_time = datetime.now()
            else:
                logger.logger.error(f"   ❌ Close failed: {result.get('error', 'Unknown')}")
        
        else:
            logger.logger.info("   ⏸️  HOLD - No action taken")
    
    def _shutdown(self):
        """Graceful shutdown procedure."""
        logger.logger.info("\n" + "=" * 80)
        logger.logger.info("🛑 Shutting down Kiwi_AI...")
        logger.logger.info("=" * 80)
        
        # Close all positions
        positions = self.broker.get_open_positions()
        if len(positions) > 0:
            logger.logger.info(f"Closing {len(positions)} open positions...")
            self.broker.close_all_positions()
        
        # Final summary
        account = self.broker.get_account_info()
        logger.logger.info(f"📊 Final Account Value: ${account.get('portfolio_value', 0):,.2f}")
        
        logger.logger.info("✅ Shutdown complete. Goodbye!")


def main():
    """Main entry point."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Check if we're in paper trading mode
    paper_trading = config.IS_PAPER_TRADING
    
    if not paper_trading:
        response = input("⚠️  WARNING: You are about to run in LIVE mode. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    # Initialize and run Kiwi_AI
    kiwi = KiwiAI(
        symbol="SPY",
        interval_minutes=60,  # Run every hour
        paper_trading=paper_trading,
        mock_mode=True  # Set to False to use real broker API
    )
    
    kiwi.run_trading_loop()


if __name__ == "__main__":
    main()
