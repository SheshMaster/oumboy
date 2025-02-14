# Old imports
from layouts import MainLayout
from styles import MAIN_WINDOW_STYLE, BUTTON_STYLE, COLORS
from login_dialog import LoginDialog
import bot2

# New imports
from ui.layouts import MainLayout
from ui.styles import MAIN_WINDOW_STYLE, BUTTON_STYLE, COLORS
from ui.dialogs.login_dialog import LoginDialog
from core.bot import TradingBot  # Note: bot2.py is now bot.py
from utils.forex_utils import ForexCalculator
from utils.device_detector import DeviceDetector 