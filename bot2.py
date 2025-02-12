import ccxt
import alpaca_trade_api as tradeapi
import pandas as pd
import time
import pandas_ta as ta  # Replace talib with pandas_ta
import threading
import json
import os
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
from oandapyV20.endpoints.orders import OrderCreate
from oandapyV20.endpoints.positions import OpenPositions, PositionClose
from config import (
    TRADING_CONFIG, 
    TECHNICAL_PARAMS, 
    FOREX_CONFIG, 
    EXCHANGE_CONFIG
)
from oandapyV20.endpoints.accounts import AccountSummary

# Global variables
exchange = None
exchange_choice = None
symbol_choice = None
risk_manager = None
strategy_choice = None
position_manager = None
account_id = None

# Configuration
EXCHANGES = {
    'oanda': 'oanda',  # We'll use oanda-v20 package
    'alpaca': tradeapi.REST
}

# Update timeframes to match forex conventions
TIMEFRAMES = {
    'day-trading': 'M5',    # 5 minutes
    'swing-trading': 'H4',  # 4 hours
    'scalping': 'M1',      # 1 minute
    'position-trading': 'D' # Daily
}

# Forex currency pairs
FOREX_PAIRS = [
    'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF',
    'AUD_USD', 'USD_CAD', 'NZD_USD'
]

SMA_SHORT = 50
SMA_LONG = 200
LOOKBACK = 20
RISK_PER_TRADE = 0.02  # 2% du capital
CAPITAL = 1000  # Exemple de capital de départ

class RiskManager:
    def __init__(self, capital, risk_per_trade, max_positions=3):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.max_positions = max_positions
        self.open_positions = []

    def calculate_position_size(self, entry_price, stop_loss, volatility):
        """Enhanced position size calculation considering volatility"""
        risk_amount = self.capital * self.risk_per_trade
        position_size = risk_amount / abs(entry_price - stop_loss)
        
        # Adjust position size based on volatility
        volatility_factor = 1 - (volatility * 0.5)  # Reduce size for high volatility
        position_size *= volatility_factor
        
        # Check if we have room for new positions
        if len(self.open_positions) >= self.max_positions:
            return 0
            
        return position_size

    def add_position(self, position):
        self.open_positions.append(position)

    def remove_position(self, position):
        self.open_positions.remove(position)

class PositionManager:
    def __init__(self, risk_manager, exchange):
        self.risk_manager = risk_manager
        self.exchange = exchange
        self.positions = {}

    def monitor_positions(self, df):
        """Monitor and manage open positions"""
        current_price = df['close'].iloc[-1]
        
        for symbol, position in self.positions.items():
            # Check stop loss
            if position['side'] == 'buy':
                if current_price <= position['stop_loss']:
                    self.close_position(symbol, 'stop_loss')
                # Trail stop loss
                elif current_price > position['entry_price']:
                    new_stop = self.calculate_trailing_stop(
                        position['side'],
                        current_price,
                        position['entry_price'],
                        position['initial_stop']
                    )
                    if new_stop > position['stop_loss']:
                        position['stop_loss'] = new_stop
                        print(f"Trailing stop updated to {new_stop}")
            else:  # sell position
                if current_price >= position['stop_loss']:
                    self.close_position(symbol, 'stop_loss')
                elif current_price < position['entry_price']:
                    new_stop = self.calculate_trailing_stop(
                        position['side'],
                        current_price,
                        position['entry_price'],
                        position['initial_stop']
                    )
                    if new_stop < position['stop_loss']:
                        position['stop_loss'] = new_stop
                        print(f"Trailing stop updated to {new_stop}")

    def calculate_trailing_stop(self, side, current_price, entry_price, initial_stop):
        """Calculate trailing stop loss"""
        risk_distance = abs(entry_price - initial_stop)
        if side == 'buy':
            return current_price - risk_distance
        return current_price + risk_distance

    def add_position(self, symbol, position_data):
        """Add new position"""
        position_data['initial_stop'] = position_data['stop_loss']
        self.positions[symbol] = position_data
        self.risk_manager.add_position(position_data)

    def close_position(self, symbol, reason='manual'):
        """Close position and update risk manager"""
        try:
            position = self.positions[symbol]
            order = self.exchange.create_order(
                symbol,
                'market',
                'sell' if position['side'] == 'buy' else 'buy',
                position['size']
            )
            print(f"Position closed: {symbol} ({reason})")
            self.risk_manager.remove_position(position)
            del self.positions[symbol]
            return order
        except Exception as e:
            print(f"Error closing position: {str(e)}")
            return None

def load_credentials():
    """Load saved credentials if they exist"""
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            return json.load(f)
    return None

def save_credentials(credentials):
    """Save credentials for future use"""
    with open('credentials.json', 'w') as f:
        json.dump(credentials, f)

def login():
    """Handle user login for different exchanges"""
    credentials = load_credentials()
    
    if credentials is None:
        exchange_choice = input("Choose exchange (oanda/alpaca): ").lower()
        api_key = input("Enter API key: ")
        account_id = input("Enter Account ID: ") if exchange_choice == 'oanda' else None
        
        if exchange_choice == 'oanda':
            try:
                # Initialize OANDA client
                exchange = oandapyV20.API(access_token=api_key, environment='practice')
                # Test authentication
                r = OpenPositions(accountID=account_id)
                exchange.request(r)
                credentials = {
                    'exchange': exchange_choice,
                    'api_key': api_key,
                    'account_id': account_id
                }
                save_credentials(credentials)
                return exchange, exchange_choice, account_id
            except Exception as e:
                print(f"Login failed: {str(e)}")
                return None, None, None
        elif exchange_choice == 'alpaca':
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            try:
                exchange = EXCHANGES[exchange_choice](
                    email,  # Using email as API key
                    password,  # Using password as secret key
                    base_url="https://paper-api.alpaca.markets"
                )
                # Test authentication
                exchange.get_account()
                credentials = {
                    'exchange': exchange_choice,
                    'email': email,
                    'password': password
                }
                save_credentials(credentials)
                return exchange, exchange_choice
            except Exception as e:
                print(f"Login failed: {str(e)}")
                return None, None
                
        # Add more exchanges as needed
        
    else:
        # Use saved credentials
        exchange_choice = credentials['exchange']
        if exchange_choice == 'alpaca':
            exchange = EXCHANGES[exchange_choice](
                credentials['email'],
                credentials['password'],
                base_url="https://paper-api.alpaca.markets"
            )
        return exchange, exchange_choice

def get_candles(self, pair, count=100):
    """Get latest candle data"""
    try:
        params = {
            "count": count,
            "granularity": "M5"  # 5-minute candles
        }
        
        # Construct the endpoint path
        path = f"/v3/instruments/{pair}/candles"
        
        # Create request
        r = instruments.InstrumentsCandles(instrument=pair, params=params)
        
        try:
            # Make request
            response = self.exchange.request(r)
            if 'candles' in response:
                return self.format_candles(response['candles'])
            else:
                print(f"No candles in response: {response}")
                return None
        except Exception as e:
            print(f"Request error: {str(e)}")
            return None
            
    except Exception as e:
        print(f"Error getting candles: {str(e)}")
        print(f"Pair: {pair}, Count: {count}")
        return None

def calculate_volatility(df, window=20):
    """Calculate price volatility using ATR"""
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], timeperiod=window)
    return df['ATR'].iloc[-1] / df['close'].iloc[-1]

def apply_indicators(df):
    """Enhanced technical indicators"""
    df['EMA9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['EMA21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    df['Resistance'] = df['high'].rolling(LOOKBACK).max()
    df['Support'] = df['low'].rolling(LOOKBACK).min()
    df['SMA50'] = df['close'].ta.sma(length=SMA_SHORT)
    df['SMA200'] = df['close'].ta.sma(length=SMA_LONG)
    df['RSI'] = ta.rsi(df['close'], timeperiod=14)
    
    # Add more sophisticated indicators
    df['ATR'] = ta.atr(df['high'], df['low'], df['close'], timeperiod=14)
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = ta.bbands(
        df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = ta.macd(
        df['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['Stoch_K'], df['Stoch_D'] = ta.stoch(
        df['high'], df['low'], df['close'], 
        fastk_period=14, slowk_period=3, slowd_period=3)
    
    # Add trend strength indicator
    df['ADX'] = ta.adx(df['high'], df['low'], df['close'], timeperiod=14)
    
    return df

class TradingStrategy:
    def __init__(self, timeframe, risk_manager):
        self.timeframe = timeframe
        self.risk_manager = risk_manager
        
    def analyze(self, df):
        """Base analysis method to be implemented by each strategy"""
        raise NotImplementedError
        
    def get_stop_loss(self, df, side):
        """Calculate dynamic stop loss based on ATR"""
        atr = df['ATR'].iloc[-1]
        price = df['close'].iloc[-1]
        if side == 'buy':
            return price - (atr * 2)
        return price + (atr * 2)

class PositionTradingStrategy(TradingStrategy):
    def analyze(self, df):
        last_row = df.iloc[-1]
        
        # Trend strength
        strong_trend = last_row['ADX'] > 25
        
        # Multiple timeframe analysis
        trend_aligned = (
            last_row['SMA50'] > last_row['SMA200'] and
            last_row['EMA9'] > last_row['EMA21']
        )
        
        # Volume confirmation
        volume_increasing = df['volume'].iloc[-1] > df['volume'].iloc[-2] * 1.2
        
        # MACD confirmation
        macd_signal = last_row['MACD'] > last_row['MACD_signal']
        
        # Entry conditions
        bullish_entry = (
            last_row['RSI'] < 35 and
            strong_trend and
            trend_aligned and
            volume_increasing and
            macd_signal and
            last_row['close'] > last_row['BB_lower']
        )
        
        bearish_entry = (
            last_row['RSI'] > 65 and
            strong_trend and
            not trend_aligned and
            volume_increasing and
            not macd_signal and
            last_row['close'] < last_row['BB_upper']
        )
        
        if bullish_entry:
            return {'side': 'buy', 'stop_loss': self.get_stop_loss(df, 'buy')}
        elif bearish_entry:
            return {'side': 'sell', 'stop_loss': self.get_stop_loss(df, 'sell')}
        return None

class SwingTradingStrategy(TradingStrategy):
    def analyze(self, df):
        last_row = df.iloc[-1]
        
        # Momentum indicators
        stoch_crossover = (
            df['Stoch_K'].iloc[-2] < df['Stoch_D'].iloc[-2] and
            df['Stoch_K'].iloc[-1] > df['Stoch_D'].iloc[-1]
        )
        
        stoch_crossunder = (
            df['Stoch_K'].iloc[-2] > df['Stoch_D'].iloc[-2] and
            df['Stoch_K'].iloc[-1] < df['Stoch_D'].iloc[-1]
        )
        
        # Price action
        bullish_engulfing = (
            df['close'].iloc[-1] > df['open'].iloc[-1] and
            df['close'].iloc[-1] > df['high'].iloc[-2] and
            df['open'].iloc[-1] < df['low'].iloc[-2]
        )
        
        bearish_engulfing = (
            df['close'].iloc[-1] < df['open'].iloc[-1] and
            df['close'].iloc[-1] < df['low'].iloc[-2] and
            df['open'].iloc[-1] > df['high'].iloc[-2]
        )
        
        if (stoch_crossover and bullish_engulfing and last_row['RSI'] < 40):
            return {'side': 'buy', 'stop_loss': self.get_stop_loss(df, 'buy')}
        elif (stoch_crossunder and bearish_engulfing and last_row['RSI'] > 60):
            return {'side': 'sell', 'stop_loss': self.get_stop_loss(df, 'sell')}
        return None

def calculate_position_size(entry_price, stop_loss, df):
    """Calculate position size with enhanced risk management"""
    volatility = calculate_volatility(df)
    risk_manager = RiskManager(CAPITAL, RISK_PER_TRADE)
    return risk_manager.calculate_position_size(entry_price, stop_loss, volatility)

def place_order(side, price, stop_loss, df):
    """Place order with proper risk management"""
    size = calculate_position_size(price, stop_loss, df)
    if size <= 0:
        return None
        
    try:
        if exchange_choice == 'oanda':
            data = {
                "order": {
                    "units": str(int(size) * (1 if side == 'buy' else -1)),
                    "instrument": symbol_choice,
                    "timeInForce": "GTC",
                    "type": "MARKET",
                    "positionFill": "DEFAULT",
                    "stopLossOnFill": {
                        "price": str(round(stop_loss, 5))
                    }
                }
            }
            
            r = OrderCreate(accountID=account_id, data=data)
            response = exchange.request(r)
            print(f"Order placed: {side} {size} {symbol_choice} at {price}")
            return response
            
        # ... rest of the function for other exchanges
        
    except Exception as e:
        print(f"Error placing order: {str(e)}")
        return None

def trade():
    """Enhanced trading loop with error handling and position management"""
    global risk_manager, position_manager
    strategies = {
        'position-trading': PositionTradingStrategy(TIMEFRAME, risk_manager),
        'swing-trading': SwingTradingStrategy(TIMEFRAME, risk_manager)
        # Add more strategies here
    }
    
    strategy = strategies.get(strategy_choice)
    if not strategy:
        print(f"Strategy {strategy_choice} not implemented")
        return
        
    while True:
        try:
            # Get and validate market data
            df = get_candles(symbol_choice, TIMEFRAME)
            if df is None or len(df) < LOOKBACK:
                print("Insufficient market data")
                time.sleep(60)
                continue
                
            # Apply technical indicators
            df = apply_indicators(df)
            
            # Check for signals
            signal = strategy.analyze(df)
            
            if signal:
                # Validate trading conditions
                if not validate_trading_conditions(df):
                    print("Market conditions unfavorable")
                    continue
                    
                # Place order with position management
                order = place_order(
                    signal['side'],
                    df['close'].iloc[-1],
                    signal['stop_loss'],
                    df
                )
                
                if order:
                    print(f"Successfully placed {signal['side']} order")
                    
            # Monitor open positions
            position_manager.monitor_positions(df)
            
            # Wait for next candle
            sleep_time = calculate_sleep_time(TIMEFRAME)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"Error in trading loop: {str(e)}")
            time.sleep(60)  # Wait before retrying

def validate_trading_conditions(df):
    """Check if market conditions are suitable for trading"""
    last_row = df.iloc[-1]
    
    # Check market volatility
    volatility = calculate_volatility(df)
    if volatility > 0.05:  # More than 5% volatility
        return False
        
    # Check trading hours (for stocks)
    if exchange_choice == 'alpaca':
        current_time = pd.Timestamp.now(tz='America/New_York').time()
        if not (time(9, 30) <= current_time <= time(16, 0)):
            return False
            
    # Check trading volume
    avg_volume = df['volume'].mean()
    if df['volume'].iloc[-1] < avg_volume * 0.5:
        return False
        
    return True

def calculate_sleep_time(timeframe):
    """Calculate appropriate sleep time based on timeframe"""
    timeframe_minutes = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }
    
    minutes = timeframe_minutes.get(timeframe, 1)
    return minutes * 60  # Convert to seconds

def main():
    """Main function to run the trading bot"""
    global exchange, exchange_choice, symbol_choice, risk_manager, strategy_choice, position_manager, account_id
    exchange, exchange_choice, account_id = login()
    
    if exchange is None:
        print("Failed to authenticate. Please try again.")
        return
        
    strategy_choice = input("Choose strategy (day-trading/swing-trading/scalping/position-trading): ")
    symbol_choice = input("Enter trading symbol (e.g., EUR_USD, GBP_USD): ")
    
    global TIMEFRAME
    TIMEFRAME = TIMEFRAMES[strategy_choice]
    
    # Initialize risk manager
    risk_manager = RiskManager(CAPITAL, RISK_PER_TRADE)
    
    # Initialize position manager
    position_manager = PositionManager(risk_manager, exchange)
    
    # Start trading thread
    thread = threading.Thread(target=trade)
    thread.start()

class Backtester:
    def __init__(self, strategy, initial_capital, start_date, end_date):
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        self.positions = []
        self.trades = []
        self.performance_metrics = {}

    def run(self, df):
        """Run backtest on historical data"""
        df = df[(df.index >= self.start_date) & (df.index <= self.end_date)].copy()
        
        for i in range(len(df) - 1):
            current_data = df.iloc[:i+1]
            signal = self.strategy.analyze(current_data)
            
            if signal:
                # Validate conditions
                if not validate_trading_conditions(current_data):
                    continue
                    
                # Calculate position size
                entry_price = current_data['close'].iloc[-1]
                position_size = self.strategy.risk_manager.calculate_position_size(
                    entry_price, 
                    signal['stop_loss'],
                    calculate_volatility(current_data)
                )
                
                # Record trade
                trade = {
                    'entry_date': current_data.index[-1],
                    'side': signal['side'],
                    'entry_price': entry_price,
                    'stop_loss': signal['stop_loss'],
                    'position_size': position_size,
                    'initial_risk': abs(entry_price - signal['stop_loss']) * position_size
                }
                
                # Track position
                self.positions.append(trade)
                self.update_positions(df.iloc[i+1])
        
        self.calculate_performance()
        return self.performance_metrics

    def update_positions(self, current_bar):
        """Update open positions and check for exits"""
        for position in self.positions[:]:  # Copy list for safe removal
            if position['side'] == 'buy':
                # Check stop loss
                if current_bar['low'] <= position['stop_loss']:
                    self.close_position(position, position['stop_loss'], current_bar.name, 'stop_loss')
                # Check take profit
                elif current_bar['high'] >= position['take_profit']:
                    self.close_position(position, position['take_profit'], current_bar.name, 'take_profit')
            else:  # sell position
                if current_bar['high'] >= position['stop_loss']:
                    self.close_position(position, position['stop_loss'], current_bar.name, 'stop_loss')
                elif current_bar['low'] <= position['take_profit']:
                    self.close_position(position, position['take_profit'], current_bar.name, 'take_profit')

    def close_position(self, position, exit_price, exit_date, exit_reason):
        """Close position and record trade"""
        pnl = (exit_price - position['entry_price']) * position['position_size']
        if position['side'] == 'sell':
            pnl *= -1
            
        trade = {
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'side': position['side'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'pnl': pnl,
            'exit_reason': exit_reason,
            'return': pnl / self.initial_capital * 100  # Percentage return
        }
        
        self.trades.append(trade)
        self.capital += pnl
        self.positions.remove(position)

    def calculate_performance(self):
        """Calculate backtest performance metrics"""
        if not self.trades:
            return
            
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        self.performance_metrics = {
            'total_trades': len(trades_df),
            'winning_trades': len(trades_df[trades_df['pnl'] > 0]),
            'losing_trades': len(trades_df[trades_df['pnl'] < 0]),
            'win_rate': len(trades_df[trades_df['pnl'] > 0]) / len(trades_df) * 100,
            'total_pnl': trades_df['pnl'].sum(),
            'total_return': (self.capital - self.initial_capital) / self.initial_capital * 100,
            'largest_win': trades_df['pnl'].max(),
            'largest_loss': trades_df['pnl'].min(),
            'average_win': trades_df[trades_df['pnl'] > 0]['pnl'].mean(),
            'average_loss': trades_df[trades_df['pnl'] < 0]['pnl'].mean(),
            'profit_factor': abs(trades_df[trades_df['pnl'] > 0]['pnl'].sum() / 
                               trades_df[trades_df['pnl'] < 0]['pnl'].sum())
        }
        
        # Calculate drawdown
        cumulative_returns = (1 + trades_df['return'] / 100).cumprod()
        rolling_max = cumulative_returns.expanding().max()
        drawdowns = (cumulative_returns - rolling_max) / rolling_max * 100
        self.performance_metrics['max_drawdown'] = drawdowns.min()

class TradingBot:
    def __init__(self, credentials):
        self.credentials = credentials
        self.connected = False
        self.setup_exchange()
        
    def setup_exchange(self):
        """Setup exchange connection with error handling"""
        try:
            if self.credentials['exchange'] == 'oanda':
                self.exchange = oandapyV20.API(
                    access_token=self.credentials['api_key'],
                    environment="practice"
                )
                self.account_id = self.credentials['account_id']
                
                # Verify connection
                r = AccountSummary(accountID=self.account_id)
                self.exchange.request(r)
                self.connected = True
                
            elif self.credentials['exchange'] == 'alpaca':
                self.exchange = tradeapi.REST(
                    self.credentials['api_key'],
                    self.credentials['api_secret'],
                    base_url='https://paper-api.alpaca.markets'
                )
                self.exchange.get_account()
                self.connected = True
                
        except Exception as e:
            self.connected = False
            raise ConnectionError(f"Failed to connect to {self.credentials['exchange']}: {str(e)}")
            
    def check_connection(self):
        """Check if connection is still active"""
        try:
            if self.credentials['exchange'] == 'oanda':
                r = AccountSummary(accountID=self.account_id)
                self.exchange.request(r)
            else:
                self.exchange.get_account()
            return True
        except:
            return False

if __name__ == "__main__":
    main()
