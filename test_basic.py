print("Testing basic Python execution...")
print("✅ Python is working!")

# Test imports
try:
    import json
    import os
    from pathlib import Path
    print("✅ Standard library imports work")
except Exception as e:
    print(f"❌ Import error: {e}")

# Test our config
try:
    import sys
    sys.path.insert(0, 'src')
    from config import load_config
    config = load_config()
    print(f"✅ Config loaded: {config.aws_region}")
except Exception as e:
    print(f"❌ Config error: {e}")

print("Basic test complete!")