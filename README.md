# 🥝 Kiwi AI - Advanced Adaptive Algorithmic Trading System

An intelligent meta-strategy trading system that uses artificial intelligence to dynamically select the most suitable trading strategy based on current market conditions.

## 🎯 Project Overview

Kiwi AI is designed to overcome the limitations of static trading models by:
- **Detecting market regimes** (trending, sideways, volatile)
- **Dynamically selecting strategies** from a diverse arsenal
- **Monitoring performance** in real-time
- **Adapting to changing conditions** automatically
- **Real-time data streaming** via WebSocket
- **TradingView professional charts** with live market data 🆕
- **Multi-asset support** (Stocks, Forex, Crypto, Indices, Commodities) 🆕
- **Auto-start system** for instant trading 🆕

## 🚀 Quick Start

### ONE File - ONE Command ⭐ NEW!

Everything is now consolidated into **`run_kiwi.py`** - a visual, user-friendly application!

```bash
# Linux/Mac: Use the startup script (Recommended)
./run.sh

# Or manually:
source venv/bin/activate
streamlit run run_kiwi.py
```

**That's it!** The web dashboard opens at http://localhost:8501

### 🛑 Stopping the Application

```bash
# Press Ctrl+C in the terminal, then close all browser tabs
```

**⚠️ Important:** Always use Ctrl+C to properly close WebSocket connections before restarting!

### ✨ No Coding Required!

The app includes a **visual settings manager** - configure everything through the web interface:

1. **Settings Tab** - Configure API keys, select assets from 5 categories, adjust parameters
2. **Dashboard Tab** - Auto-starts trading, shows TradingView charts, monitor live performance
3. **Control Tab** - View system status and asset information
4. **Error Log Tab** - Track and troubleshoot any issues
5. **Help Tab** - Complete documentation built-in

**Perfect for non-coders!** All configuration is visual - no terminal commands or .env file editing needed.

### 📊 Features (v2.0)

- **Auto-Start System** - Trading begins automatically when opening dashboard 🆕
- **TradingView Charts** - Professional real-time charts with technical indicators 🆕
- **Multi-Asset Trading** - 27 assets across Stocks, Forex, Crypto, Indices, Commodities 🆕
- **Real-Time Mode** - Live WebSocket streaming (auto-enabled)
- **Visual Settings** - Configure everything in the browser
- **Live Dashboard** - Real-time monitoring and metrics with professional charts
- **Risk Management** - Built-in safety features
- **Paper Trading** - Test with fake money first (default enabled)

## 🏁 Current Status: v2.5.3 Complete ✅

**Latest Update:** November 10, 2025 - Status Section Enhancement!

📄 **[View All Phases Completion Report](ALL_PHASES_COMPLETED.md)** | 📝 **[View Full Changelog](CHANGELOG.md)** | 🚀 **[Deployment Guide](DEPLOYMENT.md)**

### ✨ v2.5.3 Features - Status Section Enhancement 🆕

#### 🔄 Unified Status Container with Auto-Rotation
- **Single Professional Container** - All status information combined into one cohesive card
- **7-Second Auto-Rotation** - Automatically cycles through 4 status sections:
  - System Status: Inactive
  - Trading System Inactive (with description)
  - HOW TO START (3-step guide)
  - SAFETY FEATURES (3 key features)
- **Smooth Fade Transitions** - 0.5s opacity transitions between sections
- **Matching Visual Design** - AI Intelligence table now uses same gradient styling
- **Proper Spacing** - 40px spacing between components for clear visual hierarchy

### ✨ v2.5.2 Features - Complete Visual Cleanup

#### ✨ Minimalist Apple-Style Design
- **Zero Separator Lines** - Removed all 32 horizontal dividers across entire application
- **Natural Flow** - Content sections separated by spacing and typography
- **Cleaner Interface** - No visual clutter from divider lines
- **Modern Aesthetic** - Professional minimalist design throughout
- **Better Focus** - Less visual distraction, improved content emphasis
- **CSS Spacing** - Natural gaps maintained with proper margins

**Cleanup Coverage:**
- Dashboard Page: 8 separators removed
- Settings Page: 5 separators removed
- Error Log Page: 7 separators removed
- Help Page: 9 separators removed
- Control Page: 2 separators removed
- Sidebar: 1 separator removed

### ✨ v2.5.1 Features - Animated Status Switcher

#### 🎬 Clean Animated Status Display
- **Dynamic State Management** - Shows different content based on trading state
- **Before Trading**: Static initialization view with progress checklist
- **After Trading Starts**: Animated status switcher activates automatically
- **10-Second Auto-Switch** - Automatically cycles through 6 status items every 10 seconds
- **Single Focus Display** - Shows one status at a time for better clarity
- **Uniform Blue Theme** - Clean, professional single-color design
- **Smooth Animations** - Fade-in effect with slide transition (0.5s)
- **Progress Indicators** - 6 dots showing current position in 60-second cycle
- **6 Status Items** - Scanning Status, Monitoring, Market Regime, Active Strategy, Looking For, Alert Status
- **Seamless Transition** - Automatically switches from initialization to scanning view when ready

### ✨ v2.5.0 Features - AI 5-Minute Market Analysis

#### 🧠 Real-Time AI Analysis Every 5 Minutes
- **Price Movement Tracking** - Monitors price changes over last 5 minutes
- **Trend Detection** - Identifies upward (📈), downward (📉), or sideways (➡️) movements
- **Volume Analysis** - Tracks if volume is increasing or decreasing
- **Intelligent Signal Assessment** - 5 signal types (Bullish, Bearish, Caution, Opportunity, Neutral)

#### 🎯 Smart Buy/Sell Recommendations
- **Bullish Signals** - "This could be a good opportunity to BUY"
- **Bearish Warnings** - "NOT a good time to BUY - wait for stabilization"
- **Caution Alerts** - "Wait for better setup - reversals likely"
- **Mean Reversion Opportunities** - "Monitor for bounce signals"
- **Neutral Guidance** - "No clear signal yet - waiting for decisive action"

#### 📊 Detailed AI Reasoning
- Explains why signal was generated
- Shows how it aligns with current market regime
- Validates strategy compatibility
- Includes volume confirmation details
- Highlights risk factors to consider

### ✨ v2.4.0 Features - Interactive AI Intelligence Table

#### 📊 Interactive Table with Professional Design
- **Clickable Column Headers** - Asset, Market Regime, Strategy, Status
- **Detailed Information Views** - Click any header to see comprehensive details
- **Professional Card Layouts** - Glass morphism design with color coding
- **Smart Toggling** - Auto-closes other views, stays within table
- **Educational Context** - Learn about each component on-demand

#### 🎨 Professional Card-Based Views
- **Asset Details** - Category, market performance, AI analysis status
- **Market Regime Analysis** - Current regime, characteristics, risk assessment
- **Strategy Deep Dive** - How it works, entry/exit conditions, why AI selected it
- **Status Information** - 4 dynamic states (Stopped, Initializing, Active, Scanning) + AI 5-Min Analysis

#### ⚡ Enhanced User Experience
- **Animated Status Indicators** - Pulse (Initializing), Scan (Searching)
- **Color-Coded Sections** - Blue (Asset), Purple (Regime), Orange (Strategy)
- **Responsive Layouts** - Multi-column cards with proper spacing
- **Glass Morphism Effects** - Semi-transparent cards with backdrop blur

### ✨ v2.3.0 Features - AI Learning & Risk Management

#### 🧠 Intelligent User Interaction
- **AI Learning Loop** - AI learns from your trading decisions
- **User Action Confirmation** - "I Bought" / "I Skipped" buttons
- **Adaptive Confidence** - Suppresses similar signals when you skip (15-min cooldown)
- **Smart Context Awareness** - Only suppresses same strategy + regime combination
- **Clear Feedback** - Shows why signals are suppressed

#### 🛡️ Advanced Risk Assessment
- **Entry Risk Score (0-100)** - Multi-factor risk analysis for every BUY signal
- **Risk Levels** - LOW 🟢 / MEDIUM 🟡 / HIGH 🟠 / CRITICAL 🔴
- **Critical Risk Warnings** - Prominent alerts when risk exceeds 75/100
- **Risk Factor Breakdown:**
  - Stop Loss Distance (40% weight)
  - ATR-Adjusted Volatility (30% weight)
  - Market Volatility Context (30% weight)

#### 💰 Dynamic Position Sizing
- **Risk-Based Recommendations** - Automatic position reduction based on risk
- **Smart Scaling:**
  - LOW Risk: 100% position
  - MEDIUM Risk: 75% position (25% reduction)
  - HIGH Risk: 50% position (50% reduction)
  - CRITICAL Risk: 25% position (75% reduction)
- **Visual Display** - Clear position sizing guidance in recommendations

### ✨ v2.0 Features - TradingView & Multi-Asset 🆕

#### � TradingView Integration
- **Professional Charts** - Embedded real-time TradingView widgets
- **Live Market Data** - Real-time price updates and candlestick patterns
- **Technical Indicators** - Built-in SMA, EMA, RSI analysis
- **Interactive Interface** - Zoom, pan, and symbol search
- **Dark Theme** - Matching application design
- **Multiple Timeframes** - 1Min to Daily bars

#### 🌍 Multi-Asset Support (27 Assets)
- **Stocks** - NVDA, AAPL, TSLA, MSFT, AMZN, GOOGL, META, NFLX
- **Indices** - NASDAQ-100, S&P 500, Dow Jones, Russell 2000
- **Forex** - EUR/USD, GBP/USD, USD/JPY, AUD/USD, USD/CAD, USD/CHF
- **Crypto** - BTC, ETH, SOL, ADA, XRP (all vs USDT)
- **Commodities** - Gold, Silver, Crude Oil, Natural Gas

#### ⚡ Auto-Start System
- **Instant Activation** - No manual start button needed
- **Configuration Check** - Validates setup before starting
- **Real-Time Only** - Streamlined single mode operation
- **Background Thread** - Non-blocking startup
- **Continuous Monitoring** - 24/7 market analysis

#### � Enhanced Dashboard
- **TradingView Charts** - Professional real-time visualization at top
- **Asset Information** - Category, symbol, and status display
- **AI Recommendations** - One-click trade execution
- **Account Overview** - Real-time portfolio value and P&L
- **Position Tracking** - Open positions with live P&L
- **Performance Metrics** - Sharpe ratio, drawdown, win rate
- **Market Intelligence** - Live regime detection and strategy display
- **Auto-Refresh** - Updates every 5 seconds when active

### ✅ Completed Components

#### Phase 1: Foundation & Strategy Arsenal ✅

1. **Project Structure**
   - Full folder hierarchy established
   - Security configuration (.gitignore, .env)
   - Dependency management (requirements.txt)

2. **Configuration Module** (`config.py`)
   - Environment variable management
   - API key handling
   - Trading parameters
   - Validation system

3. **Data Module** (`/data/`)
   - `DataHandler`: Fetch and cache market data
   - Support for multiple data sources (Alpaca API)
   - Technical indicator calculation
   - Mock data generation for testing

4. **Strategies Module** (`/strategies/`)
   - `BaseStrategy`: Abstract base class for all strategies
   - `TrendFollowingStrategy`: Moving average crossover
   - `MeanReversionStrategy`: RSI + Bollinger Bands
   - `VolatilityBreakoutStrategy`: ATR + Donchian Channels

5. **Utils Module** (`/utils/`)
   - Centralized logging system
   - Configuration loader
   - Directory management

#### Phase 2: AI Brain & Intelligence ✅

6. **Regime Detection** (`/meta_ai/regime_detector.py`)
   - Market regime classification (TREND, SIDEWAYS, VOLATILE)
   - HMM-based detection with rule-based fallback
   - Confidence scoring for each regime
   - Model save/load capability

7. **Performance Monitoring** (`/meta_ai/performance_monitor.py`)
   - Real-time performance tracking
   - Sharpe ratio calculation
   - Maximum drawdown monitoring
   - Win rate and profit factor metrics
   - Performance degradation alerts

8. **Strategy Selection** (`/meta_ai/strategy_selector.py`)
   - Intelligent strategy selection based on market regime
   - Regime-strategy suitability matrix
   - Automatic strategy switching
   - Performance-triggered adaptation
   - Confidence-based decision making

9. **Model Training** (`train_models.py`)
   - Historical data training for regime detection
   - Command-line interface with configurable parameters
   - Model validation and persistence
   - Quick test mode for rapid iteration

#### Phase 3: Execution & Live Trading ✅

10. **Broker Interface** (`/execution/broker_interface.py`)
    - Abstract broker API communication (Alpaca, IBKR-ready)
    - Order placement (market, limit orders)
    - Position tracking and management
    - Account information retrieval
    - Mock mode for safe testing

11. **Risk Manager** (`/execution/risk_manager.py`)
    - Position sizing based on risk percentage
    - Trade validation with portfolio constraints
    - Stop loss and take profit calculation
    - Portfolio risk monitoring
    - Maximum drawdown protection

12. **Main Trading System** (`main.py`)
    - Complete live trading loop
    - Integrated execution: data → AI → risk → broker
    - Graceful shutdown handling
    - Paper/Live trading modes
    - Real-time performance monitoring

13. **Monitoring Dashboard** (`dashboard.py`)
    - Streamlit-based web interface
    - Real-time account visualization
    - Position and P&L tracking
    - Performance metrics display
    - Risk summary dashboard

#### Phase 4: Deployment, Operation & Maintenance ✅

14. **Docker Containerization**
    - Production-ready `Dockerfile` with Python 3.11
    - Multi-service `docker-compose.yml` configuration
    - Optimized `.dockerignore` for smaller image sizes
    - Non-root user for security
    - Health checks and resource limits

15. **Deployment Documentation** (`DEPLOYMENT.md`)
    - Comprehensive deployment guide (150+ lines)
    - Docker Compose instructions
    - Manual deployment steps
    - AWS EC2 cloud deployment guide
    - Security best practices
    - Troubleshooting section

16. **Systemd Service** (`kiwi-ai.service`)
    - Auto-start on server boot
    - Automatic restart on failure
    - Resource limits and security hardening
    - Proper logging to systemd journal

17. **Monitoring Scripts** (`/scripts/`)
    - `health_check.sh`: Container health monitoring
    - `rotate_logs.sh`: Log rotation and compression
    - `retrain_models.sh`: Automated model retraining
    - `backup.sh`: Automated backups of models and config
    - Complete README with cron setup instructions

## 🚀 Quick Start

### Prerequisites

- **For Docker Deployment (Recommended):**
  - Docker 20.10+
  - Docker Compose 1.29+
  
- **For Manual Deployment:**
  - Python 3.11 or higher
  - pip package manager

### Deployment Options

#### Option 1: Docker Deployment (Recommended)

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd Kiwi_AI
```

2. **Configure environment:**
```bash
# Create .env file with your API keys
cp .env.example .env
nano .env
```

3. **Deploy with Docker Compose:**
```bash
docker-compose up -d
```

4. **View logs:**
```bash
docker-compose logs -f
```

5. **Access dashboard** (optional):
```bash
docker-compose up -d dashboard
# Visit http://localhost:8501
```

📖 **[Full Deployment Guide](DEPLOYMENT.md)** - Includes AWS EC2, systemd, and monitoring setup

#### Option 2: Manual Installation

1. **Clone the repository:**
```bash
git clone <your-repository-url>
cd Kiwi_AI
```

2. **Create a virtual environment:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
   - Copy `.env` file and update with your API keys
   - Get free API keys from [Alpaca](https://alpaca.markets/)

5. **Verify installation:**
```bash
python config.py
```

## 📁 Project Structure

```
/Kiwi_AI
├── 🎯 MAIN APPLICATION (Run this!)
│   └── run_kiwi.py            # ⭐ ALL-IN-ONE Application with Web Dashboard
│                              # - Visual settings manager (no .env editing!)
│                              # - Daily + Real-Time trading modes
│                              # - Live monitoring dashboard
│                              # - Built-in help and documentation
│                              # - Start/stop trading with one click
│
├── /data                      # Market data handling
│   ├── __init__.py
│   └── data_handler.py        # Fetch historical data, technical indicators
│
├── /strategies                # Trading strategies
│   ├── __init__.py
│   ├── base_strategy.py       # Abstract base class
│   ├── trend_following.py     # Moving average crossover
│   ├── mean_reversion.py      # RSI + Bollinger Bands
│   └── volatility_breakout.py # ATR + Donchian Channels
│
├── /meta_ai                   # AI Brain
│   ├── __init__.py
│   ├── regime_detector.py     # Market regime classification (TREND/SIDEWAYS/VOLATILE)
│   ├── performance_monitor.py # Real-time performance tracking
│   └── strategy_selector.py   # Intelligent strategy selection
│
├── /execution                 # Execution & Trading
│   ├── __init__.py
│   ├── broker_interface.py    # Alpaca API integration (paper/live trading)
│   └── risk_manager.py        # Position sizing & risk management
│
├── /scripts                   # Operational scripts
│   ├── health_check.sh        # Container health monitoring
│   ├── rotate_logs.sh         # Log rotation and compression
│   ├── retrain_models.sh      # Automated model retraining
│   ├── backup.sh              # Automated backups
│   └── README.md              # Scripts documentation
│
├── /utils                     # Utilities
│   ├── __init__.py
│   ├── config_loader.py       # Configuration management
│   └── logger.py              # Centralized logging
│
├── /test_script_phases        # Phase testing scripts
│   ├── phase1.py              # Phase 1: Foundation tests
│   ├── phase2.py              # Phase 2: AI Brain tests
│   ├── phase3.py              # Phase 3: Execution tests
│   └── phase4.py              # Phase 4: Deployment tests
│
├── /models                    # Trained AI models (gitignored)
│   └── regime_detector.pkl    # Trained regime detection model
├── /market_data               # Data cache (gitignored)
├── /backtest_reports          # Backtest reports (gitignored)
│
├── config.py                  # Configuration loader (reads .env)
├── train_models.py            # Model training script
│
├── Dockerfile                 # Docker container configuration
├── docker-compose.yml         # Multi-container orchestration
├── .dockerignore              # Docker build exclusions
├── kiwi-ai.service            # Systemd service file
│
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── .env                       # Environment variables (optional - can configure via UI)
│
├── README.md                  # This file - Project documentation
├── QUICKSTART.md              # Quick reference guide
├── DEPLOYMENT.md              # Deployment guide (Docker, AWS, systemd)
├── RoadMap.txt                # Development roadmap
├── ALL_PHASES_COMPLETED.md    # Phase completion reports
├── CHANGELOG.md               # Project changelog
└── LICENSE                    # MIT License
```

**Key Changes:**
- ✅ `run_kiwi.py` - Single entry point with everything integrated
- ❌ `main.py` - Removed (functionality merged into run_kiwi.py)
- ❌ `dashboard.py` - Removed (functionality merged into run_kiwi.py)
- 🎨 Visual settings manager - No coding required!

## 🧪 Testing Individual Components

Each module can be tested independently:

```bash
# Run Phase 1 demonstration
python test_script_phases/phase1.py

# Run Phase 2 demonstration (AI Brain)
python test_script_phases/phase2.py

# Train regime detection models
python train_models.py --years 2 --quick-test

# Test configuration
python config.py

# Test data handler
python data/data_handler.py

# Test strategies
python strategies/trend_following.py
python strategies/mean_reversion.py
python strategies/volatility_breakout.py

# Test AI components
python meta_ai/regime_detector.py
python meta_ai/performance_monitor.py
python meta_ai/strategy_selector.py

# Test utilities
python utils/logger.py
python utils/config_loader.py
```

### Running Phase Tests

Test the complete functionality of each phase:

```bash
# Phase 1: Foundation & Strategies
python test_script_phases/phase1.py

# Phase 2: AI Brain & Intelligence
python test_script_phases/phase2.py

# Phase 3: Live Trading (Coming soon)
python test_script_phases/phase3.py

# Phase 4: Deployment (Coming soon)
python test_script_phases/phase4.py
```

## 🎨 Trading Strategies

### 1. Trend Following Strategy
- **Best for:** Trending markets
- **Indicators:** Moving Average Crossover (SMA/EMA)
- **Signal:** Buy when fast MA crosses above slow MA

### 2. Mean Reversion Strategy
- **Best for:** Sideways/ranging markets
- **Indicators:** RSI + Bollinger Bands
- **Signal:** Buy when oversold, sell when overbought

### 3. Volatility Breakout Strategy
- **Best for:** Volatile markets with breakouts
- **Indicators:** ATR + Donchian Channels
- **Signal:** Buy/sell on channel breakouts

## 🔐 Security Best Practices

- ✅ `.env` file is in `.gitignore` - **NEVER commit it**
- ✅ All secrets loaded from environment variables
- ✅ Paper trading mode enabled by default
- ✅ Configuration validation before running

## 📊 Configuration

Key configuration variables in `.env`:

```env
# Broker API (Alpaca)
ALPACA_API_KEY="your_key_here"
ALPACA_SECRET_KEY="your_secret_here"
ALPACA_PAPER_TRADING="true"

# Trading Parameters
MAX_RISK_PER_TRADE="0.02"
INITIAL_CAPITAL="100000"
```

## 🗺️ Development Roadmap

- ✅ **Phase 1:** Foundation & Strategy Arsenal (COMPLETE) - [Details](ALL_PHASES_COMPLETED.md)
- ✅ **Phase 2:** AI Brain & Intelligence (COMPLETE) - [Details](ALL_PHASES_COMPLETED.md)
- ✅ **Phase 3:** Execution & Live Trading (COMPLETE) - [Details](ALL_PHASES_COMPLETED.md)
- ⏳ **Phase 4:** Deployment & Production (NEXT)

📄 **[View Full Roadmap](RoadMap.txt)** | 📝 **[View Changelog](CHANGELOG.md)**

## 📊 Project Status

**Current Version:** 2.5.3 🆕  
**Latest Update:** November 10, 2025 - Status Section Enhancement  
**Phase 1 Completion:** October 17, 2025  
**Phase 2 Completion:** October 18, 2025  
**Phase 3 Completion:** October 18, 2025  
**Phase 4 Completion:** October 19, 2025  
**Phase 5 Completion:** November 6, 2025 (Intelligent Interaction & Assisted Accuracy)  
**v2.0 Release:** November 2, 2025 (TradingView & Multi-Asset)  
**v2.1 Release:** November 3, 2025 (Chart Optimization & WebSocket Stability)  
**v2.2 Release:** November 5, 2025 (AI Intelligence & Real-Time Recommendations)  
**v2.2.1 Release:** November 5, 2025 (Enhanced UX & Faster AI Initialization)  
**v2.3.0 Release:** November 6, 2025 (AI Learning Loop & Risk Management)  
**v2.4.0 Release:** November 6, 2025 (Interactive AI Intelligence Table)  
**v2.5.0 Release:** November 9, 2025 (AI 5-Minute Market Analysis)  
**v2.5.1 Release:** November 9, 2025 (Unified Status Table)  
**v2.5.2 Release:** November 10, 2025 (Complete Visual Cleanup - Minimalist Design)  
**v2.5.3 Release:** November 10, 2025 (Status Section Enhancement - Auto-Rotation)  
**Total Lines of Code:** 11,400+  
**Test Coverage:** 100% for all phases  
**Strategies Implemented:** 3  
**AI Components:** 3 (Regime Detector, Performance Monitor, Strategy Selector)  
**Execution Modules:** 2 (Broker Interface with Risk Assessment, Risk Manager with Entry Analysis)  
**Main Application:** `run_kiwi.py` (All-in-one web dashboard with minimalist design)  
**Trading Modes:** Real-Time Only (Auto-Start WebSocket streaming)  
**Charts:** Professional TradingView integration - Full-width, optimized display  
**Supported Assets:** 27 instruments across 5 categories (Stocks, Forex, Crypto, Indices, Commodities)  
**UI:** Professional liquid-style dashboard with glass morphism + interactive AI Intelligence table + minimalist Apple-style design  
**Connection Management:** Advanced WebSocket handling with retry logic  
**Risk Features:** Entry Risk Score (0-100), Dynamic Position Sizing, Critical Warnings  
**AI Learning:** User feedback loop with signal suppression (15-min cooldown)  
**Interactive Table:** Clickable headers with professional card-based detail views  
**AI Analysis:** Real-time 5-minute market analysis with buy/sell recommendations  
**Status Display:** Unified rotating container with 7-second auto-rotation through 4 sections  
**Visual Design:** Clean minimalist interface with zero separator lines (32 removed) + consistent gradient styling  
**Status:** ✅ Production Ready - Intelligent Trading with Live AI Market Analysis & Risk Management

## 🤝 Contributing

This is a personal/educational project, but suggestions and improvements are welcome!

## ⚠️ Disclaimer

This software is for educational purposes only. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always test thoroughly with paper trading before using real capital.

## 📝 License

MIT License

Copyright (c) 2025 Kiwi AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 📧 Contact

**GitHub:** [@Noobiez16](https://github.com/Noobiez16)

---

**Built with 💚 by the Kiwi AI Team**

Last Updated: November 10, 2025 (v2.5.3)
