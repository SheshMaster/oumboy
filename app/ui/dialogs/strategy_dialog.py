from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton,
    QGroupBox, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

# Fix the styles import
from ..theme import (
    COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, 
    GROUP_BOX_STYLE, LABEL_STYLE
)

class StrategyDialog(QDialog):
    def __init__(self, parent=None, instrument=None):
        super().__init__(parent)
        self.instrument = instrument
        self.selected_strategy = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Select Trading Strategy")
        self.setStyleSheet(f"background-color: {COLORS['background']}")
        
        layout = QVBoxLayout(self)
        
        # Strategy selection
        strategy_group = QGroupBox("Strategy Selection")
        strategy_group.setStyleSheet(GROUP_BOX_STYLE)
        strategy_layout = QVBoxLayout()
        
        # Strategy combo
        strategy_label = QLabel("Select Strategy:")
        strategy_label.setStyleSheet(LABEL_STYLE)
        self.strategy_combo = QComboBox()
        self.strategy_combo.setStyleSheet(INPUT_STYLE)
        self.strategy_combo.addItems([
            "Trend Following",
            "Mean Reversion",
            "Breakout Trading",
            "Grid Trading",
            "Scalping"
        ])
        
        strategy_layout.addWidget(strategy_label)
        strategy_layout.addWidget(self.strategy_combo)
        strategy_group.setLayout(strategy_layout)
        layout.addWidget(strategy_group)
        
        # Parameters group
        params_group = QGroupBox("Strategy Parameters")
        params_group.setStyleSheet(GROUP_BOX_STYLE)
        params_layout = QVBoxLayout()
        
        # Add parameters
        self.add_parameters(params_layout)
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet(BUTTON_STYLE)
        ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(BUTTON_STYLE)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def add_parameters(self, layout):
        """Add strategy parameters based on selected strategy"""
        # Risk per trade
        risk_label = QLabel("Risk per Trade (%):")
        risk_label.setStyleSheet(LABEL_STYLE)
        self.risk_spin = QDoubleSpinBox()
        self.risk_spin.setRange(0.1, 5.0)
        self.risk_spin.setValue(1.0)
        self.risk_spin.setStyleSheet(INPUT_STYLE)
        
        layout.addWidget(risk_label)
        layout.addWidget(self.risk_spin)
        
        # Take profit
        tp_label = QLabel("Take Profit (pips):")
        tp_label.setStyleSheet(LABEL_STYLE)
        self.tp_spin = QSpinBox()
        self.tp_spin.setRange(10, 500)
        self.tp_spin.setValue(50)
        self.tp_spin.setStyleSheet(INPUT_STYLE)
        
        layout.addWidget(tp_label)
        layout.addWidget(self.tp_spin)
        
        # Stop loss
        sl_label = QLabel("Stop Loss (pips):")
        sl_label.setStyleSheet(LABEL_STYLE)
        self.sl_spin = QSpinBox()
        self.sl_spin.setRange(10, 500)
        self.sl_spin.setValue(30)
        self.sl_spin.setStyleSheet(INPUT_STYLE)
        
        layout.addWidget(sl_label)
        layout.addWidget(self.sl_spin)
        
    def accept(self):
        """Store selected strategy and parameters"""
        self.selected_strategy = {
            'name': self.strategy_combo.currentText(),
            'risk_per_trade': self.risk_spin.value(),
            'take_profit': self.tp_spin.value(),
            'stop_loss': self.sl_spin.value()
        }
        super().accept() 