"""
Broker Interface Module

Abstracts communication with broker APIs (Alpaca, Interactive Brokers, etc.)
Allows switching brokers by modifying only this file.
"""

import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Add parent directory to path for imports when run as standalone
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger import TradingLogger

# Initialize logger
logger = TradingLogger()


class Broker:
    """
    Abstract broker interface for executing trades and managing positions.
    
    Currently supports:
    - Alpaca API (Paper & Live Trading)
    - Mock mode for testing
    
    Easily extensible for other brokers (IBKR, TD Ameritrade, etc.)
    """
    
    def __init__(self, api_key: str = None, secret_key: str = None, 
                 paper_trading: bool = True, mock_mode: bool = False):
        """
        Initialize broker connection.
        
        Args:
            api_key: Broker API key (from config)
            secret_key: Broker secret key (from config)
            paper_trading: Use paper trading environment
            mock_mode: If True, simulate broker without real API calls
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.paper_trading = paper_trading
        self.mock_mode = mock_mode
        
        # Mock data for testing
        self.mock_positions = {}
        self.mock_orders = []
        self.mock_cash = 100000.0
        self.mock_portfolio_value = 100000.0
        
        # Try to initialize Alpaca client
        self.client = None
        if not mock_mode:
            self.client = self._initialize_alpaca()
        
        logger.logger.info(f"Broker initialized | Mode: {'MOCK' if mock_mode else 'ALPACA'} | "
                          f"Paper: {paper_trading}")
    
    def _initialize_alpaca(self):
        """Initialize Alpaca API client."""
        try:
            from alpaca.trading.client import TradingClient
            from alpaca.trading.enums import OrderSide, TimeInForce
            
            # Store enums for later use
            self.OrderSide = OrderSide
            self.TimeInForce = TimeInForce
            
            base_url = 'https://paper-api.alpaca.markets' if self.paper_trading else 'https://api.alpaca.markets'
            
            client = TradingClient(
                api_key=self.api_key,
                secret_key=self.secret_key,
                paper=self.paper_trading
            )
            
            # Test connection
            account = client.get_account()
            logger.logger.info(f"✅ Connected to Alpaca | Account: {account.account_number} | "
                              f"Buying Power: ${float(account.buying_power):.2f}")
            
            return client
            
        except ImportError:
            logger.logger.warning("⚠️  Alpaca SDK not available, using mock mode")
            self.mock_mode = True
            return None
        except Exception as e:
            logger.logger.error(f"❌ Failed to connect to Alpaca: {e}")
            logger.logger.warning("⚠️  Falling back to mock mode")
            self.mock_mode = True
            return None
    
    def place_order(self, symbol: str, qty: int, side: str, 
                   order_type: str = "market", limit_price: float = None) -> Dict:
        """
        Place an order with the broker.
        
        Args:
            symbol: Stock symbol (e.g., 'SPY')
            qty: Number of shares
            side: 'buy' or 'sell'
            order_type: 'market' or 'limit'
            limit_price: Limit price for limit orders
            
        Returns:
            Dict with order details
        """
        if self.mock_mode:
            return self._mock_place_order(symbol, qty, side, order_type, limit_price)
        
        try:
            from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
            
            # Determine order side
            order_side = self.OrderSide.BUY if side.lower() == 'buy' else self.OrderSide.SELL
            
            # Create order request
            if order_type.lower() == 'market':
                order_data = MarketOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=self.TimeInForce.DAY
                )
            else:  # limit order
                order_data = LimitOrderRequest(
                    symbol=symbol,
                    qty=qty,
                    side=order_side,
                    time_in_force=self.TimeInForce.DAY,
                    limit_price=limit_price
                )
            
            # Submit order
            order = self.client.submit_order(order_data)
            
            result = {
                'order_id': order.id,
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'type': order_type,
                'status': order.status,
                'created_at': order.created_at
            }
            
            logger.log_trade(
                action=side.upper(),
                symbol=symbol,
                quantity=qty,
                price=limit_price if limit_price else 0.0,
                strategy=f"{order_type.upper()} order"
            )
            
            return result
            
        except Exception as e:
            logger.logger.error(f"❌ Order placement failed: {e}")
            return {'error': str(e), 'success': False}
    
    def _mock_place_order(self, symbol: str, qty: int, side: str, 
                         order_type: str, limit_price: float) -> Dict:
        """Mock order placement for testing."""
        order_id = f"MOCK-{len(self.mock_orders) + 1}"
        price = limit_price if limit_price else 100.0  # Mock price
        
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'qty': qty,
            'side': side,
            'type': order_type,
            'status': 'filled',
            'created_at': datetime.now(),
            'filled_price': price
        }
        
        self.mock_orders.append(order)
        
        # Update mock positions
        if side.lower() == 'buy':
            if symbol in self.mock_positions:
                self.mock_positions[symbol]['qty'] += qty
            else:
                self.mock_positions[symbol] = {'qty': qty, 'avg_price': price}
            self.mock_cash -= qty * price
        else:  # sell
            if symbol in self.mock_positions:
                self.mock_positions[symbol]['qty'] -= qty
                if self.mock_positions[symbol]['qty'] <= 0:
                    del self.mock_positions[symbol]
            self.mock_cash += qty * price
        
        logger.log_trade(
            action=side.upper(),
            symbol=symbol,
            quantity=qty,
            price=price,
            strategy=f"MOCK {order_type.upper()}"
        )
        
        return order
    
    def get_open_positions(self) -> List[Dict]:
        """
        Get all open positions.
        
        Returns:
            List of position dictionaries
        """
        if self.mock_mode:
            return [
                {
                    'symbol': symbol,
                    'qty': data['qty'],
                    'avg_entry_price': data['avg_price'],
                    'current_price': data['avg_price'] * 1.01,  # Mock 1% gain
                    'market_value': data['qty'] * data['avg_price'] * 1.01,
                    'unrealized_pl': data['qty'] * data['avg_price'] * 0.01
                }
                for symbol, data in self.mock_positions.items()
            ]
        
        try:
            positions = self.client.get_all_positions()
            
            return [
                {
                    'symbol': pos.symbol,
                    'qty': int(pos.qty),
                    'avg_entry_price': float(pos.avg_entry_price),
                    'current_price': float(pos.current_price),
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc)
                }
                for pos in positions
            ]
            
        except Exception as e:
            logger.logger.error(f"❌ Failed to get positions: {e}")
            return []
    
    def close_position(self, symbol: str) -> Dict:
        """
        Close a specific position.
        
        Args:
            symbol: Stock symbol to close
            
        Returns:
            Dict with close order details
        """
        if self.mock_mode:
            if symbol in self.mock_positions:
                qty = self.mock_positions[symbol]['qty']
                return self._mock_place_order(symbol, qty, 'sell', 'market', None)
            return {'error': 'Position not found', 'success': False}
        
        try:
            close_order = self.client.close_position(symbol)
            
            logger.log_trade(
                action='CLOSE',
                symbol=symbol,
                quantity=0,
                price=0.0,
                strategy="Position closed"
            )
            
            return {
                'success': True,
                'symbol': symbol,
                'status': 'closed'
            }
            
        except Exception as e:
            logger.logger.error(f"❌ Failed to close position {symbol}: {e}")
            return {'error': str(e), 'success': False}
    
    def close_all_positions(self) -> Dict:
        """
        Close all open positions.
        
        Returns:
            Dict with results
        """
        if self.mock_mode:
            results = []
            for symbol in list(self.mock_positions.keys()):
                results.append(self.close_position(symbol))
            return {'success': True, 'closed': len(results)}
        
        try:
            close_orders = self.client.close_all_positions(cancel_orders=True)
            
            logger.logger.info(f"🔒 All positions closed | Count: {len(close_orders)}")
            
            return {
                'success': True,
                'closed': len(close_orders)
            }
            
        except Exception as e:
            logger.logger.error(f"❌ Failed to close all positions: {e}")
            return {'error': str(e), 'success': False}
    
    def get_account_info(self) -> Dict:
        """
        Get account information.
        
        Returns:
            Dict with account details
        """
        if self.mock_mode:
            return {
                'cash': self.mock_cash,
                'portfolio_value': self.mock_portfolio_value,
                'buying_power': self.mock_cash,
                'equity': self.mock_portfolio_value,
                'status': 'ACTIVE'
            }
        
        try:
            account = self.client.get_account()
            
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'status': account.status,
                'pattern_day_trader': account.pattern_day_trader,
                'daytrade_count': account.daytrade_count
            }
            
        except Exception as e:
            logger.logger.error(f"❌ Failed to get account info: {e}")
            return {'error': str(e)}
    
    def get_order_status(self, order_id: str) -> Dict:
        """
        Get status of a specific order.
        
        Args:
            order_id: Order ID to check
            
        Returns:
            Dict with order status
        """
        if self.mock_mode:
            for order in self.mock_orders:
                if order['order_id'] == order_id:
                    return order
            return {'error': 'Order not found'}
        
        try:
            order = self.client.get_order_by_id(order_id)
            
            return {
                'order_id': order.id,
                'symbol': order.symbol,
                'qty': int(order.qty),
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'filled_qty': int(order.filled_qty) if order.filled_qty else 0,
                'filled_avg_price': float(order.filled_avg_price) if order.filled_avg_price else None
            }
            
        except Exception as e:
            logger.logger.error(f"❌ Failed to get order status: {e}")
            return {'error': str(e)}


# Standalone test
if __name__ == "__main__":
    print("=" * 80)
    print(" " * 25 + "🏦 BROKER INTERFACE TEST")
    print("=" * 80)
    print()
    
    # Test with mock mode
    print("📊 Testing Mock Mode...")
    print("-" * 80)
    
    broker = Broker(mock_mode=True)
    
    # Test account info
    print("\n1. Account Information:")
    account = broker.get_account_info()
    print(f"   Cash: ${account['cash']:,.2f}")
    print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
    print(f"   Status: {account['status']}")
    
    # Test order placement
    print("\n2. Placing Orders:")
    buy_order = broker.place_order('SPY', 10, 'buy', 'market')
    print(f"   ✅ Buy Order: {buy_order['order_id']} | {buy_order['qty']} shares | Status: {buy_order['status']}")
    
    # Test positions
    print("\n3. Open Positions:")
    positions = broker.get_open_positions()
    for pos in positions:
        print(f"   📍 {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
        print(f"      Current: ${pos['current_price']:.2f} | P&L: ${pos['unrealized_pl']:.2f}")
    
    # Test close position
    print("\n4. Closing Position:")
    close_result = broker.close_position('SPY')
    if close_result.get('success', True):
        print(f"   ✅ Position closed: SPY")
    
    # Final account status
    print("\n5. Final Account Status:")
    final_account = broker.get_account_info()
    print(f"   Cash: ${final_account['cash']:,.2f}")
    print(f"   Portfolio Value: ${final_account['portfolio_value']:,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ Broker Interface Test Complete!")
    print("=" * 80)
