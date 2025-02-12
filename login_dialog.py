from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QComboBox,
    QMessageBox
)
from styles import COLORS, FONTS, BUTTON_STYLE, INPUT_STYLE, LABEL_STYLE
import oandapyV20
from oandapyV20.endpoints.accounts import AccountSummary
import alpaca_trade_api as tradeapi
import json
import os

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setStyleSheet(f"background-color: {COLORS['background']}")
        
        # Add admin credentials
        self.admin_credentials = {
            'username': 'admin',
            'password': 'manager'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Add login type selection
        login_type_label = QLabel("Login Type:")
        login_type_label.setStyleSheet(LABEL_STYLE)
        self.login_type_combo = QComboBox()
        self.login_type_combo.addItems(["Trading Account", "Admin"])
        self.login_type_combo.setStyleSheet(INPUT_STYLE)
        self.login_type_combo.currentTextChanged.connect(self.on_login_type_changed)
        
        # Admin login fields
        self.username_label = QLabel("Username:")
        self.username_label.setStyleSheet(LABEL_STYLE)
        self.username_input = QLineEdit()
        self.username_input.setStyleSheet(INPUT_STYLE)
        
        self.password_label = QLabel("Password:")
        self.password_label.setStyleSheet(LABEL_STYLE)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(INPUT_STYLE)
        
        # Trading account fields
        self.exchange_label = QLabel("Select Exchange:")
        self.exchange_label.setStyleSheet(LABEL_STYLE)
        self.exchange_combo = QComboBox()
        self.exchange_combo.addItems(["OANDA", "Alpaca"])
        self.exchange_combo.setStyleSheet(INPUT_STYLE)
        
        # Load saved credentials if available
        saved_credentials = load_credentials()
        if saved_credentials:
            self.exchange_combo.setCurrentText(saved_credentials['exchange'].capitalize())
        
        self.account_id_label = QLabel("Account ID:")
        self.account_id_label.setStyleSheet(LABEL_STYLE)
        self.account_id = QLineEdit()
        self.account_id.setStyleSheet(INPUT_STYLE)
        if saved_credentials and 'account_id' in saved_credentials:
            self.account_id.setText(saved_credentials['account_id'])
        
        self.api_label = QLabel("API Key:")
        self.api_label.setStyleSheet(LABEL_STYLE)
        self.api_key = QLineEdit()
        self.api_key.setStyleSheet(INPUT_STYLE)
        if saved_credentials:
            self.api_key.setText(saved_credentials['api_key'])
        
        self.secret_label = QLabel("API Secret:")
        self.secret_label.setStyleSheet(LABEL_STYLE)
        self.api_secret = QLineEdit()
        self.api_secret.setEchoMode(QLineEdit.Password)
        self.api_secret.setStyleSheet(INPUT_STYLE)
        if saved_credentials:
            self.api_secret.setText(saved_credentials['api_secret'])
        
        # Add to layout
        layout.addWidget(login_type_label)
        layout.addWidget(self.login_type_combo)
        
        # Admin widgets
        self.admin_widgets = [
            self.username_label, self.username_input,
            self.password_label, self.password_input
        ]
        
        # Trading account widgets
        self.trading_widgets = [
            self.exchange_label, self.exchange_combo,
            self.account_id_label, self.account_id,
            self.api_label, self.api_key,
            self.secret_label, self.api_secret
        ]
        
        # Add all widgets to layout
        for widget in self.admin_widgets + self.trading_widgets:
            layout.addWidget(widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.cancel_button = QPushButton("Cancel")
        self.login_button.setStyleSheet(BUTTON_STYLE)
        self.cancel_button.setStyleSheet(BUTTON_STYLE)
        
        self.login_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        # Show appropriate fields based on initial selection
        self.on_login_type_changed(self.login_type_combo.currentText())
        
    def on_login_type_changed(self, login_type):
        """Show/hide fields based on login type"""
        is_admin = login_type == "Admin"
        
        # Show/hide admin fields
        for widget in self.admin_widgets:
            widget.setVisible(is_admin)
            
        # Show/hide trading account fields
        for widget in self.trading_widgets:
            widget.setVisible(not is_admin)
            
    def accept(self):
        """Verify credentials before accepting"""
        if self.login_type_combo.currentText() == "Admin":
            if self.verify_admin_login():
                super().accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid admin credentials!")
        else:
            try:
                credentials = self.get_credentials()
                
                if credentials['exchange'] == 'oanda':
                    # Test OANDA connection
                    api = oandapyV20.API(access_token=credentials['api_key'])
                    r = AccountSummary(accountID=credentials['account_id'])
                    api.request(r)
                    
                    QMessageBox.information(self, "Success", "Successfully connected to OANDA!")
                    save_credentials(credentials)  # Save credentials
                    super().accept()
                    
                elif credentials['exchange'] == 'alpaca':
                    # Test Alpaca connection
                    api = tradeapi.REST(
                        credentials['api_key'],
                        credentials['api_secret'],
                        base_url='https://paper-api.alpaca.markets'
                    )
                    api.get_account()
                    
                    QMessageBox.information(self, "Success", "Successfully connected to Alpaca!")
                    save_credentials(credentials)  # Save credentials
                    super().accept()
                    
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", 
                    f"Failed to connect: {str(e)}\n\nPlease verify your credentials.")
                    
    def verify_admin_login(self):
        """Verify admin credentials"""
        return (
            self.username_input.text() == self.admin_credentials['username'] and
            self.password_input.text() == self.admin_credentials['password']
        )
        
    def get_credentials(self):
        """Get credentials based on login type"""
        if self.login_type_combo.currentText() == "Admin":
            return {
                'type': 'admin',
                'username': self.username_input.text()
            }
        else:
            return {
                'type': 'trading',
                'exchange': self.exchange_combo.currentText().lower(),
                'account_id': self.account_id.text(),
                'api_key': self.api_key.text(),
                'api_secret': self.api_secret.text()
            }

def save_credentials(credentials):
    """Save credentials to a JSON file."""
    with open('credentials.json', 'w') as f:
        json.dump(credentials, f)

def load_credentials():
    """Load credentials from a JSON file if it exists."""
    if os.path.exists('credentials.json'):
        with open('credentials.json', 'r') as f:
            return json.load(f)
    return None 