import sys
import os
from pathlib import Path

# Get absolute paths
project_root = Path(__file__).parent.absolute()  # Current directory (trading_bot)
app_dir = project_root / "app"
sys.path.insert(0, str(app_dir))

print("Python Path:")
for path in sys.path:
    print(f"- {path}")

from app.main import TradingBotApp
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = TradingBotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
