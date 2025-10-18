"""
Kiwi_AI Monitoring Dashboard

Real-time monitoring interface built with Streamlit.
Displays:
- Active strategy and market regime
- Account value and P&L
- Open positions
- Recent trades
- Performance metrics
- System logs

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# Import Kiwi_AI modules
import config
from execution.broker_interface import Broker
from execution.risk_manager import RiskManager
from meta_ai.regime_detector import RegimeDetector
from meta_ai.performance_monitor import PerformanceMonitor
from data.data_handler import DataHandler

# Page configuration
st.set_page_config(
    page_title="Kiwi_AI Dashboard",
    page_icon="🥝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_resource
def initialize_components():
    """Initialize system components (cached)."""
    broker = Broker(
        api_key=config.ALPACA_KEY,
        secret_key=config.ALPACA_SECRET,
        paper_trading=config.IS_PAPER_TRADING,
        mock_mode=True  # Use mock for demo
    )
    
    risk_mgr = RiskManager(
        initial_capital=float(config.INITIAL_CAPITAL),
        max_risk_per_trade=float(config.MAX_RISK_PER_TRADE)
    )
    
    regime_detector = RegimeDetector()
    perf_monitor = PerformanceMonitor()
    data_handler = DataHandler()
    
    return broker, risk_mgr, regime_detector, perf_monitor, data_handler


def main():
    """Main dashboard function."""
    
    # Title and header
    st.title("🥝 Kiwi_AI Trading Dashboard")
    st.markdown("---")
    
    # Initialize components
    try:
        broker, risk_mgr, regime_detector, perf_monitor, data_handler = initialize_components()
    except Exception as e:
        st.error(f"❌ Failed to initialize components: {e}")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Trading mode
        mode = "📄 Paper Trading" if config.IS_PAPER_TRADING else "🔴 Live Trading"
        st.info(mode)
        
        # Refresh interval
        refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 10)
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        
        # Manual refresh button
        if st.button("🔄 Refresh Now"):
            st.rerun()
        
        st.markdown("---")
        
        # System info
        st.subheader("📊 System Info")
        st.text(f"Initial Capital: ${float(config.INITIAL_CAPITAL):,.0f}")
        st.text(f"Max Risk/Trade: {float(config.MAX_RISK_PER_TRADE)*100:.1f}%")
        st.text(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Main content area
    try:
        # Get account info
        account = broker.get_account_info()
        positions = broker.get_open_positions()
        
        # Top metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="💰 Account Value",
                value=f"${account.get('portfolio_value', 0):,.2f}",
                delta=f"{((account.get('portfolio_value', 0) / float(config.INITIAL_CAPITAL)) - 1) * 100:.2f}%"
            )
        
        with col2:
            st.metric(
                label="💵 Cash",
                value=f"${account.get('cash', 0):,.2f}"
            )
        
        with col3:
            st.metric(
                label="📍 Open Positions",
                value=len(positions)
            )
        
        with col4:
            total_pl = sum(pos.get('unrealized_pl', 0) for pos in positions)
            st.metric(
                label="📈 Unrealized P&L",
                value=f"${total_pl:.2f}",
                delta=f"{(total_pl / account.get('portfolio_value', 1)) * 100:.2f}%"
            )
        
        st.markdown("---")
        
        # Two column layout
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # Market Regime Section
            st.subheader("🧠 Market Intelligence")
            
            try:
                # Fetch recent data
                data = data_handler.fetch_data("SPY", timeframe="1D", period_days=252)
                
                if data is not None and len(data) > 0:
                    # Detect regime
                    regime = regime_detector.predict_regime(data)
                    confidence = regime_detector.get_regime_confidence()
                    
                    # Display regime
                    regime_col1, regime_col2 = st.columns(2)
                    
                    with regime_col1:
                        regime_color = {
                            'TREND': '🟢',
                            'SIDEWAYS': '🟡',
                            'VOLATILE': '🔴'
                        }
                        st.markdown(f"### {regime_color.get(regime, '⚪')} Current Regime: **{regime}**")
                    
                    with regime_col2:
                        st.markdown(f"### 🎯 Confidence: **{confidence.get(regime, 0):.1f}%**")
                    
                    # Confidence breakdown
                    confidence_df = pd.DataFrame({
                        'Regime': list(confidence.keys()),
                        'Confidence (%)': list(confidence.values())
                    })
                    st.bar_chart(confidence_df.set_index('Regime'))
                    
                else:
                    st.warning("⚠️  Unable to fetch market data")
                    
            except Exception as e:
                st.error(f"❌ Regime detection failed: {e}")
            
            # Positions Table
            st.subheader("📍 Open Positions")
            
            if len(positions) > 0:
                positions_df = pd.DataFrame([{
                    'Symbol': pos['symbol'],
                    'Quantity': pos['qty'],
                    'Avg Entry': f"${pos['avg_entry_price']:.2f}",
                    'Current': f"${pos['current_price']:.2f}",
                    'Value': f"${pos['market_value']:.2f}",
                    'P&L': f"${pos['unrealized_pl']:.2f}",
                    'P&L %': f"{pos.get('unrealized_plpc', 0)*100:.2f}%"
                } for pos in positions])
                
                st.dataframe(positions_df, use_container_width=True)
            else:
                st.info("No open positions")
        
        with right_col:
            # Strategy Info
            st.subheader("🎯 Active Strategy")
            
            # This would come from the running system
            # For demo, we'll show static info
            st.info("**Strategy:** Trend Following")
            st.success("**Status:** ✅ Running")
            
            # Performance Monitor
            st.subheader("📊 Performance Metrics")
            
            # Get performance stats
            perf_status = perf_monitor.check_performance_degradation()
            
            metrics_data = {
                'Metric': ['Sharpe Ratio', 'Max Drawdown', 'Win Rate', 'Total Trades'],
                'Value': [
                    f"{perf_monitor.calculate_sharpe_ratio():.2f}",
                    f"{perf_monitor.calculate_max_drawdown():.2f}%",
                    f"{perf_monitor.calculate_win_rate():.1f}%",
                    str(perf_monitor.total_trades)
                ]
            }
            
            metrics_df = pd.DataFrame(metrics_data)
            st.table(metrics_df)
            
            # Performance status
            status_color = {
                'EXCELLENT': '🟢',
                'GOOD': '🟡',
                'DEGRADING': '🟠',
                'POOR': '🔴'
            }
            st.markdown(f"### Status: {status_color.get(perf_status, '⚪')} {perf_status}")
            
            # Risk Summary
            st.subheader("🛡️ Risk Management")
            
            risk_summary = risk_mgr.get_risk_summary(
                account,
                {pos['symbol']: pos for pos in positions}
            )
            
            risk_data = {
                'Metric': ['Drawdown', 'Portfolio Concentration', 'Cash Position', 'Risk Status'],
                'Value': [
                    f"{risk_summary['drawdown_pct']:.2f}%",
                    f"{risk_summary['portfolio_concentration']:.1f}%",
                    f"{risk_summary['cash_pct']:.1f}%",
                    risk_summary['risk_status']
                ]
            }
            
            risk_df = pd.DataFrame(risk_data)
            st.table(risk_df)
        
        st.markdown("---")
        
        # Bottom section - Recent Activity
        st.subheader("📋 Recent Activity")
        
        # This would come from logs in a real system
        activity_data = {
            'Time': [
                datetime.now() - timedelta(minutes=30),
                datetime.now() - timedelta(minutes=45),
                datetime.now() - timedelta(hours=1)
            ],
            'Event': [
                'Strategy switched to Trend Following',
                'Regime changed to TREND',
                'Position opened: SPY'
            ],
            'Details': [
                'Performance degradation detected',
                'Confidence: 85%',
                '10 shares @ $450.00'
            ]
        }
        
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Dashboard error: {e}")
        st.exception(e)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()


if __name__ == "__main__":
    main()
