#!/usr/bin/env python3
"""
Simple test script to verify the authentication API endpoints.
Run this after setting up the database and environment variables.
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/v1/auth/health")
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200

async def test_email_auth():
    """Test email authentication"""
    print("\nTesting email authentication...")
    
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
        
        print(f"Email Auth Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Got JWT token: {data['access_token'][:20]}...")
            return data['access_token']
        else:
            print(f"Error: {response.text}")
            return None

async def test_protected_endpoint(token):
    """Test protected endpoint with JWT token"""
    if not token:
        print("\nSkipping protected endpoint test (no token)")
        return
    
    print("\nTesting protected endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/api/v1/auth/me",
            headers=headers
        )
        
        print(f"Protected Endpoint Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"User data: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")

async def main():
    """Run all tests"""
    print("Starting API tests...\n")
    
    try:
        # Test health check
        health_ok = await test_health_check()
        
        if not health_ok:
            print("Health check failed, stopping tests")
            return
        
        # Test email authentication
        token = await test_email_auth()
        
        # Test protected endpoint
        await test_protected_endpoint(token)
        
        print("\nTests completed!")
        
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
