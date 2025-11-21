"""
Configuration Module for Kiwi_AI Trading System
Loads environment variables and provides centralized configuration management.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================================
# BROKER API CONFIGURATION
# ================================
ALPACA_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY")
IS_PAPER_TRADING = os.getenv("ALPACA_PAPER_TRADING", "true").lower() == "true"

# ================================
# TRADING PARAMETERS
# ================================
MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))
MAX_PORTFOLIO_RISK = float(os.getenv("MAX_PORTFOLIO_RISK", "0.10"))
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "100000"))
TRADING_INTERVAL = int(os.getenv("TRADING_INTERVAL", "60"))
TRADING_SYMBOL = os.getenv("TRADING_SYMBOL", "SPY")

# ================================
# STRATEGY SELECTION PARAMETERS
# ================================
MIN_STRATEGY_CONFIDENCE = float(os.getenv("MIN_STRATEGY_CONFIDENCE", "0.6"))
PERFORMANCE_WINDOW = int(os.getenv("PERFORMANCE_WINDOW", "20"))
PERFORMANCE_THRESHOLD = float(os.getenv("PERFORMANCE_THRESHOLD", "0.5"))

# ================================
# REGIME DETECTION PARAMETERS
# ================================
REGIME_LOOKBACK_DAYS = int(os.getenv("REGIME_LOOKBACK_DAYS", "30"))
REGIME_MIN_CONFIDENCE = float(os.getenv("REGIME_MIN_CONFIDENCE", "0.7"))

# ================================
# RISK MANAGEMENT
# ================================
MAX_DRAWDOWN = float(os.getenv("MAX_DRAWDOWN", "0.15"))
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.20"))
DEFAULT_STOP_LOSS = float(os.getenv("DEFAULT_STOP_LOSS", "0.05"))
DEFAULT_TAKE_PROFIT = float(os.getenv("DEFAULT_TAKE_PROFIT", "0.10"))

# ================================
# DATA CONFIGURATION
# ================================
DATA_PROVIDER = os.getenv("DATA_PROVIDER", "alpaca")
DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "1Day")
HISTORICAL_LOOKBACK = int(os.getenv("HISTORICAL_LOOKBACK", "365"))

# ================================
# DATABASE CONFIGURATION (Optional)
# ================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "kiwi_ai_data")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

# ================================
# DATA SETTINGS
# ================================
DATA_DIRECTORY = "market_data"
BACKTEST_REPORTS_DIR = "backtest_reports"

# ================================
# MODEL SETTINGS
# ================================
MODELS_DIRECTORY = "models"
REGIME_MODEL_PATH = os.path.join(MODELS_DIRECTORY, "regime_detector.pkl")

# ================================
# LOGGING CONFIGURATION
# ================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "30"))
LOG_FILE = "kiwi_ai.log"

# ================================
# DASHBOARD CONFIGURATION
# ================================
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8501"))
DASHBOARD_REFRESH = int(os.getenv("DASHBOARD_REFRESH", "5"))

# ================================
# NOTIFICATIONS (Optional)
# ================================
ENABLE_EMAIL_NOTIFICATIONS = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

ENABLE_TELEGRAM_NOTIFICATIONS = os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "false").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ================================
# ENVIRONMENT
# ================================
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG_MODE = os.getenv("DEBUG_MODE", "true").lower() == "true"

# ================================
# VALIDATION
# ================================
def validate_config():
    """Validate that required configuration variables are set."""
    errors = []
    
    if not ALPACA_KEY:
        errors.append("ALPACA_API_KEY is not set in .env file")
    
    if not ALPACA_SECRET:
        errors.append("ALPACA_SECRET_KEY is not set in .env file")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
    
    return True

if __name__ == "__main__":
    # Test configuration when run directly
    try:
        validate_config()
        print("\n" + "="*60)
        print("🥝 KIWI AI CONFIGURATION")
        print("="*60)
        
        print("\n✅ Configuration loaded successfully!")
        
        print("\n📊 BROKER SETTINGS:")
        print(f"  Paper Trading Mode: {IS_PAPER_TRADING}")
        print(f"  API Key: {ALPACA_KEY[:8]}..." if ALPACA_KEY else "  API Key: NOT SET")
        
        print("\n💰 TRADING PARAMETERS:")
        print(f"  Initial Capital: ${INITIAL_CAPITAL:,.2f}")
        print(f"  Max Risk Per Trade: {MAX_RISK_PER_TRADE*100:.1f}%")
        print(f"  Max Portfolio Risk: {MAX_PORTFOLIO_RISK*100:.1f}%")
        print(f"  Trading Interval: {TRADING_INTERVAL}s")
        
        print("\n🧠 AI PARAMETERS:")
        print(f"  Min Strategy Confidence: {MIN_STRATEGY_CONFIDENCE}")
        print(f"  Performance Window: {PERFORMANCE_WINDOW} trades")
        print(f"  Regime Lookback: {REGIME_LOOKBACK_DAYS} days")
        
        print("\n🛡️ RISK MANAGEMENT:")
        print(f"  Max Drawdown: {MAX_DRAWDOWN*100:.1f}%")
        print(f"  Max Position Size: {MAX_POSITION_SIZE*100:.1f}%")
        print(f"  Default Stop Loss: {DEFAULT_STOP_LOSS*100:.1f}%")
        print(f"  Default Take Profit: {DEFAULT_TAKE_PROFIT*100:.1f}%")
        
        print("\n📈 DATA SETTINGS:")
        print(f"  Provider: {DATA_PROVIDER}")
        print(f"  Timeframe: {DEFAULT_TIMEFRAME}")
        print(f"  Historical Lookback: {HISTORICAL_LOOKBACK} days")
        
        print("\n🖥️ ENVIRONMENT:")
        print(f"  Environment: {ENVIRONMENT}")
        print(f"  Debug Mode: {DEBUG_MODE}")
        print(f"  Log Level: {LOG_LEVEL}")
        
        print("\n" + "="*60)
        print("🚀 Ready to run Kiwi AI!")
        print("="*60 + "\n")
        
    except ValueError as e:
        print(f"❌ {e}")
