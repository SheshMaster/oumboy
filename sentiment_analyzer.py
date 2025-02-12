import nltk
try:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
except Exception as e:
    print(f"Warning: Could not download NLTK data: {str(e)}")

import requests
import pandas as pd
import numpy as np
from textblob import TextBlob
from config import TECHNICAL_PARAMS
import yfinance as yf
from datetime import datetime, timedelta

class SentimentAnalyzer:
    def __init__(self, api_keys=None):
        self.api_keys = api_keys or {}
        self.sentiment_cache = {}
        self.cache_duration = timedelta(hours=1)
        
    def analyze_overall_sentiment(self, symbol):
        """Analyze overall market sentiment from multiple sources"""
        # Combine different sentiment sources
        news_sentiment = self.analyze_news_sentiment(symbol)
        social_sentiment = self.analyze_social_sentiment(symbol)
        technical_sentiment = self.analyze_technical_sentiment(symbol)
        
        # Weight the different sentiment sources
        weighted_sentiment = (
            0.4 * news_sentiment +
            0.3 * social_sentiment +
            0.3 * technical_sentiment
        )
        
        return {
            'overall_sentiment': weighted_sentiment,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment,
            'technical_sentiment': technical_sentiment
        }
        
    def analyze_news_sentiment(self, symbol):
        """Analyze sentiment from news articles"""
        if self._is_cached('news', symbol):
            return self.sentiment_cache['news'][symbol]['score']
            
        # Fetch news from multiple sources
        news_items = self._fetch_news(symbol)
        
        # Analyze sentiment for each news item
        sentiments = []
        for item in news_items:
            blob = TextBlob(item['title'] + ' ' + item['description'])
            sentiments.append(blob.sentiment.polarity)
            
        # Calculate weighted average based on recency
        weights = np.linspace(1, 0.5, len(sentiments))
        weighted_sentiment = np.average(sentiments, weights=weights)
        
        self._cache_sentiment('news', symbol, weighted_sentiment)
        return weighted_sentiment
        
    def analyze_social_sentiment(self, symbol):
        """Analyze sentiment from social media"""
        if self._is_cached('social', symbol):
            return self.sentiment_cache['social'][symbol]['score']
            
        # Fetch social media data
        social_data = self._fetch_social_data(symbol)
        
        # Calculate sentiment scores
        reddit_sentiment = self._analyze_reddit_sentiment(social_data['reddit'])
        twitter_sentiment = self._analyze_twitter_sentiment(social_data['twitter'])
        
        # Combine sentiments
        combined_sentiment = 0.5 * reddit_sentiment + 0.5 * twitter_sentiment
        
        self._cache_sentiment('social', symbol, combined_sentiment)
        return combined_sentiment
        
    def analyze_technical_sentiment(self, symbol):
        """Analyze sentiment based on technical indicators"""
        # Fetch technical data
        data = yf.download(symbol, period='1mo', interval='1d')
        
        # Calculate technical indicators
        rsi = self._calculate_rsi(data['Close'])
        macd = self._calculate_macd(data['Close'])
        bb_position = self._calculate_bb_position(data['Close'])
        
        # Combine technical signals
        technical_score = (
            0.4 * self._normalize_rsi(rsi.iloc[-1]) +
            0.3 * self._normalize_macd(macd.iloc[-1]) +
            0.3 * bb_position.iloc[-1]
        )
        
        return technical_score
        
    def _fetch_news(self, symbol):
        """Fetch news from various sources"""
        news_items = []
        
        # Add your preferred news API endpoints here
        apis = {
            'newsapi': f"https://newsapi.org/v2/everything?q={symbol}&apiKey={self.api_keys.get('newsapi')}",
            'finnhub': f"https://finnhub.io/api/v1/company-news?symbol={symbol}&token={self.api_keys.get('finnhub')}"
        }
        
        for api_name, url in apis.items():
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    news_items.extend(self._parse_news_response(api_name, response.json()))
            except Exception as e:
                print(f"Error fetching news from {api_name}: {str(e)}")
                
        return news_items
        
    def _fetch_social_data(self, symbol):
        """Fetch data from social media platforms"""
        # Implement social media API calls here
        return {
            'reddit': self._fetch_reddit_data(symbol),
            'twitter': self._fetch_twitter_data(symbol)
        }
        
    @staticmethod
    def _calculate_rsi(prices, period=14):
        """Calculate RSI technical indicator"""
        return pd.Series(prices).rolling(window=period).apply(
            lambda x: 100 - (100 / (1 + (x[x > 0].mean() / -x[x < 0].mean())))
        )
        
    @staticmethod
    def _calculate_macd(prices, fast=12, slow=26, signal=9):
        """Calculate MACD technical indicator"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd - signal_line
        
    @staticmethod
    def _calculate_bb_position(prices, period=20):
        """Calculate position within Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (2 * std)
        lower_band = sma - (2 * std)
        
        bb_position = (prices - lower_band) / (upper_band - lower_band)
        return bb_position
        
    def _is_cached(self, source, symbol):
        """Check if sentiment is cached and valid"""
        if source not in self.sentiment_cache:
            return False
            
        cache_entry = self.sentiment_cache[source].get(symbol)
        if not cache_entry:
            return False
            
        return datetime.now() - cache_entry['timestamp'] < self.cache_duration
        
    def _cache_sentiment(self, source, symbol, score):
        """Cache sentiment score"""
        if source not in self.sentiment_cache:
            self.sentiment_cache[source] = {}
            
        self.sentiment_cache[source][symbol] = {
            'score': score,
            'timestamp': datetime.now()
        } 