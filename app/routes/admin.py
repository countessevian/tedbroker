from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from datetime import timedelta, datetime
from typing import List, Optional
from bson import ObjectId

from app.admin_service import admin_service
from app.auth import create_access_token, get_current_user_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_collection, USERS_COLLECTION, TRADERS_COLLECTION, INVESTMENT_PLANS_COLLECTION
from app.schemas import Token, Trade

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# Pydantic models for admin
class AdminRegister(BaseModel):
    """Schema for admin registration"""
    username: str
    email: EmailStr
    password: str
    full_name: str


class AdminLogin(BaseModel):
    """Schema for admin login"""
    username: str
    password: str


class AdminResponse(BaseModel):
    """Schema for admin response"""
    id: str
    username: str
    email: str
    full_name: str
    role: str


class CreateTrader(BaseModel):
    """Schema for creating a trader"""
    full_name: str = Field(..., min_length=1, max_length=100)
    profile_photo: str = Field(..., description="URL to profile photo")
    description: str = Field(..., description="Trader description and expertise")
    specialization: str = Field(..., description="Trading specialization")
    ytd_return: float = Field(..., description="Year-to-date return percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    copiers: int = Field(default=0, description="Number of copiers")


class CreatePlan(BaseModel):
    """Schema for creating an investment plan"""
    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    description: str = Field(..., description="Plan description")
    minimum_investment: float = Field(..., gt=0, description="Minimum investment amount")
    expected_return_percent: float = Field(..., description="Expected return percentage")
    holding_period_months: int = Field(..., gt=0, description="Holding period in months")
    is_active: bool = Field(default=True, description="Whether the plan is active")


# Dependency to verify admin authentication
async def get_current_admin(current_user: dict = Depends(get_current_user_token)) -> dict:
    """
    Verify that the current user is an admin

    Args:
        current_user: Current user from JWT token

    Returns:
        dict: Admin data

    Raises:
        HTTPException: If user is not an admin
    """
    # Check if user has admin role in token
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Verify admin exists and is active
    if not admin_service.verify_admin_token(current_user["user_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive or not found"
        )

    return current_user


@router.get("/check-setup")
async def check_admin_setup():
    """
    Check if admin has been set up

    Returns:
        dict: Setup status
    """
    admin_exists = admin_service.check_admin_exists()
    return {
        "admin_exists": admin_exists,
        "setup_required": not admin_exists
    }


@router.post("/register", response_model=AdminResponse)
async def register_admin(admin_data: AdminRegister):
    """
    Register the first admin user (only works if no admin exists)

    Args:
        admin_data: Admin registration data

    Returns:
        AdminResponse: Created admin data
    """
    try:
        admin = admin_service.create_admin(
            username=admin_data.username,
            email=admin_data.email,
            password=admin_data.password,
            full_name=admin_data.full_name
        )

        return AdminResponse(
            id=admin["id"],
            username=admin["username"],
            email=admin["email"],
            full_name=admin["full_name"],
            role=admin["role"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login_admin(login_data: AdminLogin):
    """
    Admin login

    Args:
        login_data: Admin login credentials

    Returns:
        Token: JWT access token
    """
    admin = admin_service.authenticate_admin(
        username=login_data.username,
        password=login_data.password
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with admin role
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": admin["username"],
            "user_id": admin["id"],
            "role": "admin"
        },
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: dict = Depends(get_current_admin)):
    """
    Get current admin information

    Args:
        current_admin: Current authenticated admin

    Returns:
        AdminResponse: Admin data
    """
    admin = admin_service.get_admin_by_id(current_admin["user_id"])

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    return AdminResponse(
        id=admin["id"],
        username=admin["username"],
        email=admin["email"],
        full_name=admin["full_name"],
        role=admin["role"]
    )


# ============================================================
# USERS MANAGEMENT
# ============================================================

@router.get("/users")
async def get_all_users(
    current_admin: dict = Depends(get_current_admin),
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None
):
    """
    Get all users (admin only)

    Args:
        current_admin: Current authenticated admin
        limit: Maximum number of users to return
        offset: Number of users to skip
        search: Search term for email or username

    Returns:
        dict: Users list and count
    """
    users = get_collection(USERS_COLLECTION)

    # Build query
    query = {}
    if search:
        query = {
            "$or": [
                {"email": {"$regex": search, "$options": "i"}},
                {"username": {"$regex": search, "$options": "i"}},
                {"full_name": {"$regex": search, "$options": "i"}}
            ]
        }

    # Get total count
    total_count = users.count_documents(query)

    # Get users
    cursor = users.find(query).sort("created_at", -1).skip(offset).limit(limit)

    users_list = []
    for user in cursor:
        users_list.append({
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "phone": user.get("phone"),
            "country": user.get("country"),
            "wallet_balance": user.get("wallet_balance", 0.0),
            "is_active": user.get("is_active", True),
            "is_verified": user.get("is_verified", False),
            "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
            "referral_code": user.get("referral_code"),
            "referred_by": user.get("referred_by")
        })

    return {
        "users": users_list,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.get("/users/{user_id}")
async def get_user_details(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get detailed information about a specific user

    Args:
        user_id: User ID
        current_admin: Current authenticated admin

    Returns:
        dict: User details
    """
    users = get_collection(USERS_COLLECTION)

    try:
        user = users.find_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "phone": user.get("phone"),
        "gender": user.get("gender"),
        "country": user.get("country"),
        "account_types": user.get("account_types", []),
        "wallet_balance": user.get("wallet_balance", 0.0),
        "is_active": user.get("is_active", True),
        "is_verified": user.get("is_verified", False),
        "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
        "updated_at": user["updated_at"].isoformat() if user.get("updated_at") else None,
        "referral_code": user.get("referral_code"),
        "referred_by": user.get("referred_by")
    }


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Activate a user account

    Args:
        user_id: User ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    users = get_collection(USERS_COLLECTION)

    try:
        result = users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": True}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User activated successfully"}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Deactivate a user account

    Args:
        user_id: User ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    users = get_collection(USERS_COLLECTION)

    try:
        result = users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deactivated successfully"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete a user account

    Args:
        user_id: User ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    users = get_collection(USERS_COLLECTION)

    try:
        result = users.delete_one({"_id": ObjectId(user_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "User deleted successfully"}


# ============================================================
# STATISTICS
# ============================================================

@router.get("/statistics")
async def get_statistics(current_admin: dict = Depends(get_current_admin)):
    """
    Get platform statistics

    Args:
        current_admin: Current authenticated admin

    Returns:
        dict: Platform statistics
    """
    users = get_collection(USERS_COLLECTION)
    traders = get_collection(TRADERS_COLLECTION)
    plans = get_collection(INVESTMENT_PLANS_COLLECTION)

    total_users = users.count_documents({})
    active_users = users.count_documents({"is_active": True})
    verified_users = users.count_documents({"is_verified": True})

    # Calculate total wallet balance
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$wallet_balance"}}}
    ]
    result = list(users.aggregate(pipeline))
    total_wallet_balance = result[0]["total"] if result else 0

    total_traders = traders.count_documents({})
    total_plans = plans.count_documents({})
    active_plans = plans.count_documents({"is_active": True})

    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "verified": verified_users
        },
        "wallet": {
            "total_balance": total_wallet_balance
        },
        "traders": {
            "total": total_traders
        },
        "plans": {
            "total": total_plans,
            "active": active_plans
        }
    }


# ============================================================
# TRADERS MANAGEMENT
# ============================================================

@router.post("/traders")
async def create_trader(
    trader_data: CreateTrader,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Create a new expert trader (admin only)

    Args:
        trader_data: Trader information
        current_admin: Current authenticated admin

    Returns:
        dict: Created trader data
    """
    traders = get_collection(TRADERS_COLLECTION)

    # Create trader document
    trader_dict = {
        "full_name": trader_data.full_name,
        "profile_photo": trader_data.profile_photo,
        "description": trader_data.description,
        "specialization": trader_data.specialization,
        "ytd_return": trader_data.ytd_return,
        "win_rate": trader_data.win_rate,
        "copiers": trader_data.copiers,
        "trades": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert trader into database
    result = traders.insert_one(trader_dict)
    trader_dict["_id"] = result.inserted_id

    return {
        "id": str(trader_dict["_id"]),
        "full_name": trader_dict["full_name"],
        "profile_photo": trader_dict["profile_photo"],
        "description": trader_dict["description"],
        "specialization": trader_dict["specialization"],
        "ytd_return": trader_dict["ytd_return"],
        "win_rate": trader_dict["win_rate"],
        "copiers": trader_dict["copiers"],
        "trades": trader_dict["trades"],
        "created_at": trader_dict["created_at"].isoformat()
    }


# ============================================================
# INVESTMENT PLANS MANAGEMENT
# ============================================================

@router.post("/plans")
async def create_plan(
    plan_data: CreatePlan,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Create a new investment plan (admin only)

    Args:
        plan_data: Plan information
        current_admin: Current authenticated admin

    Returns:
        dict: Created plan data
    """
    plans = get_collection(INVESTMENT_PLANS_COLLECTION)

    # Create plan document
    plan_dict = {
        "name": plan_data.name,
        "description": plan_data.description,
        "minimum_investment": plan_data.minimum_investment,
        "expected_return_percent": plan_data.expected_return_percent,
        "holding_period_months": plan_data.holding_period_months,
        "is_active": plan_data.is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert plan into database
    result = plans.insert_one(plan_dict)
    plan_dict["_id"] = result.inserted_id

    return {
        "id": str(plan_dict["_id"]),
        "name": plan_dict["name"],
        "description": plan_dict["description"],
        "minimum_investment": plan_dict["minimum_investment"],
        "expected_return_percent": plan_dict["expected_return_percent"],
        "holding_period_months": plan_dict["holding_period_months"],
        "is_active": plan_dict["is_active"],
        "created_at": plan_dict["created_at"].isoformat()
    }
