"""
Script to create a test bank account for deposits
"""

from datetime import datetime
from app.database import get_collection, BANK_ACCOUNTS_COLLECTION

def create_test_bank_account():
    """
    Create a test bank account for testing the deposit flow
    """
    bank_accounts = get_collection(BANK_ACCOUNTS_COLLECTION)

    # Check if there's already an active account
    existing = bank_accounts.find_one({"is_active": True})

    if existing:
        print("✓ Active bank account already exists:")
        print(f"  Bank Name: {existing.get('bank_name')}")
        print(f"  Account Name: {existing.get('account_name')}")
        print(f"  Account Number: {existing.get('account_number')}")
        if existing.get('swift_code'):
            print(f"  SWIFT Code: {existing.get('swift_code')}")
        if existing.get('routing_number'):
            print(f"  Routing Number: {existing.get('routing_number')}")
        return

    # Create a test bank account
    test_account = {
        "bank_name": "TED Brokers International Bank",
        "account_name": "TED Brokers LLC",
        "account_number": "9876543210",
        "routing_number": "021000021",
        "swift_code": "TEDBROUS33XXX",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    result = bank_accounts.insert_one(test_account)

    print("✓ Test bank account created successfully!")
    print(f"  ID: {result.inserted_id}")
    print(f"  Bank Name: {test_account['bank_name']}")
    print(f"  Account Name: {test_account['account_name']}")
    print(f"  Account Number: {test_account['account_number']}")
    print(f"  Routing Number: {test_account['routing_number']}")
    print(f"  SWIFT Code: {test_account['swift_code']}")


if __name__ == "__main__":
    print("Creating test bank account...")
    create_test_bank_account()
