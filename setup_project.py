import os
import shutil

def create_directory_structure():
    # Project root directory
    root_dir = "trading_bot"
    
    # Directory structure
    directories = [
        "app",
        "app/config",
        "app/core",
        "app/ui",
        "app/ui/dialogs",
        "app/utils",
        "app/services",
        "tests",
        "docs"
    ]
    
    # Create directories
    for dir_path in directories:
        full_path = os.path.join(root_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        
        # Create __init__.py in each Python package directory
        if "app" in dir_path:
            init_file = os.path.join(full_path, "__init__.py")
            open(init_file, "a").close()

    # Move existing files to their new locations
    file_moves = {
        "main.py": "app/main.py",
        "bot2.py": "app/core/bot.py",
        "layouts.py": "app/ui/layouts.py",
        "styles.py": "app/ui/styles.py",
        "login_dialog.py": "app/ui/dialogs/login_dialog.py",
        "trading_dialog.py": "app/ui/dialogs/trading_dialog.py",
        "strategy_dialog.py": "app/ui/dialogs/strategy_dialog.py",
        "forex_utils.py": "app/utils/forex_utils.py",
        "config.py": "app/config/config.py",
        "credentials.json": "app/config/credentials.json",
        "market_analysis.py": "app/core/market_analysis.py",
        "performance_analytics.py": "app/core/performance_analytics.py"
    }
    
    for src, dst in file_moves.items():
        if os.path.exists(src):
            shutil.move(src, os.path.join(root_dir, dst))

    # Create run.py in root directory
    with open(os.path.join(root_dir, "run.py"), "w") as f:
        f.write("""import sys
import os

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.main import main

if __name__ == "__main__":
    main()
""")

    # Create requirements.txt
    with open(os.path.join(root_dir, "requirements.txt"), "w") as f:
        f.write("""PyQt5>=5.15.0
pandas>=1.3.0
numpy>=1.19.0
matplotlib>=3.4.0
oandapyV20>=0.7.2
alpaca-trade-api>=2.0.0
pandas-ta>=0.3.0
""")

    # Create README.md
    with open(os.path.join(root_dir, "docs", "README.md"), "w") as f:
        f.write("""# Trading Bot

A professional trading bot with GUI interface for forex and stock trading.

## Setup

1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your API credentials in app/config/credentials.json

3. Run the application:
   ```bash
   python run.py
   ```

## Features

- Real-time market data
- Multiple trading strategies
- Risk management
- Performance analytics
- Mobile-responsive UI
""")

if __name__ == "__main__":
    create_directory_structure()
    print("Project structure created successfully!") 