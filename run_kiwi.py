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

            logger.logger.info(f"Strategy type: {type(strategy)}")
            signal = strategy.generate_signals(df)
            logger.logger.info(f"Signal type: {type(signal)}")

            if signal is not None and len(signal) > 0:
                latest_signal = signal.iloc[-1]
                trading_state.last_signal = latest_signal

                if trading_state.position_state is None: # Looking to buy
                    if latest_signal == 1:
                        trading_state.notification = "Recommendation: BUY"
                        last_signal_time[symbol] = datetime.now()
                elif trading_state.position_state == 'long': # Looking to sell
                    if latest_signal == -1:
                        trading_state.notification = "Recommendation: SELL"
                        last_signal_time[symbol] = datetime.now()
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
        
        st.markdown("---")
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
    st.markdown("---")
    
    col_selector, col_controls = st.columns([3, 1])
    
    with col_selector:
        st.markdown("### 📊 Select Trading Asset")
        
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
        st.markdown("### ⚡ Trading Controls")
        
        # Start/Stop trading button
        if trading_state.running:
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
    
    st.markdown("---")
    
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
    
    st.markdown("---")
    
    # ============================================================================
    # TRADINGVIEW CHART - Full Width Professional Display
    # ============================================================================
    st.subheader(f"📊 {selected_asset_name} - Real-Time Chart")
    
    chart_col, info_col = st.columns([6, 1])
    
    with chart_col:
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
                "width": "100%",
                "height": "100%",
                "symbol": "{tradingview_symbol}",
                "interval": "5",
                "timezone": "America/New_York",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#0f0c29",
                "enable_publishing": false,
                "hide_top_toolbar": false,
                "hide_legend": false,
                "save_image": true,
                "container_id": "tradingview_chart",
                "backgroundColor": "rgba(15, 12, 41, 1)",
                "gridColor": "rgba(0, 217, 255, 0.06)",
                "hide_volume": false,
                "support_host": "https://www.tradingview.com",
                "studies": [
                  "RSI@tv-basicstudies",
                  "MASimple@tv-basicstudies"
                ],
                "show_popup_button": true,
                "popup_width": "1000",
                "popup_height": "650"
              }});
            </script>
        </body>
        </html>
        """
        components.html(tradingview_html, height=700)
    
    with info_col:
        st.markdown("### 🧠 AI Intelligence")
        
        # AI Status with colored indicators
        regime_colors = {
            'TREND': '🟢',
            'SIDEWAYS': '🟡', 
            'VOLATILE': '🔴',
            'Unknown': '⚪'
        }
        regime_icon = regime_colors.get(trading_state.current_regime, '⚪')
        
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(0,217,255,0.2); margin-bottom: 10px;'>
            <p style='margin: 0; color: #b0b0b0; font-size: 11px;'>MARKET REGIME</p>
            <p style='margin: 5px 0 0 0; color: #ffffff; font-size: 16px; font-weight: 600;'>{regime_icon} {trading_state.current_regime}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(0,217,255,0.2); margin-bottom: 10px;'>
            <p style='margin: 0; color: #b0b0b0; font-size: 11px;'>ACTIVE STRATEGY</p>
            <p style='margin: 5px 0 0 0; color: #00d9ff; font-size: 16px; font-weight: 600;'>🎯 {trading_state.current_strategy}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 Asset Details")
        st.markdown(f"**Symbol:** `{selected_symbol}`")
        st.markdown(f"**Exchange:** `{tradingview_symbol.split(':')[0]}`")
        st.markdown(f"**Type:** `{asset_category}`")
        
        # Show error notification if there are recent errors
        recent_errors = [e for e in trading_state.error_log if e['severity'] == 'ERROR']
        if recent_errors:
            st.markdown("---")
            st.error(f"⚠️ {len(recent_errors)} error(s)")
    
    st.markdown("---")
    
    # AI Recommendations section
    st.subheader("🧠 AI Recommendations")
    if trading_state.notification:
        st.warning(trading_state.notification)
        col1, col2 = st.columns(2)
        with col1:
            if "BUY" in trading_state.notification:
                if st.button("✅ Execute Buy", use_container_width=True, type="primary"):
                    trading_state.position_state = 'long'
                    trading_state.notification = None
                    st.rerun()
        with col2:
            if "SELL" in trading_state.notification:
                if st.button("❌ Execute Sell", use_container_width=True, type="secondary"):
                    trading_state.position_state = None
                    trading_state.notification = None
                    st.rerun()
    else:
        st.info("🤖 AI is analyzing the market... Waiting for signals.")
    
    st.markdown("---")
        
    # Account metrics
    if trading_state.broker:
        try:
            st.subheader("Account Status")
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
            st.markdown("---")
            
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

            st.markdown("---")
            
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
    
    st.markdown("---")
    
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
    # 🥝 Kiwi AI Trading System v2.0
    
    Welcome to the upgraded Kiwi AI real-time trading system with TradingView integration!
    
    ## 🚀 Quick Start
    
    1. **Configure Settings**: Go to the "Settings" tab and enter your Alpaca API keys
    2. **Select Asset**: Choose from Stocks, Forex, Crypto, Indices, or Commodities
    3. **Test Connection**: Use the "Test Connection" button to verify your setup
    4. **Auto-Start**: System automatically starts when you open the Dashboard
    5. **Monitor**: Watch real-time TradingView charts and AI signals
    
    ---
    
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
    
    ## � Troubleshooting
    
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
    
    ---
    
    ## �🔗 Resources
    
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
        st.markdown("---")
        
        # Navigation Menu with Professional Design using Custom HTML
        st.markdown('<div class="nav-group-header">NAVIGATION</div>', unsafe_allow_html=True)
        
        # Professional Navigation with clickable divs - All together
        current_page = st.session_state.current_page
        
        # Check for query parameter navigation and handle clicks
        query_params = st.query_params
        if "page" in query_params:
            page_param = query_params["page"].replace("+", " ")  # Handle URL encoding
            if page_param in ["Dashboard", "Control", "Settings", "Error Log", "Help"]:
                st.session_state.current_page = page_param
            # Clear query params after reading
            st.query_params.clear()
            st.rerun()
        
        # Create navigation buttons with proper click handlers
        st.markdown("### NAVIGATION")
        
        # Dashboard (merged with Control)
        dashboard_active = "active" if current_page == "Dashboard" else ""
        if st.button("Dashboard", key="nav_dashboard", use_container_width=True, type="primary" if dashboard_active else "secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        # Settings
        settings_active = "active" if current_page == "Settings" else ""
        if st.button("Settings", key="nav_settings", use_container_width=True, type="primary" if settings_active else "secondary"):
            st.session_state.current_page = "Settings"
            st.rerun()
        
        # Error Log
        error_log_active = "active" if current_page == "Error Log" else ""
        if st.button("Error Log", key="nav_error_log", use_container_width=True, type="primary" if error_log_active else "secondary"):
            st.session_state.current_page = "Error Log"
            st.rerun()
        
        # Help
        help_active = "active" if current_page == "Help" else ""
        if st.button("Help", key="nav_help", use_container_width=True, type="primary" if help_active else "secondary"):
            st.session_state.current_page = "Help"
            st.rerun()
        
        # Update page variable for routing
        page = st.session_state.current_page
        
        st.markdown("---")
        
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
