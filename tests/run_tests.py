#!/usr/bin/env python3
"""
Test runner for the baldness detector project.
Runs both integration tests and unit tests.
"""

import sys
import os
import subprocess
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_server_running():
    """Check if the server is running on localhost:8000"""
    import httpx
    try:
        response = httpx.get("http://localhost:8000/api/v1/auth/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False

def run_integration_tests():
    """Run integration tests that require a running server"""
    print("="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    
    if not check_server_running():
        print("❌ Server is not running on localhost:8000")
        print("Please start the server with: python -m app")
        return False
    
    print("✅ Server is running, proceeding with integration tests...\n")
    
    # Run authentication tests
    print("Running authentication tests...")
    try:
        from tests.test_auth_api import main as auth_main
        asyncio.run(auth_main())
        print("✅ Authentication tests completed\n")
    except Exception as e:
        print(f"❌ Authentication tests failed: {e}\n")
        return False
    
    # Run detector integration tests
    print("Running detector integration tests...")
    try:
        from tests.test_detector_api import main as detector_main
        asyncio.run(detector_main())
        print("✅ Detector integration tests completed\n")
    except Exception as e:
        print(f"❌ Detector integration tests failed: {e}\n")
        return False
    
    return True

def run_unit_tests():
    """Run unit tests with pytest"""
    print("="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    # Check if pytest is available
    try:
        import pytest
    except ImportError:
        print("❌ pytest not found. Installing test dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "test-requirements.txt"])
            print("✅ Test dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install test dependencies")
            return False
    
    # Run pytest
    try:
        # Change to project root directory
        os.chdir(project_root)
        
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_detector_unit.py", 
            "-v", 
            "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Unit tests passed")
            return True
        else:
            print("❌ Unit tests failed")
            return False
            
    except Exception as e:
        print(f"❌ Failed to run unit tests: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 BALDNESS DETECTOR TEST RUNNER")
    print("="*60)
    
    # Parse command line arguments
    run_integration = "--integration" in sys.argv or "--all" in sys.argv
    run_unit = "--unit" in sys.argv or "--all" in sys.argv
    
    if not run_integration and not run_unit:
        # Default: run all tests
        run_integration = True
        run_unit = True
    
    results = []
    
    if run_unit:
        unit_result = run_unit_tests()
        results.append(("Unit Tests", unit_result))
    
    if run_integration:
        integration_result = run_integration_tests()
        results.append(("Integration Tests", integration_result))
    
    # Summary
    print("="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    print("Usage:")
    print("  python run_tests.py           # Run all tests")
    print("  python run_tests.py --unit    # Run only unit tests")
    print("  python run_tests.py --integration  # Run only integration tests")
    print("  python run_tests.py --all     # Run all tests")
    print()
    
    sys.exit(main())
