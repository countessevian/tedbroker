from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import secrets

from app.schemas import DepositRequest, DepositRequestResponse
from app.auth import get_current_user_token
from app.database import get_collection, USERS_COLLECTION, DEPOSIT_REQUESTS_COLLECTION

router = APIRouter(prefix="/api/deposits", tags=["Deposits"])


def get_user_by_id(user_id: str):
    """Get user by ID from database"""
    users = get_collection(USERS_COLLECTION)
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except:
        return None


@router.post("/request")
async def create_deposit_request(
    deposit_data: DepositRequest,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Create a deposit request that requires admin approval

    For bank transfers, admin will review and approve manually
    """
    users = get_collection(USERS_COLLECTION)
    deposit_requests = get_collection(DEPOSIT_REQUESTS_COLLECTION)

    # Get user
    user = get_user_by_id(current_user["user_id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create deposit request
    deposit_request = {
        "user_id": current_user["user_id"],
        "username": user.get("username", ""),
        "email": user.get("email", ""),
        "amount": deposit_data.amount,
        "payment_method": deposit_data.payment_method,
        "payment_proof": deposit_data.payment_proof,
        "notes": deposit_data.notes,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "reviewed_by": None,
        "reviewed_at": None
    }

    # Insert deposit request
    result = deposit_requests.insert_one(deposit_request)
    deposit_request["_id"] = result.inserted_id

    return {
        "message": "Deposit request submitted successfully. Please wait for admin approval.",
        "request_id": str(deposit_request["_id"]),
        "status": deposit_request["status"]
    }


@router.get("/requests")
async def get_user_deposit_requests(
    current_user: dict = Depends(get_current_user_token),
    status_filter: Optional[str] = None
):
    """Get all deposit requests for the current user"""
    deposit_requests = get_collection(DEPOSIT_REQUESTS_COLLECTION)

    # Build query
    query = {"user_id": current_user["user_id"]}
    if status_filter:
        query["status"] = status_filter

    # Get requests
    requests = list(deposit_requests.find(query).sort("created_at", -1))

    return {
        "requests": [
            {
                "id": str(req["_id"]),
                "amount": req["amount"],
                "payment_method": req["payment_method"],
                "status": req["status"],
                "created_at": req["created_at"].isoformat(),
                "reviewed_at": req["reviewed_at"].isoformat() if req.get("reviewed_at") else None
            }
            for req in requests
        ]
    }
