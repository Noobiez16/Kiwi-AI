"""
Execution Module - Broker Interface and Risk Management

This module handles:
- Broker API communication (Alpaca, IBKR, etc.)
- Order placement and management
- Position tracking
- Risk management and position sizing
"""

from .broker_interface import Broker
from .risk_manager import RiskManager

__all__ = ['Broker', 'RiskManager']
