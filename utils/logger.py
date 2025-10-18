"""
Logging Configuration Module
Provides centralized logging setup for the Kiwi_AI system.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import config


def setup_logger(
    name: str = "kiwi_ai",
    level: str = None,
    log_file: str = None,
    console_output: bool = True
) -> logging.Logger:
    """
    Set up a configured logger for the application.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, uses config.LOG_FILE)
        console_output: Whether to output logs to console
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set level
    level = level or config.LOG_LEVEL
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        fmt='%(levelname)-8s | %(message)s'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    log_file = log_file or config.LOG_FILE
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "kiwi_ai") -> logging.Logger:
    """
    Get an existing logger or create a new one.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger hasn't been set up, set it up now
    if not logger.handlers:
        return setup_logger(name)
    
    return logger


class TradingLogger:
    """
    Specialized logger for trading operations with additional context.
    """
    
    def __init__(self, name: str = "kiwi_ai.trading"):
        self.logger = get_logger(name)
        self.trade_count = 0
    
    def log_trade(
        self,
        action: str,
        symbol: str,
        quantity: int,
        price: float,
        strategy: str = None,
        regime: str = None
    ):
        """
        Log a trade execution.
        
        Args:
            action: Trade action (BUY, SELL, CLOSE)
            symbol: Stock symbol
            quantity: Number of shares
            price: Execution price
            strategy: Strategy name (optional)
            regime: Market regime (optional)
        """
        self.trade_count += 1
        
        msg = f"TRADE #{self.trade_count} | {action} {quantity} {symbol} @ ${price:.2f}"
        
        if strategy:
            msg += f" | Strategy: {strategy}"
        
        if regime:
            msg += f" | Regime: {regime}"
        
        self.logger.info(msg)
    
    def log_signal(self, strategy: str, signal: int, confidence: float = None):
        """
        Log a trading signal generation.
        
        Args:
            strategy: Strategy name
            signal: Signal value (1, -1, 0)
            confidence: Signal confidence (0-1)
        """
        signal_type = {1: "BUY", -1: "SELL", 0: "HOLD"}.get(signal, "UNKNOWN")
        
        msg = f"SIGNAL | {strategy}: {signal_type}"
        
        if confidence is not None:
            msg += f" (Confidence: {confidence:.2%})"
        
        self.logger.info(msg)
    
    def log_performance(self, metrics: dict):
        """
        Log performance metrics.
        
        Args:
            metrics: Dictionary of performance metrics
        """
        self.logger.info("=" * 60)
        self.logger.info("PERFORMANCE METRICS")
        self.logger.info("=" * 60)
        
        for key, value in metrics.items():
            if isinstance(value, float):
                self.logger.info(f"{key}: {value:.4f}")
            else:
                self.logger.info(f"{key}: {value}")
    
    def log_regime_change(self, old_regime: str, new_regime: str):
        """
        Log a market regime change.
        
        Args:
            old_regime: Previous market regime
            new_regime: New market regime
        """
        self.logger.warning(
            f"REGIME CHANGE | {old_regime} → {new_regime}"
        )
    
    def log_strategy_switch(self, old_strategy: str, new_strategy: str, reason: str = None):
        """
        Log a strategy switch.
        
        Args:
            old_strategy: Previous strategy
            new_strategy: New strategy
            reason: Reason for switch (optional)
        """
        msg = f"STRATEGY SWITCH | {old_strategy} → {new_strategy}"
        
        if reason:
            msg += f" | Reason: {reason}"
        
        self.logger.warning(msg)
    
    def log_error(self, error: Exception, context: str = None):
        """
        Log an error with context.
        
        Args:
            error: Exception object
            context: Additional context about the error
        """
        msg = f"ERROR | {type(error).__name__}: {str(error)}"
        
        if context:
            msg = f"{context} | {msg}"
        
        self.logger.error(msg, exc_info=True)


# Example usage
if __name__ == "__main__":
    print("=" * 60)
    print("🥝 Kiwi_AI Logger Test")
    print("=" * 60)
    
    # Test basic logger
    logger = setup_logger("test_logger")
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("\n" + "=" * 60)
    print("Testing TradingLogger")
    print("=" * 60)
    
    # Test trading logger
    trade_logger = TradingLogger("test_trading")
    
    trade_logger.log_signal("Trend Following", 1, 0.85)
    trade_logger.log_trade("BUY", "SPY", 100, 450.50, "Trend Following", "TREND")
    trade_logger.log_regime_change("SIDEWAYS", "TREND")
    trade_logger.log_strategy_switch("Mean Reversion", "Trend Following", "Regime changed")
    
    metrics = {
        'total_return': 15.5,
        'sharpe_ratio': 1.8,
        'max_drawdown': -8.2,
        'num_trades': 45
    }
    trade_logger.log_performance(metrics)
    
    print("\n✅ Logger test completed!")
    print(f"📝 Logs written to: {config.LOG_FILE}")
