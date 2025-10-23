"""
Script to mark all existing users as verified in the database
Run this script once to update all existing user records
"""
import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def mark_all_users_verified():
    """Mark all existing users as verified"""
    # Get MongoDB connection details from environment
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DB_NAME", "tedbrokers")

    # Connect to MongoDB
    client = MongoClient(mongo_uri)
    db = client[db_name]
    users_collection = db["users"]

    # Find all users that are not yet verified
    unverified_users = users_collection.find({"is_verified": False})
    unverified_count = users_collection.count_documents({"is_verified": False})

    print(f"Found {unverified_count} unverified users")

    if unverified_count == 0:
        print("All users are already verified!")
        return

    # Update all users to be verified
    result = users_collection.update_many(
        {"is_verified": False},
        {
            "$set": {
                "is_verified": True,
                "updated_at": datetime.utcnow()
            }
        }
    )

    print(f"Successfully marked {result.modified_count} users as verified")

    # Verify the update
    remaining_unverified = users_collection.count_documents({"is_verified": False})
    total_verified = users_collection.count_documents({"is_verified": True})

    print(f"\nVerification Summary:")
    print(f"- Total verified users: {total_verified}")
    print(f"- Remaining unverified users: {remaining_unverified}")

    # Close connection
    client.close()
    print("\nDatabase connection closed.")

if __name__ == "__main__":
    import sys

    print("=" * 50)
    print("TED Brokers - Mark All Users as Verified")
    print("=" * 50)
    print()

    # Check for --force flag to run without confirmation
    if "--force" in sys.argv:
        mark_all_users_verified()
        print("\nOperation completed successfully!")
    else:
        try:
            confirmation = input("This will mark ALL existing users as verified. Continue? (yes/no): ")
            if confirmation.lower() in ['yes', 'y']:
                mark_all_users_verified()
                print("\nOperation completed successfully!")
            else:
                print("Operation cancelled.")
        except EOFError:
            print("\nNo input provided. Use --force flag to run without confirmation.")
            print("Example: python3 mark_users_verified.py --force")
