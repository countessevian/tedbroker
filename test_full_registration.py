#!/usr/bin/env python3
"""
Test Registration with All Fields
Validates that all registration form fields are properly captured
"""

import requests
import json
import random
import string

BASE_URL = "http://localhost:8000"

def generate_random_user():
    """Generate random user data with all fields"""
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return {
        "email": f"test_{random_str}@example.com",
        "username": f"testuser_{random_str}",
        "password": "TestPass123",
        "full_name": f"Test User {random_str}",
        "phone": f"+1234567{random.randint(1000, 9999)}",
        "gender": random.choice(["Male", "Female", "Others"]),
        "country": random.choice(["United States of America", "Canada", "United Kingdom"]),
        "account_types": random.sample([
            "Binary Option Trading",
            "Forex Trading",
            "Stock Trading",
            "CryptoCurrency Investment",
            "NFT Trading"
        ], k=random.randint(1, 3))
    }

def test_full_registration():
    """Test 1: Register with all fields"""
    print("\n" + "="*70)
    print("TEST 1: Register User with All Fields")
    print("="*70)

    user_data = generate_random_user()

    print("\nRegistering user with:")
    print(f"  Email: {user_data['email']}")
    print(f"  Username: {user_data['username']}")
    print(f"  Full Name: {user_data['full_name']}")
    print(f"  Phone: {user_data['phone']}")
    print(f"  Gender: {user_data['gender']}")
    print(f"  Country: {user_data['country']}")
    print(f"  Account Types: {', '.join(user_data['account_types'])}")

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=user_data
    )

    if response.status_code == 201:
        data = response.json()
        print("\n✓ Registration successful!")
        print(f"  User ID: {data.get('id')}")
        print(f"  Username: {data.get('username')}")
        print(f"  Email: {data.get('email')}")
        print(f"  Full Name: {data.get('full_name')}")
        print(f"  Phone: {data.get('phone')}")
        print(f"  Gender: {data.get('gender')}")
        print(f"  Country: {data.get('country')}")
        print(f"  Account Types: {', '.join(data.get('account_types', []))}")

        # Verify all fields are present
        missing_fields = []
        if not data.get('phone'):
            missing_fields.append('phone')
        if not data.get('gender'):
            missing_fields.append('gender')
        if not data.get('country'):
            missing_fields.append('country')
        if not data.get('account_types'):
            missing_fields.append('account_types')

        if missing_fields:
            print(f"\n⚠️  Warning: Missing fields in response: {', '.join(missing_fields)}")
            return None, user_data

        return data, user_data
    else:
        print(f"\n✗ Registration failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return None, user_data

def test_login_and_fetch(user_data):
    """Test 2: Login and Fetch User Data"""
    print("\n" + "="*70)
    print("TEST 2: Login and Fetch Complete User Data")
    print("="*70)

    # Login
    print(f"\nLogging in with {user_data['email']}...")
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )

    if response.status_code != 200:
        print(f"✗ Login failed: {response.status_code}")
        return False

    token = response.json().get('access_token')
    print("✓ Login successful")

    # Fetch user data
    print("\nFetching user data from /api/auth/me...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("\n✓ Successfully fetched user data:")
        print(f"  ID: {data.get('id')}")
        print(f"  Username: {data.get('username')}")
        print(f"  Email: {data.get('email')}")
        print(f"  Full Name: {data.get('full_name')}")
        print(f"  Phone: {data.get('phone')}")
        print(f"  Gender: {data.get('gender')}")
        print(f"  Country: {data.get('country')}")
        print(f"  Account Types: {', '.join(data.get('account_types', []))}")
        print(f"  Is Active: {data.get('is_active')}")
        print(f"  Is Verified: {data.get('is_verified')}")

        # Verify fields match
        print("\nVerifying field integrity...")
        errors = []
        if data.get('email') != user_data['email']:
            errors.append(f"Email mismatch: {data.get('email')} != {user_data['email']}")
        if data.get('phone') != user_data['phone']:
            errors.append(f"Phone mismatch: {data.get('phone')} != {user_data['phone']}")
        if data.get('gender') != user_data['gender']:
            errors.append(f"Gender mismatch: {data.get('gender')} != {user_data['gender']}")
        if data.get('country') != user_data['country']:
            errors.append(f"Country mismatch: {data.get('country')} != {user_data['country']}")
        if set(data.get('account_types', [])) != set(user_data['account_types']):
            errors.append(f"Account types mismatch: {data.get('account_types')} != {user_data['account_types']}")

        if errors:
            print("\n✗ Field integrity check failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        else:
            print("✓ All fields match original registration data!")
            return True
    else:
        print(f"\n✗ Failed to fetch user data: {response.status_code}")
        return False

def test_minimal_registration():
    """Test 3: Register with minimal required fields only"""
    print("\n" + "="*70)
    print("TEST 3: Register with Minimal Fields (email, username, password)")
    print("="*70)

    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    minimal_user = {
        "email": f"minimal_{random_str}@example.com",
        "username": f"minimaluser_{random_str}",
        "password": "TestPass123"
    }

    print(f"\nRegistering user with only required fields...")
    print(f"  Email: {minimal_user['email']}")
    print(f"  Username: {minimal_user['username']}")

    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=minimal_user
    )

    if response.status_code == 201:
        data = response.json()
        print("\n✓ Minimal registration successful!")
        print(f"  User ID: {data.get('id')}")
        print(f"  Optional fields are None: phone={data.get('phone')}, gender={data.get('gender')}, country={data.get('country')}")
        return True
    else:
        print(f"\n✗ Minimal registration failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "TED BROKER FULL REGISTRATION TESTS" + " "*19 + "║")
    print("╚" + "="*68 + "╝")

    results = {"passed": 0, "failed": 0}

    # Test 1: Full registration
    registration_data, user_data = test_full_registration()
    if registration_data:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n✗ Cannot continue tests without successful registration")
        return results

    # Test 2: Login and fetch
    if test_login_and_fetch(user_data):
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Test 3: Minimal registration
    if test_minimal_registration():
        results["passed"] += 1
    else:
        results["failed"] += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✓ Passed: {results['passed']}")
    print(f"✗ Failed: {results['failed']}")
    print(f"Total: {results['passed'] + results['failed']}")

    if results["failed"] == 0:
        print("\n🎉 All tests passed! All registration fields are working correctly.")
        print("\nThe database now properly stores:")
        print("  • Email, username, password (required)")
        print("  • Full name, phone, gender, country (optional)")
        print("  • Account types/trading interests (optional array)")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")

    print("="*70)
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
