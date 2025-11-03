"""
Regime Detector Module
Uses Hidden Markov Models (HMM) to detect market regimes.
"""

import numpy as np
import pandas as pd
from typing import Optional, List, Tuple
import pickle
import os
from pathlib import Path
import config


class RegimeDetector:
    """
    Detects market regimes using Hidden Markov Models.
    
    Regimes:
    - TREND: Strong directional movement (trending market)
    - SIDEWAYS: Range-bound movement (consolidation)
    - VOLATILE: High volatility with unclear direction
    """
    
    REGIMES = {
        0: 'SIDEWAYS',
        1: 'TREND',
        2: 'VOLATILE'
    }
    
    def __init__(self, model_path: str = None, n_states: int = 3):
        """
        Initialize the Regime Detector.
        
        Args:
            model_path: Path to saved HMM model (if None, will be trained)
            n_states: Number of hidden states (default: 3 for TREND, SIDEWAYS, VOLATILE)
        """
        self.model_path = model_path or config.REGIME_MODEL_PATH
        self.n_states = n_states
        self.model = None
        self.is_trained = False
        
        # Try to load existing model
        if os.path.exists(self.model_path):
            self.load_model()
    
    def prepare_features(self, data: pd.DataFrame, lookback: int = 20) -> np.ndarray:
        """
        Prepare features for regime detection.
        
        Args:
            data: DataFrame with OHLCV data
            lookback: Lookback period for feature calculation
        
        Returns:
            Array of features for HMM
        """
        df = data.copy()
        
        # Calculate returns
        df['returns'] = df['close'].pct_change()
        
        # Feature 1: Rolling volatility (normalized)
        df['volatility'] = df['returns'].rolling(window=lookback).std()
        
        # Feature 2: Rolling mean return (trend strength)
        df['mean_return'] = df['returns'].rolling(window=lookback).mean()
        
        # Feature 3: Price momentum (close vs moving average)
        df['sma'] = df['close'].rolling(window=lookback).mean()
        df['momentum'] = (df['close'] - df['sma']) / df['sma']
        
        # Feature 4: Volume change (if available)
        if 'volume' in df.columns:
            df['volume_change'] = df['volume'].pct_change().rolling(window=lookback).mean()
        else:
            df['volume_change'] = 0
        
        # Combine features
        features = df[['returns', 'volatility', 'momentum']].dropna()
        
        return features.values
    
    def train(self, data: pd.DataFrame, save_model: bool = True) -> 'RegimeDetector':
        """
        Train the HMM model on historical data.
        
        Args:
            data: DataFrame with OHLCV data
            save_model: Whether to save the trained model
        
        Returns:
            Self for method chaining
        """
        try:
            from hmmlearn import hmm
        except ImportError:
            print("⚠️  hmmlearn not installed. Using simple rule-based regime detection.")
            self.is_trained = False
            return self
        
        print("🧠 Training Regime Detection Model...")
        
        # Prepare features
        features = self.prepare_features(data)
        
        # Train Gaussian HMM
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        
        self.model.fit(features)
        self.is_trained = True
        
        print(f"✅ Model trained with {len(features)} samples")
        
        # Save model
        if save_model:
            self.save_model()
        
        return self
    
    def predict_regime(self, data: pd.DataFrame, recent_bars: int = 50) -> str:
        """
        Predict the current market regime.
        
        Args:
            data: DataFrame with recent OHLCV data
            recent_bars: Number of recent bars to use for prediction
        
        Returns:
            Regime string ('TREND', 'SIDEWAYS', 'VOLATILE')
        """
        # Use last N bars
        recent_data = data.tail(recent_bars) if len(data) > recent_bars else data
        
        # If model is trained, use HMM
        if self.is_trained and self.model is not None:
            features = self.prepare_features(recent_data)
            if len(features) < 10:
                return self._simple_regime_detection(recent_data)
            
            # Predict hidden states
            hidden_states = self.model.predict(features)
            
            # Most recent state
            current_state = hidden_states[-1]
            
            return self.REGIMES[current_state]
        else:
            # Fallback to simple rule-based detection
            return self._simple_regime_detection(recent_data)
    
    def _simple_regime_detection(self, data: pd.DataFrame) -> str:
        """
        Simple rule-based regime detection (fallback when HMM not available).
        
        Args:
            data: DataFrame with OHLCV data
        
        Returns:
            Regime string
        """
        if len(data) < 20:
            return 'SIDEWAYS'
        
        # Calculate metrics
        returns = data['close'].pct_change()
        volatility = returns.rolling(window=20).std().iloc[-1]
        mean_return = returns.rolling(window=20).mean().iloc[-1]
        
        # Calculate trend strength using linear regression slope
        close_prices = data['close'].tail(20).values
        x = np.arange(len(close_prices))
        slope = np.polyfit(x, close_prices, 1)[0]
        normalized_slope = slope / close_prices[-1]  # Normalize by current price
        
        # Classification rules
        high_volatility_threshold = returns.std() * 1.5
        trend_threshold = 0.001  # 0.1% per day
        
        if volatility > high_volatility_threshold:
            return 'VOLATILE'
        elif abs(normalized_slope) > trend_threshold:
            return 'TREND'
        else:
            return 'SIDEWAYS'
    
    def get_regime_confidence(self, data: pd.DataFrame, recent_bars: int = 50) -> dict:
        """
        Get confidence scores for each regime.
        
        Args:
            data: DataFrame with OHLCV data
            recent_bars: Number of recent bars to analyze
        
        Returns:
            Dictionary with confidence scores for each regime
        """
        recent_data = data.tail(recent_bars) if len(data) > recent_bars else data
        
        if self.is_trained and self.model is not None:
            features = self.prepare_features(recent_data)
            if len(features) < 10:
                return {regime: 0.33 for regime in ['TREND', 'SIDEWAYS', 'VOLATILE']}
            
            # Get state probabilities
            log_prob, posteriors = self.model.score_samples(features)
            
            # Average probabilities over recent period
            avg_probs = posteriors[-10:].mean(axis=0)  # Last 10 bars
            
            return {
                'TREND': float(avg_probs[1]),
                'SIDEWAYS': float(avg_probs[0]),
                'VOLATILE': float(avg_probs[2])
            }
        else:
            # Equal confidence for simple detection
            current_regime = self._simple_regime_detection(recent_data)
            return {
                regime: 0.8 if regime == current_regime else 0.1
                for regime in ['TREND', 'SIDEWAYS', 'VOLATILE']
            }
    
    def save_model(self):
        """Save the trained model to disk."""
        if not self.is_trained:
            print("⚠️  No model to save. Train the model first.")
            return
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        print(f"💾 Model saved to: {self.model_path}")
    
    def load_model(self):
        """Load a trained model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            self.is_trained = True
            print(f"✅ Model loaded from: {self.model_path}")
        except Exception as e:
            print(f"⚠️  Could not load model: {e}")
            self.is_trained = False


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("🧠 Regime Detector Test")
    print("=" * 70)
    
    # Create sample data
    from data.data_handler import DataHandler
    from datetime import datetime, timedelta
    
    handler = DataHandler()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365*2)).strftime('%Y-%m-%d')
    
    print(f"\nFetching data for training...")
    data = handler.fetch_historical_data("SPY", start_date, end_date)
    
    # Initialize detector
    detector = RegimeDetector()
    
    # Train model
    print("\n" + "=" * 70)
    detector.train(data)
    
    # Test regime detection
    print("\n" + "=" * 70)
    print("Testing Regime Detection")
    print("=" * 70)
    
    # Test on different time periods
    test_periods = [
        ("Last 30 days", -30),
        ("Last 60 days", -60),
        ("Last 90 days", -90)
    ]
    
    for period_name, days in test_periods:
        test_data = data.iloc[days:]
        regime = detector.predict_regime(test_data)
        confidence = detector.get_regime_confidence(test_data)
        
        print(f"\n{period_name}:")
        print(f"  Detected Regime: {regime}")
        print(f"  Confidence Scores:")
        for reg, conf in confidence.items():
            print(f"    {reg}: {conf:.2%}")
    
    print("\n✅ Regime Detector test completed!")
