from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import secrets

from app.schemas import (
    BankAccountCreate, BankAccountResponse,
    CryptoWithdrawalAddressCreate, CryptoWithdrawalAddressResponse,
    WithdrawalRequest, WithdrawalRequestResponse
)
from app.auth import get_current_user_token
from app.database import (
    get_collection, USERS_COLLECTION, USER_BANK_ACCOUNTS_COLLECTION,
    USER_CRYPTO_ADDRESSES_COLLECTION, WITHDRAWAL_REQUESTS_COLLECTION,
    TRANSACTIONS_COLLECTION
)

router = APIRouter(prefix="/api/withdrawals", tags=["Withdrawals"])


def get_user_by_id(user_id: str):
    """Get user by ID from database"""
    users = get_collection(USERS_COLLECTION)
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except:
        return None


# ==================== BANK ACCOUNT ENDPOINTS ====================

@router.post("/bank-accounts", response_model=BankAccountResponse)
async def create_bank_account(
    bank_data: BankAccountCreate,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Create a new bank account for withdrawals
    """
    bank_accounts_col = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    # Check if user already has bank accounts
    existing_accounts = list(bank_accounts_col.find({"user_id": current_user["user_id"]}))
    is_primary = len(existing_accounts) == 0  # First account is primary by default

    # Create bank account document
    bank_account = {
        "user_id": current_user["user_id"],
        "account_name": bank_data.account_name,
        "account_number": bank_data.account_number,
        "bank_name": bank_data.bank_name,
        "bank_branch": bank_data.bank_branch,
        "swift_code": bank_data.swift_code,
        "routing_number": bank_data.routing_number,
        "iban": bank_data.iban,
        "bank_address": bank_data.bank_address,
        "account_type": bank_data.account_type,
        "is_primary": is_primary,
        "is_verified": False,  # Requires admin verification
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert bank account
    result = bank_accounts_col.insert_one(bank_account)
    bank_account["_id"] = result.inserted_id

    return BankAccountResponse(
        id=str(bank_account["_id"]),
        user_id=bank_account["user_id"],
        account_name=bank_account["account_name"],
        account_number=bank_account["account_number"],
        bank_name=bank_account["bank_name"],
        bank_branch=bank_account.get("bank_branch"),
        swift_code=bank_account.get("swift_code"),
        routing_number=bank_account.get("routing_number"),
        iban=bank_account.get("iban"),
        bank_address=bank_account.get("bank_address"),
        account_type=bank_account.get("account_type"),
        is_primary=bank_account["is_primary"],
        is_verified=bank_account["is_verified"],
        created_at=bank_account["created_at"],
        updated_at=bank_account["updated_at"]
    )


@router.get("/bank-accounts", response_model=List[BankAccountResponse])
async def get_bank_accounts(current_user: dict = Depends(get_current_user_token)):
    """
    Get all bank accounts for the current user
    """
    bank_accounts_col = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    accounts = list(bank_accounts_col.find(
        {"user_id": current_user["user_id"]}
    ).sort("created_at", -1))

    return [
        BankAccountResponse(
            id=str(acc["_id"]),
            user_id=acc["user_id"],
            account_name=acc["account_name"],
            account_number=acc["account_number"],
            bank_name=acc["bank_name"],
            bank_branch=acc.get("bank_branch"),
            swift_code=acc.get("swift_code"),
            routing_number=acc.get("routing_number"),
            iban=acc.get("iban"),
            bank_address=acc.get("bank_address"),
            account_type=acc.get("account_type"),
            is_primary=acc["is_primary"],
            is_verified=acc["is_verified"],
            created_at=acc["created_at"],
            updated_at=acc["updated_at"]
        )
        for acc in accounts
    ]


@router.get("/bank-accounts/{account_id}", response_model=BankAccountResponse)
async def get_bank_account(
    account_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get a specific bank account
    """
    bank_accounts_col = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    try:
        account = bank_accounts_col.find_one({
            "_id": ObjectId(account_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    return BankAccountResponse(
        id=str(account["_id"]),
        user_id=account["user_id"],
        account_name=account["account_name"],
        account_number=account["account_number"],
        bank_name=account["bank_name"],
        bank_branch=account.get("bank_branch"),
        swift_code=account.get("swift_code"),
        routing_number=account.get("routing_number"),
        iban=account.get("iban"),
        bank_address=account.get("bank_address"),
        account_type=account.get("account_type"),
        is_primary=account["is_primary"],
        is_verified=account["is_verified"],
        created_at=account["created_at"],
        updated_at=account["updated_at"]
    )


@router.delete("/bank-accounts/{account_id}")
async def delete_bank_account(
    account_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Delete a bank account
    """
    bank_accounts_col = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    try:
        account = bank_accounts_col.find_one({
            "_id": ObjectId(account_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    # Delete the account
    bank_accounts_col.delete_one({"_id": ObjectId(account_id)})

    # If this was the primary account, set another account as primary
    if account["is_primary"]:
        remaining_accounts = list(bank_accounts_col.find(
            {"user_id": current_user["user_id"]}
        ).limit(1))

        if remaining_accounts:
            bank_accounts_col.update_one(
                {"_id": remaining_accounts[0]["_id"]},
                {"$set": {"is_primary": True, "updated_at": datetime.utcnow()}}
            )

    return {"message": "Bank account deleted successfully"}


@router.put("/bank-accounts/{account_id}/set-primary")
async def set_primary_bank_account(
    account_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Set a bank account as primary
    """
    bank_accounts_col = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    try:
        account = bank_accounts_col.find_one({
            "_id": ObjectId(account_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    # Unset all primary accounts for this user
    bank_accounts_col.update_many(
        {"user_id": current_user["user_id"]},
        {"$set": {"is_primary": False, "updated_at": datetime.utcnow()}}
    )

    # Set this account as primary
    bank_accounts_col.update_one(
        {"_id": ObjectId(account_id)},
        {"$set": {"is_primary": True, "updated_at": datetime.utcnow()}}
    )

    return {"message": "Primary bank account updated successfully"}


# ==================== CRYPTO ADDRESS ENDPOINTS ====================

@router.post("/crypto-addresses", response_model=CryptoWithdrawalAddressResponse)
async def create_crypto_address(
    crypto_data: CryptoWithdrawalAddressCreate,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Create a new cryptocurrency withdrawal address
    """
    crypto_addresses_col = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    # Check if user already has addresses for this currency
    existing_addresses = list(crypto_addresses_col.find({
        "user_id": current_user["user_id"],
        "currency": crypto_data.currency
    }))
    is_primary = len(existing_addresses) == 0  # First address for this currency is primary

    # Create crypto address document
    crypto_address = {
        "user_id": current_user["user_id"],
        "currency": crypto_data.currency,
        "wallet_address": crypto_data.wallet_address,
        "network": crypto_data.network,
        "label": crypto_data.label,
        "is_primary": is_primary,
        "is_verified": False,  # Requires admin verification
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert crypto address
    result = crypto_addresses_col.insert_one(crypto_address)
    crypto_address["_id"] = result.inserted_id

    return CryptoWithdrawalAddressResponse(
        id=str(crypto_address["_id"]),
        user_id=crypto_address["user_id"],
        currency=crypto_address["currency"],
        wallet_address=crypto_address["wallet_address"],
        network=crypto_address.get("network"),
        label=crypto_address.get("label"),
        is_primary=crypto_address["is_primary"],
        is_verified=crypto_address["is_verified"],
        created_at=crypto_address["created_at"],
        updated_at=crypto_address["updated_at"]
    )


@router.get("/crypto-addresses", response_model=List[CryptoWithdrawalAddressResponse])
async def get_crypto_addresses(
    currency: Optional[str] = None,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get all crypto addresses for the current user
    Optionally filter by currency
    """
    crypto_addresses_col = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    query = {"user_id": current_user["user_id"]}
    if currency:
        query["currency"] = currency.upper()

    addresses = list(crypto_addresses_col.find(query).sort("created_at", -1))

    return [
        CryptoWithdrawalAddressResponse(
            id=str(addr["_id"]),
            user_id=addr["user_id"],
            currency=addr["currency"],
            wallet_address=addr["wallet_address"],
            network=addr.get("network"),
            label=addr.get("label"),
            is_primary=addr["is_primary"],
            is_verified=addr["is_verified"],
            created_at=addr["created_at"],
            updated_at=addr["updated_at"]
        )
        for addr in addresses
    ]


@router.get("/crypto-addresses/{address_id}", response_model=CryptoWithdrawalAddressResponse)
async def get_crypto_address(
    address_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get a specific crypto address
    """
    crypto_addresses_col = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    try:
        address = crypto_addresses_col.find_one({
            "_id": ObjectId(address_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid address ID"
        )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crypto address not found"
        )

    return CryptoWithdrawalAddressResponse(
        id=str(address["_id"]),
        user_id=address["user_id"],
        currency=address["currency"],
        wallet_address=address["wallet_address"],
        network=address.get("network"),
        label=address.get("label"),
        is_primary=address["is_primary"],
        is_verified=address["is_verified"],
        created_at=address["created_at"],
        updated_at=address["updated_at"]
    )


@router.delete("/crypto-addresses/{address_id}")
async def delete_crypto_address(
    address_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Delete a crypto address
    """
    crypto_addresses_col = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    try:
        address = crypto_addresses_col.find_one({
            "_id": ObjectId(address_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid address ID"
        )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crypto address not found"
        )

    # Delete the address
    crypto_addresses_col.delete_one({"_id": ObjectId(address_id)})

    # If this was the primary address for this currency, set another address as primary
    if address["is_primary"]:
        remaining_addresses = list(crypto_addresses_col.find({
            "user_id": current_user["user_id"],
            "currency": address["currency"]
        }).limit(1))

        if remaining_addresses:
            crypto_addresses_col.update_one(
                {"_id": remaining_addresses[0]["_id"]},
                {"$set": {"is_primary": True, "updated_at": datetime.utcnow()}}
            )

    return {"message": "Crypto address deleted successfully"}


@router.put("/crypto-addresses/{address_id}/set-primary")
async def set_primary_crypto_address(
    address_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Set a crypto address as primary for its currency
    """
    crypto_addresses_col = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    try:
        address = crypto_addresses_col.find_one({
            "_id": ObjectId(address_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid address ID"
        )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crypto address not found"
        )

    # Unset all primary addresses for this user and currency
    crypto_addresses_col.update_many(
        {
            "user_id": current_user["user_id"],
            "currency": address["currency"]
        },
        {"$set": {"is_primary": False, "updated_at": datetime.utcnow()}}
    )

    # Set this address as primary
    crypto_addresses_col.update_one(
        {"_id": ObjectId(address_id)},
        {"$set": {"is_primary": True, "updated_at": datetime.utcnow()}}
    )

    return {"message": "Primary crypto address updated successfully"}


# ==================== WITHDRAWAL REQUEST ENDPOINTS ====================

@router.post("/request")
async def create_withdrawal_request(
    withdrawal_data: WithdrawalRequest,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Create a withdrawal request
    Requires sufficient balance and verified withdrawal account
    """
    users_col = get_collection(USERS_COLLECTION)
    withdrawal_requests_col = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    # Get user
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check user balance
    current_balance = user.get("wallet_balance", 0.0)
    if current_balance < withdrawal_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Current balance: ${current_balance:.2f}"
        )

    # Get withdrawal account details
    account_details = {}
    if withdrawal_data.withdrawal_method == "bank":
        bank_accounts_col = get_collection(USER_BANK_ACCOUNTS_COLLECTION)
        try:
            account = bank_accounts_col.find_one({
                "_id": ObjectId(withdrawal_data.account_id),
                "user_id": current_user["user_id"]
            })
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid bank account ID"
            )

        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank account not found"
            )

        if not account.get("is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bank account is not verified. Please contact support."
            )

        account_details = {
            "type": "bank",
            "account_name": account["account_name"],
            "account_number": account["account_number"],
            "bank_name": account["bank_name"],
            "swift_code": account.get("swift_code"),
            "iban": account.get("iban")
        }

    elif withdrawal_data.withdrawal_method == "crypto":
        crypto_addresses_col = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)
        try:
            address = crypto_addresses_col.find_one({
                "_id": ObjectId(withdrawal_data.account_id),
                "user_id": current_user["user_id"]
            })
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid crypto address ID"
            )

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Crypto address not found"
            )

        if not address.get("is_verified", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Crypto address is not verified. Please contact support."
            )

        account_details = {
            "type": "crypto",
            "currency": address["currency"],
            "wallet_address": address["wallet_address"],
            "network": address.get("network"),
            "label": address.get("label")
        }

    # Create withdrawal request
    withdrawal_request = {
        "user_id": current_user["user_id"],
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "amount": withdrawal_data.amount,
        "withdrawal_method": withdrawal_data.withdrawal_method,
        "account_id": withdrawal_data.account_id,
        "account_details": account_details,
        "notes": withdrawal_data.notes,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reviewed_by": None,
        "reviewed_at": None,
        "completed_at": None
    }

    # Insert withdrawal request
    result = withdrawal_requests_col.insert_one(withdrawal_request)
    withdrawal_request["_id"] = result.inserted_id

    return {
        "message": "Withdrawal request submitted successfully. Please wait for admin approval.",
        "request_id": str(withdrawal_request["_id"]),
        "status": withdrawal_request["status"],
        "amount": withdrawal_request["amount"]
    }


@router.get("/requests")
async def get_withdrawal_requests(
    current_user: dict = Depends(get_current_user_token),
    status_filter: Optional[str] = None
):
    """
    Get all withdrawal requests for the current user
    """
    withdrawal_requests_col = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    # Build query
    query = {"user_id": current_user["user_id"]}
    if status_filter:
        query["status"] = status_filter

    # Get requests
    requests = list(withdrawal_requests_col.find(query).sort("created_at", -1))

    return {
        "requests": [
            {
                "id": str(req["_id"]),
                "amount": req["amount"],
                "withdrawal_method": req["withdrawal_method"],
                "account_details": req["account_details"],
                "status": req["status"],
                "notes": req.get("notes"),
                "created_at": req["created_at"].isoformat(),
                "reviewed_at": req["reviewed_at"].isoformat() if req.get("reviewed_at") else None,
                "completed_at": req["completed_at"].isoformat() if req.get("completed_at") else None
            }
            for req in requests
        ]
    }


@router.get("/requests/{request_id}")
async def get_withdrawal_request(
    request_id: str,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Get a specific withdrawal request
    """
    withdrawal_requests_col = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    try:
        request = withdrawal_requests_col.find_one({
            "_id": ObjectId(request_id),
            "user_id": current_user["user_id"]
        })
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal request not found"
        )

    return {
        "id": str(request["_id"]),
        "amount": request["amount"],
        "withdrawal_method": request["withdrawal_method"],
        "account_details": request["account_details"],
        "status": request["status"],
        "notes": request.get("notes"),
        "created_at": request["created_at"].isoformat(),
        "reviewed_at": request["reviewed_at"].isoformat() if request.get("reviewed_at") else None,
        "completed_at": request["completed_at"].isoformat() if request.get("completed_at") else None
    }
