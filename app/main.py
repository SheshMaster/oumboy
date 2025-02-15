import sys
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget,
    QPushButton,
    QMessageBox,
    QDialog,
    QTableWidgetItem,
    QLabel
)
from PyQt5.QtCore import Qt, QTimer, QProcess

# Import from our app packages using relative imports
from .ui.layouts import MainLayout
from .ui.theme import MAIN_WINDOW_STYLE, BUTTON_STYLE, COLORS
from .ui.dialogs.login_dialog import LoginDialog
from .core.bot import TradingBot
from .utils.forex_utils import ForexCalculator
from .utils.device_detector import DeviceDetector
from .ui.dialogs.trading_dialog import InstrumentDialog
from .ui.dialogs.strategy_dialog import StrategyDialog

# Third party imports
from oandapyV20.endpoints.accounts import AccountSummary

class TradingBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Rest of your code...