from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from styles import COLORS, FONTS, BUTTON_STYLE, GROUP_BOX_STYLE, LABEL_STYLE

class StrategyDialog(QDialog):
    def __init__(self, parent=None, instrument=None):
        super().__init__(parent)
        self.instrument = instrument
        self.selected_strategy = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Select Trading Strategy")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"background-color: {COLORS['background']}")
        
        layout = QVBoxLayout(self)
        
        # Header with selected instrument
        header = QLabel(f"Select Strategy for {self.instrument}")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Strategy buttons container
        strategies_layout = QHBoxLayout()
        
        # Create strategy buttons with images
        strategies = [
            {
                'name': 'Trend Following',
                'image': 'trend_following.png',
                'description': 'Follow market trends with momentum indicators'
            },
            {
                'name': 'Mean Reversion',
                'image': 'mean_reversion.png',
                'description': 'Trade price returns to historical average'
            },
            {
                'name': 'Breakout',
                'image': 'breakout.png',
                'description': 'Capture strong market moves from consolidation'
            },
            {
                'name': 'Scalping',
                'image': 'scalping.png',
                'description': 'Quick trades with small profit targets'
            }
        ]
        
        for strategy in strategies:
            strategy_box = self.create_strategy_button(
                strategy['name'],
                strategy['image'],
                strategy['description']
            )
            strategies_layout.addWidget(strategy_box)
            
        layout.addLayout(strategies_layout)
        
        # Add description label at bottom
        self.description_label = QLabel("Select a strategy to view description")
        self.description_label.setStyleSheet(f"""
            color: {COLORS['text']};
            background-color: {COLORS['surface']};
            padding: 15px;
            border-radius: 5px;
            font-size: 14px;
        """)
        self.description_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.description_label)
        
    def create_strategy_button(self, name, image_path, description):
        group = QGroupBox()
        group.setStyleSheet(f"""
            QGroupBox {{
                background-color: {COLORS['surface']};
                border-radius: 10px;
                padding: 10px;
                min-width: 180px;
                max-width: 180px;
                min-height: 250px;
            }}
            QGroupBox:hover {{
                background-color: {COLORS['primary']};
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Try to load image, use placeholder if image not found
        try:
            pixmap = QPixmap(f"images/strategies/{image_path}")
            if pixmap.isNull():
                pixmap = QPixmap(f"images/strategies/placeholder.png")
        except:
            pixmap = QPixmap(f"images/strategies/placeholder.png")
            
        # Create image button
        image_button = QPushButton()
        image_button.setIcon(QIcon(pixmap))
        image_button.setIconSize(QSize(120, 120))
        image_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 10px;
            }
        """)
        image_button.setFixedSize(150, 150)
        
        # Strategy name
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            color: {COLORS['text']};
            font-weight: bold;
            font-size: 14px;
        """)
        name_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(image_button, alignment=Qt.AlignCenter)
        layout.addWidget(name_label, alignment=Qt.AlignCenter)
        group.setLayout(layout)
        
        # Connect click events
        image_button.clicked.connect(
            lambda: self.strategy_selected(name, description)
        )
        group.mousePressEvent = lambda e: self.strategy_selected(name, description)
        
        return group
        
    def strategy_selected(self, strategy_name, description):
        """Handle strategy selection"""
        self.selected_strategy = strategy_name
        self.description_label.setText(description)
        
        # Show confirmation dialog
        if self.confirm_selection():
            self.accept()
            
    def confirm_selection(self):
        """Show confirmation dialog for strategy selection"""
        from PyQt5.QtWidgets import QMessageBox
        
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setText(f"Confirm Strategy Selection")
        msg.setInformativeText(
            f"Do you want to use the {self.selected_strategy} strategy for {self.instrument}?"
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setStyleSheet(f"background-color: {COLORS['background']}; color: {COLORS['text']};")
        
        return msg.exec_() == QMessageBox.Yes 