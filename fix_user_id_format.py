#!/usr/bin/env python3
"""
Script to check and fix user_id format inconsistencies in transactions.
Some transactions might have user_id as ObjectId instead of string.
"""

from pymongo import MongoClient
from bson import ObjectId
import os

# Get MongoDB connection string from environment or use default
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'tedbroker'

def check_user_id_formats():
    """Check if transactions have user_id stored as ObjectId vs string"""

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    transactions = db['transactions']

    print("Checking user_id format in transactions...")
    print("=" * 70)

    # Get all transactions
    all_transactions = list(transactions.find({}))

    if not all_transactions:
        print("No transactions found.")
        client.close()
        return

    print(f"Found {len(all_transactions)} transaction(s).\n")

    # Check each transaction
    objectid_count = 0
    string_count = 0
    problematic_transactions = []

    for txn in all_transactions:
        user_id = txn.get('user_id')
        if isinstance(user_id, ObjectId):
            objectid_count += 1
            problematic_transactions.append(txn)
            print(f"⚠ Transaction {txn['_id']} has user_id as ObjectId: {user_id}")
            print(f"   Type: {txn.get('transaction_type')}, Status: {txn.get('status')}, Amount: ${txn.get('amount')}")
        elif isinstance(user_id, str):
            string_count += 1

    print(f"\nSummary:")
    print(f"  - Transactions with user_id as string: {string_count} ✓")
    print(f"  - Transactions with user_id as ObjectId: {objectid_count} {'⚠' if objectid_count > 0 else '✓'}")

    if problematic_transactions:
        print(f"\nFound {len(problematic_transactions)} transaction(s) with ObjectId user_id.")
        response = input("\nDo you want to convert them to strings? (yes/no): ").strip().lower()

        if response == 'yes':
            for txn in problematic_transactions:
                transactions.update_one(
                    {"_id": txn["_id"]},
                    {"$set": {"user_id": str(txn["user_id"])}}
                )
            print(f"✓ Converted {len(problematic_transactions)} user_id(s) to string format.")
        else:
            print("No changes made.")
    else:
        print("\n✓ All transactions have user_id in correct string format.")

    client.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        check_user_id_formats()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
