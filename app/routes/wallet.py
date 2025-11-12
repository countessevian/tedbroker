from fastapi import APIRouter, HTTPException, status, Depends, Body
from datetime import datetime
from bson import ObjectId
from typing import List, Optional, Dict, Any
import secrets
from pydantic import BaseModel

from app.schemas import TransactionResponse
from app.auth import get_current_user_token
from app.database import get_collection, USERS_COLLECTION, TRANSACTIONS_COLLECTION, DEPOSIT_REQUESTS_COLLECTION

router = APIRouter(prefix="/api/wallet", tags=["Wallet"])


class DepositRequest(BaseModel):
    amount: float
    payment_method: str
    password: str
    # Optional fields for different payment methods
    bank_name: Optional[str] = None
    reference_number: Optional[str] = None
    crypto_type: Optional[str] = None
    transaction_hash: Optional[str] = None
    card_number: Optional[str] = None
    card_expiry: Optional[str] = None
    card_cvv: Optional[str] = None
    card_holder_name: Optional[str] = None
    paypal_email: Optional[str] = None


class WithdrawalRequest(BaseModel):
    amount: float
    payment_method: str
    password: str


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
        payment_details["transaction_hash"] = deposit_data.transaction_hash
    elif deposit_data.payment_method == "Credit Card":
        payment_details["card_number"] = deposit_data.card_number[-4:]  # Store only last 4 digits
        payment_details["card_holder_name"] = deposit_data.card_holder_name
    elif deposit_data.payment_method == "PayPal":
        payment_details["paypal_email"] = deposit_data.paypal_email

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
        "payment_proof": payment_details.get("transaction_hash") or payment_details.get("reference_number"),
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
        "message": "Deposit request submitted successfully. Your funds will be available once approved by admin.",
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

    # Get user
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user has sufficient balance
    current_balance = user.get("wallet_balance", 0.0)
    if current_balance < withdrawal_data.amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds. Current balance: ${current_balance:.2f}"
        )

    # Generate unique reference number
    reference_number = f"WTH-{secrets.token_hex(8).upper()}"

    # Create transaction record with pending status
    transaction = {
        "user_id": current_user["user_id"],
        "transaction_type": "withdrawal",
        "amount": withdrawal_data.amount,
        "status": "pending",  # Requires admin approval
        "payment_method": withdrawal_data.payment_method,
        "reference_number": reference_number,
        "description": f"Withdrawal to {withdrawal_data.payment_method}",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert transaction
    result = transactions_col.insert_one(transaction)
    transaction["_id"] = result.inserted_id

    # Note: Wallet balance will be deducted only when admin approves the withdrawal

    return {
        "message": "Withdrawal request submitted successfully. Your request will be processed once approved by admin.",
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
