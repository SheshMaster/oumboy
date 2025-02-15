import os
import shutil

def create_directory_structure():
    # Project root directory (one level up from trading_bot)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(root_dir, "app")
    
    # Create main directories
    directories = [
        os.path.join(app_dir),
        os.path.join(app_dir, "config"),
        os.path.join(app_dir, "core"),
        os.path.join(app_dir, "ui"),
        os.path.join(app_dir, "ui", "dialogs"),
        os.path.join(app_dir, "utils"),
        os.path.join(app_dir, "services"),
        os.path.join(root_dir, "tests"),
        os.path.join(root_dir, "docs")
    ]
    
    # Create directories and __init__.py files
    for dir_path in directories:
        os.makedirs(dir_path, exist_ok=True)
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                if dir_path == app_dir:
                    f.write("# Main app package\n")
                elif dir_path == os.path.join(app_dir, "ui"):
                    f.write("from .layouts import MainLayout\nfrom .styles import COLORS, FONTS, BUTTON_STYLE\n")
                elif dir_path == os.path.join(app_dir, "ui", "dialogs"):
                    f.write("from .login_dialog import LoginDialog\nfrom .trading_dialog import InstrumentDialog\nfrom .strategy_dialog import StrategyDialog\n")

    # File moves with explicit paths
    files_to_move = {
        "main.py": os.path.join(app_dir, "main.py"),
        "bot2.py": os.path.join(app_dir, "core", "bot.py"),
        "layouts.py": os.path.join(app_dir, "ui", "layouts.py"),
        "styles.py": os.path.join(app_dir, "ui", "styles.py"),
        "login_dialog.py": os.path.join(app_dir, "ui", "dialogs", "login_dialog.py"),
        "trading_dialog.py": os.path.join(app_dir, "ui", "dialogs", "trading_dialog.py"),
        "strategy_dialog.py": os.path.join(app_dir, "ui", "dialogs", "strategy_dialog.py"),
        "forex_utils.py": os.path.join(app_dir, "utils", "forex_utils.py"),
        "config.py": os.path.join(app_dir, "config", "config.py"),
        "credentials.json": os.path.join(app_dir, "config", "credentials.json"),
    }

    # Copy files to new locations
    for src_name, dst_path in files_to_move.items():
        src_path = os.path.join(root_dir, src_name)
        if os.path.exists(src_path):
            print(f"Copying {src_path} to {dst_path}")
            shutil.copy2(src_path, dst_path)
        else:
            print(f"Warning: Source file not found: {src_path}")

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