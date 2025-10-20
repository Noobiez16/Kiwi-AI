"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🥝 KIWI AI TRADING SYSTEM v1.0                           ║
║                    Advanced Adaptive Algorithmic Trading                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Main Application Launcher

This is the ONLY file you need to run!

Usage:
    python run_kiwi.py

Features:
- Visual Web Dashboard with Settings Manager
- Daily and Real-Time trading modes
- Easy configuration (no coding required!)
- Real-time monitoring
- All-in-one execution

"""

import os
import sys
import time
import signal
import threading
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import deque
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import streamlit first
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("❌ Streamlit not installed. Install with: pip install streamlit")
    sys.exit(1)

# Import Kiwi AI modules
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

# Try to import real-time streaming
try:
    import alpaca_trade_api as tradeapi
    REALTIME_AVAILABLE = True
except ImportError:
    REALTIME_AVAILABLE = False

# Initialize logger
logger = TradingLogger()

# Global state for trading system
class TradingState:
    """Global trading state manager."""
    def __init__(self):
        self.running = False
        self.mode = None  # 'daily' or 'realtime'
        self.thread = None
        self.broker = None
        self.positions = []
        self.account = {}
        self.current_regime = "Unknown"
        self.current_strategy = "None"
        self.performance_metrics = {}
        self.recent_trades = []
        self.log_messages = []
        self.error_log = []  # Track all errors
        
trading_state = TradingState()


# ============================================================================
# ERROR TRACKING & LOGGING
# ============================================================================

def log_error(error_type: str, message: str, exception: Exception = None, context: dict = None):
    """
    Log errors with full context for debugging.
    
    Args:
        error_type: Type of error (e.g., 'API', 'Trading', 'Configuration')
        message: Human-readable error message
        exception: The exception object (if available)
        context: Additional context (dict with relevant variables)
    """
    import traceback
    
    error_entry = {
        'timestamp': datetime.now(),
        'type': error_type,
        'message': message,
        'exception': str(exception) if exception else None,
        'traceback': traceback.format_exc() if exception else None,
        'context': context or {},
        'severity': 'ERROR'
    }
    
    # Add to global error log
    trading_state.error_log.insert(0, error_entry)
    
    # Keep only last 100 errors
    if len(trading_state.error_log) > 100:
        trading_state.error_log = trading_state.error_log[:100]
    
    # Log to file
    logger.logger.error(f"[{error_type}] {message}")
    if exception:
        logger.logger.error(f"Exception: {exception}")
        logger.logger.error(f"Traceback:\n{traceback.format_exc()}")
    if context:
        logger.logger.error(f"Context: {context}")
    
    return error_entry


def log_warning(warning_type: str, message: str, context: dict = None):
    """Log warnings (non-critical issues)."""
    warning_entry = {
        'timestamp': datetime.now(),
        'type': warning_type,
        'message': message,
        'exception': None,
        'traceback': None,
        'context': context or {},
        'severity': 'WARNING'
    }
    
    trading_state.error_log.insert(0, warning_entry)
    
    if len(trading_state.error_log) > 100:
        trading_state.error_log = trading_state.error_log[:100]
    
    logger.logger.warning(f"[{warning_type}] {message}")
    if context:
        logger.logger.warning(f"Context: {context}")
    
    return warning_entry


def clear_error_log():
    """Clear all errors from the log."""
    trading_state.error_log = []
    logger.logger.info("Error log cleared")


# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

def load_settings():
    """Load settings from session state or config."""
    try:
        if 'settings' not in st.session_state:
            st.session_state.settings = {
                'alpaca_key': getattr(config, 'ALPACA_KEY', ''),
                'alpaca_secret': getattr(config, 'ALPACA_SECRET', ''),
                'is_paper_trading': getattr(config, 'IS_PAPER_TRADING', True),
                'initial_capital': float(getattr(config, 'INITIAL_CAPITAL', 100000)),
                'max_risk_per_trade': float(getattr(config, 'MAX_RISK_PER_TRADE', 0.02)),
                'max_position_size': float(getattr(config, 'MAX_POSITION_SIZE', 0.1)),
                'trading_symbol': getattr(config, 'TRADING_SYMBOL', 'SPY'),
                'check_interval': int(getattr(config, 'TRADING_INTERVAL', 60)),
                'realtime_timeframe': '1Min'
            }
        return st.session_state.settings
    except Exception as e:
        log_error('Configuration', 'Failed to load settings', e, {
            'config_module': str(config.__dict__)
        })
        # Return default settings
        return {
            'alpaca_key': '',
            'alpaca_secret': '',
            'is_paper_trading': True,
            'initial_capital': 100000.0,
            'max_risk_per_trade': 0.02,
            'max_position_size': 0.1,
            'trading_symbol': 'SPY',
            'check_interval': 60,
            'realtime_timeframe': '1Min'
        }


def save_settings(settings):
    """Save settings to session state and config file."""
    try:
        st.session_state.settings = settings
        
        # Update config module
        config.ALPACA_KEY = settings['alpaca_key']
        config.ALPACA_SECRET = settings['alpaca_secret']
        config.IS_PAPER_TRADING = settings['is_paper_trading']
        config.INITIAL_CAPITAL = settings['initial_capital']
        config.MAX_RISK_PER_TRADE = settings['max_risk_per_trade']
        config.MAX_POSITION_SIZE = settings['max_position_size']
        config.TRADING_SYMBOL = settings['trading_symbol']
        config.TRADING_INTERVAL = settings['check_interval']
        
        # Try to save to .env file
        try:
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            env_content = f"""# Kiwi AI Configuration
# Broker API Keys
ALPACA_API_KEY={settings['alpaca_key']}
ALPACA_SECRET_KEY={settings['alpaca_secret']}
ALPACA_PAPER_TRADING={str(settings['is_paper_trading']).lower()}

# Trading Parameters
INITIAL_CAPITAL={settings['initial_capital']}
MAX_RISK_PER_TRADE={settings['max_risk_per_trade']}
MAX_POSITION_SIZE={settings['max_position_size']}
TRADING_SYMBOL={settings['trading_symbol']}
TRADING_INTERVAL={settings['check_interval']}
"""
            with open(env_path, 'w') as f:
                f.write(env_content)
            logger.logger.info("Settings saved to .env file successfully")
        except Exception as e:
            log_warning('Configuration', 'Could not save to .env file', {
                'env_path': env_path,
                'error': str(e)
            })
    except Exception as e:
        log_error('Configuration', 'Failed to save settings', e, {
            'settings': str(settings)
        })
        raise


def check_configuration():
    """Check if the system is properly configured."""
    settings = load_settings()
    if not settings['alpaca_key'] or settings['alpaca_key'] == "your_alpaca_api_key_here":
        return False
    if not settings['alpaca_secret'] or settings['alpaca_secret'] == "your_alpaca_secret_key_here":
        return False
    return True


# ============================================================================
# TRADING LOGIC - DAILY MODE
# ============================================================================

class KiwiAI:
    """Main Kiwi AI trading system for daily mode."""
    
    def __init__(self, settings: dict):
        """Initialize Kiwi AI trading system."""
        self.settings = settings
        self.symbol = settings['trading_symbol']
        self.interval_minutes = settings['check_interval']
        self.paper_trading = settings['is_paper_trading']
        
        logger.logger.info("=" * 80)
        logger.logger.info(" " * 25 + "🥝 KIWI AI STARTING UP 🥝")
        logger.logger.info("=" * 80)
        
        self._initialize_components()
        
        self.current_regime = None
        self.current_strategy_name = None
        self.position = None
        
        logger.logger.info("✅ Kiwi AI initialized successfully!")
    
    def _initialize_components(self):
        """Initialize all system components."""
        self.data_handler = DataHandler()
        self.regime_detector = RegimeDetector()
        self.performance_monitor = PerformanceMonitor()
        
        strategy_list = [
            TrendFollowingStrategy(),
            MeanReversionStrategy(),
            VolatilityBreakoutStrategy()
        ]
        
        self.strategy_selector = StrategySelector(strategy_list, self.regime_detector)
        self.strategies = self.strategy_selector.strategies
        
        self.broker = Broker(
            api_key=self.settings['alpaca_key'],
            secret_key=self.settings['alpaca_secret'],
            paper_trading=self.paper_trading,
            mock_mode=True
        )
        
        self.risk_manager = RiskManager(
            initial_capital=self.settings['initial_capital'],
            max_risk_per_trade=self.settings['max_risk_per_trade']
        )
        
        # Update global state
        trading_state.broker = self.broker
    
    def run_trading_loop(self):
        """Main trading loop."""
        logger.logger.info(f"🚀 Starting daily trading loop")
        
        while trading_state.running:
            try:
                loop_start = datetime.now()
                logger.logger.info(f"\n{'='*80}\n📊 Trading Loop | {loop_start.strftime('%Y-%m-%d %H:%M:%S')}\n{'='*80}")
                
                self._execute_trading_logic()
                
                # Update state
                trading_state.account = self.broker.get_account_info()
                trading_state.positions = self.broker.get_open_positions()
                trading_state.current_regime = self.current_regime or "Unknown"
                trading_state.current_strategy = self.current_strategy_name or "None"
                
                # Sleep until next interval
                elapsed = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, (self.interval_minutes * 60) - elapsed)
                
                logger.logger.info(f"⏰ Next check in {sleep_time/60:.1f} minutes")
                time.sleep(min(sleep_time, 10))  # Check every 10 seconds for stop signal
                
            except Exception as e:
                log_error('Trading Loop', 'Error in daily trading loop', e, {
                    'symbol': self.symbol,
                    'interval': self.interval_minutes,
                    'mode': 'daily',
                    'current_regime': self.current_regime,
                    'current_strategy': self.current_strategy_name
                })
                time.sleep(60)
        
        self._shutdown()
    
    def _execute_trading_logic(self):
        """Execute one iteration of trading logic."""
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        data = self.data_handler.fetch_historical_data(
            symbol=self.symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            timeframe="1D"
        )
        
        if data is None or len(data) < 50:
            logger.logger.warning("⚠️  Insufficient data")
            return
        
        # Detect regime
        regime = self.regime_detector.predict_regime(data)
        confidence = self.regime_detector.get_regime_confidence(data)
        
        if regime != self.current_regime:
            self.current_regime = regime
        
        logger.logger.info(f"📈 Regime: {regime} ({confidence.get(regime, 0):.1f}%)")
        
        # Select strategy
        selected_strategy, reason = self.strategy_selector.select_strategy(data)
        
        if selected_strategy.name != self.current_strategy_name:
            self.current_strategy_name = selected_strategy.name
        
        logger.logger.info(f"✅ Strategy: {selected_strategy.name}")
        
        # Generate signal
        signal = selected_strategy.generate_signals(data)
        
        if signal is None or len(signal) == 0:
            return
        
        latest_signal = signal.iloc[-1]
        logger.logger.info(f"📊 Signal: {latest_signal}")
        
        # Execute trade
        self._execute_trade(latest_signal, data)
    
    def _execute_trade(self, signal: int, data):
        """Execute trade based on signal."""
        try:
            current_price = data['close'].iloc[-1]
            account = self.broker.get_account_info()
            positions = self.broker.get_open_positions()
            
            has_position = any(pos['symbol'] == self.symbol for pos in positions)
            
            if signal == 1 and not has_position:  # BUY
                logger.logger.info("📈 BUY signal")
                
                try:
                    stop_loss = self.risk_manager.calculate_stop_loss(current_price, method='percentage', percentage=0.02)
                    qty, details = self.risk_manager.calculate_position_size(current_price, stop_loss, account['portfolio_value'])
                    
                    if qty > 0:
                        result = self.broker.place_order(self.symbol, qty, 'buy', 'market')
                        if result.get('success'):
                            logger.logger.info(f"✅ BUY order: {qty} shares @ ${current_price:.2f}")
                            trading_state.recent_trades.insert(0, {
                                'time': datetime.now(),
                                'symbol': self.symbol,
                                'action': 'BUY',
                                'qty': qty,
                                'price': current_price
                            })
                        else:
                            log_error('Order Execution', 'BUY order failed', None, {
                                'symbol': self.symbol,
                                'qty': qty,
                                'price': current_price,
                                'result': result
                            })
                    else:
                        log_warning('Order Sizing', 'Position size calculated as 0', {
                            'symbol': self.symbol,
                            'price': current_price,
                            'stop_loss': stop_loss,
                            'portfolio_value': account['portfolio_value']
                        })
                except Exception as e:
                    log_error('Order Execution', 'Error executing BUY order', e, {
                        'symbol': self.symbol,
                        'price': current_price,
                        'signal': signal
                    })
            
            elif signal == -1 and has_position:  # SELL
                logger.logger.info("📉 SELL signal")
                try:
                    result = self.broker.close_position(self.symbol)
                    if result.get('success'):
                        logger.logger.info("✅ Position closed")
                        trading_state.recent_trades.insert(0, {
                            'time': datetime.now(),
                            'symbol': self.symbol,
                            'action': 'SELL',
                            'qty': 0,
                            'price': current_price
                        })
                    else:
                        log_error('Order Execution', 'SELL order failed', None, {
                            'symbol': self.symbol,
                            'result': result
                        })
                except Exception as e:
                    log_error('Order Execution', 'Error executing SELL order', e, {
                        'symbol': self.symbol,
                        'price': current_price,
                        'signal': signal
                    })
        except Exception as e:
            log_error('Trade Execution', 'Critical error in trade execution', e, {
                'symbol': self.symbol,
                'signal': signal
            })
    
    def _shutdown(self):
        """Graceful shutdown."""
        logger.logger.info("🛑 Shutting down...")
        positions = self.broker.get_open_positions()
        if len(positions) > 0:
            self.broker.close_all_positions()
        logger.logger.info("✅ Shutdown complete")


# ============================================================================
# TRADING LOGIC - REAL-TIME MODE
# ============================================================================

def run_realtime_trading(settings: dict):
    """Run real-time trading mode."""
    if not REALTIME_AVAILABLE:
        logger.logger.error("❌ Real-time mode requires alpaca-trade-api")
        return
    
    logger.logger.info("🚀 Starting real-time mode")
    
    symbols = [settings['trading_symbol']]
    timeframe = settings['realtime_timeframe']
    
    # Initialize components
    broker = Broker(
        api_key=settings['alpaca_key'],
        secret_key=settings['alpaca_secret'],
        paper_trading=settings['is_paper_trading'],
        mock_mode=True
    )
    
    risk_manager = RiskManager(
        initial_capital=settings['initial_capital'],
        max_risk_per_trade=settings['max_risk_per_trade']
    )
    
    regime_detector = RegimeDetector()
    performance_monitor = PerformanceMonitor()
    data_handler = DataHandler()
    
    strategy_list = [
        TrendFollowingStrategy(),
        MeanReversionStrategy(),
        VolatilityBreakoutStrategy()
    ]
    
    strategy_selector = StrategySelector(strategy_list, regime_detector)
    
    trading_state.broker = broker
    
    # Track data
    bar_history = {symbol: deque(maxlen=500) for symbol in symbols}
    positions = {}
    last_signal_time = {}
    
    # Initialize WebSocket
    stream = tradeapi.Stream(
        settings['alpaca_key'],
        settings['alpaca_secret'],
        base_url='https://paper-api.alpaca.markets' if settings['is_paper_trading'] else 'https://api.alpaca.markets',
        data_feed='iex'
    )
    
    async def handle_bar(bar):
        """Process incoming bar data."""
        if not trading_state.running:
            return
        
        symbol = bar.symbol
        
        bar_history[symbol].append({
            'timestamp': bar.timestamp,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        })
        
        logger.logger.info(f"📊 {symbol}: ${bar.close:.2f}")
        
        if len(bar_history[symbol]) < 50:
            return
        
        # Check cooldown
        if symbol in last_signal_time:
            time_since = (datetime.now() - last_signal_time[symbol]).total_seconds()
            if time_since < 60:
                return
        
        try:
            df = pd.DataFrame(list(bar_history[symbol]))
            df.set_index('timestamp', inplace=True)
            
            regime = regime_detector.predict_regime(df)
            trading_state.current_regime = regime
            
            strategy, reason = strategy_selector.select_strategy(df)
            trading_state.current_strategy = strategy.__class__.__name__
            
            signal = strategy.generate_signals(df)
            
            if signal is not None and len(signal) > 0:
                latest_signal = signal.iloc[-1]
                
                if latest_signal == 1:  # BUY
                    logger.logger.info(f"📈 BUY signal for {symbol}")
                    last_signal_time[symbol] = datetime.now()
                elif latest_signal == -1:  # SELL
                    logger.logger.info(f"📉 SELL signal for {symbol}")
                    last_signal_time[symbol] = datetime.now()
            
            # Update state
            trading_state.account = broker.get_account_info()
            trading_state.positions = broker.get_open_positions()
            
        except Exception as e:
            logger.logger.error(f"Error: {e}")
    
    # Subscribe
    for symbol in symbols:
        stream.subscribe_bars(handle_bar, symbol)
    
    logger.logger.info("✅ WebSocket connected")
    
    try:
        stream.run()
    except:
        stream.stop()
        logger.logger.info("✅ Stream stopped")


# ============================================================================
# STREAMLIT DASHBOARD
# ============================================================================

def show_settings_page():
    """Display settings configuration page."""
    st.title("⚙️ Settings")
    st.markdown("---")
    
    settings = load_settings()
    
    with st.form("settings_form"):
        st.subheader("� Alpaca API Configuration")
        st.markdown("Get your free API keys at [alpaca.markets](https://alpaca.markets/)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            alpaca_key = st.text_input(
                "API Key",
                value=settings['alpaca_key'],
                type="password",
                help="Your Alpaca API key"
            )
        
        with col2:
            alpaca_secret = st.text_input(
                "Secret Key",
                value=settings['alpaca_secret'],
                type="password",
                help="Your Alpaca secret key"
            )
        
        is_paper = st.checkbox(
            "📄 Use Paper Trading (Recommended)",
            value=settings['is_paper_trading'],
            help="Paper trading uses fake money for testing. Uncheck for real money trading."
        )
        
        if not is_paper:
            st.error("⚠️ WARNING: Live trading will use REAL MONEY!")
        
        st.markdown("---")
        st.subheader("💰 Trading Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            initial_capital = st.number_input(
                "Initial Capital ($)",
                min_value=1000.0,
                max_value=10000000.0,
                value=settings['initial_capital'],
                step=1000.0,
                help="Starting account balance"
            )
            
            max_risk = st.slider(
                "Max Risk Per Trade (%)",
                min_value=0.5,
                max_value=5.0,
                value=settings['max_risk_per_trade'] * 100,
                step=0.1,
                help="Maximum percentage of capital to risk on a single trade"
            ) / 100
        
        with col2:
            max_position = st.slider(
                "Max Position Size (%)",
                min_value=5.0,
                max_value=50.0,
                value=settings['max_position_size'] * 100,
                step=5.0,
                help="Maximum percentage of capital in a single position"
            ) / 100
            
            trading_symbol = st.text_input(
                "Trading Symbol",
                value=settings['trading_symbol'],
                help="Stock symbol to trade (e.g., SPY, QQQ)"
            ).upper()
        
        st.markdown("---")
        st.subheader("⏰ Trading Intervals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            check_interval = st.number_input(
                "Daily Mode Check Interval (minutes)",
                min_value=1,
                max_value=1440,
                value=settings['check_interval'],
                help="How often to check for signals in daily mode"
            )
        
        with col2:
            realtime_timeframe = st.selectbox(
                "Real-Time Timeframe",
                options=['1Min', '5Min', '15Min', '1Hour'],
                index=['1Min', '5Min', '15Min', '1Hour'].index(settings['realtime_timeframe']),
                help="Bar timeframe for real-time mode"
            )
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            submitted = st.form_submit_button("� Save Settings", use_container_width=True)
        
        with col2:
            test_connection = st.form_submit_button("🔌 Test Connection", use_container_width=True)
    
    if submitted:
        try:
            new_settings = {
                'alpaca_key': alpaca_key,
                'alpaca_secret': alpaca_secret,
                'is_paper_trading': is_paper,
                'initial_capital': initial_capital,
                'max_risk_per_trade': max_risk,
                'max_position_size': max_position,
                'trading_symbol': trading_symbol,
                'check_interval': check_interval,
                'realtime_timeframe': realtime_timeframe
            }
            
            save_settings(new_settings)
            st.success("✅ Settings saved successfully!")
            logger.logger.info("Settings saved via UI")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to save settings: {e}")
            log_error('Settings', 'Failed to save settings from UI', e, {
                'trading_symbol': trading_symbol,
                'is_paper_trading': is_paper
            })
    
    if test_connection:
        with st.spinner("Testing connection..."):
            try:
                test_broker = Broker(
                    api_key=alpaca_key,
                    secret_key=alpaca_secret,
                    paper_trading=is_paper,
                    mock_mode=False
                )
                account = test_broker.get_account_info()
                
                st.success("✅ Connection successful!")
                st.info(f"Account Value: ${account.get('portfolio_value', 0):,.2f}")
                logger.logger.info("API connection test successful")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")
                log_error('API Connection', 'Failed to connect to Alpaca API', e, {
                    'paper_trading': is_paper,
                    'api_key_length': len(alpaca_key) if alpaca_key else 0
                })


def show_dashboard_page():
    """Display main trading dashboard."""
    st.title("🥝 Kiwi AI Trading Dashboard")
    st.markdown("---")
    
    settings = load_settings()
    
    # Show error notification if there are recent errors
    recent_errors = [e for e in trading_state.error_log if e['severity'] == 'ERROR']
    if recent_errors:
        st.error(f"⚠️ {len(recent_errors)} error(s) detected! Check the 🐛 Error Log tab for details.")
    
    if not check_configuration():
        st.error("⚠️ API keys not configured! Go to Settings tab to configure.")
        return
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "🟢" if trading_state.running else "⚪"
        st.metric("System Status", f"{status_color} {'Running' if trading_state.running else 'Stopped'}")
    
    with col2:
        mode_text = trading_state.mode.upper() if trading_state.mode else "IDLE"
        st.metric("Trading Mode", mode_text)
    
    with col3:
        paper_text = "PAPER" if settings['is_paper_trading'] else "LIVE"
        st.metric("Account Type", paper_text)
    
    with col4:
        st.metric("Last Update", datetime.now().strftime("%H:%M:%S"))
    
    st.markdown("---")
    
    # Account metrics
    if trading_state.broker:
        try:
            account = trading_state.broker.get_account_info()
            positions = trading_state.broker.get_open_positions()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                portfolio_value = account.get('portfolio_value', 0)
                st.metric(
                    "💰 Portfolio Value",
                    f"${portfolio_value:,.2f}",
                    delta=f"{((portfolio_value / settings['initial_capital']) - 1) * 100:.2f}%"
                )
            
            with col2:
                st.metric("💵 Cash", f"${account.get('cash', 0):,.2f}")
            
            with col3:
                st.metric("📍 Open Positions", len(positions))
            
            with col4:
                total_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
                st.metric(
                    "📈 Unrealized P&L",
                    f"${total_pl:.2f}",
                    delta=f"{(total_pl / portfolio_value * 100):.2f}%" if portfolio_value > 0 else "0%"
                )
            
            st.markdown("---")
            
            # Two columns: Market Intelligence + Positions
            left_col, right_col = st.columns([3, 2])
            
            with left_col:
                st.subheader("🧠 Market Intelligence")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    regime_color = {
                        'TREND': '🟢',
                        'SIDEWAYS': '🟡',
                        'VOLATILE': '🔴',
                        'Unknown': '⚪'
                    }
                    st.markdown(f"### {regime_color.get(trading_state.current_regime, '⚪')} Regime: **{trading_state.current_regime}**")
                
                with col2:
                    st.markdown(f"### 🎯 Strategy: **{trading_state.current_strategy}**")
                
                st.markdown("---")
                
                st.subheader("📍 Open Positions")
                
                if len(positions) > 0:
                    positions_data = []
                    for pos in positions:
                        positions_data.append({
                            'Symbol': pos['symbol'],
                            'Quantity': pos['qty'],
                            'Entry': f"${pos['avg_entry_price']:.2f}",
                            'Current': f"${pos['current_price']:.2f}",
                            'Value': f"${pos['market_value']:.2f}",
                            'P&L': f"${pos['unrealized_pl']:.2f}",
                            'P&L %': f"{pos.get('unrealized_plpc', 0)*100:.2f}%"
                        })
                    
                    df = pd.DataFrame(positions_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No open positions")
            
            with right_col:
                st.subheader("📊 Trading Activity")
                
                if trading_state.recent_trades:
                    st.markdown("**Recent Trades:**")
                    for trade in trading_state.recent_trades[:5]:
                        action_icon = "📈" if trade['action'] == 'BUY' else "📉"
                        st.text(f"{action_icon} {trade['time'].strftime('%H:%M')} - {trade['action']} {trade['symbol']} @ ${trade['price']:.2f}")
                else:
                    st.info("No recent trades")
                
                st.markdown("---")
                st.subheader("🛡️ Risk Management")
                
                if trading_state.broker:
                    risk_manager = RiskManager(
                        initial_capital=settings['initial_capital'],
                        max_risk_per_trade=settings['max_risk_per_trade']
                    )
                    
                    risk_summary = risk_manager.get_risk_summary(
                        account,
                        {pos['symbol']: pos for pos in positions}
                    )
                    
                    st.metric("Drawdown", f"{risk_summary['drawdown_pct']:.2f}%")
                    st.metric("Portfolio Concentration", f"{risk_summary['portfolio_concentration']:.1f}%")
                    st.metric("Cash Position", f"{risk_summary['cash_pct']:.1f}%")
                    
                    status_color_map = {
                        'HEALTHY': '🟢',
                        'WARNING': '🟡',
                        'CRITICAL': '🔴'
                    }
                    st.markdown(f"**Status:** {status_color_map.get(risk_summary['risk_status'], '⚪')} {risk_summary['risk_status']}")
        
        except Exception as e:
            st.error(f"Error fetching account data: {e}")
    else:
        st.info("Start trading to see live data")


def show_control_page():
    """Display trading control panel."""
    st.title("🎮 Trading Control")
    st.markdown("---")
    
    settings = load_settings()
    
    if not check_configuration():
        st.error("⚠️ Please configure API keys in Settings first!")
        return
    
    st.subheader("🚀 Start Trading")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Daily Mode")
        st.markdown("""
        - Checks market at regular intervals
        - Uses daily bars for analysis
        - Good for swing trading
        - Lower resource usage
        """)
        
        if not trading_state.running:
            if st.button("▶️ Start Daily Mode", use_container_width=True, type="primary"):
                try:
                    trading_state.running = True
                    trading_state.mode = 'daily'
                    
                    def run_daily():
                        try:
                            kiwi = KiwiAI(settings)
                            kiwi.run_trading_loop()
                        except Exception as e:
                            log_error('Daily Mode', 'Critical error in daily mode thread', e, {
                                'settings': str(settings)
                            })
                            trading_state.running = False
                    
                    trading_state.thread = threading.Thread(target=run_daily, daemon=True)
                    trading_state.thread.start()
                    
                    st.success("✅ Daily mode started!")
                    logger.logger.info("Daily mode started via UI")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to start daily mode: {e}")
                    log_error('Daily Mode', 'Failed to start daily mode', e, {
                        'settings': str(settings)
                    })
                    trading_state.running = False
    
    with col2:
        st.markdown("### ⚡ Real-Time Mode")
        st.markdown("""
        - Live WebSocket data streaming
        - Analyzes minute-level bars
        - Instant signal generation
        - Perfect for day trading
        """)
        
        if not REALTIME_AVAILABLE:
            st.warning("Install alpaca-trade-api first:\n```pip install alpaca-trade-api```")
        elif not trading_state.running:
            if st.button("▶️ Start Real-Time Mode", use_container_width=True, type="primary"):
                try:
                    trading_state.running = True
                    trading_state.mode = 'realtime'
                    
                    def run_realtime():
                        try:
                            run_realtime_trading(settings)
                        except Exception as e:
                            log_error('Real-Time Mode', 'Critical error in real-time mode thread', e, {
                                'settings': str(settings)
                            })
                            trading_state.running = False
                    
                    trading_state.thread = threading.Thread(target=run_realtime, daemon=True)
                    trading_state.thread.start()
                    
                    st.success("✅ Real-time mode started!")
                    logger.logger.info("Real-time mode started via UI")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to start real-time mode: {e}")
                    log_error('Real-Time Mode', 'Failed to start real-time mode', e, {
                        'settings': str(settings)
                    })
                    trading_state.running = False
    
    st.markdown("---")
    
    # Stop button
    if trading_state.running:
        st.warning(f"🟢 System is running in **{trading_state.mode.upper()}** mode")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🛑 Stop Trading", use_container_width=True, type="secondary"):
                try:
                    trading_state.running = False
                    
                    if trading_state.broker:
                        try:
                            # Close all positions on stop
                            close_all = st.checkbox("Close all positions when stopping?", value=False)
                            if close_all:
                                trading_state.broker.close_all_positions()
                                st.info("✅ All positions closed")
                                logger.logger.info("All positions closed on stop")
                        except Exception as e:
                            st.error(f"Error closing positions: {e}")
                            log_error('Position Management', 'Error closing positions on stop', e)
                    
                    st.success("✅ Trading stopped!")
                    logger.logger.info("Trading stopped via UI")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error stopping trading: {e}")
                    log_error('Control', 'Error stopping trading', e)
    
    st.markdown("---")
    st.subheader("� Current Configuration")
    
    config_col1, config_col2 = st.columns(2)
    
    with config_col1:
        st.info(f"**Symbol:** {settings['trading_symbol']}")
        st.info(f"**Initial Capital:** ${settings['initial_capital']:,.0f}")
        st.info(f"**Max Risk/Trade:** {settings['max_risk_per_trade']*100:.1f}%")
    
    with config_col2:
        st.info(f"**Daily Interval:** {settings['check_interval']} min")
        st.info(f"**Real-Time Timeframe:** {settings['realtime_timeframe']}")
        st.info(f"**Trading Mode:** {'Paper' if settings['is_paper_trading'] else '🔴 LIVE'}")


def show_help_page():
    """Display help and documentation."""
    st.title("📖 Help & Documentation")
    st.markdown("---")
    
    st.markdown("""
    # 🥝 Kiwi AI Trading System
    
    Welcome to the Kiwi AI automated trading system! This guide will help you get started.
    
    ## 🚀 Quick Start
    
    1. **Configure Settings**: Go to the "Settings" tab and enter your Alpaca API keys
    2. **Test Connection**: Use the "Test Connection" button to verify your setup
    3. **Start Trading**: Go to "Control" tab and choose Daily or Real-Time mode
    4. **Monitor**: Watch the "Dashboard" tab for live updates
    
    ---
    
    ## 💡 Trading Modes
    
    ### 📊 Daily Mode
    - Checks market at regular intervals (default: 60 minutes)
    - Uses daily bars for technical analysis
    - Perfect for swing trading strategies
    - Lower resource usage and data costs
    - Recommended for beginners
    
    ### ⚡ Real-Time Mode
    - Live WebSocket data streaming
    - Analyzes 1-minute to 1-hour bars
    - Instant signal generation and execution
    - Perfect for day trading strategies
    - Requires `alpaca-trade-api` package
    - Higher resource usage
    
    ---
    
    ## 🛡️ Safety Features
    
    - **Paper Trading**: Test with fake money before going live (enabled by default)
    - **Risk Management**: Automatic position sizing and stop-loss calculation
    - **Regime Detection**: Adapts to different market conditions
    - **Performance Monitoring**: Tracks strategy performance and switches if needed
    
    ---
    
    ## ⚙️ Configuration
    
    All settings can be configured visually in the Settings tab:
    
    - **API Keys**: Your Alpaca API credentials
    - **Trading Mode**: Paper vs Live trading
    - **Capital**: Initial account balance
    - **Risk Parameters**: Max risk per trade, position size limits
    - **Trading Symbol**: Which stock to trade (e.g., SPY, QQQ)
    - **Intervals**: How often to check for signals
    
    ---
    
    ## 📊 Strategies
    
    Kiwi AI includes three adaptive strategies:
    
    1. **Trend Following**: Captures strong directional moves
    2. **Mean Reversion**: Profits from price reversals
    3. **Volatility Breakout**: Trades explosive moves
    
    The system automatically selects the best strategy based on current market regime.
    
    ---
    
    ## ⚠️ Important Notes
    
    - Always test with paper trading first!
    - Never risk more than you can afford to lose
    - Monitor the system regularly, especially in live mode
    - Market conditions can change rapidly
    - Past performance doesn't guarantee future results
    
    ---
    
    ## 🔗 Resources
    
    - **Alpaca API**: [alpaca.markets](https://alpaca.markets/)
    - **Documentation**: See README.md in project folder
    - **Support**: Check GitHub issues or documentation
    
    ---
    
    ## 💻 System Requirements
    
    - Python 3.8+
    - Internet connection
    - Alpaca brokerage account (free paper trading available)
    - Required packages: streamlit, pandas, numpy, scikit-learn
    - Optional: alpaca-trade-api (for real-time mode)
    
    """)
    
    st.markdown("---")
    st.success("💡 Tip: Start with paper trading and small position sizes to learn the system!")


def show_error_log_page():
    """Display error log viewer."""
    st.title("🐛 Error & Debug Log")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader(f"Total Errors/Warnings: {len(trading_state.error_log)}")
    
    with col2:
        if st.button("🔄 Refresh Log", use_container_width=True):
            st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Log", use_container_width=True):
            clear_error_log()
            st.success("Log cleared!")
            time.sleep(1)
            st.rerun()
    
    st.markdown("---")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect(
            "Severity",
            options=['ERROR', 'WARNING'],
            default=['ERROR', 'WARNING']
        )
    
    with col2:
        type_filter = st.multiselect(
            "Error Type",
            options=list(set([e['type'] for e in trading_state.error_log])) if trading_state.error_log else [],
            default=list(set([e['type'] for e in trading_state.error_log])) if trading_state.error_log else []
        )
    
    with col3:
        show_traceback = st.checkbox("Show Traceback", value=False)
    
    st.markdown("---")
    
    # Display errors
    if not trading_state.error_log:
        st.info("✅ No errors logged! System is running smoothly.")
    else:
        # Filter errors
        filtered_errors = [
            e for e in trading_state.error_log
            if e['severity'] in severity_filter and (not type_filter or e['type'] in type_filter)
        ]
        
        if not filtered_errors:
            st.info("No errors match the selected filters.")
        else:
            for idx, error in enumerate(filtered_errors):
                severity_color = {
                    'ERROR': '🔴',
                    'WARNING': '🟡'
                }
                
                with st.expander(
                    f"{severity_color.get(error['severity'], '⚪')} [{error['timestamp'].strftime('%H:%M:%S')}] {error['type']}: {error['message']}",
                    expanded=(idx == 0)  # Expand first error
                ):
                    # Error details
                    st.markdown(f"**Timestamp:** {error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                    st.markdown(f"**Severity:** {error['severity']}")
                    st.markdown(f"**Type:** {error['type']}")
                    st.markdown(f"**Message:** {error['message']}")
                    
                    if error['exception']:
                        st.markdown("---")
                        st.markdown("**Exception:**")
                        st.code(error['exception'], language='python')
                    
                    if error['context']:
                        st.markdown("---")
                        st.markdown("**Context:**")
                        st.json(error['context'])
                    
                    if show_traceback and error['traceback']:
                        st.markdown("---")
                        st.markdown("**Full Traceback:**")
                        st.code(error['traceback'], language='python')
                    
                    # Copy button
                    error_text = f"""
Timestamp: {error['timestamp']}
Severity: {error['severity']}
Type: {error['type']}
Message: {error['message']}
Exception: {error['exception']}
Context: {error['context']}
Traceback: {error['traceback']}
"""
                    st.markdown("---")
                    st.text_area("Copy Error Details:", error_text, height=100, key=f"error_{idx}")
    
    st.markdown("---")
    
    # Error statistics
    if trading_state.error_log:
        st.subheader("📊 Error Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Count by type
            type_counts = {}
            for error in trading_state.error_log:
                error_type = error['type']
                type_counts[error_type] = type_counts.get(error_type, 0) + 1
            
            st.markdown("**Errors by Type:**")
            for error_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                st.text(f"{error_type}: {count}")
        
        with col2:
            # Count by severity
            severity_counts = {}
            for error in trading_state.error_log:
                severity = error['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            st.markdown("**Errors by Severity:**")
            for severity, count in severity_counts.items():
                st.text(f"{severity}: {count}")
        
        # Recent error timeline
        st.markdown("---")
        st.markdown("**Recent Error Timeline:**")
        
        recent_errors = trading_state.error_log[:10]
        timeline_data = []
        
        for error in recent_errors:
            timeline_data.append({
                'Time': error['timestamp'].strftime('%H:%M:%S'),
                'Type': error['type'],
                'Severity': error['severity'],
                'Message': error['message'][:50] + '...' if len(error['message']) > 50 else error['message']
            })
        
        if timeline_data:
            df = pd.DataFrame(timeline_data)
            st.dataframe(df, use_container_width=True, hide_index=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="Kiwi AI Trading System",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Professional Trading Dashboard CSS with Liquid Animations
    st.markdown("""
        <style>
        /* Import Professional Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        /* Main App Background with Gradient */
        .stApp {
            background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
            background-attachment: fixed;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #0f0c29 100%);
            border-right: 1px solid rgba(0, 217, 255, 0.2);
        }
        
        [data-testid="stSidebar"] .stMarkdown {
            color: #e0e0e0;
        }
        
        /* Logo Area */
        [data-testid="stSidebar"] img {
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
            transition: transform 0.3s ease;
        }
        
        [data-testid="stSidebar"] img:hover {
            transform: scale(1.05);
        }
        
        /* Navigation Radio Buttons */
        .stRadio > div {
            gap: 8px;
        }
        
        .stRadio > div > label {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 12px 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            backdrop-filter: blur(10px);
        }
        
        .stRadio > div > label:hover {
            background: rgba(0, 217, 255, 0.15);
            border-color: rgba(0, 217, 255, 0.5);
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.2);
        }
        
        .stRadio > div > label[data-selected="true"] {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(76, 175, 254, 0.2) 100%);
            border-color: #00d9ff;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.4);
        }
        
        /* Metric Cards with Glass Effect */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
            color: #00d9ff;
            text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        }
        
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        [data-testid="stMetric"]:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(0, 217, 255, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 217, 255, 0.2);
        }
        
        /* Buttons with Liquid Animation */
        .stButton > button {
            background: linear-gradient(135deg, #00d9ff 0%, #4cafff 100%);
            color: #ffffff;
            border: none;
            border-radius: 12px;
            padding: 12px 32px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .stButton > button::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.6s, height 0.6s;
        }
        
        .stButton > button:hover::before {
            width: 300px;
            height: 300px;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 217, 255, 0.5);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Success/Warning/Error Buttons */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #00d9ff 0%, #4cafff 100%);
        }
        
        .stButton > button[kind="secondary"] {
            background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
        }
        
        /* Text Inputs with Glow Effect */
        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            color: #ffffff;
            padding: 12px 16px;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            background: rgba(255, 255, 255, 0.08);
            border-color: #00d9ff;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
        }
        
        /* Sliders */
        .stSlider > div > div > div {
            background: rgba(0, 217, 255, 0.2);
        }
        
        .stSlider > div > div > div > div {
            background: linear-gradient(90deg, #00d9ff 0%, #4cafff 100%);
        }
        
        /* Checkboxes */
        .stCheckbox > label {
            color: #e0e0e0;
            transition: color 0.3s ease;
        }
        
        .stCheckbox > label:hover {
            color: #00d9ff;
        }
        
        /* Tables with Hover Effects */
        .dataframe {
            background: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px;
            overflow: hidden;
        }
        
        .dataframe thead tr th {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(76, 175, 254, 0.2) 100%) !important;
            color: #00d9ff !important;
            font-weight: 600;
            border-bottom: 2px solid rgba(0, 217, 255, 0.5) !important;
        }
        
        .dataframe tbody tr {
            transition: all 0.3s ease;
        }
        
        .dataframe tbody tr:hover {
            background: rgba(0, 217, 255, 0.1) !important;
            transform: scale(1.01);
        }
        
        /* Expander with Animation */
        .streamlit-expanderHeader {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            background: rgba(0, 217, 255, 0.1);
            border-color: rgba(0, 217, 255, 0.3);
        }
        
        /* Headers with Gradient */
        h1, h2, h3 {
            color: #ffffff;
            font-weight: 700;
            background: linear-gradient(135deg, #00d9ff 0%, #4cafff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Status Indicators */
        .status-running {
            color: #00ff88;
            animation: pulse 2s infinite;
        }
        
        .status-stopped {
            color: #ff6b6b;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        /* Info/Success/Warning/Error Messages */
        .stAlert {
            border-radius: 12px;
            border-left: 4px solid;
            backdrop-filter: blur(10px);
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 12px 24px;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(0, 217, 255, 0.1);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.2) 0%, rgba(76, 175, 254, 0.2) 100%);
            border-bottom: 2px solid #00d9ff;
        }
        
        /* Progress Bars */
        .stProgress > div > div {
            background: linear-gradient(90deg, #00d9ff 0%, #4cafff 100%);
            border-radius: 10px;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #00d9ff 0%, #4cafff 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #4cafff 0%, #00d9ff 100%);
        }
        
        /* Custom Card Class */
        .trading-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        
        .trading-card:hover {
            border-color: rgba(0, 217, 255, 0.3);
            box-shadow: 0 8px 32px rgba(0, 217, 255, 0.2);
            transform: translateY(-4px);
        }
        
        /* System Info Text */
        .stText {
            color: #b0b0b0;
        }
        
        /* Divider */
        hr {
            border-color: rgba(255, 255, 255, 0.1);
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        # Professional Header with Trading Chart Icon
        st.markdown("""
            <div style='text-align: center; padding: 20px 0;'>
                <div style='font-size: 48px; margin-bottom: 10px;'>📈</div>
                <h1 style='margin: 0; font-size: 28px; font-weight: 700;'>Kiwi AI</h1>
                <p style='margin: 5px 0 0 0; color: #00d9ff; font-size: 12px; font-weight: 500;'>TRADING SYSTEM</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        page = st.radio(
            "Navigation",
            ["Dashboard", "Control", "Settings", "Error Log", "Help"],
            label_visibility="collapsed",
            format_func=lambda x: {
                "Dashboard": "📊  Dashboard",
                "Control": "▶  Control",
                "Settings": "⚙  Settings",
                "Error Log": "⚠  Error Log",
                "Help": "ℹ  Help"
            }[x]
        )
        
        st.markdown("---")
        
        # System info with professional styling
        st.markdown("### System Info")
        settings = load_settings()
        
        # Status indicator with animation
        status_class = "status-running" if trading_state.running else "status-stopped"
        status_text = "RUNNING" if trading_state.running else "IDLE"
        status_icon = "●" if trading_state.running else "○"
        
        st.markdown(f"""
            <div style='padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; margin: 10px 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>VERSION</span>
                    <span style='color: #ffffff; font-weight: 600;'>1.0.0</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>MODE</span>
                    <span style='color: #00d9ff; font-weight: 600;'>{'PAPER' if settings['is_paper_trading'] else 'LIVE'}</span>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>STATUS</span>
                    <span class='{status_class}' style='font-weight: 600; font-size: 14px;'>{status_icon} {status_text}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Real-time features status
        st.markdown("### Features")
        
        rt_status = "ENABLED" if REALTIME_AVAILABLE else "DISABLED"
        rt_color = "#00ff88" if REALTIME_AVAILABLE else "#ff6b6b"
        
        st.markdown(f"""
            <div style='padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; margin: 10px 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>REAL-TIME</span>
                    <span style='color: {rt_color}; font-weight: 600;'>{rt_status}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>STREAMLIT</span>
                    <span style='color: #00ff88; font-weight: 600;'>ENABLED</span>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>ERRORS</span>
                    <span style='color: {'#ff6b6b' if len(trading_state.error_log) > 0 else '#00ff88'}; font-weight: 600;'>{len(trading_state.error_log)}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if not REALTIME_AVAILABLE:
            st.caption("Install: pip install alpaca-trade-api")
        
        st.markdown("---")
        st.caption("© 2025 Kiwi AI Trading System")
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Control":
        show_control_page()
    elif page == "Settings":
        show_settings_page()
    elif page == "Error Log":
        show_error_log_page()
    elif page == "Help":
        show_help_page()
    
    # Auto-refresh for live updates (every 5 seconds when running)
    if trading_state.running:
        time.sleep(5)
        st.rerun()


if __name__ == "__main__":
    # Print startup message
    print("\n" + "=" * 80)
    print("=" * 80)
    print(f"{'🥝 KIWI AI TRADING SYSTEM 🥝':^80}")
    print("=" * 80)
    print(f"{'Starting Web Dashboard...':^80}")
    print("=" * 80)
    print()
    print("  🌐 Dashboard will open at: http://localhost:8501")
    print("  📖 Use the sidebar to navigate between pages")
    print("  ⚙️  Configure your API keys in the Settings page")
    print("  🎮 Start trading from the Control page")
    print()
    print("  Press Ctrl+C to stop the application")
    print()
    print("=" * 80 + "\n")
    
    main()
