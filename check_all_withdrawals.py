#!/usr/bin/env python3
"""
Script to check all withdrawal-related collections for pending items.
"""

from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os

# Get MongoDB connection string from environment or use default
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'tedbroker'

def check_all_withdrawals():
    """Check all withdrawal-related collections"""

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    print("Checking all withdrawal-related data...")
    print("=" * 70)

    # 1. Check TRANSACTIONS collection for withdrawals
    print("\n1. TRANSACTIONS COLLECTION - Withdrawals:")
    print("-" * 70)
    transactions = db['transactions']
    all_withdrawals = list(transactions.find({"transaction_type": "withdrawal"}))

    if all_withdrawals:
        print(f"   Total withdrawals: {len(all_withdrawals)}")
        for status in ['pending', 'completed', 'rejected', 'cancelled']:
            count = len([w for w in all_withdrawals if w.get('status') == status])
            if count > 0:
                print(f"   - {status.capitalize()}: {count}")

        print("\n   Details:")
        for idx, txn in enumerate(all_withdrawals, 1):
            print(f"\n   {idx}. ID: {txn['_id']}")
            print(f"      User ID: {txn.get('user_id')}")
            print(f"      Amount: ${txn.get('amount')}")
            print(f"      Status: {txn.get('status')}")
            print(f"      Method: {txn.get('payment_method')}")
            print(f"      Created: {txn.get('created_at')}")
    else:
        print("   No withdrawal transactions found.")

    # 2. Check WITHDRAWAL_REQUESTS collection
    print("\n\n2. WITHDRAWAL_REQUESTS COLLECTION:")
    print("-" * 70)
    withdrawal_requests = db['withdrawal_requests']
    all_requests = list(withdrawal_requests.find({}))

    if all_requests:
        print(f"   Total withdrawal requests: {len(all_requests)}")
        for status in ['pending', 'completed', 'rejected', 'cancelled']:
            count = len([w for w in all_requests if w.get('status') == status])
            if count > 0:
                print(f"   - {status.capitalize()}: {count}")

        print("\n   Details:")
        for idx, req in enumerate(all_requests, 1):
            print(f"\n   {idx}. ID: {req['_id']}")
            print(f"      User ID: {req.get('user_id')}")
            print(f"      Username: {req.get('username')}")
            print(f"      Email: {req.get('email')}")
            print(f"      Amount: ${req.get('amount')}")
            print(f"      Status: {req.get('status')}")
            print(f"      Method: {req.get('withdrawal_method')}")
            print(f"      Created: {req.get('created_at')}")
    else:
        print("   No withdrawal requests found.")

    # 3. Check users collection for pending withdrawal data
    print("\n\n3. CHECKING USERS WITH WALLET DATA:")
    print("-" * 70)
    users = db['users']
    users_with_balance = list(users.find(
        {"wallet_balance": {"$exists": True}},
        {"_id": 1, "email": 1, "username": 1, "wallet_balance": 1}
    ))

    if users_with_balance:
        print(f"   Found {len(users_with_balance)} users with wallet data:")
        for user in users_with_balance:
            print(f"\n   - User ID: {user['_id']}")
            print(f"     Email: {user.get('email')}")
            print(f"     Username: {user.get('username')}")
            print(f"     Balance: ${user.get('wallet_balance', 0)}")
    else:
        print("   No users with wallet data found.")

    client.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    try:
        check_all_withdrawals()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
