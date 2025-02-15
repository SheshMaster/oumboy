import sys
import os

# Add app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.main import main

if __name__ == "__main__":
    main()
