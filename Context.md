# Automated Trading Bot

A versatile cryptocurrency and stock trading bot that supports multiple exchanges, trading strategies, and technical indicators.

## Features

- Multi-exchange support (Binance, Alpaca)
- Multiple trading strategies:
  - Position Trading
  - Day Trading
  - Swing Trading
  - Scalping
- Technical indicators:
  - EMA (9 & 21 periods)
  - SMA (50 & 200 periods)
  - VWAP (Volume Weighted Average Price)
  - RSI (Relative Strength Index)
  - Support & Resistance levels
- Risk management with position sizing
- Credential management with local storage
- Real-time market monitoring

## Prerequisites
python

pip install ccxt alpaca-trade-api pandas ta-lib


## Configuration

The bot uses the following default settings:

- Risk per trade: 2% of capital
- Default capital: $1000
- Timeframes:
  - Position Trading: 1d
  - Swing Trading: 4h
  - Day Trading: 5m
  - Scalping: 1m
- Technical Parameters:
  - Short SMA: 50 periods
  - Long SMA: 200 periods
  - Lookback period: 20 candles

## Usage

1. Run the bot:

bash

python bot2.py


2. Follow the prompts to:
   - Choose your exchange (binance/alpaca)
   - Enter your API credentials
   - Select trading strategy
   - Enter trading symbol

## Authentication

The bot supports two authentication methods:
- First-time login with API credentials
- Saved credentials for subsequent logins

Credentials are stored locally in `credentials.json` for convenience.

## Trading Strategies

### Position Trading
- Uses RSI and SMA crossovers for entry signals
- Entry conditions:
  - Oversold (RSI < 30) with bullish trend (SMA50 > SMA200)
  - Overbought (RSI > 70) or price at resistance level

### Day Trading
**Timeframe:** 5m (5 minutes)
**Best for:** Intraday movements
**Implementation:**
- Entry Signals:
  - Bullish: Price crosses above VWAP with EMA9 > EMA21
  - Bearish: Price crosses below VWAP with EMA9 < EMA21
- Exit Signals:
  - Take Profit: 1.5:1 reward-to-risk ratio
  - Stop Loss: Below/above recent swing low/high

### Swing Trading
**Timeframe:** 4h (4 hours)
**Best for:** Medium-term trends
**Implementation:**
- Entry Signals:
  - Bullish: RSI bouncing from oversold (30) with support confirmation
  - Bearish: RSI bouncing from overbought (70) with resistance break
- Exit Signals:
  - Take Profit: Major resistance/support levels
  - Stop Loss: Below/above key technical levels

### Other Strategies
- Day Trading, Swing Trading, and Scalping implementations can be extended in the code

### Scalping
**Timeframe:** 1m (1 minute)
**Best for:** Quick price movements
**Implementation:**
- Entry Signals:
  - Bullish: Price above VWAP with increasing volume
  - Bearish: Price below VWAP with increasing volume
- Exit Signals:
  - Take Profit: 0.5% movement
  - Stop Loss: 0.2% against movement

## Risk Management

The bot implements position sizing based on:
- Defined risk percentage per trade (default 2%)
- Entry price and stop-loss levels
- Available capital

### Risk Management for Each Strategy

- Position Trading: 2% risk per trade, wider stops
- Day Trading: 1% risk per trade, moderate stops
- Swing Trading: 1.5% risk per trade, adaptive stops
- Scalping: 0.5% risk per trade, tight stops

### Strategy Selection Guidelines

Choose your strategy based on:
- Available trading time
- Market volatility
- Capital size
- Risk tolerance
- Exchange fees

Remember to:
- Backtest strategies before live trading
- Start with paper trading
- Monitor strategy performance
- Adjust parameters based on market conditions

## Security Notes

- API credentials are stored locally
- Use paper trading accounts for testing
- Review exchange-specific security requirements

## Disclaimer

This trading bot is for educational purposes only. Always:
- Test with paper trading first
- Understand the risks involved
- Never trade with money you can't afford to lose
- Verify all signals before trading

## Contributing

Feel free to fork this repository and submit pull requests for improvements.

## License

This project is open-source and available under the MIT License.

2. Add strategy to the main trading loop:
```python
def trade():
    while True:
        df = get_candles(symbol_choice, TIMEFRAME)
        df = apply_indicators(df)
        
        if strategy_choice == 'your-strategy':
            signal = check_custom_strategy(df)
            if signal:
                execute_trade(signal, df)
        
        time.sleep(strategy_timeframe_seconds)
```

### Strategy Implementation Guide

To implement a new strategy:

1. Create a strategy check function:
```python
def check_custom_strategy(df):
    # Add your custom indicators
    df['CustomIndicator'] = calculate_custom_indicator(df)
    
    # Define entry conditions
    entry_condition = check_entry_conditions(df)
    
    # Return trading signal
    return entry_condition  # 'buy', 'sell', or None
```

2. Add strategy to the main trading loop:
```python
def trade():
    while True:
        df = get_candles(symbol_choice, TIMEFRAME)
        df = apply_indicators(df)
        
        if strategy_choice == 'your-strategy':
            signal = check_custom_strategy(df)
            if signal:
                execute_trade(signal, df)
        
        time.sleep(strategy_timeframe_seconds)
```