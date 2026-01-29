#!/usr/bin/env python3
"""Test script to verify withdrawal requests API"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import get_collection, WITHDRAWAL_REQUESTS_COLLECTION
from bson import ObjectId

def test_withdrawal_requests():
    """Test if there are any withdrawal requests in the database"""
    withdrawal_requests = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    # Get all withdrawal requests
    all_requests = list(withdrawal_requests.find())

    print(f"\n{'='*60}")
    print(f"WITHDRAWAL REQUESTS TEST")
    print(f"{'='*60}")
    print(f"\nTotal withdrawal requests in database: {len(all_requests)}")

    if all_requests:
        print(f"\nShowing first 5 requests:")
        for i, req in enumerate(all_requests[:5], 1):
            print(f"\n  Request #{i}:")
            print(f"    ID: {req.get('_id')}")
            print(f"    User ID: {req.get('user_id')}")
            print(f"    Amount: ${req.get('amount', 0):.2f}")
            print(f"    Method: {req.get('withdrawal_method', 'N/A')}")
            print(f"    Status: {req.get('status', 'N/A')}")
            print(f"    Created: {req.get('created_at', 'N/A')}")
    else:
        print("\n  ⚠ No withdrawal requests found in database!")

    # Check by status
    print(f"\n{'='*60}")
    print(f"WITHDRAWAL REQUESTS BY STATUS")
    print(f"{'='*60}")

    statuses = ["pending", "approved", "rejected", "processing", "completed"]
    for status_val in statuses:
        count = withdrawal_requests.count_documents({"status": status_val})
        print(f"  {status_val.upper():15} : {count}")

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    test_withdrawal_requests()
