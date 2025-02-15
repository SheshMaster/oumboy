from .device_detector import DeviceDetector
# We'll add forex_utils import after creating the file
try:
    from .forex_utils import ForexCalculator
except ImportError:
    pass 