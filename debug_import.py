
import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import germinette
    print(f"germinette imported from: {getattr(germinette, '__file__', 'unknown')}")
    print(f"germinette path: {getattr(germinette, '__path__', 'unknown')}")
    print(f"dir(germinette): {dir(germinette)}")
    print(f"Has __version__? {'__version__' in dir(germinette)}")
except Exception as e:
    print(f"Error importing germinette: {e}")
