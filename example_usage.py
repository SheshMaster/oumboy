import pandas as pd
import datetime
import matplotlib.pyplot as plt

# Create sample trade data
sample_trades = {
    'entry_date': [
        datetime.datetime(2024, 1, 1, 10, 30),
        datetime.datetime(2024, 1, 2, 14, 15),
        datetime.datetime(2024, 1, 3, 9, 45)
    ],
    'exit_date': [
        datetime.datetime(2024, 1, 1, 15, 45),
        datetime.datetime(2024, 1, 2, 16, 30),
        datetime.datetime(2024, 1, 3, 11, 00)
    ],
    'pnl': [100, -50, 75],  # Profit/Loss for each trade
    'return': [0.01, -0.005, 0.0075]  # Return percentage for each trade
}

# Create DataFrame
trades_df = pd.DataFrame(sample_trades)

# Initialize the analyzer
from performance_analytics import PerformanceAnalyzer
analyzer = PerformanceAnalyzer(trades_df)

# Print metrics
for metric, value in analyzer.metrics.items():
    print(f"{metric}: {value}")

# Generate and show plots
fig = analyzer.plot_performance()
plt.show() 