#!/usr/bin/env python3
"""Test script for TED Broker API authentication endpoints"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(response):
    """Pretty print response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 50)


def test_register():
    """Test user registration"""
    print("\n1. Testing User Registration...")
    data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print_response(response)
    return response.status_code == 201


def test_login():
    """Test user login"""
    print("\n2. Testing User Login...")
    data = {
        "email": "testuser@example.com",
        "password": "TestPassword123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print_response(response)

    if response.status_code == 200:
        return response.json()["access_token"]
    return None


def test_get_current_user(token):
    """Test getting current user"""
    print("\n3. Testing Get Current User (Protected Route)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print_response(response)
    return response.status_code == 200


def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n4. Testing Login with Invalid Credentials...")
    data = {
        "email": "testuser@example.com",
        "password": "WrongPassword"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print_response(response)
    return response.status_code == 401


def test_without_token():
    """Test accessing protected route without token"""
    print("\n5. Testing Protected Route Without Token...")
    response = requests.get(f"{BASE_URL}/api/auth/me")
    print_response(response)
    return response.status_code == 401


def test_duplicate_registration():
    """Test registering with duplicate email"""
    print("\n6. Testing Duplicate Registration...")
    data = {
        "email": "testuser@example.com",
        "username": "testuser2",
        "password": "TestPassword123",
        "full_name": "Test User 2"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print_response(response)
    return response.status_code == 400


if __name__ == "__main__":
    print("=" * 50)
    print("TED Broker API Authentication Tests")
    print("=" * 50)

    results = []

    # Test 1: Register user
    results.append(("User Registration", test_register()))

    # Test 2: Login user
    token = test_login()
    results.append(("User Login", token is not None))

    # Test 3: Get current user
    if token:
        results.append(("Get Current User", test_get_current_user(token)))

    # Test 4: Invalid login
    results.append(("Invalid Login", test_invalid_login()))

    # Test 5: Access without token
    results.append(("Access Without Token", test_without_token()))

    # Test 6: Duplicate registration
    results.append(("Duplicate Registration", test_duplicate_registration()))

    # Print results
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")

    print("\n" + "=" * 50)
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"Total: {passed_count}/{total_count} tests passed")
    print("=" * 50)
