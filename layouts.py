from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, 
                           QWidget, QLabel, QPushButton, QLineEdit,
                           QComboBox, QTableWidget, QFrame, QGroupBox, QCheckBox, QTableWidgetItem)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QBrush, QColor, QPainter
from styles import (
    COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, 
    TABLE_STYLE, LABEL_STYLE, GROUP_BOX_STYLE
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
plt.style.use('dark_background')  # Style sombre pour correspondre au thème

class MainLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.setSpacing(20)
        self.setContentsMargins(20, 20, 20, 20)
        
        # Add header with account info
        self.add_header()
        
        # Market data table
        self.add_market_data_table()
        
        # Control buttons
        self.add_control_buttons()
        
        # Start bot button
        self.add_start_section()
        
        # Add footer with status
        self.add_footer()
        
    def add_header(self):
        header = QHBoxLayout()
        
        # Account info section
        account_info = QGroupBox("Account Information")
        account_info.setStyleSheet(GROUP_BOX_STYLE)
        account_layout = QGridLayout()
        
        # Account balance
        self.balance_label = QLabel("Balance: $0.00")
        self.balance_label.setStyleSheet(LABEL_STYLE)
        self.balance_label.setFont(FONTS['header'])
        
        # Account type
        self.account_type = QLabel("Account Type: --")
        self.account_type.setStyleSheet(LABEL_STYLE)
        
        # Account status
        self.account_status = QLabel("Status: Not Connected")
        self.account_status.setStyleSheet(LABEL_STYLE)
        
        account_layout.addWidget(self.balance_label, 0, 0)
        account_layout.addWidget(self.account_type, 1, 0)
        account_layout.addWidget(self.account_status, 2, 0)
        account_info.setLayout(account_layout)
        
        header.addWidget(account_info)
        self.addLayout(header)
        
    def add_market_data_table(self):
        market_group = QGroupBox("Market Overview")
        market_group.setStyleSheet(GROUP_BOX_STYLE)
        market_layout = QVBoxLayout()
        
        # Create market data table
        self.market_table = QTableWidget(0, 4)
        self.market_table.setHorizontalHeaderLabels([
            "Symbol", "Price", "Change", "Volume"
        ])
        self.market_table.setStyleSheet(TABLE_STYLE)
        self.market_table.horizontalHeader().setStretchLastSection(True)
        
        market_layout.addWidget(self.market_table)
        market_group.setLayout(market_layout)
        self.addWidget(market_group)
        
    def add_control_buttons(self):
        """Add control buttons section"""
        buttons_layout = QHBoxLayout()
        
        # Create control buttons
        self.start_button = QPushButton("Start Trading")
        self.stop_button = QPushButton("Stop Trading")
        self.restart_button = QPushButton("Restart")
        
        # Style buttons
        self.start_button.setStyleSheet(BUTTON_STYLE)
        self.stop_button.setStyleSheet(BUTTON_STYLE)
        self.restart_button.setStyleSheet(BUTTON_STYLE)
        
        # Initially disable stop button
        self.stop_button.setEnabled(False)
        
        # Add buttons to layout
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.restart_button)
        
        # Add buttons layout to main layout
        self.addLayout(buttons_layout)

    def add_start_section(self):
        start_layout = QHBoxLayout()
        
        self.start_bot_button = QPushButton("Start Trading Bot")
        self.start_bot_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 15px 32px;
                font-size: 16px;
                border-radius: 10px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        
        start_layout.addWidget(self.start_bot_button, alignment=Qt.AlignCenter)
        self.addLayout(start_layout)
        
    def update_account_info(self, balance, account_type, status):
        """Update account information display"""
        self.balance_label.setText(f"Balance: ${balance:,.2f}")
        self.account_type.setText(f"Account Type: {account_type}")
        
        # Set status color based on connection state
        status_color = COLORS['success'] if status.lower() == 'connected' else COLORS['danger']
        self.update_status(status, status_color)
        
    def update_market_data(self, market_data):
        """Update market data table"""
        self.market_table.setRowCount(len(market_data))
        for row, data in enumerate(market_data):
            self.market_table.setItem(row, 0, QTableWidgetItem(data['symbol']))
            self.market_table.setItem(row, 1, QTableWidgetItem(f"${data['price']:.2f}"))
            
            # Color code the change column
            change_item = QTableWidgetItem(f"{data['change']:.2f}%")
            change_item.setForeground(
                QBrush(QColor("#2ecc71" if data['change'] >= 0 else "#e74c3c"))
            )
            self.market_table.setItem(row, 2, change_item)
            
            self.market_table.setItem(row, 3, QTableWidgetItem(f"{data['volume']:,}"))

    def create_left_panel(self):
        layout = QVBoxLayout()
        
        # Strategy selection
        strategy_group = QGroupBox("Strategy")
        strategy_group.setStyleSheet(GROUP_BOX_STYLE)
        strategy_layout = QVBoxLayout()
        
        # Add currency pair selection
        pair_label = QLabel("Currency Pair:")
        pair_label.setStyleSheet(LABEL_STYLE)
        self.pair_combo = QComboBox()
        self.pair_combo.addItems([
            'EUR_USD', 'GBP_USD', 'USD_JPY', 'USD_CHF',
            'AUD_USD', 'USD_CAD', 'NZD_USD'
        ])
        self.pair_combo.setStyleSheet(INPUT_STYLE)
        strategy_layout.addWidget(pair_label)
        strategy_layout.addWidget(self.pair_combo)
        
        # Strategy combo
        strategy_label = QLabel("Strategy:")
        strategy_label.setStyleSheet(LABEL_STYLE)
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "Position Trading", 
            "Swing Trading", 
            "Day Trading",
            "Scalping"
        ])
        self.strategy_combo.setStyleSheet(INPUT_STYLE)
        strategy_layout.addWidget(strategy_label)
        strategy_layout.addWidget(self.strategy_combo)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # Parameters
        params_group = QGroupBox("Trading Parameters")
        params_layout = QGridLayout()
        params = [
            ("Risk per trade", "2%"),
            ("Stop Loss (pips)", "50"),
            ("Take Profit (pips)", "150"),
            ("Max Positions", "3"),
            ("Lot Size", "0.01")  # Add forex lot size
        ]
        for i, (label, value) in enumerate(params):
            label_widget = QLabel(label)
            label_widget.setStyleSheet(LABEL_STYLE)
            params_layout.addWidget(label_widget, i, 0)
            input_field = QLineEdit(value)
            input_field.setStyleSheet(INPUT_STYLE)
            params_layout.addWidget(input_field, i, 1)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Forex Indicators
        indicators_group = QGroupBox("Forex Indicators")
        indicators_group.setStyleSheet(GROUP_BOX_STYLE)
        indicators_layout = QVBoxLayout()
        
        # Add forex-specific indicators
        self.indicators = {
            'pivot_points': QCheckBox("Pivot Points"),
            'fibonacci': QCheckBox("Fibonacci Levels"),
            'ichimoku': QCheckBox("Ichimoku Cloud"),
            'momentum': QCheckBox("Momentum Index"),
            'atr': QCheckBox("ATR")
        }
        
        # Add checkbox style
        checkbox_style = f"""
            QCheckBox {{
                color: {COLORS['text']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS['text_secondary']};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS['primary']};
                border: 2px solid {COLORS['primary']};
            }}
        """
        
        for indicator in self.indicators.values():
            indicator.setStyleSheet(checkbox_style)
            indicators_layout.addWidget(indicator)
        
        indicators_group.setLayout(indicators_layout)
        layout.addWidget(indicators_group)
        
        # Controls
        self.controls = QVBoxLayout()
        self.start_button = QPushButton("Start Trading")
        self.stop_button = QPushButton("Stop Trading")
        self.restart_button = QPushButton("Restart App")
        self.start_button.setStyleSheet(BUTTON_STYLE)
        self.stop_button.setStyleSheet(BUTTON_STYLE)
        self.restart_button.setStyleSheet(BUTTON_STYLE)
        self.controls.addWidget(self.start_button)
        self.controls.addWidget(self.stop_button)
        self.controls.addWidget(self.restart_button)
        layout.addLayout(self.controls)
        
        layout.addStretch()
        return layout

    def create_chart_area(self):
        layout = QVBoxLayout()
        
        # Chart controls
        controls = QHBoxLayout()
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "1h", "4h", "1d"])
        self.timeframe_combo.setStyleSheet(INPUT_STYLE)
        controls.addWidget(self.timeframe_combo)
        
        self.indicator_combo = QComboBox()
        self.indicator_combo.addItems(["RSI", "MACD", "Bollinger Bands"])
        self.indicator_combo.setStyleSheet(INPUT_STYLE)
        controls.addWidget(self.indicator_combo)
        
        layout.addLayout(controls)
        
        # Create matplotlib figure
        self.figure = Figure(facecolor=COLORS['surface'])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(400)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(COLORS['surface'])
        
        # Style the plot
        self.ax.grid(True, alpha=0.2)
        self.ax.tick_params(colors=COLORS['text'])
        
        layout.addWidget(self.canvas)
        return layout

    def create_right_panel(self):
        layout = QVBoxLayout()
        
        # Portfolio summary
        portfolio_group = QGroupBox("Forex Account")
        portfolio_group.setStyleSheet(GROUP_BOX_STYLE)
        portfolio_layout = QGridLayout()
        metrics = [
            ("Balance", "$10,000"),
            ("Equity", "$10,500"),
            ("Margin", "25%"),
            ("Free Margin", "$7,500"),
            ("Open P/L", "+$500"),
            ("Daily P/L", "+2.5%"),
            ("Open Positions", "2")
        ]
        for i, (label, value) in enumerate(metrics):
            label_widget = QLabel(label)
            label_widget.setStyleSheet(LABEL_STYLE)
            portfolio_layout.addWidget(label_widget, i, 0)
            value_label = QLabel(value)
            value_label.setFont(FONTS['mono'])
            value_label.setStyleSheet(LABEL_STYLE)
            portfolio_layout.addWidget(value_label, i, 1)
        portfolio_group.setLayout(portfolio_layout)
        layout.addWidget(portfolio_group)
        
        # Open positions with pip values
        positions_group = QGroupBox("Open Positions")
        positions_group.setStyleSheet(GROUP_BOX_STYLE)
        positions_layout = QVBoxLayout()
        positions_table = QTableWidget(0, 6)  # Added columns for pips
        positions_table.setHorizontalHeaderLabels([
            "Pair", "Type", "Size", "Entry", "P/L ($)", "P/L (pips)"
        ])
        positions_table.setStyleSheet(TABLE_STYLE)
        positions_layout.addWidget(positions_table)
        positions_group.setLayout(positions_layout)
        layout.addWidget(positions_group)
        
        return layout

    @staticmethod
    def create_status_widget(label, status):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(5)
        
        indicator = QLabel()
        indicator.setStyleSheet(f"""
            background-color: {COLORS['success'] if status == 'active' else COLORS['warning']};
            border-radius: 5px;
            min-width: 10px;
            max-width: 10px;
            min-height: 10px;
            max-height: 10px;
        """)
        
        text = QLabel(label)
        text.setStyleSheet(f"color: {COLORS['text']}")
        
        layout.addWidget(indicator)
        layout.addWidget(text)
        widget.setLayout(layout)
        return widget

    def add_footer(self):
        footer = QHBoxLayout()
        
        # Add version info
        version = QLabel("v1.0.0")
        version.setStyleSheet(f"color: {COLORS['text_secondary']}")
        version.setFont(FONTS['small'])
        footer.addWidget(version)
        
        # Add connection status
        status = QLabel("Status: Disconnected")
        status.setObjectName("connection_status")
        status.setStyleSheet(f"color: {COLORS['danger']}")
        status.setFont(FONTS['small'])
        footer.addWidget(status)
        
        # Add status message
        message = QLabel("Ready")
        message.setStyleSheet(f"color: {COLORS['text_secondary']}")
        message.setFont(FONTS['small'])
        footer.addWidget(message, alignment=Qt.AlignRight)
        
        self.addLayout(footer)

    def get_start_button(self):
        """Return reference to start button"""
        return self.start_button

    def get_stop_button(self):
        """Return reference to stop button"""
        return self.stop_button

    def get_restart_button(self):
        """Return reference to restart button"""
        return self.restart_button

    def get_positions_table(self):
        """Get reference to positions table"""
        return self.positions_table  # Make sure to make positions_table an instance variable
    
    def get_pair_combo(self):
        """Get reference to currency pair combo box"""
        return self.pair_combo 

    def update_chart(self, df):
        """Update chart with new data"""
        try:
            print("Updating chart with data:", df.tail())  # Debug print
            
            if df is None or df.empty:
                print("No data to display")
                return
            
            self.ax.clear()
            
            # Plot candlesticks
            width = 0.6
            width2 = width * 0.8
            
            up = df[df.close >= df.open]
            down = df[df.close < df.open]
            
            # Plot up candles
            if not up.empty:
                self.ax.bar(up.index, up.close-up.open, width, bottom=up.open, color='green', alpha=0.8)
                self.ax.bar(up.index, up.high-up.close, width2, bottom=up.close, color='green', alpha=0.8)
                self.ax.bar(up.index, up.low-up.open, width2, bottom=up.open, color='green', alpha=0.8)
            
            # Plot down candles
            if not down.empty:
                self.ax.bar(down.index, down.close-down.open, width, bottom=down.open, color='red', alpha=0.8)
                self.ax.bar(down.index, down.high-down.open, width2, bottom=down.open, color='red', alpha=0.8)
                self.ax.bar(down.index, down.low-down.close, width2, bottom=down.close, color='red', alpha=0.8)
            
            # Add indicators if available
            if 'SMA20' in df.columns:
                self.ax.plot(df.index, df['SMA20'], color='blue', label='SMA20', alpha=0.7)
            if 'SMA50' in df.columns:
                self.ax.plot(df.index, df['SMA50'], color='yellow', label='SMA50', alpha=0.7)
            
            # Customize chart
            self.ax.set_title(f"{self.pair_combo.currentText()} - {self.timeframe_combo.currentText()}")
            self.ax.grid(True, alpha=0.2)
            self.ax.legend()
            
            # Format dates on x-axis
            self.ax.tick_params(axis='x', rotation=45)
            
            # Refresh canvas
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart: {str(e)}")
            import traceback
            traceback.print_exc()

    def update_account_info(self, balance, equity, margin, free_margin, open_pl, daily_pl, positions):
        """Update account information display"""
        try:
            # Update portfolio metrics
            metrics = {
                "Balance": f"${balance:,.2f}",
                "Equity": f"${equity:,.2f}",
                "Margin": f"{margin:.1f}%",
                "Free Margin": f"${free_margin:,.2f}",
                "Open P/L": f"{'+' if open_pl >= 0 else ''}{open_pl:,.2f}",
                "Daily P/L": f"{'+' if daily_pl >= 0 else ''}{daily_pl:,.1f}%",
                "Open Positions": str(positions)
            }
            
            # Find and update labels in the portfolio group
            portfolio_group = self.findChild(QGroupBox, "Forex Account")
            if portfolio_group:
                layout = portfolio_group.layout()
                for i, (label, value) in enumerate(metrics.items()):
                    value_label = layout.itemAtPosition(i, 1).widget()
                    if value_label:
                        value_label.setText(value)
                        if "P/L" in label:
                            color = COLORS['success'] if float(value.replace('+', '')) >= 0 else COLORS['error']
                            value_label.setStyleSheet(f"color: {color}")
        except Exception as e:
            print(f"Error updating account info: {str(e)}")

    def update_status(self, status_text, status_color):
        """Update connection status display"""
        # Find status label in header
        self.account_status.setText(f"Status: {status_text}")
        self.account_status.setStyleSheet(f"""
            QLabel {{
                color: {status_color};
                padding: 5px;
                border: 1px solid {status_color};
                border-radius: 4px;
                background-color: {COLORS['surface']};
            }}
        """)
        
        # Also update footer status if it exists
        status_label = self.findChild(QLabel, "connection_status")
        if status_label:
            status_label.setText(f"Status: {status_text}")
            status_label.setStyleSheet(f"""
                color: {status_color};
                padding: 5px;
                border: 1px solid {status_color};
                border-radius: 4px;
                background-color: {COLORS['surface']};
            """) 