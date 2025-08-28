
#!/bin/bash

echo "🧪 Running API Tests for Baldness Detector"
echo "=========================================="

echo "Starting Authentication API tests..."
python test_auth_api.py

echo -e "\nStarting Detector API tests..."
python test_detector_api.py

echo -e "\n✨ All tests completed!"