from datetime import datetime
import math

class ForexCalculator:
    # Standard pip values for currency pairs
    PIP_VALUES = {
        'EUR_USD': 0.0001,
        'GBP_USD': 0.0001,
        'USD_JPY': 0.01,
        'USD_CHF': 0.0001,
        'AUD_USD': 0.0001,
        'USD_CAD': 0.0001,
        'NZD_USD': 0.0001
    }
    
    @staticmethod
    def calculate_pip_value(pair, lot_size):
        """Calculate pip value in USD"""
        standard_lot = 100000  # Standard lot size
        pip_value = ForexCalculator.PIP_VALUES.get(pair, 0.0001)
        
        # Convert lot size to units
        units = lot_size * standard_lot
        
        # Calculate pip value
        if pair.startswith('USD'):
            return pip_value * units
        elif pair.endswith('USD'):
            return (pip_value * units)
        else:
            # For cross rates, need to get conversion rate
            return (pip_value * units)  # Simplified for now
    
    @staticmethod
    def calculate_position_value(pair, lot_size, price):
        """Calculate total position value"""
        standard_lot = 100000
        return lot_size * standard_lot * price
    
    @staticmethod
    def calculate_margin_required(pair, lot_size, leverage=100):
        """Calculate required margin"""
        position_value = ForexCalculator.calculate_position_value(pair, lot_size, 1)
        return position_value / leverage
    
    @staticmethod
    def pips_difference(pair, price1, price2):
        """Calculate difference in pips between two prices"""
        pip_size = ForexCalculator.PIP_VALUES.get(pair, 0.0001)
        return abs(price1 - price2) / pip_size 