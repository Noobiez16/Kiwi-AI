"""
Model Training Script
Train and save AI models for regime detection.
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_handler import DataHandler
from meta_ai.regime_detector import RegimeDetector
import config


def train_regime_model(
    symbol: str = "SPY",
    years_of_data: int = 10,
    save_model: bool = True
):
    """
    Train the regime detection model on historical data.
    
    Args:
        symbol: Stock symbol to use for training
        years_of_data: Number of years of historical data
        save_model: Whether to save the trained model
    """
    print("=" * 80)
    print(" " * 20 + "🧠 KIWI_AI MODEL TRAINING 🧠")
    print("=" * 80)
    print()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years_of_data)
    
    print(f"📊 Training Configuration:")
    print(f"   Symbol: {symbol}")
    print(f"   Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"   Duration: {years_of_data} years")
    print()
    
    # Fetch training data
    print("🌐 Fetching training data...")
    handler = DataHandler()
    
    try:
        data = handler.fetch_historical_data(
            symbol,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            use_cache=True
        )
        
        print(f"✅ Loaded {len(data)} bars of data")
        print(f"   Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"   Price range: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
        print()
        
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None
    
    # Data quality checks
    print("🔍 Data Quality Checks:")
    missing = data.isnull().sum().sum()
    print(f"   Missing values: {missing}")
    
    if missing > 0:
        print(f"   ⚠️  Filling missing values...")
        data = data.fillna(method='ffill').fillna(method='bfill')
    
    # Check for sufficient data
    if len(data) < 252 * 2:  # At least 2 years
        print(f"❌ Insufficient data: {len(data)} bars (need at least {252*2})")
        return None
    
    print(f"   ✅ Data quality: OK")
    print()
    
    # Initialize and train regime detector
    print("🧠 Training Regime Detection Model...")
    print("-" * 80)
    
    detector = RegimeDetector(n_states=3)
    
    try:
        detector.train(data, save_model=save_model)
        print()
        print("✅ Model training completed successfully!")
        
    except Exception as e:
        print(f"❌ Error training model: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # Validate model on different periods
    print()
    print("=" * 80)
    print("🔬 Model Validation")
    print("=" * 80)
    print()
    
    validation_periods = [
        ("Last Year", -252),
        ("Last 6 Months", -126),
        ("Last 3 Months", -63),
        ("Last Month", -21)
    ]
    
    for period_name, days in validation_periods:
        test_data = data.iloc[days:]
        regime = detector.predict_regime(test_data)
        confidence = detector.get_regime_confidence(test_data)
        
        print(f"{period_name}:")
        print(f"   Detected Regime: {regime}")
        print(f"   Confidence:")
        for reg, conf in confidence.items():
            bar = "█" * int(conf * 20)
            print(f"      {reg:10s}: {bar} {conf:.2%}")
        print()
    
    # Summary statistics
    print("=" * 80)
    print("📈 Training Summary")
    print("=" * 80)
    print()
    
    # Analyze regime distribution
    print("Regime Distribution Analysis:")
    regimes = []
    window_size = 50
    
    for i in range(window_size, len(data), window_size):
        window_data = data.iloc[i-window_size:i]
        regime = detector.predict_regime(window_data)
        regimes.append(regime)
    
    from collections import Counter
    regime_counts = Counter(regimes)
    total = len(regimes)
    
    for regime, count in regime_counts.most_common():
        pct = (count / total) * 100
        print(f"   {regime:10s}: {count:3d} periods ({pct:5.1f}%)")
    
    print()
    
    if save_model:
        print(f"💾 Model saved to: {config.REGIME_MODEL_PATH}")
        print(f"   You can now use this model in live trading!")
    
    print()
    print("=" * 80)
    print("✅ Model training and validation complete!")
    print("=" * 80)
    
    return detector


def quick_test(detector: RegimeDetector, symbol: str = "SPY"):
    """
    Quick test of the trained model on recent data.
    
    Args:
        detector: Trained RegimeDetector
        symbol: Symbol to test on
    """
    print()
    print("=" * 80)
    print("🧪 Quick Test on Recent Data")
    print("=" * 80)
    print()
    
    handler = DataHandler()
    
    # Get last 90 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    data = handler.fetch_historical_data(symbol, start_date, end_date, use_cache=False)
    
    regime = detector.predict_regime(data)
    confidence = detector.get_regime_confidence(data)
    
    print(f"Recent Market Condition ({symbol}):")
    print(f"   Detected Regime: {regime}")
    print(f"   Confidence Scores:")
    for reg, conf in confidence.items():
        status = "⭐" if reg == regime else "  "
        print(f"      {status} {reg:10s}: {conf:.2%}")
    
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Kiwi_AI regime detection model")
    parser.add_argument(
        "--symbol",
        type=str,
        default="SPY",
        help="Stock symbol to use for training (default: SPY)"
    )
    parser.add_argument(
        "--years",
        type=int,
        default=10,
        help="Years of historical data to use (default: 10)"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save the trained model"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test after training"
    )
    
    args = parser.parse_args()
    
    # Train model
    detector = train_regime_model(
        symbol=args.symbol,
        years_of_data=args.years,
        save_model=not args.no_save
    )
    
    # Quick test if requested
    if detector and args.quick_test:
        quick_test(detector, args.symbol)
