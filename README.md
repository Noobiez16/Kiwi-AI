# 🥝 Kiwi_AI - Advanced Adaptive Algorithmic Trading System

An intelligent meta-strategy trading system that uses artificial intelligence to dynamically select the most suitable trading strategy based on current market conditions.

## 🎯 Project Overview

Kiwi_AI is designed to overcome the limitations of static trading models by:
- **Detecting market regimes** (trending, sideways, volatile)
- **Dynamically selecting strategies** from a diverse arsenal
- **Monitoring performance** in real-time
- **Adapting to changing conditions** automatically

## 📋 Current Status: Phase 1 Complete ✅

### ✅ Completed Components

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

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

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
├── /data                      # Market data handling
│   ├── __init__.py
│   └── data_handler.py
├── /strategies                # Trading strategies
│   ├── __init__.py
│   ├── base_strategy.py
│   ├── trend_following.py
│   ├── mean_reversion.py
│   └── volatility_breakout.py
├── /utils                     # Utilities
│   ├── __init__.py
│   ├── config_loader.py
│   └── logger.py
├── /test_script_phases        # Phase testing scripts
│   ├── phase1.py             # Phase 1 demonstration
│   ├── phase2.py             # Phase 2 tests (future)
│   ├── phase3.py             # Phase 3 tests (future)
│   └── phase4.py             # Phase 4 tests (future)
├── config.py                  # Main configuration
├── requirements.txt           # Dependencies
├── .gitignore                 # Git ignore rules
├── .env                       # Environment variables (NOT in git)
└── README.md                  # This file
```

## 🧪 Testing Individual Components

Each module can be tested independently:

```bash
# Test configuration
python config.py

# Test data handler
python data/data_handler.py

# Test strategies
python strategies/trend_following.py
python strategies/mean_reversion.py
python strategies/volatility_breakout.py

# Test logger
python utils/logger.py

# Test config loader
python utils/config_loader.py
```

### Running Phase Tests

Test the complete functionality of each phase:

```bash
# Phase 1: Foundation & Strategies
python test_script_phases/phase1.py

# Phase 2: AI & Backtesting (Coming soon)
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

- ✅ **Phase 1:** Foundation & Strategy Arsenal (COMPLETE)
- ⏳ **Phase 2:** AI Brain & Backtesting Engine (NEXT)
- 🔜 **Phase 3:** Market Connection & Live Simulation
- 🔜 **Phase 4:** Deployment & Production

## 🤝 Contributing

This is a personal/educational project, but suggestions and improvements are welcome!

## ⚠️ Disclaimer

This software is for educational purposes only. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always test thoroughly with paper trading before using real capital.

## 📝 License

[Your chosen license]

## 📧 Contact

[Your contact information]

---

**Built with 💚 by the Kiwi_AI Team**

Last Updated: October 17, 2025
