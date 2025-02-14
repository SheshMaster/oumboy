import sys
import os

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from main import TradingBotApp
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    window = TradingBotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
