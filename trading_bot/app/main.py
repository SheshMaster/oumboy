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
from PyQt5.QtCore import Qt, QTimer
from layouts import MainLayout
from styles import (
    MAIN_WINDOW_STYLE, 
    BUTTON_STYLE,
    COLORS
)
from login_dialog import LoginDialog
import bot2  # Import your trading bot
from forex_utils import ForexCalculator
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QProcess
from oandapyV20.endpoints.accounts import AccountSummary
from trading_dialog import InstrumentDialog
from strategy_dialog import StrategyDialog
from PyQt5.QtCore import QSize, QRect
from PyQt5.QtWidgets import QDesktopWidget

class DeviceDetector:
    @staticmethod
    def is_mobile():
        """Detect if running on mobile device"""
        screen = QDesktopWidget().screenGeometry()
        width = screen.width()
        height = screen.height()
        
        # Check screen dimensions and aspect ratio
        is_mobile = (width < 800 or height < 600) or (height > width)
        return is_mobile
        
    @staticmethod
    def get_screen_size():
        """Get current screen dimensions"""
        screen = QDesktopWidget().screenGeometry()
        return QSize(screen.width(), screen.height())

class TradingBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.bot = None
        self.main_layout = None
        self.connection_status = False
        self.is_mobile = DeviceDetector.is_mobile()
        self.screen_size = DeviceDetector.get_screen_size()
        
        # Adjust window size based on device
        if self.is_mobile:
            self.setWindowState(Qt.WindowMaximized)
        else:
            self.resize(1200, 800)
        
        # Show loading screen
        self.show_loading("Initializing Trading Bot...")
        
        # Show login dialog first
        login_dialog = LoginDialog(self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.credentials = login_dialog.get_credentials()
            self.setup_main_window()
            self.setup_forex_updates()
            # Start connection monitoring after setup is complete
            self.setup_connection_monitor()
        else:
            sys.exit()
            
    def setup_main_window(self):
        """Setup main window and initialize bot"""
        try:
            self.setWindowTitle("Trading Bot Dashboard")
            self.setStyleSheet(MAIN_WINDOW_STYLE)
            
            # Create central widget and set main layout
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create main layout
            self.main_layout = MainLayout()
            central_widget.setLayout(self.main_layout)
            
            # Connect buttons
            self.connect_signals()
            
            # Initialize bot with credentials
            self.initialize_bot()
            
            # Start market data updates
            self.setup_market_updates()
            
        except Exception as e:
            QMessageBox.critical(self, "Setup Error", f"Error setting up main window: {str(e)}")
            sys.exit()
        
    def connect_signals(self):
        """Connect button signals"""
        self.main_layout.start_bot_button.clicked.connect(self.show_instrument_dialog)
        self.main_layout.get_stop_button().clicked.connect(self.stop_bot)
        self.main_layout.get_restart_button().clicked.connect(self.restart_app)
    
    def start_bot(self):
        """Start the trading bot"""
        try:
            self.show_loading("Starting trading bot...")
            
            def init_bot():
                bot = bot2.TradingBot(self.credentials)
                bot.start()
                return bot
            
            with ThreadPoolExecutor() as executor:
                future = executor.submit(init_bot)
                self.bot = future.result(timeout=30)
            
            self.setup_main_window()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error starting bot: {str(e)}")
            
    def stop_bot(self):
        """Stop the trading bot"""
        try:
            if self.bot:
                self.bot.stop()
                self.main_layout.update_status("Stopped", COLORS['warning'])
                # Disable stop button and enable start button
                self.main_layout.get_stop_button().setEnabled(False)
                self.main_layout.get_start_button().setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error stopping bot: {str(e)}")
    
    def setup_forex_updates(self):
        """Setup real-time forex updates"""
        self.forex_calculator = ForexCalculator()
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_forex_data)
        self.update_timer.start(5000)  # Update every 5 seconds instead of every second
    
    def update_forex_data(self):
        """Update forex prices and calculations"""
        try:
            if hasattr(self, 'bot') and self.bot and hasattr(self, 'main_layout'):
                # Get current pair
                current_pair = self.main_layout.pair_combo.currentText()
                
                # Get current data
                current_data = self.bot.get_current_data(current_pair)
                if current_data is not None:
                    # Update chart
                    self.main_layout.update_chart(current_data)
                    
                    # Update account info
                    account_info = self.bot.get_account_info()
                    if account_info:
                        self.main_layout.update_account_info(
                            balance=account_info['balance'],
                            account_type=self.credentials['exchange'].upper(),
                            status="Connected",
                            free_margin=account_info['margin_available'],
                            open_pl=account_info['unrealized_pl'],
                            daily_pl=account_info['daily_pl'],
                            positions=account_info['positions']
                        )
        except Exception as e:
            print(f"Error updating forex data: {str(e)}")
    
    def update_positions_table(self, current_data):
        """Update positions table with pip values"""
        table = self.main_layout.get_positions_table()
        table.setRowCount(len(self.bot.position_manager.positions))
        
        for i, (symbol, pos) in enumerate(self.bot.position_manager.positions.items()):
            # Calculate pip difference
            pips = self.forex_calculator.pips_difference(
                symbol,
                pos['entry_price'],
                current_data['close']
            )
            
            # Calculate P/L
            pip_value = self.forex_calculator.calculate_pip_value(
                symbol,
                pos['size']
            )
            pl_usd = pips * pip_value * (1 if pos['side'] == 'buy' else -1)
            
            # Update table
            table.setItem(i, 0, QTableWidgetItem(symbol))
            table.setItem(i, 1, QTableWidgetItem(pos['side'].upper()))
            table.setItem(i, 2, QTableWidgetItem(str(pos['size'])))
            table.setItem(i, 3, QTableWidgetItem(f"{pos['entry_price']:.5f}"))
            table.setItem(i, 4, QTableWidgetItem(f"${pl_usd:.2f}"))
            table.setItem(i, 5, QTableWidgetItem(f"{pips:.1f}"))

    def show_loading(self, message):
        """Show loading message"""
        loading = QLabel(message)
        loading.setStyleSheet(f"""
            color: {COLORS['text']};
            background-color: {COLORS['background']};
            padding: 20px;
            border-radius: 10px;
            font-size: 16px;
        """)
        loading.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(loading)
        self.resize(400, 100)
        self.show()
        QApplication.processEvents()

    def restart_app(self):
        """Restart the application"""
        try:
            if self.bot:
                self.stop_bot()
            QApplication.quit()
            status = QProcess.startDetached(sys.executable, sys.argv)
            if not status:
                QMessageBox.warning(self, "Error", "Could not restart application")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error restarting app: {str(e)}")

    def update_account_info(self):
        """Update account information"""
        try:
            if self.bot and self.bot.exchange:
                # Get account info from OANDA
                account_info = self.bot.get_account_info()
                if account_info:
                    # Update labels in the right panel
                    self.main_layout.update_account_info(
                        balance=account_info['balance'],
                        equity=account_info['equity'],
                        margin=account_info['margin_rate'],
                        free_margin=account_info['margin_available'],
                        open_pl=account_info['unrealized_pl'],
                        daily_pl=account_info['daily_pl'],
                        positions=len(self.bot.position_manager.positions)
                    )
        except Exception as e:
            print(f"Error updating account info: {str(e)}")

    def setup_connection_monitor(self):
        """Setup connection status monitoring"""
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_connection_status)
        self.status_timer.start(30000)  # Check every 30 seconds
        
    def initialize_bot(self):
        """Initialize the trading bot"""
        try:
            self.bot = bot2.TradingBot(self.credentials)
            # Update initial connection status
            if self.check_connection_status():
                self.main_layout.update_status(
                    "Connected", 
                    COLORS['success']
                )
                QMessageBox.information(
                    self,
                    "Connection Success",
                    f"Successfully connected to {self.credentials['exchange'].upper()} account!"
                )
            else:
                self.main_layout.update_status(
                    "Disconnected", 
                    COLORS['danger']
                )
        except Exception as e:
            self.main_layout.update_status(
                "Connection Failed", 
                COLORS['danger']
            )
            QMessageBox.warning(
                self,
                "Warning", 
                f"Could not initialize bot: {str(e)}\nSome features may be limited."
            )

    def check_connection_status(self):
        """Check if still connected to exchange"""
        try:
            if not hasattr(self, 'bot') or not self.bot:
                self.main_layout.update_status("Disconnected", COLORS['danger'])
                return False
                
            if not hasattr(self, 'main_layout'):
                return False
                
            if self.credentials['exchange'] == 'oanda':
                r = AccountSummary(accountID=self.credentials['account_id'])
                response = self.bot.exchange.request(r)
                # Get account details for display
                account = response.get('account', {})
                
                self.connection_status = True
                self.main_layout.update_status("Connected", COLORS['success'])
                self.main_layout.update_account_info(
                    balance=float(account.get('balance', 0)),
                    account_type=self.credentials['exchange'].upper(),
                    status="Connected",
                    free_margin=float(account.get('marginAvailable', 0)),
                    open_pl=float(account.get('unrealizedPL', 0)),
                    daily_pl=float(account.get('pl', 0)),
                    positions=len(account.get('positions', []))
                )
            else:
                account = self.bot.exchange.get_account()
                self.connection_status = True
                self.main_layout.update_status("Connected", COLORS['success'])
                self.main_layout.update_account_info(
                    balance=float(account.cash),
                    account_type=self.credentials['exchange'].upper(),
                    status="Connected",
                    free_margin=float(account.buying_power),
                    open_pl=float(account.unrealized_pl),
                    daily_pl=float(account.equity) - float(account.last_equity),
                    positions=len(self.bot.exchange.list_positions())
                )
                
            return True
                
        except Exception as e:
            print(f"Connection lost: {str(e)}")
            self.connection_status = False
            if hasattr(self, 'main_layout'):
                self.main_layout.update_status("Disconnected", COLORS['danger'])
            return False

    def update_connection_status(self, connected, details=""):
        """Update UI connection status"""
        if not hasattr(self, 'main_layout'):
            return  # Skip update if main_layout isn't ready
            
        status_text = "Connected" if connected else "Disconnected"
        if connected and details:
            status_text = f"Connected - {details}"
        status_color = COLORS['success'] if connected else COLORS['danger']
        
        # Update status in footer
        self.main_layout.update_status(status_text, status_color)
        
        # Update window title to show connection status
        self.setWindowTitle(f"Trading Bot Dashboard - {status_text}")
        
        # If disconnected, show reconnect dialog
        if not connected:
            self.show_reconnect_dialog()
            
    def show_reconnect_dialog(self):
        """Show reconnection dialog"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("Connection Lost")
        msg.setInformativeText("Would you like to reconnect?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        
        if msg.exec_() == QMessageBox.Yes:
            self.reconnect()
            
    def reconnect(self):
        """Attempt to reconnect"""
        try:
            self.stop_bot()
            self.start_bot()
        except Exception as e:
            QMessageBox.critical(self, "Reconnection Failed", 
                f"Could not reconnect: {str(e)}\n\nPlease check your connection and try again.")

    def setup_market_updates(self):
        """Setup periodic market data updates"""
        self.market_timer = QTimer()
        self.market_timer.timeout.connect(self.update_market_data)
        self.market_timer.start(5000)  # Update every 5 seconds
        
    def update_market_data(self):
        """Update market data display"""
        try:
            if self.bot and self.bot.exchange:
                # Get account info
                account_info = self.bot.get_account_info()
                if account_info:
                    self.main_layout.update_account_info(
                        balance=account_info['balance'],
                        account_type=self.credentials['exchange'].upper(),
                        status="Connected"
                    )
                
                # Get market data
                market_data = self.bot.get_market_data()
                if market_data:
                    self.main_layout.update_market_data(market_data)
                    
        except Exception as e:
            print(f"Error updating market data: {str(e)}")

    def show_instrument_dialog(self):
        """Show the instrument selection dialog"""
        dialog = InstrumentDialog(self, self.credentials['exchange'])
        if dialog.exec_() == QDialog.Accepted:
            selected_instrument = dialog.selected_instrument
            if selected_instrument:
                self.show_strategy_selection(selected_instrument)
                
    def show_strategy_selection(self, instrument):
        """Show strategy selection dialog"""
        dialog = StrategyDialog(self, instrument)
        if dialog.exec_() == QDialog.Accepted:
            selected_strategy = dialog.selected_strategy
            if selected_strategy:
                self.start_trading(instrument, selected_strategy)
                
    def start_trading(self, instrument, strategy):
        """Start trading with selected instrument and strategy"""
        try:
            # Initialize trading parameters
            self.bot.set_trading_parameters(
                instrument=instrument,
                strategy=strategy
            )
            
            # Show success message
            QMessageBox.information(
                self,
                "Trading Started",
                f"Started trading {instrument} using {strategy} strategy.\n\n"
                f"Monitor the dashboard for updates."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to start trading: {str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TradingBotApp()
    window.show()
    sys.exit(app.exec_()) 