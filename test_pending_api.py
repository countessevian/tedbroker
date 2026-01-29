#!/usr/bin/env python3
"""
Script to test what the pending-transactions API returns for a user.
"""

from pymongo import MongoClient
from bson import ObjectId
import os

# Get MongoDB connection string from environment or use default
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = 'tedbroker'

def test_pending_transactions_api():
    """Simulate the /api/wallet/pending-transactions endpoint"""

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    transactions = db['transactions']
    users = db['users']

    print("Testing pending-transactions API logic...")
    print("=" * 70)

    # Get all users
    all_users = list(users.find({}, {"_id": 1, "email": 1, "username": 1}))

    if not all_users:
        print("No users found in database.")
        client.close()
        return

    print(f"Found {len(all_users)} user(s) in database.\n")

    # Check pending transactions for each user
    for user in all_users:
        user_id = str(user['_id'])
        email = user.get('email', 'N/A')
        username = user.get('username', 'N/A')

        print(f"User: {username} ({email})")
        print(f"User ID: {user_id}")
        print("-" * 70)

        # Find pending deposits
        pending_deposits = list(transactions.find({
            "user_id": user_id,
            "transaction_type": "deposit",
            "status": "pending"
        }))

        # Find pending withdrawals
        pending_withdrawals = list(transactions.find({
            "user_id": user_id,
            "transaction_type": "withdrawal",
            "status": "pending"
        }))

        # Calculate totals
        total_pending_deposits = sum(txn["amount"] for txn in pending_deposits)
        total_pending_withdrawals = sum(txn["amount"] for txn in pending_withdrawals)

        print(f"Pending Deposits: {len(pending_deposits)} (Total: ${total_pending_deposits})")
        if pending_deposits:
            for dep in pending_deposits:
                print(f"  - {dep['_id']}: ${dep['amount']} ({dep.get('payment_method', 'N/A')})")

        print(f"Pending Withdrawals: {len(pending_withdrawals)} (Total: ${total_pending_withdrawals})")
        if pending_withdrawals:
            for wth in pending_withdrawals:
                print(f"  - {wth['_id']}: ${wth['amount']} ({wth.get('payment_method', 'N/A')})")

        print()

    client.close()
    print("=" * 70)

if __name__ == "__main__":
    try:
        test_pending_transactions_api()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
