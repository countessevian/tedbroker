#!/usr/bin/env python3
"""
Script to clean up orphaned pending withdrawal transactions.
This will cancel all pending withdrawals that were created before the proper implementation.
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os

# Get MongoDB connection string from environment or use default
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'tedbroker'

def cleanup_pending_withdrawals():
    """Cancel all pending withdrawal transactions"""

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    transactions = db['transactions']

    print("Cleaning up pending withdrawal transactions...")
    print("=" * 60)

    # Find all pending withdrawals
    pending_withdrawals = list(transactions.find({
        "transaction_type": "withdrawal",
        "status": "pending"
    }))

    if not pending_withdrawals:
        print("✓ No pending withdrawals found. Database is clean.")
        return

    print(f"Found {len(pending_withdrawals)} pending withdrawal(s):\n")

    # Display each pending withdrawal
    for idx, txn in enumerate(pending_withdrawals, 1):
        print(f"{idx}. Transaction ID: {txn['_id']}")
        print(f"   User ID: {txn['user_id']}")
        print(f"   Amount: ${txn['amount']}")
        print(f"   Payment Method: {txn.get('payment_method', 'N/A')}")
        print(f"   Created: {txn.get('created_at', 'N/A')}")
        print(f"   Reference: {txn.get('reference_number', 'N/A')}")

        # Check if it has payment_details (proper implementation)
        has_payment_details = bool(txn.get('payment_details'))
        print(f"   Has Payment Details: {'Yes' if has_payment_details else 'No (Orphaned)'}")
        print()

    # Ask for confirmation
    response = input("\nDo you want to cancel ALL these pending withdrawals? (yes/no): ").strip().lower()

    if response != 'yes':
        print("Operation cancelled.")
        return

    # Cancel all pending withdrawals
    result = transactions.update_many(
        {
            "transaction_type": "withdrawal",
            "status": "pending"
        },
        {
            "$set": {
                "status": "cancelled",
                "description": "Cancelled - System cleanup of orphaned transactions",
                "updated_at": datetime.utcnow()
            }
        }
    )

    print(f"\n✓ Successfully cancelled {result.modified_count} pending withdrawal(s).")
    print("Users will no longer see pending withdrawal indicators.")

    client.close()

if __name__ == "__main__":
    try:
        cleanup_pending_withdrawals()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
