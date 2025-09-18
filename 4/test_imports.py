#!/usr/bin/env python3
"""
Test script to check which modules are missing
"""

def test_imports():
    """Test all required imports"""
    missing_modules = []
    
    # Test standard library imports
    try:
        import yaml
        print("✓ yaml: OK")
    except ImportError as e:
        missing_modules.append("yaml")
        print(f"✗ yaml: MISSING - {e}")
    
    try:
        import logging
        print("✓ logging: OK")
    except ImportError as e:
        missing_modules.append("logging")
        print(f"✗ logging: MISSING - {e}")
    
    # Test third-party imports
    try:
        import click
        print("✓ click: OK")
    except ImportError as e:
        missing_modules.append("click")
        print(f"✗ click: MISSING - {e}")
    
    try:
        import PIL
        print("✓ PIL (Pillow): OK")
    except ImportError as e:
        missing_modules.append("pillow")
        print(f"✗ PIL (Pillow): MISSING - {e}")
    
    try:
        import numpy
        print("✓ numpy: OK")
    except ImportError as e:
        missing_modules.append("numpy")
        print(f"✗ numpy: MISSING - {e}")
    
    # Test local module imports
    try:
        from modules.cli import PlantCareCLI
        print("✓ modules.cli: OK")
    except ImportError as e:
        missing_modules.append("modules.cli")
        print(f"✗ modules.cli: MISSING - {e}")
    
    # Summary
    if missing_modules:
        print(f"\n❌ Missing modules: {', '.join(missing_modules)}")
        print("\nTo fix, run:")
        print("pip install --user pyyaml click pillow numpy python-dotenv")
    else:
        print("\n✅ All modules are available!")
    
    return missing_modules

if __name__ == "__main__":
    test_imports()
