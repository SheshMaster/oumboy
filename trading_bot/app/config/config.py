# Trading parameters
TRADING_CONFIG = {
    'capital': 1000,
    'risk_per_trade': 0.02,
    'max_positions': 3,
    'lookback': 20
}

# Technical analysis parameters
TECHNICAL_PARAMS = {
    'sma_short': 50,
    'sma_long': 200,
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'atr_period': 14,
    'volatility_threshold': 0.05
}

# Forex specific settings
FOREX_CONFIG = {
    'timeframes': {
        'day-trading': 'M5',    # 5 minutes
        'swing-trading': 'H4',  # 4 hours
        'scalping': 'M1',      # 1 minute
        'position-trading': 'D' # Daily
    },
    'pairs': [
        'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF',
        'AUD_USD', 'USD_CAD', 'NZD_USD'
    ],
    'pip_values': {
        'EUR_USD': 0.0001,
        'GBP_USD': 0.0001,
        'USD_JPY': 0.01,
        'USD_CHF': 0.0001,
        'AUD_USD': 0.0001,
        'USD_CAD': 0.0001,
        'NZD_USD': 0.0001
    }
}

# Exchange settings
EXCHANGE_CONFIG = {
    'oanda': {
        'type': 'oanda',
        'base_url': 'api-fxpractice.oanda.com',  # Practice account
        'streaming_url': 'stream-fxpractice.oanda.com'
    },
    'alpaca': {
        'type': 'rest',
        'base_url': 'https://paper-api.alpaca.markets'
    }
}

# Strategy parameters
STRATEGY_PARAMS = {
    'position-trading': {
        'timeframe': '1d',
        'indicators': ['SMA', 'EMA', 'RSI', 'ADX'],
        'risk_per_trade': 0.02,
        'max_positions': 5,
        'min_volume': 1000000
    },
    'swing-trading': {
        'timeframe': '4h',
        'indicators': ['MACD', 'Stochastic', 'Bollinger'],
        'risk_per_trade': 0.015,
        'max_positions': 3,
        'min_volume': 500000
    },
    'day-trading': {
        'timeframe': '5m',
        'indicators': ['VWAP', 'EMA', 'RSI'],
        'risk_per_trade': 0.01,
        'max_positions': 2,
        'min_volume': 100000
    }
}

# Risk management settings
RISK_PARAMS = {
    'max_daily_drawdown': 0.03,  # 3% max daily drawdown
    'max_position_size': 0.1,    # 10% max position size
    'correlation_threshold': 0.7, # Maximum correlation between positions
    'max_leverage': 2,           # Maximum leverage
    'min_risk_reward': 1.5       # Minimum risk-reward ratio
}

# Backtesting parameters
BACKTEST_PARAMS = {
    'initial_capital': 10000,
    'commission': 0.001,
    'slippage': 0.001,
    'data_resolution': '1m'
} 