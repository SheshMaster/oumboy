from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import QSize

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

    @staticmethod
    def get_device_type():
        """Get device type and characteristics"""
        screen = QDesktopWidget().screenGeometry()
        width = screen.width()
        height = screen.height()
        
        if width < 800 or height < 600:
            return "phone"
        elif width < 1200:
            return "tablet"
        else:
            return "desktop"

    @staticmethod
    def get_scaling_factor():
        """Get appropriate scaling factor for current device"""
        device_type = DeviceDetector.get_device_type()
        if device_type == "phone":
            return 1.5
        elif device_type == "tablet":
            return 1.25
        return 1.0 