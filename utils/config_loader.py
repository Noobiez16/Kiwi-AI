"""
Configuration Loader Module
Provides utilities for loading and validating configuration.
"""

import os
from typing import Dict, Any
import config


def load_config() -> Dict[str, Any]:
    """
    Load all configuration settings into a dictionary.
    
    Returns:
        Dictionary containing all configuration settings
    """
    config_dict = {
        # Broker settings
        'alpaca_key': config.ALPACA_KEY,
        'alpaca_secret': config.ALPACA_SECRET,
        'is_paper_trading': config.IS_PAPER_TRADING,
        
        # Database settings
        'db_host': config.DB_HOST,
        'db_name': config.DB_NAME,
        'db_user': config.DB_USER,
        'db_pass': config.DB_PASS,
        
        # Trading parameters
        'max_risk_per_trade': config.MAX_RISK_PER_TRADE,
        'initial_capital': config.INITIAL_CAPITAL,
        
        # Directory settings
        'data_directory': config.DATA_DIRECTORY,
        'backtest_reports_dir': config.BACKTEST_REPORTS_DIR,
        'models_directory': config.MODELS_DIRECTORY,
        
        # Model settings
        'regime_model_path': config.REGIME_MODEL_PATH,
        
        # Logging settings
        'log_level': config.LOG_LEVEL,
        'log_file': config.LOG_FILE,
    }
    
    return config_dict


def validate_config() -> bool:
    """
    Validate that all required configuration is properly set.
    
    Returns:
        True if configuration is valid
    
    Raises:
        ValueError: If configuration is invalid
    """
    return config.validate_config()


def get_config_value(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key: Configuration key
        default: Default value if key not found
    
    Returns:
        Configuration value or default
    """
    config_dict = load_config()
    return config_dict.get(key, default)


def print_config_summary():
    """
    Print a summary of the current configuration.
    Useful for debugging and verification.
    """
    print("=" * 70)
    print("🥝 KIWI_AI CONFIGURATION SUMMARY")
    print("=" * 70)
    
    print("\n📊 BROKER SETTINGS:")
    print(f"  • Paper Trading: {'YES' if config.IS_PAPER_TRADING else 'NO'}")
    print(f"  • API Key Set: {'YES' if config.ALPACA_KEY else 'NO'}")
    print(f"  • API Secret Set: {'YES' if config.ALPACA_SECRET else 'NO'}")
    
    print("\n💰 TRADING PARAMETERS:")
    print(f"  • Initial Capital: ${config.INITIAL_CAPITAL:,.2f}")
    print(f"  • Max Risk Per Trade: {config.MAX_RISK_PER_TRADE*100:.1f}%")
    
    print("\n📁 DIRECTORIES:")
    print(f"  • Data Directory: {config.DATA_DIRECTORY}")
    print(f"  • Reports Directory: {config.BACKTEST_REPORTS_DIR}")
    print(f"  • Models Directory: {config.MODELS_DIRECTORY}")
    
    print("\n🔧 SYSTEM SETTINGS:")
    print(f"  • Log Level: {config.LOG_LEVEL}")
    print(f"  • Log File: {config.LOG_FILE}")
    
    print("\n" + "=" * 70)
    
    # Check if required directories exist
    print("\n📂 DIRECTORY STATUS:")
    dirs_to_check = [
        config.DATA_DIRECTORY,
        config.BACKTEST_REPORTS_DIR,
        config.MODELS_DIRECTORY
    ]
    
    for dir_path in dirs_to_check:
        exists = os.path.exists(dir_path)
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  • {dir_path}: {status}")
    
    print("\n" + "=" * 70)


def create_directories():
    """
    Create all required directories for the application.
    """
    directories = [
        config.DATA_DIRECTORY,
        config.BACKTEST_REPORTS_DIR,
        config.MODELS_DIRECTORY,
    ]
    
    print("📁 Creating required directories...")
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")
    
    print("\n✅ All directories created successfully!")


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("🥝 Configuration Loader Test")
    print("=" * 70)
    
    # Create directories
    create_directories()
    
    # Print configuration summary
    print_config_summary()
    
    # Test validation
    try:
        validate_config()
        print("\n✅ Configuration validation PASSED!")
    except ValueError as e:
        print(f"\n❌ Configuration validation FAILED!")
        print(f"   Error: {e}")
    
    # Test loading config
    config_dict = load_config()
    print(f"\n📊 Loaded {len(config_dict)} configuration items")
    
    print("\n✅ Config Loader test completed!")
