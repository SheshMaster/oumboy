from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

# Color scheme
COLORS = {
    'primary': '#2962FF',      # Main blue color
    'secondary': '#304FFE',    # Darker blue
    'success': '#00E676',      # Brighter green
    'danger': '#FF1744',       # Brighter red
    'warning': '#FFD600',      # Yellow
    'background': '#1C1C1C',   # Dark background
    'surface': '#242424',      # Slightly lighter background
    'text': '#FFFFFF',         # White text
    'text_secondary': '#FFFFFF'  # Gray text
}

# Font configurations
FONTS = {
    'header': QFont('Roboto', 16, QFont.Bold),
    'subheader': QFont('Roboto', 14, QFont.Medium),
    'body': QFont('Roboto', 12),
    'small': QFont('Roboto', 10),
    'mono': QFont('Roboto Mono', 12),  # For numbers and code
    'header_mobile': QFont('Roboto', 20, QFont.Bold),
    'subheader_mobile': QFont('Roboto', 18, QFont.Medium),
    'body_mobile': QFont('Roboto', 16),
    'small_mobile': QFont('Roboto', 14),
    'mono_mobile': QFont('Roboto Mono', 16)
}

# Main window style
MAIN_WINDOW_STYLE = f"""
    QMainWindow {{
        background-color: {COLORS['background']};
    }}
"""

# Button style
BUTTON_STYLE = f"""
    QPushButton {{
        background-color: {COLORS['primary']};
        color: {COLORS['text']};
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
    }}
    QPushButton:hover {{
        background-color: {COLORS['secondary']};
    }}
    QPushButton:pressed {{
        background-color: {COLORS['primary']};
    }}
    QPushButton:disabled {{
        background-color: #404040;
        color: #808080;
    }}
"""

# Input style
INPUT_STYLE = f"""
    QLineEdit, QComboBox {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid #404040;
        padding: 6px;
        border-radius: 4px;
    }}
    QLineEdit:focus, QComboBox:focus {{
        border: 2px solid {COLORS['primary']};
    }}
    QComboBox::drop-down {{
        border: none;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-width: 0px;
    }}
"""

# Table style
TABLE_STYLE = f"""
    QTableWidget {{
        background-color: {COLORS['surface']};
        color: {COLORS['text']};
        gridline-color: #404040;
        border: none;
    }}
    QTableWidget::item {{
        padding: 5px;
    }}
    QHeaderView::section {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
        padding: 5px;
        border: 1px solid #404040;
    }}
"""

# Label style
LABEL_STYLE = f"""
    QLabel {{
        color: {COLORS['text']};
    }}
"""

# Group box style
GROUP_BOX_STYLE = f"""
    QGroupBox {{
        color: {COLORS['text']};
        font-weight: bold;
        border: 1px solid {COLORS['text_secondary']};
        border-radius: 4px;
        margin-top: 8px;
        padding-top: 8px;
    }}
    QGroupBox::title {{
        color: {COLORS['text']};
        subcontrol-origin: margin;
        left: 8px;
        padding: 0 3px;
    }}
"""

# ... rest of the styles code ... 