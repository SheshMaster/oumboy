import numpy as np
from scipy.optimize import minimize
from itertools import product
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from market_analysis import MarketAnalyzer
from config import STRATEGY_PARAMS, TECHNICAL_PARAMS

class StrategyOptimizer:
    def __init__(self, strategy_class, data, initial_capital):
        self.strategy_class = strategy_class
        self.data = data
        self.initial_capital = initial_capital
        self.market_analyzer = MarketAnalyzer()
        
    def optimize_parameters(self, param_ranges, metric='sharpe_ratio'):
        """Optimize strategy parameters using grid search and genetic algorithm"""
        # First, perform grid search
        best_params = self._grid_search(param_ranges, metric)
        
        # Refine results with genetic algorithm
        optimized_params = self._genetic_optimization(best_params, param_ranges, metric)
        
        return optimized_params
        
    def _grid_search(self, param_ranges, metric):
        """Perform grid search for initial parameter optimization"""
        param_combinations = list(product(*param_ranges.values()))
        param_names = list(param_ranges.keys())
        
        results = []
        with ProcessPoolExecutor() as executor:
            futures = []
            for params in param_combinations:
                param_dict = dict(zip(param_names, params))
                futures.append(
                    executor.submit(self._evaluate_parameters, param_dict)
                )
            
            for future in futures:
                result = future.result()
                results.append(result)
        
        # Find best parameters
        best_idx = np.argmax([r[metric] for r in results])
        return dict(zip(param_names, param_combinations[best_idx]))
        
    def _genetic_optimization(self, initial_params, param_ranges, metric):
        """Refine parameters using genetic algorithm"""
        bounds = [(param_ranges[k][0], param_ranges[k][-1]) 
                 for k in initial_params.keys()]
                 
        result = minimize(
            lambda x: -self._evaluate_parameters(
                dict(zip(initial_params.keys(), x))
            )[metric],
            x0=list(initial_params.values()),
            bounds=bounds,
            method='SLSQP'
        )
        
        return dict(zip(initial_params.keys(), result.x))
        
    def _evaluate_parameters(self, params):
        """Evaluate a set of parameters"""
        strategy = self.strategy_class(params)
        
        # Run backtest
        results = self._run_backtest(strategy)
        
        # Calculate metrics
        metrics = {
            'sharpe_ratio': self._calculate_sharpe_ratio(results['returns']),
            'max_drawdown': self._calculate_max_drawdown(results['equity']),
            'profit_factor': self._calculate_profit_factor(results['trades']),
            'win_rate': self._calculate_win_rate(results['trades'])
        }
        
        return metrics
        
    def _run_backtest(self, strategy):
        """Run backtest with given strategy"""
        equity = [self.initial_capital]
        trades = []
        returns = []
        
        for i in range(len(self.data) - 1):
            current_data = self.data.iloc[:i+1]
            signal = strategy.analyze(current_data)
            
            if signal:
                trade_result = self._simulate_trade(
                    signal, 
                    current_data, 
                    self.data.iloc[i+1]
                )
                trades.append(trade_result)
                equity.append(equity[-1] * (1 + trade_result['return']))
                returns.append(trade_result['return'])
                
        return {
            'equity': equity,
            'trades': trades,
            'returns': returns
        }
        
    def _simulate_trade(self, signal, entry_data, exit_data):
        """Simulate trade execution with slippage and fees"""
        slippage = 0.001  # 0.1% slippage
        commission = 0.001  # 0.1% commission
        
        entry_price = entry_data['close'].iloc[-1]
        exit_price = exit_data['close']
        
        if signal['side'] == 'buy':
            entry_price *= (1 + slippage)
            exit_price *= (1 - slippage)
        else:
            entry_price *= (1 - slippage)
            exit_price *= (1 + slippage)
            
        gross_return = (exit_price - entry_price) / entry_price
        net_return = gross_return - (2 * commission)  # Entry and exit commission
        
        return {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'return': net_return,
            'side': signal['side']
        }
        
    @staticmethod
    def _calculate_sharpe_ratio(returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        excess_returns = np.array(returns) - risk_free_rate/252
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        
    @staticmethod
    def _calculate_max_drawdown(equity):
        """Calculate maximum drawdown"""
        peaks = pd.Series(equity).expanding(min_periods=1).max()
        drawdowns = (equity - peaks) / peaks
        return drawdowns.min()
        
    @staticmethod
    def _calculate_profit_factor(trades):
        """Calculate profit factor"""
        gains = sum(t['return'] for t in trades if t['return'] > 0)
        losses = abs(sum(t['return'] for t in trades if t['return'] < 0))
        return gains / losses if losses != 0 else float('inf')
        
    @staticmethod
    def _calculate_win_rate(trades):
        """Calculate win rate"""
        winning_trades = sum(1 for t in trades if t['return'] > 0)
        return winning_trades / len(trades) if trades else 0 