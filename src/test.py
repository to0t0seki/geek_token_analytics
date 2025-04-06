import sys
import os

print("=== Environment Variables ===")
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

print("\n=== sys.path ===")
for path in sys.path:
    print(path)

