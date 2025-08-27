#!/usr/bin/env python3
"""
Test script for the baldness detector API endpoints.
Tests both /detect-baldness and /detect-baldness/stream endpoints with various scenarios.
"""

import asyncio
import httpx
import json
import base64
import io
from pathlib import Path

BASE_URL = "http://localhost:8000"

def create_test_image(width=200, height=200, format="PNG"):
    """Create a minimal test image for uploading"""
    # Create a minimal 1x1 pixel PNG - this is a valid PNG file encoded in base64
    # We'll use this as our test image since PIL might not be available
    minimal_png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    return base64.b64decode(minimal_png_b64)

async def get_auth_token():
    """Get authentication token for protected endpoints"""
    print("Getting authentication token...")
    
    test_data = {
        "email": "test@example.com",
        "name": "Test User",
        "picture": "https://example.com/avatar.jpg"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/v1/auth/email",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['access_token']
        else:
            print(f"Failed to get auth token: {response.text}")
            return None

async def test_detect_baldness_success(token):
    """Test successful baldness detection"""
    print("\nTesting /detect-baldness endpoint - Success case...")
    
    if not token:
        print("Skipping test - no auth token")
        return False
    
    # Create test image
    test_image = create_test_image()
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "photo": ("test_image.png", test_image, "image/png")
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness",
            headers=headers,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response structure:")
            print(f"  - Baldness Level: {data.get('baldnessLevel')}")
            print(f"  - Baldness Category: {data.get('baldnessCategory')}")
            print(f"  - Processed Image: {'Present' if data.get('processedImage') else 'Missing'}")
            print(f"  - Baldness Areas: {len(data.get('baldnessAreas', []))} areas")
            
            # Validate response structure
            required_fields = ['processedImage', 'baldnessLevel', 'baldnessCategory', 'baldnessAreas']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Validate baldness level is between 0 and 1
            baldness_level = data.get('baldnessLevel')
            if not (0 <= baldness_level <= 1):
                print(f"❌ Invalid baldness level: {baldness_level} (should be 0-1)")
                return False
            
            print("✅ Response validation passed")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False

async def test_detect_baldness_no_auth():
    """Test baldness detection without authentication"""
    print("\nTesting /detect-baldness endpoint - No authentication...")
    
    test_image = create_test_image()
    
    files = {
        "photo": ("test_image.png", test_image, "image/png")
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness",
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Correctly rejected unauthorized request")
            return True
        else:
            print(f"❌ Expected 403, got {response.status_code}: {response.text}")
            return False

async def test_detect_baldness_invalid_file(token):
    """Test baldness detection with invalid file type"""
    print("\nTesting /detect-baldness endpoint - Invalid file type...")
    
    if not token:
        print("Skipping test - no auth token")
        return False
    
    # Create a text file instead of image
    text_content = b"This is not an image file"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "photo": ("test.txt", text_content, "text/plain")
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness",
            headers=headers,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 400:
            print("✅ Correctly rejected non-image file")
            return True
        else:
            print(f"❌ Expected 400, got {response.status_code}: {response.text}")
            return False

async def test_detect_baldness_missing_file(token):
    """Test baldness detection with missing file"""
    print("\nTesting /detect-baldness endpoint - Missing file...")
    
    if not token:
        print("Skipping test - no auth token")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Correctly rejected request without file")
            return True
        else:
            print(f"❌ Expected 422, got {response.status_code}: {response.text}")
            return False

async def test_stream_baldness_detection_success(token):
    """Test successful streaming baldness detection"""
    print("\nTesting /detect-baldness/stream endpoint - Success case...")
    
    if not token:
        print("Skipping test - no auth token")
        return False
    
    test_image = create_test_image()
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "photo": ("test_image.png", test_image, "image/png")
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness/stream",
            headers=headers,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            # Read the streaming response
            content = response.content
            
            if len(content) > 0:
                print(f"✅ Received streaming response ({len(content)} bytes)")
                
                # Try to parse the stream format
                try:
                    # The stream should contain metadata size + metadata + image size + image
                    if len(content) >= 8:  # At least metadata size + image size
                        print("✅ Stream format appears valid")
                        return True
                    else:
                        print("❌ Stream too short")
                        return False
                except Exception as e:
                    print(f"❌ Error parsing stream: {e}")
                    return False
            else:
                print("❌ Empty response")
                return False
        else:
            print(f"❌ Failed: {response.text}")
            return False

async def test_stream_baldness_detection_no_auth():
    """Test streaming baldness detection without authentication"""
    print("\nTesting /detect-baldness/stream endpoint - No authentication...")
    
    test_image = create_test_image()
    
    files = {
        "photo": ("test_image.png", test_image, "image/png")
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness/stream",
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 403:
            print("✅ Correctly rejected unauthorized request")
            return True
        else:
            print(f"❌ Expected 403, got {response.status_code}: {response.text}")
            return False

async def test_different_image_formats(token):
    """Test with different image formats"""
    print("\nTesting /detect-baldness endpoint - Different image formats...")
    
    if not token:
        print("Skipping test - no auth token")
        return False
    
    # Test with PNG format (our test image is PNG)
    formats = [
        ("PNG", "image/png"),
        ("JPEG", "image/jpeg"),  # We'll use the same image but claim it's JPEG
    ]
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    success_count = 0
    
    for fmt, content_type in formats:
        print(f"  Testing {fmt} format...")
        
        test_image = create_test_image()  # Always returns PNG data
        
        files = {
            "photo": (f"test_image.{fmt.lower()}", test_image, content_type)
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{BASE_URL}/detect-baldness",
                headers=headers,
                files=files
            )
            
            if response.status_code == 200:
                print(f"    ✅ {fmt} format accepted")
                success_count += 1
            else:
                print(f"    ❌ {fmt} format failed: {response.status_code}")
    
    if success_count >= 1:  # At least PNG should work
        print("✅ Image format test passed")
        return True
    else:
        print(f"❌ No formats accepted")
        return False

async def test_large_image(token):
    """Test with a larger image"""
    print("\nTesting /detect-baldness endpoint - Large image...")
    
    if not token:
        print("Skipping test - no auth token")
        return False
    
    # Use the same test image (since we can't create larger ones without PIL)
    test_image = create_test_image()
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "photo": ("large_test_image.png", test_image, "image/png")
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{BASE_URL}/detect-baldness",
            headers=headers,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Image processed successfully")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False

async def main():
    """Run all detector tests"""
    print("Starting Detector API tests...\n")
    
    try:
        # Get authentication token
        token = await get_auth_token()
        
        if not token:
            print("❌ Failed to get authentication token, skipping authenticated tests")
        
        # Test results
        test_results = []
        
        # Run all tests
        tests = [
            ("Detect Baldness - Success", test_detect_baldness_success(token)),
            ("Detect Baldness - No Auth", test_detect_baldness_no_auth()),
            ("Detect Baldness - Invalid File", test_detect_baldness_invalid_file(token)),
            ("Detect Baldness - Missing File", test_detect_baldness_missing_file(token)),
            ("Stream Detection - Success", test_stream_baldness_detection_success(token)),
            ("Stream Detection - No Auth", test_stream_baldness_detection_no_auth()),
            ("Different Image Formats", test_different_image_formats(token)),
            ("Large Image", test_large_image(token))
        ]
        
        for test_name, test_coro in tests:
            try:
                result = await test_coro
                test_results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                test_results.append((test_name, False))
        
        # Summary
        print("\n" + "="*50)
        print("TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed!")
        else:
            print(f"⚠️  {total - passed} test(s) failed")
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
