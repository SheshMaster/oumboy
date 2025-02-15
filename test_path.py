import sys
import os

# Add app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, "app")
sys.path.append(app_dir)

print("Python Path:")
for path in sys.path:
    print(f"- {path}") 