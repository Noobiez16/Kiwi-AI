"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                    🥝 KIWI AI TRADING SYSTEM v2.0                           ║
║          Advanced Real-Time Algorithmic Trading with TradingView            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Main Application Launcher

This is the ONLY file you need to run!

Usage:
    streamlit run run_kiwi.py

Features:
- 🔴 Auto-Start Real-Time Trading
- 📊 TradingView Charts Integration
- 🌍 Multi-Asset Support (Stocks, Forex, Crypto, Indices)
- 🧠 AI-Powered Market Analysis
- 🛡️ Advanced Risk Management
- 📈 Professional Web Dashboard
- ⚙️ Easy Configuration (no coding required!)

"""

import os
print("Script execution started...")
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
import plotly.graph_objects as go

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import streamlit first
try:
    import streamlit as st
    import streamlit.components.v1 as components
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

# Global state for trading system - using Streamlit session state to persist across reruns
class TradingState:
    """Global trading state manager."""
    def __init__(self):
        # Check if already initialized in session state
        if 'initialized' not in st.session_state:
            st.session_state.running = False
            st.session_state.mode = None  # 'daily' or 'realtime'
            st.session_state.thread = None
            st.session_state.broker = None
            st.session_state.positions = []
            st.session_state.account = {}
            st.session_state.current_regime = "Unknown"
            st.session_state.current_strategy = "None"
            st.session_state.performance_metrics = {}
            st.session_state.recent_trades = []
            st.session_state.log_messages = []
            st.session_state.error_log = []
            st.session_state.stream = None
            st.session_state.bar_history = []
            st.session_state.last_signal = None
            st.session_state.position_state = None
            st.session_state.notification = None
            st.session_state.connecting = False  # Flag to prevent multiple connection attempts
            st.session_state.initialized = True
    
    @property
    def running(self):
        return st.session_state.get('running', False)
    
    @running.setter
    def running(self, value):
        st.session_state.running = value
    
    @property
    def mode(self):
        return st.session_state.get('mode', None)
    
    @mode.setter
    def mode(self, value):
        st.session_state.mode = value
    
    @property
    def thread(self):
        return st.session_state.get('thread', None)
    
    @thread.setter
    def thread(self, value):
        st.session_state.thread = value
    
    @property
    def broker(self):
        return st.session_state.get('broker', None)
    
    @broker.setter
    def broker(self, value):
        st.session_state.broker = value
    
    @property
    def positions(self):
        return st.session_state.get('positions', [])
    
    @positions.setter
    def positions(self, value):
        st.session_state.positions = value
    
    @property
    def account(self):
        return st.session_state.get('account', {})
    
    @account.setter
    def account(self, value):
        st.session_state.account = value
    
    @property
    def current_regime(self):
        return st.session_state.get('current_regime', "Unknown")
    
    @current_regime.setter
    def current_regime(self, value):
        st.session_state.current_regime = value
    
    @property
    def current_strategy(self):
        return st.session_state.get('current_strategy', "None")
    
    @current_strategy.setter
    def current_strategy(self, value):
        st.session_state.current_strategy = value
    
    @property
    def performance_metrics(self):
        return st.session_state.get('performance_metrics', {})
    
    @performance_metrics.setter
    def performance_metrics(self, value):
        st.session_state.performance_metrics = value
    
    @property
    def recent_trades(self):
        return st.session_state.get('recent_trades', [])
    
    @recent_trades.setter
    def recent_trades(self, value):
        st.session_state.recent_trades = value
    
    @property
    def log_messages(self):
        return st.session_state.get('log_messages', [])
    
    @log_messages.setter
    def log_messages(self, value):
        st.session_state.log_messages = value
    
    @property
    def error_log(self):
        return st.session_state.get('error_log', [])
    
    @error_log.setter
    def error_log(self, value):
        st.session_state.error_log = value
    
    @property
    def stream(self):
        return st.session_state.get('stream', None)
    
    @stream.setter
    def stream(self, value):
        st.session_state.stream = value
    
    @property
    def bar_history(self):
        return st.session_state.get('bar_history', [])
    
    @bar_history.setter
    def bar_history(self, value):
        st.session_state.bar_history = value
        
    @property
    def last_signal(self):
        return st.session_state.get('last_signal', None)
        
    @last_signal.setter
    def last_signal(self, value):
        st.session_state.last_signal = value
        
    @property
    def position_state(self):
        return st.session_state.get('position_state', None)
        
    @position_state.setter
    def position_state(self, value):
        st.session_state.position_state = value
        
    @property
    def notification(self):
        return st.session_state.get('notification', None)
        
    @notification.setter
    def notification(self, value):
        st.session_state.notification = value
    
    @property
    def connecting(self):
        return st.session_state.get('connecting', False)
        
    @connecting.setter
    def connecting(self, value):
        st.session_state.connecting = value

        
trading_state = TradingState()


# ============================================================================
# TRADINGVIEW INTEGRATION & ASSET DEFINITIONS
# ============================================================================

# Asset categories with TradingView symbols
ASSET_CATEGORIES = {
    "Stocks": {
        "NVIDIA Corporation": "NASDAQ:NVDA",
        "Apple Inc.": "NASDAQ:AAPL",
        "Tesla Inc.": "NASDAQ:TSLA",
        "Microsoft Corporation": "NASDAQ:MSFT",
        "Amazon.com Inc.": "NASDAQ:AMZN",
        "Alphabet Inc. (Google)": "NASDAQ:GOOGL",
        "Meta Platforms Inc.": "NASDAQ:META",
        "Netflix Inc.": "NASDAQ:NFLX"
    },
    "Indices": {
        "NASDAQ-100": "NASDAQ:NDX",
        "S&P 500": "SP:SPX",
        "Dow Jones": "DJ:DJI",
        "Russell 2000": "TVC:RUT"
    },
    "Forex": {
        "Euro/U.S. Dollar": "FX:EURUSD",
        "British Pound/U.S. Dollar": "FX:GBPUSD",
        "U.S. Dollar/Japanese Yen": "FX:USDJPY",
        "Australian Dollar/U.S. Dollar": "FX:AUDUSD",
        "U.S. Dollar/Canadian Dollar": "FX:USDCAD",
        "U.S. Dollar/Swiss Franc": "FX:USDCHF"
    },
    "Crypto": {
        "Bitcoin/USD": "BINANCE:BTCUSDT",
        "Ethereum/USD": "BINANCE:ETHUSDT",
        "Solana/USD": "BINANCE:SOLUSDT",
        "Cardano/USD": "BINANCE:ADAUSDT",
        "Ripple/USD": "BINANCE:XRPUSDT"
    },
    "Commodities": {
        "Gold": "TVC:GOLD",
        "Silver": "TVC:SILVER",
        "Crude Oil": "TVC:USOIL",
        "Natural Gas": "TVC:NATURALGAS"
    }
}

def get_tradingview_widget(symbol: str, height: int = 500) -> str:
    """
    Generate TradingView widget HTML for embedding.
    
    Args:
        symbol: TradingView symbol (e.g., "NASDAQ:AAPL")
        height: Height of the widget in pixels
        
    Returns:
        HTML string for the TradingView widget
    """
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div id="tradingview_{symbol.replace(':', '_')}" style="height:100%;width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": {height},
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "America/New_York",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_{symbol.replace(':', '_')}"
      }});
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    return widget_html

def get_tradingview_mini_widget(symbol: str, width: str = "100%", height: int = 400) -> str:
    """
    Generate TradingView advanced real-time chart widget.
    
    Args:
        symbol: TradingView symbol
        width: Width (e.g., "100%" or "500px")
        height: Height in pixels
        
    Returns:
        HTML string for the widget
    """
    widget_html = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:{height}px;width:{width}">
      <div id="tradingview_chart_{symbol.replace(':', '_')}" style="height:calc(100% - 32px);width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "1",
        "timezone": "America/New_York",
        "theme": "dark",
        "style": "1",
        "locale": "en",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": false,
        "studies": [
          "STD;SMA",
          "STD;EMA",
          "STD;RSI"
        ],
        "container_id": "tradingview_chart_{symbol.replace(':', '_')}"
      }});
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    return widget_html


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
    
    # Initialize AI Intelligence states
    trading_state.current_regime = "Initializing..."
    trading_state.current_strategy = "Analyzing..."
    trading_state.notification = None
    
    logger.logger.info("🧠 AI Intelligence initialized - waiting for market data...")
    
    # Track data
    bar_history = {symbol: deque(maxlen=500) for symbol in symbols}
    positions = {}
    last_signal_time = {}

    # Pre-fill with some historical data
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5) # Fetch a few days to get enough bars
        hist_data = data_handler.fetch_historical_data(
            symbol=settings['trading_symbol'],
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            timeframe=timeframe
        )
        if hist_data is not None and not hist_data.empty:
            # Convert to list of dicts
            hist_data.reset_index(inplace=True)
            trading_state.bar_history = hist_data.to_dict('records')
            logger.logger.info(f"Pre-filled bar history with {len(trading_state.bar_history)} bars.")
    except Exception as e:
        logger.logger.error(f"Could not pre-fill bar history: {e}")

    
    # Prevent multiple connection attempts
    if trading_state.connecting:
        logger.logger.warning("⚠️ Connection attempt already in progress, skipping...")
        return
    
    trading_state.connecting = True
    
    try:
        # Close any existing WebSocket connection first
        if trading_state.stream is not None:
            try:
                logger.logger.info("🔌 Closing existing WebSocket connection...")
                trading_state.stream.stop()
                time.sleep(3)  # Give more time to properly close
                trading_state.stream = None
                logger.logger.info("✅ Existing connection closed")
            except Exception as e:
                logger.logger.warning(f"Warning closing old stream: {e}")
                trading_state.stream = None
        
        # Wait a bit to ensure connection is fully closed
        time.sleep(2)
        
        # Initialize WebSocket with retry logic
        max_retries = 3
        retry_count = 0
        stream = None
        
        while retry_count < max_retries and trading_state.running:
            try:
                logger.logger.info(f"Initializing WebSocket connection (attempt {retry_count + 1}/{max_retries})...")
                stream = tradeapi.Stream(
                    settings['alpaca_key'],
                    settings['alpaca_secret'],
                    base_url='https://paper-api.alpaca.markets' if settings['is_paper_trading'] else 'https://api.alpaca.markets',
                    data_feed='iex'
                )
                logger.logger.info("✅ WebSocket initialized successfully")
                break
            except Exception as e:
                logger.logger.error(f"Failed to initialize WebSocket: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    logger.logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)  # Wait before retry
                else:
                    logger.logger.error("❌ Max retries reached. Cannot establish WebSocket connection.")
                    logger.logger.error("💡 Please wait at least 5 minutes before trying again (connection limit).")
                    trading_state.running = False
                    trading_state.connecting = False
                    return
        
        if stream is None or not trading_state.running:
            logger.logger.error("Could not initialize stream or trading was stopped")
            trading_state.connecting = False
            return
        
        # Store in global state
        trading_state.stream = stream
        
    except Exception as e:
        logger.logger.error(f"Unexpected error during connection setup: {e}")
        trading_state.running = False
        trading_state.connecting = False
        return
    
    async def handle_bar(bar):
        """Process incoming bar data."""
        if not trading_state.running:
            return
        
        symbol = bar.symbol
        
        bar_data = {
            'timestamp': bar.timestamp,
            'open': bar.open,
            'high': bar.high,
            'low': bar.low,
            'close': bar.close,
            'volume': bar.volume
        }
        bar_history[symbol].append(bar_data)
        
        # Update trading_state bar history
        new_bar_history = trading_state.bar_history
        new_bar_history.append(bar_data)
        trading_state.bar_history = new_bar_history


        logger.logger.info(f"📊 {symbol}: ${bar.close:.2f}")

        # Need at least 20 bars for fast analysis (AI is smart enough!)
        if len(bar_history[symbol]) < 20:
            bars_needed = 20 - len(bar_history[symbol])
            trading_state.notification = f"""🔄 **AI Intelligence Initializing...**

� **Collecting live market data:** {len(bar_history[symbol])}/20 bars

⏱️ **Status:** Receiving real-time price updates every minute
🧠 **Next:** AI will analyze {symbol} once we have enough data

💡 This typically takes 1-2 minutes. The dashboard will update automatically!"""
            return

        # Check cooldown
        if symbol in last_signal_time:
            time_since = (datetime.now() - last_signal_time[symbol]).total_seconds()
            if time_since < 60:
                return

        try:
            df = pd.DataFrame(list(bar_history[symbol]))
            df.set_index('timestamp', inplace=True)

            # Detect market regime
            regime = regime_detector.predict_regime(df)
            
            # Check if this is first time detecting regime
            first_initialization = (trading_state.current_regime == "Initializing...")
            
            trading_state.current_regime = regime
            logger.logger.info(f"🧠 Market Regime: {regime}")

            # Select optimal strategy
            strategy, reason = strategy_selector.select_strategy(df)
            
            # Update strategy display name
            strategy_name = strategy.__class__.__name__
            trading_state.current_strategy = strategy_name
            
            logger.logger.info(f"🎯 Strategy: {strategy_name} - {reason}")
            
            # Show activation message on first initialization
            if first_initialization:
                strategy_display = strategy_name.replace('Strategy', '').replace('Trend', 'Trend ').replace('Mean', 'Mean ').replace('Volatility', 'Volatility ')
                logger.logger.info(f"✅ AI Intelligence fully activated!")
                trading_state.notification = f"""✅ **AI INTELLIGENCE ACTIVATED!**

🧠 **Market Analysis Complete:**
- **Regime:** {regime.upper()} 
- **Strategy:** {strategy_display}
- **Asset:** {symbol}

📊 **AI is now monitoring in real-time!**
You'll receive instant alerts when strong trading signals are detected.

🔍 **Status:** Actively scanning for opportunities..."""

            logger.logger.info(f"Strategy type: {type(strategy)}")
            signal = strategy.generate_signals(df)
            logger.logger.info(f"Signal type: {type(signal)}")

            if signal is not None and len(signal) > 0:
                latest_signal = signal.iloc[-1]
                trading_state.last_signal = latest_signal
                
                # Get current price and calculate additional metrics
                current_price = bar.close
                last_signal_time[symbol] = datetime.now()

                # 🧠 PHASE 5: AI Re-Analysis Logic - Confidence Reduction when user skips signals
                signal_suppressed = False
                if hasattr(st.session_state, 'user_skipped_signal') and st.session_state.user_skipped_signal:
                    skipped_time = st.session_state.get('skipped_signal_time', None)
                    skipped_strategy = st.session_state.get('skipped_strategy', '')
                    skipped_regime = st.session_state.get('skipped_regime', '')
                    
                    # Check if skip was recent (within 15 minutes)
                    if skipped_time:
                        time_since_skip = (datetime.now() - skipped_time).total_seconds()
                        
                        # Suppress similar signals for 15 minutes if same strategy AND same regime
                        if time_since_skip < 900:  # 15 minutes
                            if strategy_name == skipped_strategy and regime == skipped_regime:
                                signal_suppressed = True
                                logger.logger.info(f"⚠️ Signal suppressed: User skipped {skipped_strategy} in {skipped_regime} regime {time_since_skip/60:.1f} minutes ago")
                                trading_state.notification = f"""⏸️ **AI LEARNING FROM YOUR FEEDBACK**

🧠 **Confidence Reduced:** The AI detected the same signal pattern you recently skipped.

📊 **Suppressed Signal:**
- **Strategy:** {strategy_name}
- **Regime:** {regime.upper()}
- **Reason:** You skipped this signal {time_since_skip/60:.0f} minutes ago

💡 **AI Action:** Waiting for different market conditions before suggesting this strategy again (cooldown: {15 - time_since_skip/60:.0f} minutes remaining).

🔍 **Status:** Continuing to monitor for better opportunities..."""
                        else:
                            # Reset skip flag after cooldown expires
                            st.session_state.user_skipped_signal = False
                            logger.logger.info(f"✅ Skip cooldown expired, re-enabling {skipped_strategy} signals")

                if trading_state.position_state is None: # Looking to buy
                    if latest_signal == 1 and not signal_suppressed:
                        # BUY recommendation with detailed analysis
                        strategy_name = strategy.__class__.__name__.replace('Strategy', '').replace('Trend', 'Trend ').replace('Mean', 'Mean ').replace('Volatility', 'Volatility ')
                        
                        # 🎯 PHASE 5: Calculate Entry Risk Score
                        # Calculate stop loss
                        stop_loss = risk_manager.calculate_stop_loss(current_price, method='percentage', percentage=0.02)
                        
                        # Calculate ATR if available in dataframe
                        atr_value = None
                        if 'atr' in df.columns:
                            atr_value = df['atr'].iloc[-1]
                        else:
                            # Calculate simple ATR for risk assessment
                            if len(df) >= 14:
                                high_low = df['high'] - df['low']
                                high_close = abs(df['high'] - df['close'].shift())
                                low_close = abs(df['low'] - df['close'].shift())
                                tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                                atr_value = tr.rolling(window=14).mean().iloc[-1]
                        
                        # Calculate current volatility (20-period standard deviation)
                        current_volatility = None
                        if len(df) >= 20:
                            returns = df['close'].pct_change()
                            current_volatility = returns.rolling(window=20).std().iloc[-1] * 100 * (252 ** 0.5)  # Annualized
                        
                        # Get entry risk score
                        risk_score, risk_level, risk_details = risk_manager.calculate_entry_risk(
                            entry_price=current_price,
                            stop_loss_price=stop_loss,
                            atr=atr_value,
                            current_volatility=current_volatility
                        )
                        
                        # Check for critical risk
                        is_critical, risk_warning = risk_manager.check_critical_risk(risk_score)
                        
                        # Build risk assessment message
                        risk_emoji = "🟢" if risk_level == "LOW" else "�" if risk_level == "MEDIUM" else "🟠" if risk_level == "HIGH" else "🔴"
                        risk_section = f"""
🛡️ **Entry Risk Analysis:**
{risk_emoji} **Risk Level:** {risk_level} ({risk_score:.0f}/100)
- **Stop Loss:** ${stop_loss:.2f} ({abs(current_price - stop_loss)/current_price*100:.2f}% distance)"""
                        
                        if atr_value:
                            risk_section += f"\n- **Volatility (ATR):** ${atr_value:.2f} ({atr_value/current_price*100:.2f}%)"
                        
                        if is_critical:
                            risk_section += f"\n\n⚠️ **{risk_warning}**"
                        
                        trading_state.notification = f"""�🚀 **BUY SIGNAL DETECTED!**

📊 **Asset:** {symbol} @ ${current_price:.2f}
🎯 **Strategy:** {strategy_name}
🧠 **Market Regime:** {regime.upper()}
⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}

💡 **AI Analysis:** Market conditions are favorable for entering a LONG position. The {strategy_name} strategy has identified a strong buy signal based on current price action and technical indicators.
{risk_section}

✅ **Recommendation:** {"Enter with CAUTION - High Risk!" if is_critical else "Enter LONG position now!"}"""
                        
                        # Store risk details in session state for position sizing
                        st.session_state['last_entry_risk_score'] = risk_score
                        st.session_state['last_entry_risk_level'] = risk_level
                        st.session_state['last_stop_loss'] = stop_loss
                        
                        logger.logger.info(f"🚀 BUY recommendation: {symbol} @ ${current_price:.2f} | Strategy: {strategy_name} | Regime: {regime} | Risk: {risk_level} ({risk_score:.0f}/100)")
                        
                elif trading_state.position_state == 'long': # Looking to sell
                    if latest_signal == -1 and not signal_suppressed:
                        # SELL recommendation with detailed analysis
                        strategy_name = strategy.__class__.__name__.replace('Strategy', '').replace('Trend', 'Trend ').replace('Mean', 'Mean ').replace('Volatility', 'Volatility ')
                        
                        trading_state.notification = f"""📉 **SELL SIGNAL DETECTED!**

📊 **Asset:** {symbol} @ ${current_price:.2f}
🎯 **Strategy:** {strategy_name}
🧠 **Market Regime:** {regime.upper()}
⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}

💡 **AI Analysis:** Market conditions suggest it's time to exit the LONG position. The {strategy_name} strategy has identified a strong sell signal to protect profits or minimize losses.

❌ **Recommendation:** Close LONG position now!"""
                        
                        logger.logger.info(f"📉 SELL recommendation: {symbol} @ ${current_price:.2f} | Strategy: {strategy_name} | Regime: {regime}")
                    else:
                        # Hold recommendation - still in position with no sell signal
                        if latest_signal == 1:
                            strategy_name = strategy.__class__.__name__.replace('Strategy', '').replace('Trend', 'Trend ').replace('Mean', 'Mean ').replace('Volatility', 'Volatility ')
                            trading_state.notification = f"""📊 **HOLD POSITION**

📊 **Asset:** {symbol} @ ${current_price:.2f}
🎯 **Strategy:** {strategy_name}
🧠 **Market Regime:** {regime.upper()}
⏰ **Time:** {datetime.now().strftime('%H:%M:%S')}

💡 **AI Analysis:** Continue holding your LONG position. Market momentum remains strong and conditions are still favorable.

✅ **Recommendation:** Keep position open!"""
                            
        except Exception as e:
            logger.logger.error(f"Error in handle_bar: {e}")

    
    # Subscribe
    try:
        for symbol in symbols:
            stream.subscribe_bars(handle_bar, symbol)
        
        logger.logger.info("✅ WebSocket subscribed to symbols")
    except Exception as e:
        logger.logger.error(f"Failed to subscribe to symbols: {e}")
        trading_state.running = False
        trading_state.stream = None
        return
    
    logger.logger.info("✅ Starting WebSocket stream...")
    
    try:
        stream.run()
    except ValueError as e:
        error_msg = str(e)
        if "connection limit exceeded" in error_msg or "429" in error_msg:
            logger.logger.error("⚠️ CONNECTION LIMIT EXCEEDED")
            logger.logger.error("━" * 50)
            logger.logger.error("Alpaca's free tier has connection limits.")
            logger.logger.error("Please wait 5-10 minutes before restarting.")
            logger.logger.error("💡 Always use the Stop button before closing!")
            logger.logger.error("━" * 50)
        else:
            logger.logger.error(f"Stream error: {e}")
        trading_state.running = False
    except Exception as e:
        logger.logger.error(f"Stream error: {e}")
        trading_state.running = False
    finally:
        try:
            if stream is not None:
                logger.logger.info("🔌 Stopping stream...")
                stream.stop()
                time.sleep(2)
                logger.logger.info("✅ Stream stopped cleanly")
        except Exception as e:
            logger.logger.warning(f"Error stopping stream: {e}")
        
        # Ensure cleanup
        trading_state.stream = None
        trading_state.connecting = False
        logger.logger.info("✅ Connection cleanup complete")
        time.sleep(2)  # Give time for cleanup


# ============================================================================
# STREAMLIT DASHBOARD
# ============================================================================

def show_settings_page():
    """Display settings configuration page."""
    st.title("⚙️ Settings")
    
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
        
        st.subheader("📈 Asset Selection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Get current trading symbol
            current_symbol = settings.get('trading_symbol', 'SPY')
            
            # Asset category selection
            asset_category = st.selectbox(
                "Asset Category",
                options=list(ASSET_CATEGORIES.keys()),
                index=0,
                help="Choose the type of asset you want to trade"
            )
        
        with col2:
            # Get assets in selected category
            assets_in_category = ASSET_CATEGORIES[asset_category]
            asset_names = list(assets_in_category.keys())
            
            # Try to find current symbol in selected category
            default_index = 0
            for idx, name in enumerate(asset_names):
                tradingview_symbol = assets_in_category[name]
                # Extract base symbol (e.g., "NVDA" from "NASDAQ:NVDA")
                base_symbol = tradingview_symbol.split(':')[-1].replace('USDT', '')
                if base_symbol == current_symbol or tradingview_symbol == current_symbol:
                    default_index = idx
                    break
            
            selected_asset = st.selectbox(
                "Select Asset",
                options=asset_names,
                index=default_index,
                help="Choose the specific asset to trade"
            )
            
            # Get the TradingView symbol and extract Alpaca-compatible symbol
            tradingview_symbol = assets_in_category[selected_asset]
            
            # Convert TradingView symbol to Alpaca symbol
            if ':' in tradingview_symbol:
                trading_symbol = tradingview_symbol.split(':')[-1]
            else:
                trading_symbol = tradingview_symbol
            
            # For crypto, remove USDT suffix for display
            if asset_category == "Crypto":
                trading_symbol = trading_symbol.replace('USDT', '')
            
            # Store full TradingView symbol for charts
            st.session_state.tradingview_symbol = tradingview_symbol
            st.session_state.asset_category = asset_category
            
            st.info(f"📊 Trading: **{selected_asset}** ({trading_symbol})")
        
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
                'realtime_timeframe': realtime_timeframe,
                'asset_category': st.session_state.get('asset_category', 'Stocks'),
                'tradingview_symbol': st.session_state.get('tradingview_symbol', 'NASDAQ:SPY')
            }
            
            save_settings(new_settings)
            st.success("✅ Settings saved successfully!")
            logger.logger.info(f"Settings saved via UI - Trading {selected_asset}")
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
    """Display unified trading dashboard with controls and asset selector."""
    st.title("🥝 Kiwi AI Trading Dashboard")
    
    settings = load_settings()
    
    if not check_configuration():
        st.error("⚠️ API keys not configured! Go to Settings tab to configure.")
        return
    
    # ============================================================================
    # PROFESSIONAL ASSET SELECTOR - Top Bar
    # ============================================================================
    
    # Apple-style minimalist design with clean layout
    st.markdown("""
    <style>
    /* Apple-style selectbox and button styling */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
    }
    .stSelectbox > div > div:hover {
        background: rgba(255, 255, 255, 0.12) !important;
        border-color: rgba(0, 217, 255, 0.4) !important;
    }
    .stSelectbox label {
        font-size: 12px !important;
        font-weight: 500 !important;
        color: rgba(255, 255, 255, 0.7) !important;
        letter-spacing: 0.5px !important;
        text-transform: uppercase !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col_selector, col_controls = st.columns([3, 1])
    
    with col_selector:
        # Clean header with icon
        st.markdown("""
        <div style='margin-bottom: 20px;'>
            <h3 style='color: #ffffff; font-size: 20px; font-weight: 600; margin: 0; 
                       display: flex; align-items: center; gap: 10px; letter-spacing: -0.5px;'>
                <span style='font-size: 24px;'>📊</span>
                Select Trading Asset
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Category and Asset selection in one row
        sel_col1, sel_col2 = st.columns([1, 2])
        
        with sel_col1:
            current_category = settings.get('asset_category', 'Stocks')
            asset_category = st.selectbox(
                "Category",
                options=list(ASSET_CATEGORIES.keys()),
                index=list(ASSET_CATEGORIES.keys()).index(current_category),
                key="asset_category_selector"
            )
        
        with sel_col2:
            assets_in_category = ASSET_CATEGORIES[asset_category]
            asset_names = list(assets_in_category.keys())
            
            # Find current selection or default to first
            current_symbol = settings.get('trading_symbol', '')
            current_tv_symbol = settings.get('tradingview_symbol', '')
            
            default_index = 0
            for idx, (name, tv_sym) in enumerate(assets_in_category.items()):
                if tv_sym == current_tv_symbol:
                    default_index = idx
                    break
            
            selected_asset_name = st.selectbox(
                "Asset",
                options=asset_names,
                index=default_index,
                key="asset_selector"
            )
            
            selected_tradingview_symbol = assets_in_category[selected_asset_name]
            
            # Extract Alpaca symbol from TradingView symbol
            if asset_category == "Stocks":
                selected_symbol = selected_tradingview_symbol.split(':')[1]
            elif asset_category == "Crypto":
                # Convert BTCUSDT to BTC/USD format for Alpaca
                crypto_symbol = selected_tradingview_symbol.split(':')[1].replace('USDT', '/USD')
                selected_symbol = crypto_symbol
            else:
                selected_symbol = selected_asset_name
            
            # Update settings if changed
            if (settings.get('trading_symbol') != selected_symbol or 
                settings.get('tradingview_symbol') != selected_tradingview_symbol or
                settings.get('asset_category') != asset_category):
                
                settings['trading_symbol'] = selected_symbol
                settings['tradingview_symbol'] = selected_tradingview_symbol
                settings['asset_category'] = asset_category
                save_settings(settings)
                st.success(f"✅ Switched to {selected_asset_name}")
                time.sleep(1)
                st.rerun()
    
    with col_controls:
        # Clean header with icon
        st.markdown("""
        <div style='margin-bottom: 20px;'>
            <h3 style='color: #ffffff; font-size: 20px; font-weight: 600; margin: 0; 
                       display: flex; align-items: center; gap: 10px; letter-spacing: -0.5px;'>
                <span style='font-size: 24px;'>⚡</span>
                Trading Controls
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Start/Stop trading button with Apple-style design
        if trading_state.running:
            # Stop button with refined styling
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button[kind="secondary"] {
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.9), rgba(220, 38, 38, 0.9)) !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 14px 24px !important;
                font-size: 15px !important;
                font-weight: 600 !important;
                letter-spacing: 0.3px !important;
                color: white !important;
                box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            div[data-testid="stButton"] > button[kind="secondary"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("🛑 Stop Trading", use_container_width=True, type="secondary"):
                try:
                    # First stop the trading flag
                    trading_state.running = False
                    logger.logger.info("🛑 Stopping trading system...")
                    
                    # Close WebSocket connection with proper cleanup
                    if trading_state.stream is not None:
                        try:
                            logger.logger.info("🔌 Closing WebSocket connection...")
                            trading_state.stream.stop()
                            time.sleep(3)  # Give more time for proper cleanup
                            trading_state.stream = None
                            logger.logger.info("✅ WebSocket closed successfully")
                        except Exception as e:
                            logger.logger.warning(f"Warning closing WebSocket: {e}")
                            trading_state.stream = None
                    
                    # Wait for thread to finish
                    if trading_state.thread is not None:
                        trading_state.thread.join(timeout=5)
                        trading_state.thread = None
                    
                    st.success("✅ Trading stopped! Waiting 5 seconds before allowing restart...")
                    logger.logger.info("Trading stopped via UI")
                    time.sleep(5)  # Prevent immediate restart
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    logger.logger.error(f"Error stopping trading: {e}")
        else:
            # Start button with refined Apple-style design
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button[kind="primary"] {
                background: linear-gradient(135deg, rgba(0, 217, 255, 1), rgba(0, 180, 255, 1)) !important;
                border: none !important;
                border-radius: 12px !important;
                padding: 14px 24px !important;
                font-size: 15px !important;
                font-weight: 600 !important;
                letter-spacing: 0.3px !important;
                color: white !important;
                box-shadow: 0 4px 14px rgba(0, 217, 255, 0.4) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            div[data-testid="stButton"] > button[kind="primary"]:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 6px 20px rgba(0, 217, 255, 0.5) !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("🚀 Start Trading", use_container_width=True, type="primary"):
                # Check if there's already an active stream
                if trading_state.stream is not None:
                    st.warning("⚠️ Cleaning up existing connection first...")
                    try:
                        trading_state.stream.stop()
                        time.sleep(3)
                        trading_state.stream = None
                    except:
                        pass
                
                st.info("🚀 Starting Real-Time Trading System...")
                try:
                    trading_state.running = True
                    trading_state.mode = 'realtime'
                    
                    def run_realtime():
                        try:
                            run_realtime_trading(settings)
                        except Exception as e:
                            log_error('Real-Time Mode', 'Critical error', e, {'settings': str(settings)})
                            trading_state.running = False
                    
                    trading_state.thread = threading.Thread(target=run_realtime, daemon=True)
                    trading_state.thread.start()
                    logger.logger.info("Real-time mode started")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to start: {e}")
                    logger.logger.error(f"Failed to start trading: {e}")
    
    # Get current asset info
    selected_symbol = settings.get('trading_symbol', 'SPY')
    tradingview_symbol = settings.get('tradingview_symbol', 'NASDAQ:SPY')
    asset_category = settings.get('asset_category', 'Stocks')
    
    # ============================================================================
    # LIVE STATUS BAR
    # ============================================================================
    status_cols = st.columns([1, 1, 1, 1])
    
    with status_cols[0]:
        if trading_state.running:
            st.success("🔴 **LIVE TRADING**")
        else:
            st.info("⚪ **STOPPED**")
    
    with status_cols[1]:
        st.info(f"**Asset:** {selected_symbol}")
    
    with status_cols[2]:
        st.info(f"**Category:** {asset_category}")
    
    with status_cols[3]:
        mode_text = "PAPER" if settings.get('is_paper_trading', True) else "🔴 LIVE"
        st.warning(f"**Mode:** {mode_text}")
    
    # ============================================================================
    # TRADINGVIEW CHART - Full Width Professional Display
    # ============================================================================
    st.subheader(f"📊 {selected_asset_name} - Real-Time Chart")
    
    # Full width chart - no columns needed
    # Embed TradingView Advanced Chart with professional settings
    tradingview_html = f"""
        <!DOCTYPE html>
        <html style="height: 100%; margin: 0; padding: 0;">
        <head>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                html, body {{
                    height: 100%;
                    width: 100%;
                    overflow: hidden;
                    background: #0f0c29;
                }}
                .tradingview-widget-container {{ 
                    height: 100%;
                    width: 100%;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 8px 32px rgba(0, 217, 255, 0.15);
                    border: 1px solid rgba(0, 217, 255, 0.2);
                    display: flex;
                    flex-direction: column;
                }}
                #tradingview_chart {{
                    height: 100% !important;
                    width: 100% !important;
                }}
            </style>
        </head>
        <body>
            <div class="tradingview-widget-container">
              <div id="tradingview_chart"></div>
            </div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
              new TradingView.widget({{
                "autosize": true,
                "symbol": "{tradingview_symbol}",
                "interval": "5",
                "timezone": "America/New_York",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#131722",
                "enable_publishing": false,
                "withdateranges": true,
                "range": "1D",
                "hide_side_toolbar": false,
                "allow_symbol_change": true,
                "details": true,
                "hotlist": true,
                "calendar": true,
                "show_popup_button": true,
                "popup_width": "1000",
                "popup_height": "650",
                "studies": [
                  "RSI@tv-basicstudies",
                  "MASimple@tv-basicstudies",
                  "MACD@tv-basicstudies",
                  "BB@tv-basicstudies"
                ],
                "container_id": "tradingview_chart",
                "enabled_features": [
                  "study_templates",
                  "use_localstorage_for_settings",
                  "save_chart_properties_to_local_storage",
                  "create_volume_indicator_by_default",
                  "side_toolbar_in_fullscreen_mode",
                  "header_in_fullscreen_mode",
                  "left_toolbar"
                ],
                "disabled_features": [],
                "overrides": {{
                  "mainSeriesProperties.candleStyle.upColor": "#00d9ff",
                  "mainSeriesProperties.candleStyle.downColor": "#ff4444",
                  "mainSeriesProperties.candleStyle.borderUpColor": "#00d9ff",
                  "mainSeriesProperties.candleStyle.borderDownColor": "#ff4444",
                  "mainSeriesProperties.candleStyle.wickUpColor": "#00d9ff",
                  "mainSeriesProperties.candleStyle.wickDownColor": "#ff4444"
                }}
              }});
            </script>
        </body>
        </html>
        """
    components.html(tradingview_html, height=700)
    
    # ============================================================================
    # AI INTELLIGENCE & ANALYSIS - Unified Table View
    # ============================================================================
    st.subheader("🧠 AI Intelligence & Analysis")
    
    # Determine all display values
    regime_colors = {
        'TREND': '🟢',
        'SIDEWAYS': '🟡', 
        'VOLATILE': '🔴',
        'Unknown': '⚪',
        'Initializing...': '🔄'
    }
    
    # Current regime - show actual state from trading_state
    regime_display = trading_state.current_regime or "Unknown"
    regime_icon = regime_colors.get(regime_display, '⚪')
    
    # Current strategy - show actual state from trading_state
    if trading_state.current_strategy in ['None', None]:
        strategy_display = "None"
    elif trading_state.current_strategy == 'Analyzing...':
        strategy_display = "Analyzing..."
    else:
        strategy_name = trading_state.current_strategy
        strategy_display = strategy_name.replace('Strategy', '').replace('TrendFollowing', 'Trend Following').replace('MeanReversion', 'Mean Reversion').replace('VolatilityBreakout', 'Volatility Breakout')
    
    # Current status
    if not trading_state.running:
        status_display = "⚪ System Stopped"
        status_color = "#6c757d"
        status_detail = "Click Start to begin analysis"
    elif trading_state.current_regime == "Initializing...":
        status_display = "🔄 Initializing..."
        status_color = "#00d9ff"
        status_detail = "Collecting live market data (1-2 minutes)"
    elif trading_state.position_state == 'long':
        status_display = "✅ Position Active"
        status_color = "#4caf50"
        status_detail = "Monitoring for exit signals"
    else:
        status_display = "🔍 Scanning"
        status_color = "#2196f3"
        status_detail = "Analyzing for entry opportunities"
    
    # Initialize session state for detail views
    if 'show_asset_details' not in st.session_state:
        st.session_state.show_asset_details = False
    if 'show_regime_details' not in st.session_state:
        st.session_state.show_regime_details = False
    if 'show_strategy_details' not in st.session_state:
        st.session_state.show_strategy_details = False
    if 'show_status_details' not in st.session_state:
        st.session_state.show_status_details = False
    
    # Create button columns for headers
    header_cols = st.columns(4)
    
    with header_cols[0]:
        if st.button("📊 Asset", key="btn_asset", use_container_width=True):
            st.session_state.show_asset_details = not st.session_state.show_asset_details
            st.session_state.show_regime_details = False
            st.session_state.show_strategy_details = False
            st.session_state.show_status_details = False
    
    with header_cols[1]:
        if st.button("🌊 Market Regime", key="btn_regime", use_container_width=True):
            st.session_state.show_regime_details = not st.session_state.show_regime_details
            st.session_state.show_asset_details = False
            st.session_state.show_strategy_details = False
            st.session_state.show_status_details = False
    
    with header_cols[2]:
        if st.button("🎯 Strategy", key="btn_strategy", use_container_width=True):
            st.session_state.show_strategy_details = not st.session_state.show_strategy_details
            st.session_state.show_asset_details = False
            st.session_state.show_regime_details = False
            st.session_state.show_status_details = False
    
    with header_cols[3]:
        if st.button("⚡ Status", key="btn_status", use_container_width=True):
            st.session_state.show_status_details = not st.session_state.show_status_details
            st.session_state.show_asset_details = False
            st.session_state.show_regime_details = False
            st.session_state.show_strategy_details = False
    
    # Data row - clean display without extra containers
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.02); border-radius: 8px; padding: 24px; margin-top: 10px;'>
        <div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; align-items: center;'>
            <div style='text-align: center;'>
                <p style='margin: 0; color: #ffffff; font-size: 20px; font-weight: 700;'>{selected_symbol}</p>
                <p style='margin: 4px 0 0 0; color: #888; font-size: 12px;'>{asset_category}</p>
            </div>
            <div style='text-align: center;'>
                <p style='margin: 0; color: #ffffff; font-size: 20px; font-weight: 700;'>{regime_icon} {regime_display}</p>
                <p style='margin: 4px 0 0 0; color: #888; font-size: 12px;'>Real-time detection</p>
            </div>
            <div style='text-align: center;'>
                <p style='margin: 0; color: #00d9ff; font-size: 20px; font-weight: 700;'>🎯 {strategy_display}</p>
                <p style='margin: 4px 0 0 0; color: #888; font-size: 12px;'>Auto-selected</p>
            </div>
            <div style='text-align: center;'>
                <p style='margin: 0; color: {status_color}; font-size: 20px; font-weight: 700;'>{status_display}</p>
                <p style='margin: 4px 0 0 0; color: #888; font-size: 12px;'>{status_detail}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show detailed view BELOW the table if any button was clicked
    if any([st.session_state.show_asset_details, st.session_state.show_regime_details, 
            st.session_state.show_strategy_details, st.session_state.show_status_details]):
    
        # Show detailed information based on which button was clicked
        if st.session_state.show_asset_details:
            # Professional Asset Details with styled table
            st.markdown(f"""
            <div style='color: #00d9ff; font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center;'>
                📊 Asset Overview: {selected_symbol}
            </div>
            """, unsafe_allow_html=True)
            
            # Asset Information Table
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style='background: rgba(0,217,255,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(0,217,255,0.3);'>
                    <p style='color: #00d9ff; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>📋 ASSET DETAILS</p>
                    <table style='width: 100%; color: #ffffff;'>
                        <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>
                            <td style='padding: 8px 0; color: #888;'>Symbol:</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 600;'>{selected_symbol}</td>
                        </tr>
                        <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>
                            <td style='padding: 8px 0; color: #888;'>Name:</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 600;'>{selected_asset_name}</td>
                        </tr>
                        <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>
                            <td style='padding: 8px 0; color: #888;'>Category:</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 600;'>{asset_category}</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 0; color: #888;'>Exchange:</td>
                            <td style='padding: 8px 0; text-align: right; font-weight: 600;'>{tradingview_symbol.split(':')[0]}</td>
                        </tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: rgba(76,175,80,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(76,175,80,0.3);'>
                    <p style='color: #4caf50; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>📈 MARKET PERFORMANCE</p>
                    <p style='color: #ffffff; margin: 10px 0; font-size: 13px;'>Access comprehensive market data and live performance metrics:</p>
                    <a href='https://www.google.com/finance/quote/{selected_symbol}:{'NASDAQ' if asset_category == 'Stocks' else 'INDEX'}' 
                       target='_blank' 
                       style='display: inline-block; background: linear-gradient(135deg, #4caf50, #45a049); 
                              color: white; padding: 10px 20px; border-radius: 6px; text-decoration: none; 
                              font-weight: 600; font-size: 13px; margin-top: 10px;'>
                        🔗 View on Google Finance
                    </a>
                </div>
                """, unsafe_allow_html=True)
            
            # Current Analysis Section
            st.markdown("""
            <div style='background: rgba(33,150,243,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(33,150,243,0.3);'>
                <p style='color: #2196f3; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🤖 AI ANALYSIS STATUS</p>
            """, unsafe_allow_html=True)
            
            status_col1, status_col2, status_col3 = st.columns(3)
            
            with status_col1:
                st.markdown("""
                <div style='text-align: center; padding: 10px;'>
                    <div style='font-size: 24px; margin-bottom: 5px;'>✅</div>
                    <div style='color: #4caf50; font-weight: 600; font-size: 12px;'>Price Tracking</div>
                    <div style='color: #888; font-size: 11px;'>Real-time</div>
                </div>
                """, unsafe_allow_html=True)
            
            with status_col2:
                st.markdown("""
                <div style='text-align: center; padding: 10px;'>
                    <div style='font-size: 24px; margin-bottom: 5px;'>✅</div>
                    <div style='color: #4caf50; font-weight: 600; font-size: 12px;'>Technical Indicators</div>
                    <div style='color: #888; font-size: 11px;'>Active</div>
                </div>
                """, unsafe_allow_html=True)
            
            with status_col3:
                st.markdown("""
                <div style='text-align: center; padding: 10px;'>
                    <div style='font-size: 24px; margin-bottom: 5px;'>✅</div>
                    <div style='color: #4caf50; font-weight: 600; font-size: 12px;'>Volume Analysis</div>
                    <div style='color: #888; font-size: 11px;'>Monitoring</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Why This Asset Section
            st.markdown(f"""
            <div style='background: rgba(255,152,0,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(255,152,0,0.3);'>
                <p style='color: #ff9800; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>💡 WHY THIS ASSET?</p>
                <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                    <strong>{selected_symbol}</strong> was selected based on your configuration settings. 
                    The AI continuously monitors price action, trading volume, and multiple technical indicators 
                    to identify optimal entry and exit opportunities. This asset is being analyzed in real-time 
                    to detect high-probability trading setups that align with current market conditions.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        elif st.session_state.show_regime_details:
            regime_info = {
                'TREND': {
                    'description': 'Strong directional movement in prices',
                    'characteristics': '• Clear price direction\n• Higher highs or lower lows\n• Sustained momentum',
                    'best_for': 'Trend Following strategies work best',
                    'risk': 'Medium - Follow the trend, avoid fighting it'
                },
                'SIDEWAYS': {
                    'description': 'Price consolidation within a range',
                    'characteristics': '• Limited price movement\n• Support and resistance levels\n• Low volatility',
                    'best_for': 'Mean Reversion strategies excel here',
                    'risk': 'Low - Predictable range-bound movement'
                },
                'VOLATILE': {
                    'description': 'High price fluctuations and uncertainty',
                    'characteristics': '• Rapid price swings\n• Increased volume\n• Breakout potential',
                    'best_for': 'Volatility Breakout strategies thrive',
                    'risk': 'High - Requires careful position sizing'
                },
                'Unknown': {
                    'description': 'Insufficient data for classification',
                    'characteristics': '• Collecting market data\n• Building price history\n• Analyzing patterns',
                    'best_for': 'Waiting for clear market structure',
                    'risk': 'N/A - System initializing'
                }
            }
            
            current_regime_info = regime_info.get(regime_display, regime_info['Unknown'])
            
            # Professional Market Regime Details
            st.markdown(f"""
            <div style='color: #4cafff; font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center;'>
                🌊 Market Regime Analysis: {regime_icon} {regime_display}
            </div>
            """, unsafe_allow_html=True)
            
            # Regime Overview
            st.markdown(f"""
            <div style='background: rgba(76,175,254,0.1); border-radius: 8px; padding: 20px; border: 1px solid rgba(76,175,254,0.3); margin-bottom: 15px;'>
                <p style='color: #4cafff; font-size: 16px; font-weight: 600; margin: 0 0 10px 0; text-align: center;'>
                    {regime_icon} Current Market Condition
                </p>
                <p style='color: #ffffff; margin: 0; font-size: 14px; text-align: center; line-height: 1.6;'>
                    {current_regime_info['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Two-column layout for characteristics and strategy
            col1, col2 = st.columns(2)
            
            with col1:
                characteristics_lines = current_regime_info['characteristics'].split('\n')
                characteristics_html = '<br>'.join([f"<div style='padding: 5px 0;'>{line}</div>" for line in characteristics_lines])
                
                st.markdown(f"""
                <div style='background: rgba(33,150,243,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(33,150,243,0.3); height: 100%;'>
                    <p style='color: #2196f3; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>📋 KEY CHARACTERISTICS</p>
                    <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                        {characteristics_html}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: rgba(76,175,80,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(76,175,80,0.3); height: 100%;'>
                    <p style='color: #4caf50; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🎯 OPTIMAL STRATEGY</p>
                    <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.8;'>
                        {current_regime_info['best_for']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Risk Level and AI Detection
            risk_colors = {'LOW': '#4caf50', 'MEDIUM': '#ff9800', 'HIGH': '#f44336', 'N/A': '#888'}
            risk_word = current_regime_info['risk'].split(' - ')[0].split(': ')[-1] if ' - ' in current_regime_info['risk'] else 'MEDIUM'
            risk_color = risk_colors.get(risk_word.upper(), '#ff9800')
            
            st.markdown(f"""
            <div style='background: rgba(255,152,0,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(255,152,0,0.3);'>
                <p style='color: #ff9800; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>⚠️ RISK ASSESSMENT</p>
                <p style='color: {risk_color}; margin: 0; font-size: 14px; font-weight: 600;'>
                    {current_regime_info['risk']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='background: rgba(156,39,176,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(156,39,176,0.3);'>
                <p style='color: #9c27b0; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🤖 AI DETECTION METHOD</p>
                <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                    The AI uses machine learning algorithms to analyze price patterns, volatility, and momentum 
                    to classify market conditions in real-time. This enables automatic strategy selection 
                    that adapts to changing market dynamics.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        elif st.session_state.show_strategy_details:
            strategy_info = {
                'Trend Following': {
                    'description': 'Captures sustained directional moves',
                    'logic': 'Identifies and follows strong trends using moving averages and momentum indicators',
                    'indicators': '• EMA (20/50 periods)\n• MACD\n• ADX for trend strength',
                    'entry': 'When price crosses above EMA and MACD confirms',
                    'exit': 'When trend reverses or momentum weakens',
                    'best_in': 'TREND markets',
                    'advantage': 'High reward potential in strong trends'
                    },
                'Mean Reversion': {
                    'description': 'Profits from price returning to average',
                    'logic': 'Identifies overbought/oversold conditions and trades reversals back to mean',
                    'indicators': '• Bollinger Bands\n• RSI\n• Standard deviation',
                    'entry': 'When price reaches extreme levels (oversold/overbought)',
                    'exit': 'When price returns to moving average',
                    'best_in': 'SIDEWAYS markets',
                    'advantage': 'Consistent profits in range-bound conditions'
                },
                'Volatility Breakout': {
                    'description': 'Captures explosive price movements',
                    'logic': 'Detects compression followed by expansion, trading the breakout',
                    'indicators': '• ATR (Average True Range)\n• Donchian Channels\n• Volume spikes',
                    'entry': 'When price breaks out of consolidation with volume',
                    'exit': 'When volatility contracts or breakout fails',
                    'best_in': 'VOLATILE markets',
                    'advantage': 'Large moves in short timeframes'
                },
                'Analyzing...': {
                    'description': 'AI is evaluating market conditions',
                    'logic': 'Analyzing historical data and current market regime',
                    'indicators': '• Collecting price data\n• Calculating indicators\n• Detecting patterns',
                    'entry': 'Waiting for strategy selection',
                    'exit': 'Pending analysis completion',
                    'best_in': 'Initializing...',
                    'advantage': 'Ensuring optimal strategy selection'
                },
                'None': {
                    'description': 'No strategy selected - system stopped',
                    'logic': 'Start trading to enable AI strategy selection',
                    'indicators': '• System idle',
                    'entry': 'N/A',
                    'exit': 'N/A',
                    'best_in': 'N/A',
                    'advantage': 'Safe mode - no active trading'
                }
            }
            
            current_strategy_info = strategy_info.get(strategy_display, strategy_info['None'])
            
            # Professional Strategy Details
            st.markdown(f"""
            <div style='color: #ffc107; font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center;'>
                🎯 Strategy Deep Dive: {strategy_display}
            </div>
            """, unsafe_allow_html=True)
            
            # Strategy Overview
            st.markdown(f"""
            <div style='background: rgba(255,193,7,0.1); border-radius: 8px; padding: 20px; border: 1px solid rgba(255,193,7,0.3); margin-bottom: 15px;'>
                <p style='color: #ffc107; font-size: 16px; font-weight: 600; margin: 0 0 10px 0; text-align: center;'>
                    💡 Strategy Overview
                </p>
                <p style='color: #ffffff; margin: 0; font-size: 14px; text-align: center; line-height: 1.6;'>
                    {current_strategy_info['description']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # How It Works
            st.markdown(f"""
            <div style='background: rgba(33,150,243,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(33,150,243,0.3); margin-bottom: 15px;'>
                <p style='color: #2196f3; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🔍 HOW IT WORKS</p>
                <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                    {current_strategy_info['logic']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Key Indicators
            indicators_lines = current_strategy_info['indicators'].split('\n')
            indicators_html = '<br>'.join([f"<div style='padding: 5px 0;'>{line}</div>" for line in indicators_lines])
            
            st.markdown(f"""
            <div style='background: rgba(156,39,176,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(156,39,176,0.3); margin-bottom: 15px;'>
                <p style='color: #9c27b0; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>� KEY INDICATORS</p>
                <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                    {indicators_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Entry and Exit Conditions in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div style='background: rgba(76,175,80,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(76,175,80,0.3); height: 100%;'>
                    <p style='color: #4caf50; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🟢 ENTRY CONDITIONS</p>
                    <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                        {current_strategy_info['entry']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: rgba(244,67,54,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(244,67,54,0.3); height: 100%;'>
                    <p style='color: #f44336; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🔴 EXIT CONDITIONS</p>
                    <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                        {current_strategy_info['exit']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Best Performance and Advantage
            st.markdown(f"""
            <div style='background: rgba(0,188,212,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(0,188,212,0.3);'>
                <p style='color: #00bcd4; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>✨ BEST PERFORMANCE</p>
                <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                    This strategy excels in <strong>{current_strategy_info['best_in']}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='background: rgba(255,152,0,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(255,152,0,0.3);'>
                <p style='color: #ff9800; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>💪 COMPETITIVE ADVANTAGE</p>
                <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                    {current_strategy_info['advantage']}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Why AI Selected This
            st.markdown(f"""
            <div style='background: rgba(0,217,255,0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border: 1px solid rgba(0,217,255,0.3);'>
                <p style='color: #00d9ff; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🤖 WHY AI SELECTED THIS</p>
                <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                    The AI automatically chooses the most suitable strategy based on current market regime. 
                    This ensures you're always trading with the optimal approach for current conditions, 
                    maximizing your probability of success.
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        elif st.session_state.show_status_details:
            
            if not trading_state.running:
                # Professional Status Details - System Stopped
                st.markdown("""
                <div style='color: #888; font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center;'>
                    ⚪ System Status: Inactive
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background: rgba(108,117,125,0.1); border-radius: 8px; padding: 20px; border: 1px solid rgba(108,117,125,0.3); margin-bottom: 15px;'>
                    <p style='color: #6c757d; font-size: 16px; font-weight: 600; margin: 0 0 10px 0; text-align: center;'>
                        ⚪ Trading System Inactive
                    </p>
                    <p style='color: #ffffff; margin: 0; font-size: 14px; text-align: center; line-height: 1.6;'>
                        The trading system is currently not running. Start trading to activate AI analysis and signal detection.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # How to Start
                st.markdown("""
                <div style='background: rgba(0,217,255,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(0,217,255,0.3); margin-bottom: 15px;'>
                    <p style='color: #00d9ff; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🚀 HOW TO START</p>
                    <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                        <div style='padding: 5px 0;'><strong>1.</strong> Click the <strong>Start Trading</strong> button above</div>
                        <div style='padding: 5px 0;'><strong>2.</strong> System will connect to live market data</div>
                        <div style='padding: 5px 0;'><strong>3.</strong> AI will begin analysis within 1-2 minutes</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Safety Features
                st.markdown("""
                <div style='background: rgba(76,175,80,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(76,175,80,0.3);'>
                    <p style='color: #4caf50; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🛡️ SAFETY FEATURES</p>
                    <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                        <div style='padding: 5px 0;'>✅ Paper trading enabled by default</div>
                        <div style='padding: 5px 0;'>✅ Risk management active</div>
                        <div style='padding: 5px 0;'>✅ Stop-loss protection ready</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif trading_state.current_regime == "Initializing...":
                # Professional Status Details - Initializing (Static Display)
                st.markdown("""
                <div style='color: #00d9ff; font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center;'>
                    🔄 System Status: Initializing
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background: rgba(0,217,255,0.1); border-radius: 8px; padding: 20px; border: 1px solid rgba(0,217,255,0.3); margin-bottom: 15px;'>
                    <p style='color: #00d9ff; font-size: 16px; font-weight: 600; margin: 0 0 10px 0; text-align: center;'>
                        🔄 Initializing AI Intelligence
                    </p>
                    <p style='color: #ffffff; margin: 0; font-size: 14px; text-align: center; line-height: 1.6;'>
                        Collecting live market data for <strong>{selected_symbol}</strong> and preparing analysis algorithms...
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Progress Checklist
                st.markdown("""
                <div style='background: rgba(33,150,243,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(33,150,243,0.3); margin-bottom: 15px;'>
                    <p style='color: #2196f3; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>📊 PROGRESS STATUS</p>
                    <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                        <div style='padding: 5px 0;'>✅ Connected to market feed</div>
                        <div style='padding: 5px 0;'>🔄 Building price history (20+ bars needed)</div>
                        <div style='padding: 5px 0;'>⏳ Preparing regime detection</div>
                        <div style='padding: 5px 0;'>⏳ Loading strategy algorithms</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Estimated Time
                st.markdown("""
                <div style='background: rgba(255,152,0,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(255,152,0,0.3);'>
                    <p style='color: #ff9800; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>⏱️ ESTIMATED TIME</p>
                    <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                        <strong>1-2 minutes</strong> - This is a one-time setup. Once complete, 
                        analysis will run continuously in real-time!
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Add animated progress
                st.markdown("""
                <div style='text-align: center; padding: 30px 20px;'>
                    <div style='display: inline-block; font-size: 50px; animation: pulse 1.5s ease-in-out infinite;'>
                        🔄
                    </div>
                    <p style='color: #00d9ff; margin-top: 15px; font-weight: 600; font-size: 16px;'>Initializing...</p>
                </div>
                <style>
                    @keyframes pulse {{
                        0%, 100% {{ transform: scale(1); opacity: 1; }}
                        50% {{ transform: scale(1.1); opacity: 0.7; }}
                    }}
                </style>
                """, unsafe_allow_html=True)
            elif trading_state.position_state == 'long':
                # Professional Status Details - Position Active
                st.markdown(f"""
                <div style='color: #4caf50; font-size: 18px; font-weight: 700; margin-bottom: 20px; text-align: center;'>
                    ✅ System Status: Position Active
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style='background: rgba(76,175,80,0.1); border-radius: 8px; padding: 20px; border: 1px solid rgba(76,175,80,0.3); margin-bottom: 15px;'>
                    <p style='color: #4caf50; font-size: 16px; font-weight: 600; margin: 0 0 10px 0; text-align: center;'>
                        ✅ LONG Position Active on {selected_symbol}
                    </p>
                    <p style='color: #ffffff; margin: 0; font-size: 14px; text-align: center; line-height: 1.6;'>
                        You have an active long position. AI is continuously monitoring for optimal exit signals.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # AI Monitoring
                st.markdown("""
                <div style='background: rgba(0,217,255,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(0,217,255,0.3); margin-bottom: 15px;'>
                    <p style='color: #00d9ff; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🤖 AI MONITORING</p>
                    <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                        <div style='padding: 5px 0;'>📊 Tracking price movements in real-time</div>
                        <div style='padding: 5px 0;'>🎯 Analyzing exit signals continuously</div>
                        <div style='padding: 5px 0;'>🛡️ Stop-loss protection active</div>
                        <div style='padding: 5px 0;'>⏱️ Updates every 3 seconds</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # What AI Is Watching
                st.markdown("""
                <div style='background: rgba(255,152,0,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(255,152,0,0.3); margin-bottom: 15px;'>
                    <p style='color: #ff9800; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>👁️ WHAT AI IS WATCHING</p>
                    <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                        <div style='padding: 5px 0;'>• Trend reversal signals</div>
                        <div style='padding: 5px 0;'>• Momentum weakening</div>
                        <div style='padding: 5px 0;'>• Support level breaks</div>
                        <div style='padding: 5px 0;'>• Volume changes</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Notification Alert
                st.markdown("""
                <div style='background: rgba(33,150,243,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(33,150,243,0.3);'>
                    <p style='color: #2196f3; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🔔 YOU'LL BE NOTIFIED WHEN</p>
                    <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                        The AI detects optimal exit conditions to protect profits or minimize losses. 
                        Exit signals will appear prominently when conditions are met.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Professional Status Details - Scanning (Unified Full Box)
                
                # Animated Status Switcher - cycles every 10 seconds
                current_time = int(time.time())
                cycle_index = (current_time // 10) % 6  # 6 status items, switch every 10 seconds
                
                # Define all status items
                status_items = [
                    {
                        'icon': '🔍',
                        'label': 'Scanning Status',
                        'content': f'AI actively analyzing <strong>{selected_symbol}</strong> for high-probability entry signals'
                    },
                    {
                        'icon': '📊',
                        'label': 'Monitoring',
                        'content': 'Price action analyzed every minute with 3-second updates'
                    },
                    {
                        'icon': '🧠',
                        'label': 'Market Regime',
                        'content': f'Evaluating <strong>{regime_display}</strong> market conditions'
                    },
                    {
                        'icon': '🎯',
                        'label': 'Active Strategy',
                        'content': f'Using <strong>{strategy_display}</strong> strategy'
                    },
                    {
                        'icon': '🎯',
                        'label': 'Looking For',
                        'content': 'Optimal entry points • Risk/reward setups • Multi-indicator confirmation • Volume validation'
                    },
                    {
                        'icon': '🔔',
                        'label': 'Alert Status',
                        'content': 'Ready to notify when strong buy signals detected with high confidence'
                    }
                ]
                
                # Get current status item
                current_status = status_items[cycle_index]
                
                # Build progress dots
                dot_color_0 = "#2196f3" if cycle_index == 0 else "rgba(33,150,243,0.3)"
                dot_color_1 = "#2196f3" if cycle_index == 1 else "rgba(33,150,243,0.3)"
                dot_color_2 = "#2196f3" if cycle_index == 2 else "rgba(33,150,243,0.3)"
                dot_color_3 = "#2196f3" if cycle_index == 3 else "rgba(33,150,243,0.3)"
                dot_color_4 = "#2196f3" if cycle_index == 4 else "rgba(33,150,243,0.3)"
                dot_color_5 = "#2196f3" if cycle_index == 5 else "rgba(33,150,243,0.3)"
                
                # Build the animated status display - UNIFIED FULL BOX with same gradient throughout
                st.markdown(f"""
                <style>
                    @keyframes fadeIn {{
                        from {{ opacity: 0; transform: translateY(-10px); }}
                        to {{ opacity: 1; transform: translateY(0); }}
                    }}
                </style>
                <div style='background: linear-gradient(135deg, rgba(33,150,243,0.15) 0%, rgba(0,217,255,0.15) 100%); 
                            border-radius: 12px; padding: 30px; border: 2px solid rgba(33,150,243,0.4); 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.3); animation: fadeIn 0.5s ease-in;'>
                    <div style='text-align: center; margin-bottom: 25px;'>
                        <p style='color: #2196f3; font-size: 18px; font-weight: 700; margin: 0;'>🔍 AI SCANNING STATUS</p>
                        <p style='color: #ffffff; margin: 8px 0 0 0; font-size: 13px; opacity: 0.9;'>Real-time market analysis and signal detection</p>
                    </div>
                    <div style='text-align: center; margin-bottom: 25px;'>
                        <div style='margin-bottom: 15px;'>
                            <span style='font-size: 48px;'>{current_status['icon']}</span>
                        </div>
                        <div style='margin-bottom: 12px;'>
                            <span style='color: #2196f3; font-weight: 700; font-size: 18px;'>{current_status['label']}</span>
                        </div>
                        <div style='max-width: 600px; margin: 0 auto;'>
                            <span style='color: #ffffff; font-size: 15px; line-height: 1.8;'>{current_status['content']}</span>
                        </div>
                    </div>
                    <div style='display: flex; justify-content: center; gap: 10px; margin-top: 20px;'>
                        <div style='width: 10px; height: 10px; border-radius: 50%; background: {dot_color_0}; transition: all 0.3s ease;'></div>
                        <div style='width: 10px; height: 10px; border-radius: 50%; background: {dot_color_1}; transition: all 0.3s ease;'></div>
                        <div style='width: 10px; height: 10px; border-radius: 50%; background: {dot_color_2}; transition: all 0.3s ease;'></div>
                        <div style='width: 10px; height: 10px; border-radius: 50%; background: {dot_color_3}; transition: all 0.3s ease;'></div>
                        <div style='width: 10px; height: 10px; border-radius: 50%; background: {dot_color_4}; transition: all 0.3s ease;'></div>
                        <div style='width: 10px; height: 10px; border-radius: 50%; background: {dot_color_5}; transition: all 0.3s ease;'></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # AI 5-Minute Analysis (NEW FEATURE)
                if 'bar_history' in st.session_state and selected_symbol in st.session_state.bar_history:
                    bars = st.session_state.bar_history[selected_symbol]
                    
                    if len(bars) >= 5:  # Need at least 5 bars for analysis
                        # Get last 5 bars for 5-minute analysis
                        recent_bars = bars[-5:]
                        
                        # Calculate price movement
                        first_price = recent_bars[0]['c']
                        last_price = recent_bars[-1]['c']
                        price_change = ((last_price - first_price) / first_price) * 100
                        
                        # Calculate volume trend
                        avg_volume = sum(bar.get('v', 0) for bar in recent_bars) / len(recent_bars)
                        latest_volume = recent_bars[-1].get('v', 0)
                        volume_trend = "increasing" if latest_volume > avg_volume else "decreasing"
                        
                        # Determine trend direction
                        if price_change > 0.5:
                            trend_direction = "📈 Upward"
                            trend_color = "#4caf50"
                            trend_bg = "rgba(76,175,80,0.1)"
                            trend_border = "rgba(76,175,80,0.3)"
                        elif price_change < -0.5:
                            trend_direction = "📉 Downward"
                            trend_color = "#f44336"
                            trend_bg = "rgba(244,67,54,0.1)"
                            trend_border = "rgba(244,67,54,0.3)"
                        else:
                            trend_direction = "➡️ Sideways"
                            trend_color = "#ff9800"
                            trend_bg = "rgba(255,152,0,0.1)"
                            trend_border = "rgba(255,152,0,0.3)"
                        
                        # Generate AI analysis message
                        if price_change > 0.5:
                            if regime_display == "TREND":
                                signal_assessment = "✅ BULLISH SIGNAL"
                                signal_color = "#4caf50"
                                reasoning = f"Price is rising (+{price_change:.2f}%) in a <strong>TREND</strong> market. This aligns with our {strategy_display} strategy. Volume is {volume_trend}, confirming momentum."
                                recommendation = "💡 <strong>This could be a good opportunity to BUY</strong> if entry conditions are fully met. Monitor for confirmation signals."
                            else:
                                signal_assessment = "⚠️ CAUTION"
                                signal_color = "#ff9800"
                                reasoning = f"Price is rising (+{price_change:.2f}%) but market regime is <strong>{regime_display}</strong>. Current conditions may not sustain upward movement."
                                recommendation = "💡 <strong>Wait for better setup.</strong> Price rise in non-trending markets often leads to reversals."
                        elif price_change < -0.5:
                            if regime_display == "SIDEWAYS" and strategy_display == "Mean Reversion":
                                signal_assessment = "✅ POTENTIAL OPPORTUNITY"
                                signal_color = "#4caf50"
                                reasoning = f"Price dropped ({price_change:.2f}%) in a <strong>SIDEWAYS</strong> market. Mean reversion strategy may find entry as price approaches support."
                                recommendation = "💡 <strong>Monitor for bounce signals</strong> near support levels. This could present a buying opportunity."
                            else:
                                signal_assessment = "🛑 BEARISH SIGNAL"
                                signal_color = "#f44336"
                                reasoning = f"Price is falling ({price_change:.2f}%) with {volume_trend} volume. Current {strategy_display} strategy suggests caution."
                                recommendation = "💡 <strong>NOT a good time to BUY.</strong> Wait for price stabilization or trend reversal confirmation."
                        else:
                            signal_assessment = "⏸️ NEUTRAL"
                            signal_color = "#888"
                            reasoning = f"Price movement is minimal ({price_change:+.2f}%) over the last 5 minutes. Market is consolidating."
                            recommendation = "💡 <strong>No clear signal yet.</strong> Waiting for more decisive price action before suggesting entry."
                        
                        # Display AI 5-Minute Analysis
                        st.markdown(f"""
                        <div style='background: {trend_bg}; border-radius: 8px; padding: 15px; border: 1px solid {trend_border}; margin-bottom: 15px;'>
                            <p style='color: {trend_color}; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🧠 AI 5-MINUTE ANALYSIS</p>
                            <div style='color: #ffffff; font-size: 13px; line-height: 1.8;'>
                                <div style='padding: 5px 0;'><strong>Price Movement:</strong> {trend_direction} ({price_change:+.2f}%)</div>
                                <div style='padding: 5px 0;'><strong>Current Price:</strong> ${last_price:.2f}</div>
                                <div style='padding: 5px 0;'><strong>Volume Trend:</strong> {volume_trend.capitalize()}</div>
                                <div style='padding: 5px 0; margin-top: 10px;'><span style='color: {signal_color}; font-weight: 600;'>{signal_assessment}</span></div>
                                <div style='padding: 5px 0; margin-top: 5px; background: rgba(0,0,0,0.2); border-radius: 4px; padding: 10px;'>
                                    {reasoning}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # AI Recommendation Box
                        st.markdown(f"""
                        <div style='background: rgba(0,217,255,0.1); border-radius: 8px; padding: 15px; border: 1px solid rgba(0,217,255,0.3); margin-bottom: 15px;'>
                            <p style='color: #00d9ff; font-size: 14px; font-weight: 600; margin: 0 0 10px 0;'>🎯 AI RECOMMENDATION</p>
                            <p style='color: #ffffff; margin: 0; font-size: 13px; line-height: 1.6;'>
                                {recommendation}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Add scanning animation
                st.markdown("""
                <div style='text-align: center; padding: 30px 20px;'>
                    <div style='display: inline-block; font-size: 50px; animation: scan 2s linear infinite;'>
                        🔍
                    </div>
                    <p style='color: #2196f3; margin-top: 15px; font-weight: 600; font-size: 16px;'>Actively Scanning...</p>
                </div>
                <style>
                    @keyframes scan {
                        0% { transform: translateX(-20px); }
                        50% { transform: translateX(20px); }
                        100% { transform: translateX(-20px); }
                    }
                </style>
                """, unsafe_allow_html=True)
    
    # Footer section removed - no table wrapper needed
    
    # Show error notification if there are recent errors
    recent_errors = [e for e in trading_state.error_log if e['severity'] == 'ERROR']
    if recent_errors:
        st.error(f"⚠️ {len(recent_errors)} error(s)")
    
    # Show notifications/signals when available
    if trading_state.notification:
        # Display notification with markdown formatting
        st.markdown(trading_state.notification)
        
        # 🎯 PHASE 5: Show Position Sizing Recommendation for BUY signals
        if "BUY" in trading_state.notification and hasattr(st.session_state, 'last_entry_risk_score'):
            risk_score = st.session_state.get('last_entry_risk_score', 50)
            risk_level = st.session_state.get('last_entry_risk_level', 'MEDIUM')
            
            # Calculate recommended position size reduction
            base_qty = 100  # Example: 100 shares baseline
            recommended_qty, sizing_explanation = risk_manager.recommend_position_size(base_qty, risk_score)
            
            # Show position sizing recommendation
            st.markdown("##### 💰 Recommended Position Sizing")
            
            sizing_color = "#4caf50" if risk_level == "LOW" else "#ff9800" if risk_level == "MEDIUM" else "#f44336"
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 3px solid {sizing_color}; margin-top: 15px;'>
                <p style='margin: 0; font-size: 13px;'>{sizing_explanation}</p>
                <p style='margin: 8px 0 0 0; color: {sizing_color}; font-size: 14px; font-weight: 600;'>
                    💡 Suggested: {recommended_qty} shares (adjust based on your capital)
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Primary action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if "BUY" in trading_state.notification:
                if st.button("✅ Execute Buy", use_container_width=True, type="primary"):
                    trading_state.position_state = 'long'
                    st.success("✅ Position opened! Monitoring for sell signals...")
                    trading_state.notification = None
                    time.sleep(2)
                    st.rerun()
        
        with col2:
            if "SELL" in trading_state.notification:
                if st.button("❌ Execute Sell", use_container_width=True, type="secondary"):
                    trading_state.position_state = None
                    st.success("✅ Position closed! Monitoring for buy signals...")
                    trading_state.notification = None
                    time.sleep(2)
                    st.rerun()
        
        with col3:
            if st.button("🔕 Dismiss", use_container_width=True):
                trading_state.notification = None
                st.rerun()
        
        # Phase 5: User Action Confirmation Loop - "Did You Buy?" Feature
        st.markdown("##### 📝 Manual Execution Confirmation")
        st.markdown("*Did you manually execute this trade on TradingView?*")
        
        conf_col1, conf_col2 = st.columns([1, 1])
        
        with conf_col1:
            if "BUY" in trading_state.notification:
                if st.button("✅ I Bought", use_container_width=True, key="confirm_buy"):
                    # User confirmed they bought manually
                    trading_state.position_state = 'long'
                    st.session_state.user_confirmed_action = True
                    st.session_state.last_action_time = datetime.now()
                    st.success("✅ Confirmed! AI will now monitor for exit signals.")
                    trading_state.notification = None
                    time.sleep(2)
                    st.rerun()
            
            if "SELL" in trading_state.notification and trading_state.position_state == 'long':
                if st.button("✅ I Sold", use_container_width=True, key="confirm_sell"):
                    # User confirmed they sold manually
                    trading_state.position_state = None
                    st.session_state.user_confirmed_action = True
                    st.session_state.last_action_time = datetime.now()
                    st.success("✅ Confirmed! AI will scan for new opportunities.")
                    trading_state.notification = None
                    time.sleep(2)
                    st.rerun()
        
        with conf_col2:
            if "BUY" in trading_state.notification or "SELL" in trading_state.notification:
                if st.button("❌ I Skipped", use_container_width=True, key="skip_signal"):
                    # User chose to skip this signal
                    st.session_state.user_skipped_signal = True
                    st.session_state.skipped_signal_time = datetime.now()
                    st.session_state.skipped_strategy = trading_state.current_strategy
                    st.session_state.skipped_regime = trading_state.current_regime
                    
                    st.warning("⚠️ Signal skipped. AI will reduce confidence for this strategy temporarily.")
                    trading_state.notification = None
                    time.sleep(2)
                    st.rerun()
    
    # ============================================================================
    # ACCOUNT METRICS - Only show if trading is active
    # ============================================================================
    if trading_state.broker and trading_state.running:
        try:
            st.subheader("💼 Account Status")
            acc_cols = st.columns(4)
            
            portfolio_value = account.get('portfolio_value', 0)
            acc_cols[0].metric(
                "💰 Portfolio Value",
                f"${portfolio_value:,.2f}",
                delta=f"{((portfolio_value / settings['initial_capital']) - 1) * 100:.2f}%"
            )
            
            acc_cols[1].metric("💵 Cash", f"${account.get('cash', 0):,.2f}")
            acc_cols[2].metric("📍 Open Positions", len(positions))
            
            total_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
            acc_cols[3].metric(
                "📈 Unrealized P&L",
                f"${total_pl:.2f}",
                delta=f"{(total_pl / portfolio_value * 100):.2f}%" if portfolio_value > 0 else "0%"
            )
            
            # Market Intelligence & Risk
            st.subheader("Market Analysis & Risk")
            intel_cols = st.columns(2)
            
            with intel_cols[0]:
                st.markdown("**🧠 Market Intelligence**")
                regime_color = {
                    'TREND': '🟢',
                    'SIDEWAYS': '🟡',
                    'VOLATILE': '🔴',
                    'Unknown': '⚪'
                }
                st.markdown(f"- **Regime:** {regime_color.get(trading_state.current_regime, '⚪')} {trading_state.current_regime}")
                st.markdown(f"- **Strategy:** 🎯 {trading_state.current_strategy}")

            with intel_cols[1]:
                st.markdown("**🛡️ Risk Management**")
                risk_manager = RiskManager(
                    initial_capital=settings['initial_capital'],
                    max_risk_per_trade=settings['max_risk_per_trade']
                )
                risk_summary = risk_manager.get_risk_summary(
                    account,
                    {pos['symbol']: pos for pos in positions}
                )
                status_color_map = {
                    'HEALTHY': '🟢',
                    'WARNING': '🟡',
                    'CRITICAL': '🔴'
                }
                st.markdown(f"- **Status:** {status_color_map.get(risk_summary['risk_status'], '⚪')} {risk_summary['risk_status']}")
                st.markdown(f"- **Drawdown:** {risk_summary['drawdown_pct']:.2f}%")

            
            # Two columns: Positions & Trading Activity
            left_col, right_col = st.columns([3, 2])
            
            with left_col:
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
        
        except Exception as e:
            st.error(f"Error fetching account data: {e}")
    # Auto-refresh dashboard when trading is active - ONLY ONCE at the bottom
    if trading_state.running:
        # Create a container for the refresh indicator to prevent duplicates
        with st.container():
            refresh_col1, refresh_col2, refresh_col3 = st.columns([1, 2, 1])
            with refresh_col2:
                st.markdown("""
                <div style='text-align: center; padding: 10px; background: rgba(0, 217, 255, 0.1); border-radius: 8px; border: 1px solid rgba(0, 217, 255, 0.3); margin-top: 20px;'>
                    <p style='margin: 0; color: #00d9ff; font-size: 14px;'>
                        🔄 <b>Live Updates Active</b> - Refreshing every 3 seconds
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        time.sleep(3)  # Refresh every 3 seconds for responsive UI
        st.rerun()


def show_control_page():
    """Display trading control panel."""
    st.title("🎮 Trading Control")
    
    settings = load_settings()
    
    if not check_configuration():
        st.error("⚠️ Please configure API keys in Settings first!")
        return
    
    # Get selected asset info
    selected_symbol = settings.get('trading_symbol', 'SPY')
    tradingview_symbol = settings.get('tradingview_symbol', 'NASDAQ:SPY')
    asset_category = settings.get('asset_category', 'Stocks')
    
    st.info(f"📊 **Current Asset:** {selected_symbol} ({asset_category})")
    
    st.subheader("⚡ Real-Time Trading System")
    st.markdown("""
    **System Features:**
    - 🔴 **Live Market Data** from TradingView
    - 🧠 **AI-Powered Analysis** with regime detection
    - 📊 **Real-Time Signals** for optimal entry/exit
    - 🛡️ **Advanced Risk Management**
    - 📈 **Multi-Asset Support** (Stocks, Forex, Crypto, Indices)
    """)
    
    if not REALTIME_AVAILABLE:
        st.error("❌ Install alpaca-trade-api first:\n```pip install alpaca-trade-api```")
        return
    
    # Stop button
    if trading_state.running:
        st.warning(f"🟢 System is running in **{trading_state.mode.upper()}** mode")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🛑 Stop Trading", use_container_width=True, type="secondary"):
                try:
                    trading_state.running = False
                    
                    # Close WebSocket connection if exists
                    if trading_state.stream is not None:
                        try:
                            logger.logger.info("🔌 Closing WebSocket connection...")
                            trading_state.stream.stop()
                            time.sleep(1)  # Give time to properly close
                            trading_state.stream = None
                            logger.logger.info("✅ WebSocket closed")
                        except Exception as e:
                            logger.logger.warning(f"Warning closing WebSocket: {e}")
                            trading_state.stream = None
                    
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
    
    st.subheader("⚙️ Current Configuration")
    
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
    
    st.markdown("""
    # 🥝 Kiwi AI Trading System v2.0
    
    Welcome to the upgraded Kiwi AI real-time trading system with TradingView integration!
    
    ## 🚀 Quick Start
    
    1. **Configure Settings**: Go to the "Settings" tab and enter your Alpaca API keys
    2. **Select Asset**: Choose from Stocks, Forex, Crypto, Indices, or Commodities
    3. **Test Connection**: Use the "Test Connection" button to verify your setup
    4. **Auto-Start**: System automatically starts when you open the Dashboard
    5. **Monitor**: Watch real-time TradingView charts and AI signals
    
    ## 🆕 What's New in v2.0
    
    ### 📊 TradingView Integration
    - **Real-time professional charts** embedded in the dashboard
    - **Multi-asset support**: Trade stocks, forex, crypto, indices, and commodities
    - **Advanced technical indicators** built into the charts
    - **Live market data** from TradingView
    
    ### ⚡ Auto-Start System
    - **Instant activation**: No need to manually start trading
    - **Real-time only**: Always connected to live market data
    - **Continuous monitoring**: AI analyzes markets 24/7
    - **Smart alerts**: Get notified of trading opportunities instantly
    
    ### 🌍 Multi-Asset Trading
    - **Stocks**: NVDA, AAPL, TSLA, MSFT, AMZN, and more
    - **Forex**: EUR/USD, GBP/USD, USD/JPY, etc.
    - **Crypto**: BTC, ETH, SOL, ADA, XRP
    - **Indices**: NASDAQ, S&P 500, Dow Jones
    - **Commodities**: Gold, Silver, Oil, Natural Gas
    
    ## 🛡️ Safety Features
    
    - **Paper Trading**: Test with fake money before going live (enabled by default)
    - **Risk Management**: Automatic position sizing and stop-loss calculation
    - **Regime Detection**: Adapts to different market conditions
    - **Performance Monitoring**: Tracks strategy performance and switches if needed
    
    ## ⚙️ Configuration
    
    All settings can be configured visually in the Settings tab:
    
    - **API Keys**: Your Alpaca API credentials
    - **Trading Mode**: Paper vs Live trading
    - **Capital**: Initial account balance
    - **Risk Parameters**: Max risk per trade, position size limits
    - **Trading Symbol**: Which stock to trade (e.g., SPY, QQQ)
    - **Intervals**: How often to check for signals
    
    ## 📊 Strategies
    
    Kiwi AI includes three adaptive strategies:
    
    1. **Trend Following**: Captures strong directional moves
    2. **Mean Reversion**: Profits from price reversals
    3. **Volatility Breakout**: Trades explosive moves
    
    The system automatically selects the best strategy based on current market regime.
    
    ## ⚠️ Important Notes
    
    - Always test with paper trading first!
    - Never risk more than you can afford to lose
    - Monitor the system regularly, especially in live mode
    - Market conditions can change rapidly
    - Past performance doesn't guarantee future results
    
    ## 🔧 Troubleshooting
    
    ### "Connection limit exceeded" Error
    
    **Problem:** You see `ValueError: connection limit exceeded` or `HTTP 429` errors.
    
    **Causes:**
    - Multiple instances of the app running
    - Old WebSocket connections not properly closed
    - Alpaca free tier allows only 1 concurrent connection
    
    **Solutions:**
    1. **Stop the current session:** Click "🛑 Stop Trading" button
    2. **Close all app instances:** Check Task Manager and close all `python.exe` or `streamlit` processes
    3. **Restart the application:** Run `python run_kiwi.py` again
    4. **Wait 30 seconds** before starting a new session
    5. **Use Daily Mode** instead of Real-Time Mode (no WebSocket needed)
    
    ### Other Common Issues
    
    - **Invalid API keys:** Check Settings tab and verify your Alpaca credentials
    - **Market closed:** Trading only works during market hours (9:30 AM - 4:00 PM ET)
    - **Insufficient funds:** Check your account balance in the Dashboard
    - **Network errors:** Verify your internet connection
    
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
    
    st.success("💡 Tip: Start with paper trading and small position sizes to learn the system!")


def show_error_log_page():
    """Display error log viewer."""
    st.title("🐛 Error & Debug Log")
    
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
                        st.markdown("**Exception:**")
                        st.code(error['exception'], language='python')
                    
                    if error['context']:
                        st.markdown("**Context:**")
                        st.json(error['context'])
                    
                    if show_traceback and error['traceback']:
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
                    st.text_area("Copy Error Details:", error_text, height=100, key=f"error_{idx}")
    
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
        @import url('https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;600;700&display=swap');
        
        /* Global Styles */
        * {
            font-family: 'Ubuntu', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
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
        
        /* Professional Navigation Buttons */
        .nav-btn {
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            padding: 14px 16px;
            margin: 6px 0;
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            color: #e0e0e0;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            user-select: none;
        }
        
        .nav-btn:hover {
            background: rgba(0, 217, 255, 0.12);
            border-color: rgba(0, 217, 255, 0.4);
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.15);
        }
        
        .nav-btn.active {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.18) 0%, rgba(76, 175, 254, 0.18) 100%);
            border-color: #00d9ff;
            color: #00d9ff;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
        }
        
        .nav-btn svg {
            width: 20px;
            height: 20px;
            flex-shrink: 0;
        }
        
        .nav-btn.active svg {
            filter: drop-shadow(0 0 4px rgba(0, 217, 255, 0.6));
        }
        
        .nav-btn:active {
            transform: translateX(2px) scale(0.98);
        }
        
        /* Style Streamlit navigation buttons to match nav-btn */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            color: #e0e0e0 !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 14px 16px !important;
            margin: 6px 0 !important;
            width: 100% !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(0, 217, 255, 0.12) !important;
            border-color: rgba(0, 217, 255, 0.4) !important;
            transform: translateX(4px) !important;
            box-shadow: 0 4px 12px rgba(0, 217, 255, 0.15) !important;
        }
        
        [data-testid="stSidebar"] .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.18) 0%, rgba(76, 175, 254, 0.18) 100%) !important;
            border-color: #00d9ff !important;
            color: #00d9ff !important;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.3) !important;
        }
        
        /* Navigation Group Header */
        .nav-group-header {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 16px;
            margin: -20px 0 12px 0;
            color: #b0b0b0;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Sidebar Logo */
        .sidebar-logo {
            text-align: center;
            padding: 24px 0;
            margin-bottom: 8px;
        }
        
        .sidebar-logo-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 12px;
            display: block;
        }
        
        .sidebar-logo-title {
            margin: 0;
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.5px;
        }
        
        .sidebar-logo-subtitle {
            margin: 4px 0 0 0;
            color: #00d9ff;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
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
        # Initialize page in session state if not exists
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"
        
        # Professional Header with SVG Logo
        st.markdown("""
            <div class="sidebar-logo">
                <svg class="sidebar-logo-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" style="stop-color:#00d9ff;stop-opacity:1" />
                            <stop offset="100%" style="stop-color:#4cafff;stop-opacity:1" />
                        </linearGradient>
                    </defs>
                    <path d="M24 4L8 14V34L24 44L40 34V14L24 4Z" stroke="url(#logoGradient)" stroke-width="2" fill="rgba(0, 217, 255, 0.1)"/>
                    <path d="M24 12L14 18V30L24 36L34 30V18L24 12Z" fill="url(#logoGradient)"/>
                    <circle cx="24" cy="24" r="3" fill="#0f0c29"/>
                    <path d="M20 20L24 24L28 20" stroke="#0f0c29" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M20 28L24 24L28 28" stroke="#0f0c29" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                <h1 class="sidebar-logo-title">Kiwi AI</h1>
                <p class="sidebar-logo-subtitle">Trading System</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Professional Navigation with clickable divs - Collapsible menu
        current_page = st.session_state.current_page
        
        # Initialize dashboard expanded state
        if 'dashboard_expanded' not in st.session_state:
            st.session_state.dashboard_expanded = True
        
        # Check for query parameter navigation and handle clicks
        query_params = st.query_params
        if "page" in query_params:
            page_param = query_params["page"].replace("+", " ")  # Handle URL encoding
            if page_param in ["Dashboard", "Control", "Settings", "Error Log", "Help"]:
                st.session_state.current_page = page_param
            # Clear query params after reading
            st.query_params.clear()
            st.rerun()
        
        # Create collapsible navigation with Apple-style design
        st.markdown("### NAVIGATION")
        
        # Dashboard - Main button with expand/collapse
        dashboard_active = current_page in ["Dashboard", "Settings", "Error Log", "Help"]
        expand_icon = "▼" if st.session_state.dashboard_expanded else "▶"
        
        # Custom styled button for Dashboard
        st.markdown(f"""
        <style>
        .dashboard-main-btn {{
            background: {'linear-gradient(135deg, rgba(0, 217, 255, 0.2), rgba(76, 175, 254, 0.2))' if dashboard_active else 'rgba(255, 255, 255, 0.05)'};
            border: 1px solid {'rgba(0, 217, 255, 0.4)' if dashboard_active else 'rgba(255, 255, 255, 0.1)'};
            border-radius: 10px;
            padding: 12px 16px;
            margin: 8px 0;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .dashboard-main-btn:hover {{
            background: linear-gradient(135deg, rgba(0, 217, 255, 0.15), rgba(76, 175, 254, 0.15));
            border-color: rgba(0, 217, 255, 0.3);
            transform: translateX(4px);
        }}
        .dashboard-main-text {{
            color: {'#00d9ff' if dashboard_active else '#ffffff'};
            font-weight: 600;
            font-size: 15px;
        }}
        .dashboard-expand-icon {{
            color: {'#00d9ff' if dashboard_active else 'rgba(255, 255, 255, 0.5)'};
            font-size: 14px;
        }}
        .sub-menu-item {{
            background: rgba(255, 255, 255, 0.03);
            border-left: 3px solid rgba(0, 217, 255, 0.3);
            border-radius: 6px;
            padding: 10px 16px;
            margin: 4px 0 4px 20px;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .sub-menu-item:hover {{
            background: rgba(0, 217, 255, 0.1);
            border-left-color: rgba(0, 217, 255, 0.6);
            transform: translateX(4px);
        }}
        .sub-menu-item.active {{
            background: rgba(0, 217, 255, 0.15);
            border-left-color: #00d9ff;
        }}
        .sub-menu-text {{
            color: #ffffff;
            font-size: 14px;
            font-weight: 500;
        }}
        .sub-menu-text.active {{
            color: #00d9ff;
            font-weight: 600;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # Dashboard main button - toggle expand/collapse
        if st.button(f"{expand_icon}  📊 Dashboard", key="nav_dashboard_main", use_container_width=True, 
                     type="primary" if dashboard_active else "secondary"):
            st.session_state.dashboard_expanded = not st.session_state.dashboard_expanded
            # If clicking on dashboard, set to Dashboard page
            if not st.session_state.dashboard_expanded:
                st.session_state.current_page = "Dashboard"
            st.rerun()
        
        # Show sub-menu items when expanded
        if st.session_state.dashboard_expanded:
            # Dashboard Overview
            col1, col2 = st.columns([0.1, 0.9])
            with col2:
                dashboard_selected = current_page == "Dashboard"
                if st.button("📈 Overview", key="nav_dashboard_overview", use_container_width=True,
                           type="primary" if dashboard_selected else "secondary"):
                    st.session_state.current_page = "Dashboard"
                    st.rerun()
            
            # Settings
            col1, col2 = st.columns([0.1, 0.9])
            with col2:
                settings_selected = current_page == "Settings"
                if st.button("⚙️ Settings", key="nav_settings_sub", use_container_width=True,
                           type="primary" if settings_selected else "secondary"):
                    st.session_state.current_page = "Settings"
                    st.rerun()
            
            # Error Log
            col1, col2 = st.columns([0.1, 0.9])
            with col2:
                error_log_selected = current_page == "Error Log"
                if st.button("🔍 Error Log", key="nav_error_log_sub", use_container_width=True,
                           type="primary" if error_log_selected else "secondary"):
                    st.session_state.current_page = "Error Log"
                    st.rerun()
            
            # Help
            col1, col2 = st.columns([0.1, 0.9])
            with col2:
                help_selected = current_page == "Help"
                if st.button("❓ Help", key="nav_help_sub", use_container_width=True,
                           type="primary" if help_selected else "secondary"):
                    st.session_state.current_page = "Help"
                    st.rerun()
        
        # Update page variable for routing
        page = st.session_state.current_page
        
        # System info with professional styling
        st.markdown("### System Info")
        settings = load_settings()
        
        # Status indicator with animation
        status_class = "status-running" if trading_state.running else "status-stopped"
        status_text = "LIVE" if trading_state.running else "STOPPED"
        status_icon = "🔴" if trading_state.running else "⚪"
        
        # Always show REAL-TIME mode
        mode_display = "REAL-TIME"
        
        # Get current trading symbol
        current_symbol = settings.get('trading_symbol', 'SPY')
        
        st.markdown(f"""
            <div style='padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 12px; margin: 10px 0;'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>VERSION</span>
                    <span style='color: #ffffff; font-weight: 600;'>2.0.0</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>MODE</span>
                    <span style='color: #00d9ff; font-weight: 600;'>{mode_display}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>ASSET</span>
                    <span style='color: #ffffff; font-weight: 600;'>{current_symbol}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 8px;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>ACCOUNT</span>
                    <span style='color: #00d9ff; font-weight: 600;'>{'PAPER' if settings['is_paper_trading'] else 'LIVE'}</span>
                </div>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='color: #b0b0b0; font-size: 12px;'>STATUS</span>
                    <span style='font-weight: 600; font-size: 14px;'>{status_icon} {status_text}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # End of sidebar - NO additional content should appear below
    # All navigation is within the collapsible Dashboard menu
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Settings":
        show_settings_page()
    elif page == "Error Log":
        show_error_log_page()
    elif page == "Help":
        show_help_page()
    else:
        # Default to dashboard if unknown page
        st.session_state.current_page = "Dashboard"
        show_dashboard_page()
    
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
