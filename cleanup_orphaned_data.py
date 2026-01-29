#!/usr/bin/env python3
"""
Comprehensive script to clean up all orphaned or problematic withdrawal data.
This should be run whenever there are sync issues between user and admin dashboards.
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os

# Get MongoDB connection string from environment or use default
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'tedbroker'

def cleanup_all_orphaned_data():
    """Clean up all orphaned withdrawal-related data"""

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print("=" * 70)
    print("COMPREHENSIVE WITHDRAWAL DATA CLEANUP")
    print("=" * 70)

    total_cleaned = 0

    # 1. Cancel all pending withdrawal transactions
    print("\n1. Checking TRANSACTIONS collection for pending withdrawals...")
    print("-" * 70)
    transactions = db['transactions']

    pending_tx_withdrawals = list(transactions.find({
        "transaction_type": "withdrawal",
        "status": "pending"
    }))

    if pending_tx_withdrawals:
        print(f"   Found {len(pending_tx_withdrawals)} pending withdrawal transaction(s):")
        for txn in pending_tx_withdrawals:
            print(f"   - ID: {txn['_id']}, Amount: ${txn.get('amount')}, User: {txn.get('user_id')}")

        response = input("\n   Cancel these transactions? (yes/no): ").strip().lower()
        if response == 'yes':
            result = transactions.update_many(
                {
                    "transaction_type": "withdrawal",
                    "status": "pending"
                },
                {
                    "$set": {
                        "status": "cancelled",
                        "description": "Cancelled - Administrative cleanup",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            print(f"   ✓ Cancelled {result.modified_count} transaction(s).")
            total_cleaned += result.modified_count
        else:
            print("   Skipped.")
    else:
        print("   ✓ No pending withdrawal transactions found.")

    # 2. Cancel all pending withdrawal requests
    print("\n2. Checking WITHDRAWAL_REQUESTS collection...")
    print("-" * 70)
    withdrawal_requests = db['withdrawal_requests']

    pending_requests = list(withdrawal_requests.find({"status": "pending"}))

    if pending_requests:
        print(f"   Found {len(pending_requests)} pending withdrawal request(s):")
        for req in pending_requests:
            print(f"   - ID: {req['_id']}, Amount: ${req.get('amount')}, User: {req.get('username')} ({req.get('email')})")

        response = input("\n   Cancel these requests? (yes/no): ").strip().lower()
        if response == 'yes':
            result = withdrawal_requests.update_many(
                {"status": "pending"},
                {
                    "$set": {
                        "status": "cancelled",
                        "reviewed_by": "admin",
                        "reviewed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            print(f"   ✓ Cancelled {result.modified_count} request(s).")
            total_cleaned += result.modified_count
        else:
            print("   Skipped.")
    else:
        print("   ✓ No pending withdrawal requests found.")

    # 3. Fix user_id format inconsistencies
    print("\n3. Checking for user_id format inconsistencies...")
    print("-" * 70)

    objectid_transactions = list(transactions.find({
        "user_id": {"$type": "objectId"}
    }))

    if objectid_transactions:
        print(f"   Found {len(objectid_transactions)} transaction(s) with ObjectId user_id format.")
        response = input("   Convert to string format? (yes/no): ").strip().lower()
        if response == 'yes':
            for txn in objectid_transactions:
                transactions.update_one(
                    {"_id": txn["_id"]},
                    {"$set": {"user_id": str(txn["user_id"])}}
                )
            print(f"   ✓ Converted {len(objectid_transactions)} user_id(s) to string format.")
            total_cleaned += len(objectid_transactions)
        else:
            print("   Skipped.")
    else:
        print("   ✓ No format inconsistencies found.")

    # 4. Summary
    print("\n" + "=" * 70)
    print(f"CLEANUP COMPLETE: {total_cleaned} item(s) cleaned up.")
    print("=" * 70)

    if total_cleaned > 0:
        print("\nRecommendation: Ask users to:")
        print("  1. Hard refresh their browser (Ctrl+F5 or Cmd+Shift+R)")
        print("  2. Clear browser cache")
        print("  3. Log out and log back in")

    client.close()

if __name__ == "__main__":
    try:
        cleanup_all_orphaned_data()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
