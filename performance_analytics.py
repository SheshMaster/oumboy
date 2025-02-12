import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

class PerformanceAnalyzer:
    def __init__(self, trades_df):
        self.trades_df = trades_df
        self.metrics: Dict[str, Any] = {}
        self.calculate_metrics()

    def calculate_metrics(self):
        """Calculate comprehensive performance metrics"""
        if len(self.trades_df) == 0:
            return
            
        # Basic metrics
        self.metrics['total_trades'] = len(self.trades_df)
        self.metrics['winning_trades'] = len(self.trades_df[self.trades_df['pnl'] > 0])
        self.metrics['losing_trades'] = len(self.trades_df[self.trades_df['pnl'] < 0])
        
        # Advanced metrics
        self.metrics['win_rate'] = self.metrics['winning_trades'] / self.metrics['total_trades']
        self.metrics['avg_win'] = self.trades_df[self.trades_df['pnl'] > 0]['pnl'].mean()
        self.metrics['avg_loss'] = self.trades_df[self.trades_df['pnl'] < 0]['pnl'].mean()
        self.metrics['profit_factor'] = abs(self.metrics['avg_win'] / self.metrics['avg_loss'])
        
        # Risk metrics
        returns = self.trades_df['return']
        self.metrics['sharpe_ratio'] = self.calculate_sharpe_ratio(returns)
        self.metrics['sortino_ratio'] = self.calculate_sortino_ratio(returns)
        self.metrics['max_drawdown'] = self.calculate_max_drawdown(returns)
        
        # Strategy consistency
        self.metrics['consistency_score'] = self.calculate_consistency_score()
        
        # Additional advanced metrics
        self.metrics['avg_trade_duration'] = self.calculate_avg_trade_duration()
        self.metrics['risk_reward_ratio'] = abs(self.metrics['avg_win'] / self.metrics['avg_loss'])
        self.metrics['expectancy'] = (self.metrics['win_rate'] * self.metrics['avg_win']) + \
                                   ((1 - self.metrics['win_rate']) * self.metrics['avg_loss'])
        
        # Volatility metrics
        self.metrics['volatility'] = returns.std() * np.sqrt(252)  # Annualized volatility
        self.metrics['var_95'] = self.calculate_var(returns, 0.95)
        self.metrics['cvar_95'] = self.calculate_cvar(returns, 0.95)
        
        # Trading patterns
        self.metrics['best_day'] = returns.max()
        self.metrics['worst_day'] = returns.min()
        self.metrics['avg_winning_streak'] = self.calculate_streak_metrics()['avg_winning_streak']
        self.metrics['avg_losing_streak'] = self.calculate_streak_metrics()['avg_losing_streak']

    def calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate annualized Sharpe ratio"""
        excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def calculate_sortino_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sortino ratio using downside deviation"""
        excess_returns = returns - risk_free_rate/252
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.sqrt(np.mean(downside_returns**2))
        return np.sqrt(252) * excess_returns.mean() / downside_std

    def calculate_max_drawdown(self, returns):
        """Calculate maximum drawdown and duration"""
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        return drawdowns.min()

    def calculate_consistency_score(self):
        """Calculate strategy consistency score"""
        monthly_returns = self.trades_df.set_index('entry_date')['return'].resample('M').sum()
        positive_months = (monthly_returns > 0).sum()
        return positive_months / len(monthly_returns)

    def calculate_avg_trade_duration(self):
        """Calculate average duration of trades"""
        durations = (self.trades_df['exit_date'] - self.trades_df['entry_date'])
        return durations.mean().total_seconds() / 3600  # Convert to hours

    def calculate_var(self, returns, confidence_level):
        """Calculate Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)

    def calculate_cvar(self, returns, confidence_level):
        """Calculate Conditional Value at Risk (Expected Shortfall)"""
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    def calculate_streak_metrics(self):
        """Calculate winning and losing streak metrics"""
        wins = self.trades_df['pnl'] > 0
        streak_groups = (wins != wins.shift()).cumsum()
        
        winning_streaks = wins.groupby(streak_groups).sum()[wins.groupby(streak_groups).sum() > 0]
        losing_streaks = (~wins).groupby(streak_groups).sum()[~wins.groupby(streak_groups).sum() > 0]
        
        return {
            'avg_winning_streak': winning_streaks.mean() if len(winning_streaks) > 0 else 0,
            'avg_losing_streak': losing_streaks.mean() if len(losing_streaks) > 0 else 0
        }

    def plot_performance(self):
        """Generate enhanced performance visualization"""
        fig = plt.figure(figsize=(20, 15))
        gs = plt.GridSpec(3, 3, figure=fig)
        
        # Equity curve with drawdown
        ax1 = fig.add_subplot(gs[0, :])
        self._plot_equity_curve_with_drawdown(ax1)
        
        # Return distribution
        ax2 = fig.add_subplot(gs[1, 0])
        self._plot_return_distribution(ax2)
        
        # Rolling Sharpe ratio
        ax3 = fig.add_subplot(gs[1, 1])
        self._plot_rolling_sharpe(ax3)
        
        # Rolling volatility
        ax4 = fig.add_subplot(gs[1, 2])
        self._plot_rolling_volatility(ax4)
        
        # Monthly returns heatmap
        ax5 = fig.add_subplot(gs[2, :2])
        self._plot_monthly_returns_heatmap(ax5)
        
        # Trade clustering
        ax6 = fig.add_subplot(gs[2, 2])
        self._plot_trade_clustering(ax6)
        
        plt.tight_layout()
        return fig

    def _plot_equity_curve_with_drawdown(self, ax):
        """Plot equity curve with drawdown overlay"""
        cumulative_returns = (1 + self.trades_df['return']).cumprod()
        drawdown = self.calculate_drawdown_series()
        
        ax.plot(cumulative_returns.index, cumulative_returns.values, 'b-', label='Equity')
        ax2 = ax.twinx()
        ax2.fill_between(drawdown.index, drawdown.values, 0, color='r', alpha=0.3, label='Drawdown')
        ax.set_title('Equity Curve with Drawdown')
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')

    def _plot_return_distribution(self, ax):
        """Plot return distribution with normal distribution overlay"""
        sns.histplot(self.trades_df['return'], kde=True, ax=ax)
        ax.axvline(x=0, color='r', linestyle='--')
        ax.set_title('Return Distribution')

    def _plot_rolling_sharpe(self, ax):
        """Plot rolling Sharpe ratio"""
        window = min(60, len(self.trades_df))
        rolling_sharpe = self.trades_df['return'].rolling(window=window).apply(
            lambda x: self.calculate_sharpe_ratio(x))
        ax.plot(rolling_sharpe.index, rolling_sharpe.values)
        ax.set_title(f'Rolling Sharpe Ratio ({window} periods)')

    def _plot_rolling_volatility(self, ax):
        """Plot rolling volatility"""
        window = min(30, len(self.trades_df))
        rolling_vol = self.trades_df['return'].rolling(window=window).std() * np.sqrt(252)
        ax.plot(rolling_vol.index, rolling_vol.values)
        ax.set_title(f'Rolling Volatility ({window} periods)')

    def _plot_monthly_returns_heatmap(self, ax):
        """Plot enhanced monthly returns heatmap"""
        monthly_returns = self.trades_df.set_index('entry_date')['return'].resample('M').sum()
        monthly_returns = monthly_returns.unstack()
        sns.heatmap(monthly_returns, ax=ax, cmap='RdYlGn', center=0)
        ax.set_title('Monthly Returns Heatmap')

    def _plot_trade_clustering(self, ax):
        """Plot trade clustering analysis"""
        trade_times = pd.Series(self.trades_df['entry_date'].dt.hour)
        trade_times.value_counts().plot(kind='bar', ax=ax)
        ax.set_title('Trade Entry Time Distribution')
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Number of Trades')

    def calculate_drawdown_series(self):
        """Calculate drawdown series for plotting"""
        cum_returns = (1 + self.trades_df['return']).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = (cum_returns - rolling_max) / rolling_max
        return drawdowns 