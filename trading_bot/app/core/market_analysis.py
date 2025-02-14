import pandas as pd
import pandas_ta as ta
import numpy as np
from scipy import stats

class MarketAnalyzer:
    def __init__(self, lookback_period=100):
        self.lookback_period = lookback_period

    def analyze_market_regime(self, df):
        """Determine current market regime (trending/ranging/volatile)"""
        # Calculate directional movement
        adx = df['ADX'].iloc[-1]
        
        # Calculate volatility state
        current_volatility = df['ATR'].iloc[-1] / df['close'].iloc[-1]
        hist_volatility = df['ATR'].rolling(20).mean().iloc[-1] / df['close'].iloc[-1]
        
        # Determine market regime
        if adx > 25:
            if current_volatility > hist_volatility * 1.5:
                return 'volatile_trend'
            return 'trending'
        else:
            if current_volatility > hist_volatility * 1.5:
                return 'volatile_range'
            return 'ranging'

    def detect_divergence(self, df):
        """Detect price and indicator divergences"""
        price_highs = df['high'].rolling(5).max()
        price_lows = df['low'].rolling(5).min()
        
        rsi_highs = df['RSI'].rolling(5).max()
        rsi_lows = df['RSI'].rolling(5).min()
        
        # Bearish divergence
        bearish_div = (
            price_highs.iloc[-1] > price_highs.iloc[-2] and
            rsi_highs.iloc[-1] < rsi_highs.iloc[-2]
        )
        
        # Bullish divergence
        bullish_div = (
            price_lows.iloc[-1] < price_lows.iloc[-2] and
            rsi_lows.iloc[-1] > rsi_lows.iloc[-2]
        )
        
        return {
            'bullish_divergence': bullish_div,
            'bearish_divergence': bearish_div
        }

    def analyze_volume_profile(self, df):
        """Analyze volume profile for support/resistance"""
        price_bins = pd.qcut(df['close'], q=20, duplicates='drop')
        volume_profile = df.groupby(price_bins)['volume'].sum()
        
        # Find high volume nodes
        high_volume_levels = volume_profile[volume_profile > volume_profile.mean()]
        
        return {
            'high_volume_levels': high_volume_levels.index.mid,
            'volume_profile': volume_profile
        }

    def calculate_market_strength(self, df):
        """Calculate overall market strength index"""
        # Trend strength
        trend_strength = min(100, df['ADX'].iloc[-1])
        
        # Momentum
        momentum = (df['close'].iloc[-1] / df['close'].iloc[-20] - 1) * 100
        
        # Volume strength
        volume_sma = df['volume'].rolling(20).mean()
        volume_strength = (df['volume'].iloc[-1] / volume_sma.iloc[-1]) * 100
        
        # Combine metrics
        market_strength = (
            0.4 * trend_strength +
            0.3 * abs(momentum) +
            0.3 * volume_strength
        )
        
        return {
            'overall_strength': market_strength,
            'trend_strength': trend_strength,
            'momentum': momentum,
            'volume_strength': volume_strength
        }

    def find_key_levels(self, df):
        """Find key support and resistance levels"""
        # Calculate pivot points
        pivot = (df['high'].iloc[-1] + df['low'].iloc[-1] + df['close'].iloc[-1]) / 3
        r1 = 2 * pivot - df['low'].iloc[-1]
        r2 = pivot + (df['high'].iloc[-1] - df['low'].iloc[-1])
        s1 = 2 * pivot - df['high'].iloc[-1]
        s2 = pivot - (df['high'].iloc[-1] - df['low'].iloc[-1])
        
        # Find historical support/resistance
        peaks = df[df['high'] == df['high'].rolling(5).max()]
        troughs = df[df['low'] == df['low'].rolling(5).min()]
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            's1': s1,
            's2': s2,
            'historical_resistance': peaks['high'].tolist(),
            'historical_support': troughs['low'].tolist()
        } 