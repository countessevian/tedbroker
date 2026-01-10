"""
Migration script to update all existing users' referral codes to their usernames
"""

from datetime import datetime
from app.database import get_collection, USERS_COLLECTION

def migrate_referral_codes():
    """
    Update all existing users' referral codes to use their usernames
    """
    users = get_collection(USERS_COLLECTION)

    # Get all users
    all_users = list(users.find({}))

    print(f"Found {len(all_users)} users in the database")

    updated_count = 0
    skipped_count = 0
    error_count = 0

    for user in all_users:
        username = user.get("username")
        current_referral_code = user.get("referral_code")

        # Skip users without usernames
        if not username:
            print(f"⚠ Skipping user {user.get('_id')} - no username")
            skipped_count += 1
            continue

        # Check if referral code needs updating
        if current_referral_code == username:
            print(f"✓ User {username} already has correct referral code")
            continue

        try:
            # Update referral code to username
            result = users.update_one(
                {"_id": user["_id"]},
                {
                    "$set": {
                        "referral_code": username,
                        "updated_at": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                print(f"✓ Updated user {username}: {current_referral_code} -> {username}")
                updated_count += 1
            else:
                print(f"⚠ No changes made for user {username}")

        except Exception as e:
            print(f"✗ Error updating user {username}: {str(e)}")
            error_count += 1

    print("\n" + "="*60)
    print("Migration Summary:")
    print(f"  Total users: {len(all_users)}")
    print(f"  Updated: {updated_count}")
    print(f"  Skipped (no username): {skipped_count}")
    print(f"  Errors: {error_count}")
    print("="*60)

    return {
        "total": len(all_users),
        "updated": updated_count,
        "skipped": skipped_count,
        "errors": error_count
    }


if __name__ == "__main__":
    print("Starting referral code migration...")
    print("This will update all users' referral codes to their usernames\n")

    result = migrate_referral_codes()

    if result["errors"] == 0:
        print("\n✓ Migration completed successfully!")
    else:
        print(f"\n⚠ Migration completed with {result['errors']} errors")
