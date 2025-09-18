#!/usr/bin/env python3
"""
Simple launcher script for the Plant Care System
"""

import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import and run the main module
if __name__ == "__main__":
    try:
        from main import main
        main()
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure you're in the project directory and all files are present.")
        print("Current directory:", current_dir)
        print("Files in directory:", os.listdir(current_dir))
        sys.exit(1)
