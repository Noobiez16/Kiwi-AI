"""
Risk Manager Module

Manages position sizing and portfolio-level risk.
Implements risk management rules to protect capital.
"""

import os
import sys
from typing import Dict, Tuple, Optional
import pandas as pd

# Add parent directory to path for imports when run as standalone
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import TradingLogger
import config

# Initialize logger
logger = TradingLogger()


class RiskManager:
    """
    Risk management system for position sizing and portfolio risk control.
    
    Key Features:
    - Position sizing based on risk percentage
    - Maximum position limits
    - Portfolio-level risk monitoring
    - Stop-loss validation
    - Concentration limits
    """
    
    def __init__(self, initial_capital: float = None,
                 max_risk_per_trade: float = None,
                 max_position_size: float = None,
                 max_portfolio_risk: float = None):
        """
        Initialize Risk Manager.
        
        Args:
            initial_capital: Starting capital (from config if not specified)
            max_risk_per_trade: Maximum risk per trade as decimal (e.g., 0.02 for 2%)
            max_position_size: Maximum position size as decimal (e.g., 0.10 for 10%)
            max_portfolio_risk: Maximum portfolio risk as decimal (e.g., 0.20 for 20%)
        """
        self.initial_capital = initial_capital or float(config.INITIAL_CAPITAL)
        self.max_risk_per_trade = max_risk_per_trade or float(config.MAX_RISK_PER_TRADE)
        self.max_position_size = max_position_size or 0.10  # 10% max per position
        self.max_portfolio_risk = max_portfolio_risk or 0.20  # 20% max drawdown
        
        logger.logger.info(
            f"Risk Manager initialized | Capital: ${self.initial_capital:,.2f} | "
            f"Max Risk/Trade: {self.max_risk_per_trade*100:.1f}% | "
            f"Max Position: {self.max_position_size*100:.1f}%"
        )
    
    def calculate_position_size(
        self,
        current_price: float,
        stop_loss_price: float,
        account_value: float
    ) -> Tuple[int, Dict]:
        """
        Calculate position size based on risk parameters.
        
        Uses the formula:
        Position Size = (Account Value * Risk %) / (Entry Price - Stop Loss Price)
        
        Args:
            current_price: Current stock price
            stop_loss_price: Stop loss price
            account_value: Current account value
            
        Returns:
            Tuple of (quantity, details_dict)
        """
        # Calculate risk per share
        risk_per_share = abs(current_price - stop_loss_price)
        
        if risk_per_share == 0:
            logger.logger.warning("⚠️  Stop loss price equals entry price, using 1% default")
            risk_per_share = current_price * 0.01
        
        # Calculate dollar risk amount
        dollar_risk = account_value * self.max_risk_per_trade
        
        # Calculate position size based on risk
        risk_based_qty = int(dollar_risk / risk_per_share)
        
        # Calculate maximum position size based on capital limit
        max_capital_for_position = account_value * self.max_position_size
        capital_based_qty = int(max_capital_for_position / current_price)
        
        # Take the minimum to respect both constraints
        final_qty = min(risk_based_qty, capital_based_qty)
        
        # Ensure at least 1 share if we have enough capital
        if final_qty < 1 and account_value >= current_price:
            final_qty = 1
        
        details = {
            'quantity': final_qty,
            'entry_price': current_price,
            'stop_loss': stop_loss_price,
            'risk_per_share': risk_per_share,
            'dollar_risk': final_qty * risk_per_share,
            'position_value': final_qty * current_price,
            'position_pct': (final_qty * current_price) / account_value if account_value > 0 else 0,
            'risk_pct': (final_qty * risk_per_share) / account_value if account_value > 0 else 0
        }
        
        logger.logger.info(
            f"Position sizing | Qty: {final_qty} | Value: ${details['position_value']:,.2f} "
            f"({details['position_pct']*100:.1f}%) | Risk: ${details['dollar_risk']:.2f} "
            f"({details['risk_pct']*100:.1f}%)"
        )
        
        return final_qty, details
    
    def validate_trade(
        self,
        symbol: str,
        quantity: int,
        price: float,
        account_value: float,
        current_positions: Dict = None
    ) -> Tuple[bool, str]:
        """
        Validate if a trade should be allowed.
        
        Args:
            symbol: Stock symbol
            quantity: Number of shares
            price: Price per share
            account_value: Current account value
            current_positions: Dict of current positions
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if current_positions is None:
            current_positions = {}
        
        # Check if we have enough capital
        trade_value = quantity * price
        if trade_value > account_value:
            return False, f"Insufficient capital: ${trade_value:,.2f} > ${account_value:,.2f}"
        
        # Check position size limit
        position_pct = trade_value / account_value
        if position_pct > self.max_position_size:
            return False, f"Position too large: {position_pct*100:.1f}% > {self.max_position_size*100:.1f}%"
        
        # Check if adding to existing position would exceed limits
        if symbol in current_positions:
            existing_value = current_positions[symbol].get('market_value', 0)
            total_value = existing_value + trade_value
            total_pct = total_value / account_value
            
            if total_pct > self.max_position_size:
                return False, f"Combined position too large: {total_pct*100:.1f}% > {self.max_position_size*100:.1f}%"
        
        # Check portfolio concentration
        total_position_value = sum(pos.get('market_value', 0) for pos in current_positions.values())
        total_position_value += trade_value
        portfolio_concentration = total_position_value / account_value
        
        if portfolio_concentration > 0.95:  # Don't use more than 95% of capital
            return False, f"Portfolio too concentrated: {portfolio_concentration*100:.1f}%"
        
        return True, "Trade validated"
    
    def check_portfolio_risk(
        self,
        current_equity: float,
        peak_equity: float = None
    ) -> Tuple[bool, float, str]:
        """
        Check if portfolio drawdown exceeds risk limits.
        
        Args:
            current_equity: Current portfolio equity
            peak_equity: Peak equity (uses initial capital if not specified)
            
        Returns:
            Tuple of (within_limits, drawdown_pct, status_message)
        """
        peak_equity = peak_equity or self.initial_capital
        
        # Calculate drawdown
        drawdown = (peak_equity - current_equity) / peak_equity if peak_equity > 0 else 0
        
        # Check if drawdown exceeds limit
        within_limits = drawdown <= self.max_portfolio_risk
        
        if not within_limits:
            status = f"⚠️  RISK LIMIT EXCEEDED: {drawdown*100:.1f}% drawdown > {self.max_portfolio_risk*100:.1f}%"
        elif drawdown > self.max_portfolio_risk * 0.75:
            status = f"⚠️  Warning: Approaching risk limit ({drawdown*100:.1f}%)"
        else:
            status = f"✅ Portfolio risk within limits ({drawdown*100:.1f}%)"
        
        logger.logger.info(status)
        
        return within_limits, drawdown, status
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        method: str = 'percentage',
        atr: float = None,
        percentage: float = None
    ) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            method: 'percentage', 'atr', or 'fixed'
            atr: Average True Range (for ATR method)
            percentage: Stop loss percentage (for percentage method)
            
        Returns:
            Stop loss price
        """
        if method == 'percentage':
            stop_pct = percentage or 0.02  # Default 2%
            stop_loss = entry_price * (1 - stop_pct)
        elif method == 'atr':
            if atr is None:
                raise ValueError("ATR value required for ATR method")
            stop_loss = entry_price - (2 * atr)  # 2x ATR
        elif method == 'fixed':
            stop_loss = entry_price - (entry_price * 0.02)  # Fixed 2%
        else:
            raise ValueError(f"Unknown stop loss method: {method}")
        
        return max(stop_loss, 0)  # Ensure positive
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_reward_ratio: float = 2.0
    ) -> float:
        """
        Calculate take profit price based on risk-reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_reward_ratio: Target risk-reward ratio
            
        Returns:
            Take profit price
        """
        risk = entry_price - stop_loss_price
        reward = risk * risk_reward_ratio
        take_profit = entry_price + reward
        
        return take_profit
    
    def get_risk_summary(self, account_info: Dict, positions: Dict) -> Dict:
        """
        Get a summary of current risk metrics.
        
        Args:
            account_info: Account information dict
            positions: Current positions dict
            
        Returns:
            Dict with risk summary
        """
        account_value = account_info.get('portfolio_value', self.initial_capital)
        
        # Calculate total position value
        total_position_value = sum(
            pos.get('market_value', 0) for pos in positions.values()
        )
        
        # Calculate portfolio metrics
        portfolio_concentration = total_position_value / account_value if account_value > 0 else 0
        cash_pct = account_info.get('cash', 0) / account_value if account_value > 0 else 0
        
        # Calculate drawdown
        peak_equity = max(account_value, self.initial_capital)
        drawdown = (peak_equity - account_value) / peak_equity if peak_equity > 0 else 0
        
        summary = {
            'account_value': account_value,
            'initial_capital': self.initial_capital,
            'total_return_pct': ((account_value / self.initial_capital) - 1) * 100,
            'drawdown_pct': drawdown * 100,
            'portfolio_concentration': portfolio_concentration * 100,
            'cash_pct': cash_pct * 100,
            'max_risk_per_trade': self.max_risk_per_trade * 100,
            'max_position_size': self.max_position_size * 100,
            'max_portfolio_risk': self.max_portfolio_risk * 100,
            'risk_status': 'OK' if drawdown <= self.max_portfolio_risk else 'EXCEEDED'
        }
        
        return summary


# Standalone test
if __name__ == "__main__":
    print("=" * 80)
    print(" " * 25 + "🛡️ RISK MANAGER TEST")
    print("=" * 80)
    print()
    
    # Initialize risk manager
    risk_mgr = RiskManager(
        initial_capital=100000.0,
        max_risk_per_trade=0.02,  # 2%
        max_position_size=0.10,   # 10%
        max_portfolio_risk=0.20   # 20%
    )
    
    # Test 1: Position Sizing
    print("1. Position Sizing Calculation:")
    print("-" * 80)
    current_price = 450.0
    stop_loss = 440.0  # $10 stop
    account_value = 100000.0
    
    qty, details = risk_mgr.calculate_position_size(current_price, stop_loss, account_value)
    print(f"   Entry Price: ${current_price:.2f}")
    print(f"   Stop Loss: ${stop_loss:.2f}")
    print(f"   Risk per Share: ${details['risk_per_share']:.2f}")
    print(f"   → Position Size: {qty} shares")
    print(f"   → Position Value: ${details['position_value']:,.2f} ({details['position_pct']*100:.1f}%)")
    print(f"   → Dollar Risk: ${details['dollar_risk']:.2f} ({details['risk_pct']*100:.1f}%)")
    
    # Test 2: Trade Validation
    print("\n2. Trade Validation:")
    print("-" * 80)
    
    # Valid trade
    is_valid, reason = risk_mgr.validate_trade('SPY', qty, current_price, account_value)
    print(f"   ✅ Trade valid: {is_valid} | {reason}")
    
    # Invalid trade (too large)
    large_qty = 500
    is_valid, reason = risk_mgr.validate_trade('SPY', large_qty, current_price, account_value)
    print(f"   ❌ Large trade valid: {is_valid} | {reason}")
    
    # Test 3: Portfolio Risk Check
    print("\n3. Portfolio Risk Check:")
    print("-" * 80)
    
    # Small drawdown
    current_equity = 95000.0
    within_limits, drawdown, status = risk_mgr.check_portfolio_risk(current_equity)
    print(f"   Drawdown: {drawdown*100:.1f}% | {status}")
    
    # Large drawdown
    current_equity = 75000.0
    within_limits, drawdown, status = risk_mgr.check_portfolio_risk(current_equity)
    print(f"   Drawdown: {drawdown*100:.1f}% | {status}")
    
    # Test 4: Stop Loss Calculation
    print("\n4. Stop Loss Calculation:")
    print("-" * 80)
    
    entry = 450.0
    stop_pct = risk_mgr.calculate_stop_loss(entry, method='percentage', percentage=0.02)
    stop_atr = risk_mgr.calculate_stop_loss(entry, method='atr', atr=5.0)
    
    print(f"   Entry: ${entry:.2f}")
    print(f"   Stop (2% method): ${stop_pct:.2f}")
    print(f"   Stop (ATR method): ${stop_atr:.2f}")
    
    # Test 5: Take Profit Calculation
    print("\n5. Take Profit Calculation:")
    print("-" * 80)
    
    take_profit = risk_mgr.calculate_take_profit(entry, stop_pct, risk_reward_ratio=2.0)
    print(f"   Entry: ${entry:.2f}")
    print(f"   Stop: ${stop_pct:.2f}")
    print(f"   Take Profit (2:1 R:R): ${take_profit:.2f}")
    print(f"   Risk: ${entry - stop_pct:.2f}")
    print(f"   Reward: ${take_profit - entry:.2f}")
    
    # Test 6: Risk Summary
    print("\n6. Risk Summary:")
    print("-" * 80)
    
    mock_account = {
        'portfolio_value': 98000.0,
        'cash': 50000.0
    }
    mock_positions = {
        'SPY': {'market_value': 30000.0},
        'QQQ': {'market_value': 18000.0}
    }
    
    summary = risk_mgr.get_risk_summary(mock_account, mock_positions)
    print(f"   Account Value: ${summary['account_value']:,.2f}")
    print(f"   Total Return: {summary['total_return_pct']:.2f}%")
    print(f"   Drawdown: {summary['drawdown_pct']:.2f}%")
    print(f"   Portfolio Concentration: {summary['portfolio_concentration']:.1f}%")
    print(f"   Cash: {summary['cash_pct']:.1f}%")
    print(f"   Risk Status: {summary['risk_status']}")
    
    print("\n" + "=" * 80)
    print("✅ Risk Manager Test Complete!")
    print("=" * 80)
