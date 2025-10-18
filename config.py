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
# DATABASE CONFIGURATION (Optional)
# ================================
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "kiwi_ai_data")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

# ================================
# TRADING PARAMETERS
# ================================
MAX_RISK_PER_TRADE = float(os.getenv("MAX_RISK_PER_TRADE", "0.02"))
INITIAL_CAPITAL = float(os.getenv("INITIAL_CAPITAL", "100000"))

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
LOG_FILE = "kiwi_ai.log"

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
        print("✅ Configuration loaded successfully!")
        print(f"📊 Paper Trading Mode: {IS_PAPER_TRADING}")
        print(f"💰 Initial Capital: ${INITIAL_CAPITAL:,.2f}")
        print(f"⚠️  Max Risk Per Trade: {MAX_RISK_PER_TRADE*100:.1f}%")
    except ValueError as e:
        print(f"❌ {e}")
