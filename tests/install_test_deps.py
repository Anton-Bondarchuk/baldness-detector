#!/usr/bin/env python3
"""
Script to install test dependencies for the baldness detector project.
Run this before running the tests.
"""

import subprocess
import sys

def install_test_dependencies():
    """Install test dependencies"""
    dependencies = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.24.0",  # Already in requirements but ensuring version
        "pillow>=9.0.0",  # For image processing in tests
    ]
    
    print("Installing test dependencies...")
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Successfully installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ All test dependencies installed successfully!")
    return True

if __name__ == "__main__":
    success = install_test_dependencies()
    if not success:
        sys.exit(1)
