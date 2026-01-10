from fastapi import APIRouter, HTTPException, status, Depends, Body
from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any
import secrets
from pydantic import BaseModel

from app.schemas import TransactionResponse
from app.auth import get_current_user_token, verify_password
from app.database import get_collection, USERS_COLLECTION, TRANSACTIONS_COLLECTION, DEPOSIT_REQUESTS_COLLECTION, WITHDRAWAL_REQUESTS_COLLECTION, BANK_ACCOUNTS_COLLECTION

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])


class DepositRequest(BaseModel):
    amount: float
    payment_method: str
    password: str
    # Optional fields for different payment methods
    bank_name: Optional[str] = None
    reference_number: Optional[str] = None
    crypto_type: Optional[str] = None
    wallet_address: Optional[str] = None  # Admin's wallet address shown to user


class WithdrawalRequest(BaseModel):
    amount: float
    withdrawal_method: str
    password: str
    crypto_type: Optional[str] = None
    wallet_address: Optional[str] = None


def get_user_by_id(user_id: str):
    """Get user by ID from database"""
    users = get_collection(USERS_COLLECTION)
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except:
        return None


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(current_user: dict = Depends(get_current_user_token)):
    """Get all transactions for the current user"""
    transactions_col = get_collection(TRANSACTIONS_COLLECTION)

    # Fetch all transactions for this user, sorted by created_at (newest first)
    transactions = list(transactions_col.find(
        {"user_id": current_user["user_id"]}
    ).sort("created_at", -1))

    # Convert MongoDB documents to response models
    return [
        TransactionResponse(
            id=str(txn["_id"]),
            transaction_type=txn["transaction_type"],
            amount=txn["amount"],
            status=txn["status"],
            payment_method=txn["payment_method"],
            reference_number=txn["reference_number"],
            description=txn.get("description"),
            created_at=txn["created_at"]
        )
        for txn in transactions
    ]


@router.post("/deposit")
async def create_deposit(
    deposit_data: DepositRequest,
    current_user: dict = Depends(get_current_user_token)
):
    """Create a deposit transaction"""
    if deposit_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )

    if deposit_data.amount > 1000000:  # Max deposit limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum deposit amount is $1,000,000"
        )

    users = get_collection(USERS_COLLECTION)
    transactions_col = get_collection(TRANSACTIONS_COLLECTION)
    deposit_requests_col = get_collection(DEPOSIT_REQUESTS_COLLECTION)

    # Get user
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate unique reference number
    reference_number = deposit_data.reference_number or f"DEP-{secrets.token_hex(8).upper()}"

    # Prepare payment details
    payment_details = {}
    if deposit_data.payment_method == "Bank Transfer":
        payment_details["bank_name"] = deposit_data.bank_name
        payment_details["reference_number"] = deposit_data.reference_number
    elif deposit_data.payment_method == "Cryptocurrency":
        payment_details["crypto_type"] = deposit_data.crypto_type
        payment_details["wallet_address"] = deposit_data.wallet_address  # Admin's wallet address where user sent payment
    elif deposit_data.payment_method == "PayPal":
        # PayPal is not currently available, but we accept the selection
        # No additional details needed for now
        pass

    # Create transaction record with pending status
    transaction = {
        "user_id": current_user["user_id"],
        "transaction_type": "deposit",
        "amount": deposit_data.amount,
        "status": "pending",  # Requires admin approval
        "payment_method": deposit_data.payment_method,
        "reference_number": reference_number,
        "payment_details": payment_details,
        "description": f"Deposit via {deposit_data.payment_method}",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert transaction
    result = transactions_col.insert_one(transaction)
    transaction["_id"] = result.inserted_id

    # Also create deposit request for admin dashboard
    deposit_request = {
        "user_id": current_user["user_id"],
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "amount": deposit_data.amount,
        "payment_method": deposit_data.payment_method,
        "payment_proof": payment_details.get("wallet_address") or payment_details.get("reference_number"),
        "notes": None,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reviewed_by": None,
        "reviewed_at": None
    }
    deposit_requests_col.insert_one(deposit_request)

    # Note: Wallet balance will be updated only when admin approves the deposit
    current_balance = user.get("wallet_balance", 0.0)

    return {
        "message": "Deposit request submitted successfully. Your funds will be available once confirmed on-chain.",
        "transaction": TransactionResponse(
            id=str(transaction["_id"]),
            transaction_type=transaction["transaction_type"],
            amount=transaction["amount"],
            status=transaction["status"],
            payment_method=transaction["payment_method"],
            reference_number=transaction["reference_number"],
            description=transaction.get("description"),
            created_at=transaction["created_at"]
        ),
        "current_balance": current_balance
    }


@router.post("/withdraw")
async def create_withdrawal(
    withdrawal_data: WithdrawalRequest,
    current_user: dict = Depends(get_current_user_token)
):
    """Create a withdrawal transaction"""
    if withdrawal_data.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be greater than 0"
        )

    users = get_collection(USERS_COLLECTION)
    transactions_col = get_collection(TRANSACTIONS_COLLECTION)
    withdrawal_requests_col = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify password only for users who have passwords (non-OAuth users)
    user_password = user.get("password")
    if user_password and withdrawal_data.password:
        # User has a password set, verify it
        try:
            if not verify_password(withdrawal_data.password, user_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password"
                )
        except Exception:
            # If password verification fails (e.g., invalid hash), reject
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
    # For OAuth users without passwords, they're already authenticated via JWT, so allow withdrawal

    current_balance = user.get("wallet_balance", 0.0)
    if current_balance < withdrawal_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Current balance: ${current_balance:.2f}"
        )

    reference_number = f"WTH-{secrets.token_hex(8).upper()}"
    payment_details = {}

    if withdrawal_data.withdrawal_method == "Cryptocurrency":
        if not withdrawal_data.crypto_type or not withdrawal_data.wallet_address:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Crypto withdrawal requires crypto_type and wallet_address"
            )
        payment_details["crypto_type"] = withdrawal_data.crypto_type
        payment_details["wallet_address"] = withdrawal_data.wallet_address

    # Additional handling can be added here for other withdrawal methods

    transaction = {
        "user_id": current_user["user_id"],
        "transaction_type": "withdrawal",
        "amount": withdrawal_data.amount,
        "status": "pending",  # Requires admin approval
        "payment_method": withdrawal_data.withdrawal_method,
        "reference_number": reference_number,
        "payment_details": payment_details,
        "description": f"Withdrawal to {withdrawal_data.withdrawal_method}",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = transactions_col.insert_one(transaction)
    transaction["_id"] = result.inserted_id

    # Also create withdrawal request for admin dashboard
    withdrawal_request = {
        "user_id": current_user["user_id"],
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "amount": withdrawal_data.amount,
        "withdrawal_method": withdrawal_data.withdrawal_method,
        "account_id": None,  # Simple withdrawal doesn't require account_id
        "account_details": {
            "type": "crypto" if withdrawal_data.withdrawal_method == "Cryptocurrency" else "other",
            "crypto_type": payment_details.get("crypto_type"),
            "wallet_address": payment_details.get("wallet_address")
        },
        "notes": None,
        "status": "pending",
        "transaction_id": str(transaction["_id"]),  # Link to transaction
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reviewed_by": None,
        "reviewed_at": None,
        "completed_at": None
    }
    withdrawal_requests_col.insert_one(withdrawal_request)

    return {
        "message": "Withdrawal request submitted successfully. Your request will be processed confirmed on-chain.",
        "transaction": TransactionResponse(
            id=str(transaction["_id"]),
            transaction_type=transaction["transaction_type"],
            amount=transaction["amount"],
            status=transaction["status"],
            payment_method=transaction["payment_method"],
            reference_number=transaction["reference_number"],
            description=transaction.get("description"),
            created_at=transaction["created_at"]
        ),
        "current_balance": current_balance
    }


@router.get("/balance")
async def get_balance(current_user: dict = Depends(get_current_user_token)):
    """Get current wallet balance"""
    user = get_user_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "balance": user.get("wallet_balance", 0.0)
    }


@router.get("/deposit-bank-accounts")
async def get_deposit_bank_accounts():
    """
    Get active bank accounts for deposits (public endpoint)

    Returns:
        list: Active bank accounts where users can deposit funds
    """
    bank_accounts = get_collection(BANK_ACCOUNTS_COLLECTION)

    # Get all active bank accounts
    active_accounts = list(bank_accounts.find({"is_active": True}))

    # Return formatted account details (only one account if multiple exist, use the first one)
    if active_accounts:
        account = active_accounts[0]  # Get the first active account
        return {
            "bank_name": account.get("bank_name"),
            "account_name": account.get("account_name"),
            "account_number": account.get("account_number"),
            "routing_number": account.get("routing_number"),
            "swift_code": account.get("swift_code")
        }

    # Return None if no active accounts
    return None


@router.get("/pending-transactions")
async def get_pending_transactions(current_user: dict = Depends(get_current_user_token)):
    """Get summary of pending transactions for the current user"""
    transactions_col = get_collection(TRANSACTIONS_COLLECTION)

    # Find pending deposits and withdrawals
    pending_deposits = list(transactions_col.find({
        "user_id": current_user["user_id"],
        "transaction_type": "deposit",
        "status": "pending"
    }))

    pending_withdrawals = list(transactions_col.find({
        "user_id": current_user["user_id"],
        "transaction_type": "withdrawal",
        "status": "pending"
    }))

    # Calculate totals
    total_pending_deposits = sum(txn["amount"] for txn in pending_deposits)
    total_pending_withdrawals = sum(txn["amount"] for txn in pending_withdrawals)

    return {
        "pending_deposits": {
            "count": len(pending_deposits),
            "total_amount": total_pending_deposits,
            "transactions": [
                {
                    "id": str(txn["_id"]),
                    "amount": txn["amount"],
                    "payment_method": txn["payment_method"],
                    "created_at": txn["created_at"]
                }
                for txn in pending_deposits
            ]
        },
        "pending_withdrawals": {
            "count": len(pending_withdrawals),
            "total_amount": total_pending_withdrawals,
            "transactions": [
                {
                    "id": str(txn["_id"]),
                    "amount": txn["amount"],
                    "payment_method": txn["payment_method"],
                    "created_at": txn["created_at"]
                }
                for txn in pending_withdrawals
            ]
        }
    }
