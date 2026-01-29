"""
Test script to verify the updated referral system works correctly
"""

from app.database import get_collection, USERS_COLLECTION
from app.referrals_service import referrals_service

def test_referral_system():
    """
    Test the referral system with username-based codes
    """
    users = get_collection(USERS_COLLECTION)

    print("Testing Username-Based Referral System")
    print("=" * 60)

    # Get a sample user
    sample_user = users.find_one({"username": {"$exists": True}})

    if not sample_user:
        print("✗ No users found in database")
        return False

    user_id = str(sample_user["_id"])
    username = sample_user.get("username")

    print(f"\nTest User: {username}")
    print(f"User ID: {user_id}")

    # Test 1: Get referral link
    print("\n" + "-" * 60)
    print("Test 1: Generate Referral Link")
    try:
        referral_link = referrals_service.get_referral_link(user_id)
        print(f"✓ Referral Link: {referral_link}")

        # Verify it contains the username
        if username in referral_link:
            print(f"✓ Referral link contains username: {username}")
        else:
            print(f"✗ Referral link does NOT contain username")
            return False
    except Exception as e:
        print(f"✗ Error generating referral link: {str(e)}")
        return False

    # Test 2: Get referral code
    print("\n" + "-" * 60)
    print("Test 2: Get Referral Code")
    try:
        referral_code = referrals_service.get_referral_code_by_user_id(user_id)
        print(f"✓ Referral Code: {referral_code}")

        # Verify it matches username
        if referral_code == username:
            print(f"✓ Referral code matches username: {username}")
        else:
            print(f"✗ Referral code ({referral_code}) does NOT match username ({username})")
            return False
    except Exception as e:
        print(f"✗ Error getting referral code: {str(e)}")
        return False

    # Test 3: Verify database has username as referral_code
    print("\n" + "-" * 60)
    print("Test 3: Verify Database")
    try:
        user_from_db = users.find_one({"username": username})
        db_referral_code = user_from_db.get("referral_code")

        print(f"Database referral_code: {db_referral_code}")

        if db_referral_code == username:
            print(f"✓ Database referral_code matches username")
        else:
            print(f"✗ Database referral_code ({db_referral_code}) does NOT match username")
            return False
    except Exception as e:
        print(f"✗ Error checking database: {str(e)}")
        return False

    # Test 4: Lookup user by referral code (username)
    print("\n" + "-" * 60)
    print("Test 4: Lookup User by Referral Code (Username)")
    try:
        found_user = users.find_one({"referral_code": username})

        if found_user:
            found_username = found_user.get("username")
            print(f"✓ Found user by referral code: {found_username}")

            if found_username == username:
                print(f"✓ Correctly found the same user")
            else:
                print(f"✗ Found different user")
                return False
        else:
            print(f"✗ Could not find user by referral code")
            return False
    except Exception as e:
        print(f"✗ Error looking up user: {str(e)}")
        return False

    # Test 5: Check all users have username as referral code
    print("\n" + "-" * 60)
    print("Test 5: Verify All Users")
    try:
        all_users = list(users.find({"username": {"$exists": True}}))
        mismatched = []

        for user in all_users:
            user_username = user.get("username")
            user_ref_code = user.get("referral_code")

            if user_username != user_ref_code:
                mismatched.append({
                    "username": user_username,
                    "referral_code": user_ref_code
                })

        if len(mismatched) == 0:
            print(f"✓ All {len(all_users)} users have username as referral code")
        else:
            print(f"✗ Found {len(mismatched)} users with mismatched codes:")
            for user in mismatched:
                print(f"  - {user['username']}: {user['referral_code']}")
            return False
    except Exception as e:
        print(f"✗ Error checking all users: {str(e)}")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_referral_system()
    exit(0 if success else 1)
