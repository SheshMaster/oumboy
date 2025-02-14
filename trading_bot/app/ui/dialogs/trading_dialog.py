from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QListWidget, QGroupBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush
from styles import COLORS, FONTS, BUTTON_STYLE, TABLE_STYLE, GROUP_BOX_STYLE, LABEL_STYLE

class InstrumentDialog(QDialog):
    def __init__(self, parent=None, exchange_type='forex'):
        super().__init__(parent)
        self.exchange_type = exchange_type
        self.selected_instrument = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Select Trading Instrument")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"background-color: {COLORS['background']}")
        
        layout = QHBoxLayout(self)
        
        # Left panel - Instrument list
        left_panel = QGroupBox("Available Instruments")
        left_panel.setStyleSheet(GROUP_BOX_STYLE)
        left_layout = QVBoxLayout()
        
        self.instrument_list = QListWidget()
        self.instrument_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border: 1px solid {COLORS['text_secondary']};
                border-radius: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['primary']};
            }}
        """)
        
        # Add instruments based on exchange type
        if self.exchange_type == 'forex':
            self.instrument_list.addItems([
                'EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF',
                'AUD/USD', 'USD/CAD', 'NZD/USD'
            ])
        else:
            # Add stock symbols for Alpaca
            self.instrument_list.addItems([
                'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA'
            ])
            
        self.instrument_list.currentItemChanged.connect(self.update_instrument_info)
        left_layout.addWidget(self.instrument_list)
        left_panel.setLayout(left_layout)
        
        # Right panel - Instrument details
        right_panel = QVBoxLayout()
        
        # Instrument info
        info_group = QGroupBox("Instrument Information")
        info_group.setStyleSheet(GROUP_BOX_STYLE)
        info_layout = QVBoxLayout()
        
        # Create tabs for different types of information
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {COLORS['text_secondary']};
                background: {COLORS['surface']};
            }}
            QTabBar::tab {{
                background: {COLORS['background']};
                color: {COLORS['text']};
                padding: 8px 12px;
                border: 1px solid {COLORS['text_secondary']};
            }}
            QTabBar::tab:selected {{
                background: {COLORS['primary']};
            }}
        """)
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        self.overview_table = QTableWidget(5, 2)
        self.overview_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.overview_table.setStyleSheet(TABLE_STYLE)
        overview_layout.addWidget(self.overview_table)
        overview_tab.setLayout(overview_layout)
        
        # Technical tab
        technical_tab = QWidget()
        technical_layout = QVBoxLayout()
        self.technical_table = QTableWidget(5, 2)
        self.technical_table.setHorizontalHeaderLabels(["Indicator", "Value"])
        self.technical_table.setStyleSheet(TABLE_STYLE)
        technical_layout.addWidget(self.technical_table)
        technical_tab.setLayout(technical_layout)
        
        tabs.addTab(overview_tab, "Overview")
        tabs.addTab(technical_tab, "Technical")
        info_layout.addWidget(tabs)
        info_group.setLayout(info_layout)
        right_panel.addWidget(info_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.select_button = QPushButton("Select & Continue")
        self.select_button.setStyleSheet(BUTTON_STYLE)
        self.select_button.clicked.connect(self.accept)
        self.select_button.setEnabled(False)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(BUTTON_STYLE)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.select_button)
        button_layout.addWidget(cancel_button)
        right_panel.addLayout(button_layout)
        
        # Add panels to main layout
        layout.addWidget(left_panel, 1)
        layout.addLayout(right_panel, 2)
        
    def update_instrument_info(self, current, previous):
        """Update instrument information when selection changes"""
        if current is None:
            return
            
        self.selected_instrument = current.text()
        self.select_button.setEnabled(True)
        
        # Update overview table
        overview_data = [
            ("Symbol", self.selected_instrument),
            ("Bid", "1.2345"),
            ("Ask", "1.2347"),
            ("Spread", "0.0002"),
            ("Daily Change", "+0.05%")
        ]
        
        for i, (metric, value) in enumerate(overview_data):
            self.overview_table.setItem(i, 0, QTableWidgetItem(metric))
            self.overview_table.setItem(i, 1, QTableWidgetItem(value))
            
        # Update technical table
        technical_data = [
            ("RSI", "45.5"),
            ("MACD", "0.0023"),
            ("MA(20)", "1.2340"),
            ("BB Upper", "1.2400"),
            ("BB Lower", "1.2300")
        ]
        
        for i, (indicator, value) in enumerate(technical_data):
            self.technical_table.setItem(i, 0, QTableWidgetItem(indicator))
            self.technical_table.setItem(i, 1, QTableWidgetItem(value)) 