from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, 
                           QWidget, QLabel, QPushButton, QLineEdit,
                           QComboBox, QTableWidget, QFrame, QGroupBox, QCheckBox, QTableWidgetItem, QTabWidget)
from PyQt5.QtCore import Qt, QDateTime, QSize
from PyQt5.QtGui import QBrush, QColor, QPainter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd

# Use relative imports
from .theme import (
    COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, 
    TABLE_STYLE, LABEL_STYLE, GROUP_BOX_STYLE
)
from ..utils.device_detector import DeviceDetector

plt.style.use('dark_background')

class MainLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.is_mobile = DeviceDetector.is_mobile()
        self.screen_size = DeviceDetector.get_screen_size()
        
        # Initialize attributes
        self.pair_combo = QComboBox()
        self.strategy_combo = QComboBox()
        self.timeframe_combo = QComboBox()
        self.balance_label = QLabel()
        self.account_type = QLabel()
        self.market_table = QTableWidget()
        
        # Initialize matplotlib figure
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        self.setup_responsive_layout()
        
    def create_left_panel(self):
        """Create left panel with trading controls"""
        layout = QVBoxLayout()
        
        # Strategy selection
        strategy_group = QGroupBox("Trading Strategy")
        strategy_group.setStyleSheet(GROUP_BOX_STYLE)
        strategy_layout = QVBoxLayout()
        
        # Add trading pairs combo
        self.pair_combo.addItems(['EUR/USD', 'GBP/USD', 'USD/JPY'])
        strategy_layout.addWidget(QLabel("Trading Pair:"))
        strategy_layout.addWidget(self.pair_combo)
        
        # Add strategy combo
        self.strategy_combo.addItems(['Trend Following', 'Mean Reversion', 'Breakout'])
        strategy_layout.addWidget(QLabel("Strategy:"))
        strategy_layout.addWidget(self.strategy_combo)
        
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        return layout
        
    def create_chart_area(self):
        """Create central chart area"""
        layout = QVBoxLayout()
        
        # Add timeframe selection
        timeframe_layout = QHBoxLayout()
        self.timeframe_combo.addItems(['1m', '5m', '15m', '1h', '4h', '1d'])
        timeframe_layout.addWidget(QLabel("Timeframe:"))
        timeframe_layout.addWidget(self.timeframe_combo)
        layout.addLayout(timeframe_layout)
        
        # Add chart
        layout.addWidget(self.canvas)
        
        return layout
        
    def create_right_panel(self):
        """Create right panel with account info"""
        layout = QVBoxLayout()
        
        # Account info group
        account_group = QGroupBox("Account Info")
        account_group.setStyleSheet(GROUP_BOX_STYLE)
        account_layout = QVBoxLayout()
        
        self.balance_label.setText("Balance: $0.00")
        self.account_type.setText("Account Type: Demo")
        
        account_layout.addWidget(self.balance_label)
        account_layout.addWidget(self.account_type)
        
        account_group.setLayout(account_layout)
        layout.addWidget(account_group)
        
        # Market data table
        market_group = QGroupBox("Market Data")
        market_group.setStyleSheet(GROUP_BOX_STYLE)
        market_layout = QVBoxLayout()
        
        self.market_table.setColumnCount(4)
        self.market_table.setHorizontalHeaderLabels(['Symbol', 'Price', 'Change', 'Volume'])
        self.market_table.setStyleSheet(TABLE_STYLE)
        
        market_layout.addWidget(self.market_table)
        market_group.setLayout(market_layout)
        layout.addWidget(market_group)
        
        return layout
        
    def add_header(self, mobile=False):
        """Add header section"""
        header_layout = QHBoxLayout()
        title = QLabel("Trading Bot Dashboard")
        title.setFont(FONTS['header_mobile' if mobile else 'header'])
        title.setStyleSheet(LABEL_STYLE)
        header_layout.addWidget(title)
        self.addLayout(header_layout)
        
    def add_footer(self):
        """Add footer section"""
        footer_layout = QHBoxLayout()
        status_label = QLabel("Status: Ready")
        status_label.setStyleSheet(LABEL_STYLE)
        footer_layout.addWidget(status_label)
        self.addLayout(footer_layout)
        
    def get_mobile_tab_style(self):
        """Get style for mobile tabs"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['text_secondary']};
                background: {COLORS['surface']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background: {COLORS['background']};
                color: {COLORS['text']};
                padding: 12px;
                margin: 2px;
                border-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
            }}
        """

    def setup_responsive_layout(self):
        """Setup layout based on device type"""
        self.setSpacing(20 if not self.is_mobile else 10)
        self.setContentsMargins(
            *(20 if not self.is_mobile else 10 for _ in range(4))
        )
        
        # Create panels
        left_panel = self.create_left_panel()
        center_panel = self.create_chart_area()
        right_panel = self.create_right_panel()
        
        if self.is_mobile:
            # Mobile layout: Stack panels vertically
            self.add_header(mobile=True)
            self.addLayout(center_panel, 2)  # Chart gets more space
            
            # Create tab widget for panels
            tabs = QTabWidget()
            tabs.setStyleSheet(self.get_mobile_tab_style())
            
            # Add panels as tabs
            left_tab = QWidget()
            left_tab.setLayout(left_panel)
            tabs.addTab(left_tab, "Strategy")
            
            right_tab = QWidget()
            right_tab.setLayout(right_panel)
            tabs.addTab(right_tab, "Account")
            
            self.addWidget(tabs, 1)
        else:
            # Desktop layout: Horizontal arrangement
            main_content = QHBoxLayout()
            main_content.addLayout(left_panel, 1)
            main_content.addLayout(center_panel, 2)
            main_content.addLayout(right_panel, 1)
            
            self.add_header(mobile=False)
            self.addLayout(main_content)
            
        self.add_footer()

    # ... rest of your MainLayout class methods ... 