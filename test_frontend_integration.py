#!/usr/bin/env python3
"""
End-to-End Authentication Flow Test
Tests the complete authentication flow including dashboard access
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:8000"

def generate_random_user():
    """Generate random user data for testing"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "email": f"test_{random_str}@example.com",
        "username": f"testuser_{random_str}",
        "password": "TestPass123",
        "full_name": f"Test User {random_str}"
    }

def test_dashboard_route():
    """Test 1: Verify dashboard route is accessible"""
    print("\n" + "="*60)
    print("TEST 1: Dashboard Route Accessibility")
    print("="*60)

    response = requests.get(f"{BASE_URL}/dashboard")

    if response.status_code == 200:
        print("✓ Dashboard route is accessible")
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('content-type')}")
        return True
    else:
        print(f"✗ Dashboard route failed: {response.status_code}")
        return False

def test_user_registration():
    """Test 2: User Registration"""
    print("\n" + "="*60)
    print("TEST 2: User Registration")
    print("="*60)

    user_data = generate_random_user()
    print(f"Testing registration with email: {user_data['email']}")

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )

    if response.status_code == 201:
        data = response.json()
        print("✓ Registration successful")
        print(f"  User ID: {data.get('id')}")
        print(f"  Username: {data.get('username')}")
        print(f"  Email: {data.get('email')}")
        return user_data
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_user_login(email, password):
    """Test 3: User Login"""
    print("\n" + "="*60)
    print("TEST 3: User Login")
    print("="*60)

    print(f"Testing login with email: {email}")

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": email, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print("✓ Login successful")
        print(f"  Token type: {data.get('token_type')}")
        print(f"  Access token: {token[:20]}..." if token else "  No token received")
        return token
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_fetch_current_user(token):
    """Test 4: Fetch Current User Data"""
    print("\n" + "="*60)
    print("TEST 4: Fetch Current User Data")
    print("="*60)

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print("✓ Successfully fetched user data")
        print(f"  ID: {data.get('id')}")
        print(f"  Username: {data.get('username')}")
        print(f"  Email: {data.get('email')}")
        print(f"  Full Name: {data.get('full_name')}")
        print(f"  Is Active: {data.get('is_active')}")
        print(f"  Is Verified: {data.get('is_verified')}")
        print(f"  Created At: {data.get('created_at')}")
        return data
    else:
        print(f"✗ Failed to fetch user data: {response.status_code}")
        print(f"  Error: {response.text}")
        return None

def test_dashboard_access_without_token():
    """Test 5: Dashboard Access Without Token (should still load HTML)"""
    print("\n" + "="*60)
    print("TEST 5: Dashboard Access Without Token")
    print("="*60)

    response = requests.get(f"{BASE_URL}/dashboard")

    if response.status_code == 200:
        print("✓ Dashboard HTML loads (client-side JS will handle auth check)")
        return True
    else:
        print(f"✗ Dashboard failed to load: {response.status_code}")
        return False

def test_invalid_login():
    """Test 6: Invalid Login Attempt"""
    print("\n" + "="*60)
    print("TEST 6: Invalid Login Attempt")
    print("="*60)

    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "invalid@example.com", "password": "wrongpassword"}
    )

    if response.status_code == 401:
        print("✓ Invalid login correctly rejected")
        print(f"  Status: {response.status_code}")
        return True
    else:
        print(f"✗ Unexpected response: {response.status_code}")
        return False

def run_all_tests():
    """Run all end-to-end tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "TED BROKER AUTHENTICATION TESTS" + " "*16 + "║")
    print("╚" + "="*58 + "╝")

    results = {
        "passed": 0,
        "failed": 0
    }

    # Test 1: Dashboard route
    if test_dashboard_route():
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 2: Registration
    user_data = test_user_registration()
    if user_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n✗ Cannot continue tests without successful registration")
        return results

    # Test 3: Login
    token = test_user_login(user_data["email"], user_data["password"])
    if token:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n✗ Cannot continue tests without successful login")
        return results

    # Test 4: Fetch user data
    if test_fetch_current_user(token):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 5: Dashboard access
    if test_dashboard_access_without_token():
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 6: Invalid login
    if test_invalid_login():
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✓ Passed: {results['passed']}")
    print(f"✗ Failed: {results['failed']}")
    print(f"Total: {results['passed'] + results['failed']}")

    if results["failed"] == 0:
        print("\n🎉 All tests passed! Authentication system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")

    print("\n" + "="*60)
    print("NEXT STEPS FOR MANUAL TESTING")
    print("="*60)
    print("1. Open your browser and navigate to: http://localhost:8000")
    print("2. Click 'Sign Up' and register a new account")
    print("3. After registration, login with your credentials")
    print("4. You should be redirected to the dashboard")
    print("5. Verify that your user information is displayed correctly")
    print("6. Test the logout button")
    print("7. Try accessing /dashboard directly (should redirect to login)")
    print("="*60)

    return results

if __name__ == "__main__":
    try:
        results = run_all_tests()
        exit(0 if results["failed"] == 0 else 1)
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
