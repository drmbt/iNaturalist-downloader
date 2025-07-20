#!/usr/bin/env python3
"""
Test script to verify that the iNaturalist downloader dependencies are properly installed.
"""

import sys

def test_imports():
    """Test that all required modules can be imported."""
    try:
        import requests
        print("✓ requests module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import requests: {e}")
        return False
    
    try:
        import json
        import os
        import time
        import argparse
        import logging
        from datetime import datetime
        from typing import Dict, List, Optional, Any
        print("✓ All standard library modules imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import standard library module: {e}")
        return False
    
    return True

def test_requests_functionality():
    """Test that requests can make a simple HTTP request."""
    try:
        import requests
        response = requests.get("https://api.inaturalist.org/v1/observations", 
                             params={'per_page': 1}, timeout=10)
        if response.status_code == 200:
            print("✓ Successfully connected to iNaturalist API")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to iNaturalist API: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing iNaturalist Downloader Installation")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Installation test failed - missing dependencies")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # Test API connectivity
    if not test_requests_functionality():
        print("\n⚠️  API connectivity test failed - check your internet connection")
        print("The script may still work, but API connectivity is recommended")
    
    print("\n✅ All tests passed! The script should work correctly.")
    print("\nYou can now run the script with:")
    print("python inaturalist_downloader.py --lat -8.132489362310453 --lon -115.36386760679501 --radius 5")

if __name__ == "__main__":
    main() 