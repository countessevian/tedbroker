from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import timedelta, datetime
from typing import List, Optional
from bson import ObjectId

from app.admin_service import admin_service
from app.auth import create_access_token, get_current_user_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_collection, USERS_COLLECTION, TRADERS_COLLECTION, INVESTMENT_PLANS_COLLECTION, DEPOSIT_REQUESTS_COLLECTION, TRANSACTIONS_COLLECTION, CRYPTO_WALLETS_COLLECTION, BANK_ACCOUNTS_COLLECTION, USER_BANK_ACCOUNTS_COLLECTION, USER_CRYPTO_ADDRESSES_COLLECTION, WITHDRAWAL_REQUESTS_COLLECTION, CHAT_CONVERSATIONS_COLLECTION, CHAT_MESSAGES_COLLECTION, NOTIFICATIONS_COLLECTION
from app.schemas import Token, Trade, NotificationCreate, NotificationResponse
import secrets

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
    minimum_copy_amount: float = Field(default=100.0, gt=0, description="Minimum amount required to copy this trader in USD")


class CreatePlan(BaseModel):
    """Schema for creating an investment plan"""
    name: str = Field(..., min_length=1, max_length=100, description="Plan name")
    description: str = Field(..., description="Plan description")
    minimum_investment: float = Field(..., gt=0, description="Minimum investment amount")
    expected_return_percent: float = Field(..., description="Expected return percentage")
    holding_period_months: int = Field(..., gt=0, description="Holding period in months")
    is_active: bool = Field(default=True, description="Whether the plan is active")


class CreateCryptoWallet(BaseModel):
    """Schema for creating a crypto wallet"""
    currency: str = Field(..., description="Cryptocurrency type (BTC, ETH, USDT)")
    wallet_address: str = Field(..., min_length=1, description="Wallet address")
    network: Optional[str] = Field(None, description="Network (e.g., TRC20 for USDT)")
    is_active: bool = Field(default=True, description="Whether the wallet is active")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        allowed = ['BTC', 'ETH', 'USDT']
        if v.upper() not in allowed:
            raise ValueError(f'Currency must be one of: {", ".join(allowed)}')
        return v.upper()


class CreateBankAccount(BaseModel):
    """Schema for creating a bank account"""
    bank_name: str = Field(..., min_length=1, max_length=100, description="Bank name")
    account_name: str = Field(..., min_length=1, max_length=100, description="Account holder name")
    account_number: str = Field(..., min_length=1, description="Account number")
    routing_number: Optional[str] = Field(None, description="Routing/sort code")
    swift_code: Optional[str] = Field(None, description="SWIFT/BIC code")
    is_active: bool = Field(default=True, description="Whether the account is active")


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
    Get detailed information about a specific user including KYC and login history

    Args:
        user_id: User ID
        current_admin: Current authenticated admin

    Returns:
        dict: User details with KYC and login history
    """
    users = get_collection(USERS_COLLECTION)

    # Import login history service
    from app.login_history import LoginHistoryService

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

    # Get onboarding/KYC data
    onboarding_data = user.get("onboarding", {})
    kyc_data = {
        "document_number": onboarding_data.get("document_number"),
        "document_photo": onboarding_data.get("document_photo"),
        "kyc_status": onboarding_data.get("kyc_status", "not_submitted"),
        "kyc_submitted_at": onboarding_data.get("kyc_submitted_at").isoformat() if onboarding_data.get("kyc_submitted_at") else None,
        "first_name": onboarding_data.get("first_name"),
        "last_name": onboarding_data.get("last_name"),
        "gender": onboarding_data.get("gender"),
        "street": onboarding_data.get("street"),
        "city": onboarding_data.get("city"),
        "state": onboarding_data.get("state"),
        "zip_code": onboarding_data.get("zip_code"),
        "country": onboarding_data.get("country"),
        "personal_info_completed": onboarding_data.get("personal_info_completed", False),
        "address_completed": onboarding_data.get("address_completed", False),
        "kyc_completed": onboarding_data.get("kyc_completed", False)
    }

    # Get login history
    login_history = LoginHistoryService.get_user_login_history(user_id, limit=20)

    # Get login statistics
    login_stats = LoginHistoryService.get_login_statistics(user_id, days=30)

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
        "two_fa_enabled": user.get("two_fa_enabled", False),
        "auth_provider": user.get("auth_provider", "local"),
        "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
        "updated_at": user["updated_at"].isoformat() if user.get("updated_at") else None,
        "referral_code": user.get("referral_code"),
        "referred_by": user.get("referred_by"),
        "kyc": kyc_data,
        "login_history": login_history,
        "login_statistics": login_stats
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

@router.get("/traders")
async def get_all_traders(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all traders (admin only)

    Args:
        current_admin: Current authenticated admin

    Returns:
        list: All traders
    """
    traders = get_collection(TRADERS_COLLECTION)

    traders_list = []
    for trader in traders.find().sort("created_at", -1):
        traders_list.append({
            "id": str(trader["_id"]),
            "full_name": trader["full_name"],
            "profile_photo": trader["profile_photo"],
            "description": trader["description"],
            "specialization": trader["specialization"],
            "ytd_return": trader["ytd_return"],
            "win_rate": trader["win_rate"],
            "copiers": trader.get("copiers", 0),
            "trades": trader.get("trades", []),
            "created_at": trader["created_at"].isoformat() if trader.get("created_at") else None,
            "updated_at": trader["updated_at"].isoformat() if trader.get("updated_at") else None
        })

    return traders_list


@router.get("/traders/{trader_id}")
async def get_trader_details(
    trader_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get details of a specific trader (admin only)

    Args:
        trader_id: Trader ID
        current_admin: Current authenticated admin

    Returns:
        dict: Trader details
    """
    traders = get_collection(TRADERS_COLLECTION)

    try:
        trader = traders.find_one({"_id": ObjectId(trader_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trader ID"
        )

    if not trader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trader not found"
        )

    return {
        "id": str(trader["_id"]),
        "full_name": trader["full_name"],
        "profile_photo": trader["profile_photo"],
        "description": trader["description"],
        "specialization": trader["specialization"],
        "ytd_return": trader["ytd_return"],
        "win_rate": trader["win_rate"],
        "copiers": trader.get("copiers", 0),
        "trades": trader.get("trades", []),
        "created_at": trader["created_at"].isoformat() if trader.get("created_at") else None,
        "updated_at": trader["updated_at"].isoformat() if trader.get("updated_at") else None
    }


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


@router.put("/traders/{trader_id}")
async def update_trader(
    trader_id: str,
    trader_data: CreateTrader,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Update an existing trader (admin only)

    Args:
        trader_id: Trader ID
        trader_data: Updated trader information
        current_admin: Current authenticated admin

    Returns:
        dict: Updated trader data
    """
    traders = get_collection(TRADERS_COLLECTION)

    try:
        trader = traders.find_one({"_id": ObjectId(trader_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trader ID"
        )

    if not trader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trader not found"
        )

    # Update trader document
    update_dict = {
        "full_name": trader_data.full_name,
        "profile_photo": trader_data.profile_photo,
        "description": trader_data.description,
        "specialization": trader_data.specialization,
        "ytd_return": trader_data.ytd_return,
        "win_rate": trader_data.win_rate,
        "copiers": trader_data.copiers,
        "updated_at": datetime.utcnow()
    }

    # Update trader in database
    traders.update_one(
        {"_id": ObjectId(trader_id)},
        {"$set": update_dict}
    )

    # Get updated trader
    updated_trader = traders.find_one({"_id": ObjectId(trader_id)})

    return {
        "id": str(updated_trader["_id"]),
        "full_name": updated_trader["full_name"],
        "profile_photo": updated_trader["profile_photo"],
        "description": updated_trader["description"],
        "specialization": updated_trader["specialization"],
        "ytd_return": updated_trader["ytd_return"],
        "win_rate": updated_trader["win_rate"],
        "copiers": updated_trader.get("copiers", 0),
        "trades": updated_trader.get("trades", []),
        "created_at": updated_trader["created_at"].isoformat() if updated_trader.get("created_at") else None,
        "updated_at": updated_trader["updated_at"].isoformat()
    }


@router.delete("/traders/{trader_id}")
async def delete_trader(
    trader_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete a trader (admin only)

    Args:
        trader_id: Trader ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    traders = get_collection(TRADERS_COLLECTION)

    try:
        result = traders.delete_one({"_id": ObjectId(trader_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid trader ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trader not found"
        )

    return {"message": "Trader deleted successfully"}


# ============================================================
# INVESTMENT PLANS MANAGEMENT
# ============================================================

@router.get("/plans")
async def get_all_plans(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all investment plans (admin only)

    Args:
        current_admin: Current authenticated admin

    Returns:
        list: All investment plans
    """
    plans = get_collection(INVESTMENT_PLANS_COLLECTION)

    plans_list = []
    for plan in plans.find().sort("created_at", -1):
        plans_list.append({
            "id": str(plan["_id"]),
            "name": plan["name"],
            "description": plan["description"],
            "minimum_investment": plan["minimum_investment"],
            "expected_return_percent": plan["expected_return_percent"],
            "holding_period_months": plan["holding_period_months"],
            "current_subscribers": plan.get("current_subscribers", 0),
            "is_active": plan.get("is_active", True),
            "created_at": plan["created_at"].isoformat() if plan.get("created_at") else None,
            "updated_at": plan["updated_at"].isoformat() if plan.get("updated_at") else None
        })

    return plans_list


@router.get("/plans/{plan_id}")
async def get_plan_details(
    plan_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get details of a specific investment plan (admin only)

    Args:
        plan_id: Plan ID
        current_admin: Current authenticated admin

    Returns:
        dict: Plan details
    """
    plans = get_collection(INVESTMENT_PLANS_COLLECTION)

    try:
        plan = plans.find_one({"_id": ObjectId(plan_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment plan not found"
        )

    return {
        "id": str(plan["_id"]),
        "name": plan["name"],
        "description": plan["description"],
        "minimum_investment": plan["minimum_investment"],
        "expected_return_percent": plan["expected_return_percent"],
        "holding_period_months": plan["holding_period_months"],
        "current_subscribers": plan.get("current_subscribers", 0),
        "is_active": plan.get("is_active", True),
        "created_at": plan["created_at"].isoformat() if plan.get("created_at") else None,
        "updated_at": plan["updated_at"].isoformat() if plan.get("updated_at") else None
    }


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
        "current_subscribers": 0,
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
        "current_subscribers": plan_dict["current_subscribers"],
        "is_active": plan_dict["is_active"],
        "created_at": plan_dict["created_at"].isoformat()
    }


@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: str,
    plan_data: CreatePlan,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Update an existing investment plan (admin only)

    Args:
        plan_id: Plan ID
        plan_data: Updated plan information
        current_admin: Current authenticated admin

    Returns:
        dict: Updated plan data
    """
    plans = get_collection(INVESTMENT_PLANS_COLLECTION)

    try:
        plan = plans.find_one({"_id": ObjectId(plan_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment plan not found"
        )

    # Update plan document
    update_dict = {
        "name": plan_data.name,
        "description": plan_data.description,
        "minimum_investment": plan_data.minimum_investment,
        "expected_return_percent": plan_data.expected_return_percent,
        "holding_period_months": plan_data.holding_period_months,
        "is_active": plan_data.is_active,
        "updated_at": datetime.utcnow()
    }

    # Update plan in database
    plans.update_one(
        {"_id": ObjectId(plan_id)},
        {"$set": update_dict}
    )

    # Get updated plan
    updated_plan = plans.find_one({"_id": ObjectId(plan_id)})

    return {
        "id": str(updated_plan["_id"]),
        "name": updated_plan["name"],
        "description": updated_plan["description"],
        "minimum_investment": updated_plan["minimum_investment"],
        "expected_return_percent": updated_plan["expected_return_percent"],
        "holding_period_months": updated_plan["holding_period_months"],
        "current_subscribers": updated_plan.get("current_subscribers", 0),
        "is_active": updated_plan["is_active"],
        "created_at": updated_plan["created_at"].isoformat() if updated_plan.get("created_at") else None,
        "updated_at": updated_plan["updated_at"].isoformat()
    }


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete an investment plan (admin only)

    Args:
        plan_id: Plan ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    plans = get_collection(INVESTMENT_PLANS_COLLECTION)

    try:
        result = plans.delete_one({"_id": ObjectId(plan_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment plan not found"
        )

    return {"message": "Investment plan deleted successfully"}


# ============================================================
# DEPOSIT REQUESTS MANAGEMENT
# ============================================================

@router.get("/deposit-requests")
async def get_all_deposit_requests(
    current_admin: dict = Depends(get_current_admin),
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get all deposit requests (admin only)

    Args:
        current_admin: Current authenticated admin
        status_filter: Filter by status (pending, approved, rejected)
        limit: Maximum number of requests to return
        offset: Number of requests to skip

    Returns:
        dict: Deposit requests list and count
    """
    deposit_requests = get_collection(DEPOSIT_REQUESTS_COLLECTION)

    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter

    # Get total count
    total_count = deposit_requests.count_documents(query)

    # Get requests
    cursor = deposit_requests.find(query).sort("created_at", -1).skip(offset).limit(limit)

    requests_list = []
    for req in cursor:
        requests_list.append({
            "id": str(req["_id"]),
            "user_id": req["user_id"],
            "username": req.get("username", ""),
            "email": req.get("email", ""),
            "amount": req["amount"],
            "payment_method": req["payment_method"],
            "payment_proof": req.get("payment_proof"),
            "notes": req.get("notes"),
            "status": req["status"],
            "created_at": req["created_at"].isoformat(),
            "updated_at": req["updated_at"].isoformat(),
            "reviewed_by": req.get("reviewed_by"),
            "reviewed_at": req["reviewed_at"].isoformat() if req.get("reviewed_at") else None
        })

    return {
        "requests": requests_list,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.put("/deposit-requests/{request_id}/approve")
async def approve_deposit_request(
    request_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Approve a deposit request and credit user wallet

    Args:
        request_id: Deposit request ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    deposit_requests = get_collection(DEPOSIT_REQUESTS_COLLECTION)
    users = get_collection(USERS_COLLECTION)
    transactions = get_collection(TRANSACTIONS_COLLECTION)

    # Get deposit request
    try:
        deposit_request = deposit_requests.find_one({"_id": ObjectId(request_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

    if not deposit_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit request not found"
        )

    if deposit_request["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {deposit_request['status']}"
        )

    # Update user wallet balance
    user_id = deposit_request["user_id"]
    amount = deposit_request["amount"]

    try:
        user_result = users.update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"wallet_balance": amount}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )

    if user_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Create transaction record
    transaction = {
        "user_id": user_id,
        "transaction_type": "deposit",
        "amount": amount,
        "status": "completed",
        "payment_method": deposit_request["payment_method"],
        "reference_number": secrets.token_hex(16),
        "description": f"Deposit approved by admin - {deposit_request['payment_method']}",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    transactions.insert_one(transaction)

    # Update deposit request status
    deposit_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "status": "approved",
                "reviewed_by": current_admin["user_id"],
                "reviewed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "message": "Deposit request approved successfully",
        "amount": amount,
        "user_id": user_id
    }


@router.put("/deposit-requests/{request_id}/reject")
async def reject_deposit_request(
    request_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Reject a deposit request

    Args:
        request_id: Deposit request ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    deposit_requests = get_collection(DEPOSIT_REQUESTS_COLLECTION)

    # Get deposit request
    try:
        deposit_request = deposit_requests.find_one({"_id": ObjectId(request_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

    if not deposit_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit request not found"
        )

    if deposit_request["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {deposit_request['status']}"
        )

    # Update deposit request status
    result = deposit_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "status": "rejected",
                "reviewed_by": current_admin["user_id"],
                "reviewed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "message": "Deposit request rejected successfully",
        "request_id": request_id
    }


# ============================================================
# CRYPTO WALLETS MANAGEMENT
# ============================================================

@router.get("/crypto-wallets")
async def get_crypto_wallets(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all crypto wallets (admin only)

    Args:
        current_admin: Current authenticated admin

    Returns:
        list: Crypto wallets
    """
    crypto_wallets = get_collection(CRYPTO_WALLETS_COLLECTION)

    wallets = list(crypto_wallets.find().sort("created_at", -1))

    return [
        {
            "id": str(wallet["_id"]),
            "currency": wallet["currency"],
            "wallet_address": wallet["wallet_address"],
            "network": wallet.get("network"),
            "is_active": wallet.get("is_active", True),
            "created_at": wallet["created_at"].isoformat() if wallet.get("created_at") else None
        }
        for wallet in wallets
    ]


@router.post("/crypto-wallets")
async def create_crypto_wallet(
    wallet_data: CreateCryptoWallet,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Create a new crypto wallet (admin only)

    Args:
        wallet_data: Crypto wallet information
        current_admin: Current authenticated admin

    Returns:
        dict: Created wallet data
    """
    crypto_wallets = get_collection(CRYPTO_WALLETS_COLLECTION)

    # Create wallet document
    wallet_dict = {
        "currency": wallet_data.currency,
        "wallet_address": wallet_data.wallet_address,
        "network": wallet_data.network,
        "is_active": wallet_data.is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert wallet into database
    result = crypto_wallets.insert_one(wallet_dict)
    wallet_dict["_id"] = result.inserted_id

    return {
        "id": str(wallet_dict["_id"]),
        "currency": wallet_dict["currency"],
        "wallet_address": wallet_dict["wallet_address"],
        "network": wallet_dict["network"],
        "is_active": wallet_dict["is_active"],
        "created_at": wallet_dict["created_at"].isoformat()
    }


@router.delete("/crypto-wallets/{wallet_id}")
async def delete_crypto_wallet(
    wallet_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete a crypto wallet

    Args:
        wallet_id: Wallet ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    crypto_wallets = get_collection(CRYPTO_WALLETS_COLLECTION)

    try:
        result = crypto_wallets.delete_one({"_id": ObjectId(wallet_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wallet not found"
        )

    return {"message": "Crypto wallet deleted successfully"}


# ============================================================
# BANK ACCOUNTS MANAGEMENT
# ============================================================

@router.get("/bank-accounts")
async def get_bank_accounts(
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get all bank accounts (admin only)

    Args:
        current_admin: Current authenticated admin

    Returns:
        list: Bank accounts
    """
    bank_accounts = get_collection(BANK_ACCOUNTS_COLLECTION)

    accounts = list(bank_accounts.find().sort("created_at", -1))

    return [
        {
            "id": str(account["_id"]),
            "bank_name": account["bank_name"],
            "account_name": account["account_name"],
            "account_number": account["account_number"],
            "routing_number": account.get("routing_number"),
            "swift_code": account.get("swift_code"),
            "is_active": account.get("is_active", True),
            "created_at": account["created_at"].isoformat() if account.get("created_at") else None
        }
        for account in accounts
    ]


@router.post("/bank-accounts")
async def create_bank_account(
    account_data: CreateBankAccount,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Create a new bank account (admin only)

    Args:
        account_data: Bank account information
        current_admin: Current authenticated admin

    Returns:
        dict: Created account data
    """
    bank_accounts = get_collection(BANK_ACCOUNTS_COLLECTION)

    # Create account document
    account_dict = {
        "bank_name": account_data.bank_name,
        "account_name": account_data.account_name,
        "account_number": account_data.account_number,
        "routing_number": account_data.routing_number,
        "swift_code": account_data.swift_code,
        "is_active": account_data.is_active,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert account into database
    result = bank_accounts.insert_one(account_dict)
    account_dict["_id"] = result.inserted_id

    return {
        "id": str(account_dict["_id"]),
        "bank_name": account_dict["bank_name"],
        "account_name": account_dict["account_name"],
        "account_number": account_dict["account_number"],
        "routing_number": account_dict["routing_number"],
        "swift_code": account_dict["swift_code"],
        "is_active": account_dict["is_active"],
        "created_at": account_dict["created_at"].isoformat()
    }


@router.delete("/bank-accounts/{account_id}")
async def delete_bank_account(
    account_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete a bank account

    Args:
        account_id: Account ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    bank_accounts = get_collection(BANK_ACCOUNTS_COLLECTION)

    try:
        result = bank_accounts.delete_one({"_id": ObjectId(account_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    return {"message": "Bank account deleted successfully"}


# ============================================================
# WITHDRAWAL REQUESTS MANAGEMENT
# ============================================================

@router.get("/withdrawal-requests")
async def get_all_withdrawal_requests(
    current_admin: dict = Depends(get_current_admin),
    status_filter: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get all withdrawal requests (admin only)

    Args:
        current_admin: Current authenticated admin
        status_filter: Filter by status (pending, approved, rejected, processing, completed)
        limit: Maximum number of requests to return
        offset: Number of requests to skip

    Returns:
        dict: Withdrawal requests list and count
    """
    withdrawal_requests = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter

    # Get total count
    total_count = withdrawal_requests.count_documents(query)

    # Get requests
    cursor = withdrawal_requests.find(query).sort("created_at", -1).skip(offset).limit(limit)

    requests_list = []
    for req in cursor:
        requests_list.append({
            "id": str(req["_id"]),
            "user_id": req["user_id"],
            "username": req.get("username", ""),
            "email": req.get("email", ""),
            "amount": req["amount"],
            "withdrawal_method": req["withdrawal_method"],
            "account_details": req["account_details"],
            "notes": req.get("notes"),
            "status": req["status"],
            "created_at": req["created_at"].isoformat(),
            "updated_at": req["updated_at"].isoformat(),
            "reviewed_by": req.get("reviewed_by"),
            "reviewed_at": req["reviewed_at"].isoformat() if req.get("reviewed_at") else None,
            "completed_at": req["completed_at"].isoformat() if req.get("completed_at") else None
        })

    return {
        "requests": requests_list,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.put("/withdrawal-requests/{request_id}/approve")
async def approve_withdrawal_request(
    request_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Approve a withdrawal request and deduct from user wallet

    Args:
        request_id: Withdrawal request ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    withdrawal_requests = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)
    users = get_collection(USERS_COLLECTION)
    transactions = get_collection(TRANSACTIONS_COLLECTION)

    # Get withdrawal request
    try:
        withdrawal_request = withdrawal_requests.find_one({"_id": ObjectId(request_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

    if not withdrawal_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal request not found"
        )

    if withdrawal_request["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {withdrawal_request['status']}"
        )

    # Get user and verify balance
    user_id = withdrawal_request["user_id"]
    amount = withdrawal_request["amount"]

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

    current_balance = user.get("wallet_balance", 0.0)
    if current_balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient user balance. Current: ${current_balance:.2f}, Requested: ${amount:.2f}"
        )

    # Deduct from user wallet balance
    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"wallet_balance": -amount}}
    )

    # Create transaction record
    transaction = {
        "user_id": user_id,
        "transaction_type": "withdrawal",
        "amount": amount,
        "status": "completed",
        "payment_method": withdrawal_request["withdrawal_method"],
        "reference_number": secrets.token_hex(16),
        "description": f"Withdrawal approved by admin - {withdrawal_request['withdrawal_method']}",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    transactions.insert_one(transaction)

    # Update withdrawal request status
    withdrawal_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "status": "completed",
                "reviewed_by": current_admin["user_id"],
                "reviewed_at": datetime.utcnow(),
                "completed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "message": "Withdrawal request approved and completed successfully",
        "amount": amount,
        "user_id": user_id
    }


@router.put("/withdrawal-requests/{request_id}/reject")
async def reject_withdrawal_request(
    request_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Reject a withdrawal request

    Args:
        request_id: Withdrawal request ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    withdrawal_requests = get_collection(WITHDRAWAL_REQUESTS_COLLECTION)

    # Get withdrawal request
    try:
        withdrawal_request = withdrawal_requests.find_one({"_id": ObjectId(request_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request ID"
        )

    if not withdrawal_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Withdrawal request not found"
        )

    if withdrawal_request["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {withdrawal_request['status']}"
        )

    # Update withdrawal request status
    result = withdrawal_requests.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "status": "rejected",
                "reviewed_by": current_admin["user_id"],
                "reviewed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "message": "Withdrawal request rejected successfully",
        "request_id": request_id
    }


# ============================================================
# USER WITHDRAWAL ACCOUNTS VERIFICATION
# ============================================================

@router.get("/user-bank-accounts")
async def get_all_user_bank_accounts(
    current_admin: dict = Depends(get_current_admin),
    verified_only: bool = False
):
    """
    Get all user bank accounts for verification

    Args:
        current_admin: Current authenticated admin
        verified_only: Only return verified accounts

    Returns:
        list: User bank accounts
    """
    bank_accounts = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    query = {}
    if verified_only:
        query["is_verified"] = True

    accounts = list(bank_accounts.find(query).sort("created_at", -1))

    return [
        {
            "id": str(acc["_id"]),
            "user_id": acc["user_id"],
            "account_name": acc["account_name"],
            "account_number": acc["account_number"],
            "bank_name": acc["bank_name"],
            "bank_branch": acc.get("bank_branch"),
            "swift_code": acc.get("swift_code"),
            "iban": acc.get("iban"),
            "is_primary": acc["is_primary"],
            "is_verified": acc["is_verified"],
            "created_at": acc["created_at"].isoformat()
        }
        for acc in accounts
    ]


@router.put("/user-bank-accounts/{account_id}/verify")
async def verify_user_bank_account(
    account_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Verify a user's bank account

    Args:
        account_id: Bank account ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    bank_accounts = get_collection(USER_BANK_ACCOUNTS_COLLECTION)

    try:
        result = bank_accounts.update_one(
            {"_id": ObjectId(account_id)},
            {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid account ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )

    return {"message": "Bank account verified successfully"}


@router.get("/user-crypto-addresses")
async def get_all_user_crypto_addresses(
    current_admin: dict = Depends(get_current_admin),
    verified_only: bool = False
):
    """
    Get all user crypto addresses for verification

    Args:
        current_admin: Current authenticated admin
        verified_only: Only return verified addresses

    Returns:
        list: User crypto addresses
    """
    crypto_addresses = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    query = {}
    if verified_only:
        query["is_verified"] = True

    addresses = list(crypto_addresses.find(query).sort("created_at", -1))

    return [
        {
            "id": str(addr["_id"]),
            "user_id": addr["user_id"],
            "currency": addr["currency"],
            "wallet_address": addr["wallet_address"],
            "network": addr.get("network"),
            "label": addr.get("label"),
            "is_primary": addr["is_primary"],
            "is_verified": addr["is_verified"],
            "created_at": addr["created_at"].isoformat()
        }
        for addr in addresses
    ]


@router.put("/user-crypto-addresses/{address_id}/verify")
async def verify_user_crypto_address(
    address_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Verify a user's crypto address

    Args:
        address_id: Crypto address ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    crypto_addresses = get_collection(USER_CRYPTO_ADDRESSES_COLLECTION)

    try:
        result = crypto_addresses.update_one(
            {"_id": ObjectId(address_id)},
            {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid address ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crypto address not found"
        )

    return {"message": "Crypto address verified successfully"}


# ============================================================
# CHAT SUPPORT MANAGEMENT
# ============================================================

@router.get("/chat/conversations")
async def get_all_chat_conversations(
    current_admin: dict = Depends(get_current_admin),
    status_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """
    Get all chat conversations (admin only)

    Args:
        current_admin: Current authenticated admin
        status_filter: Filter by status (active, closed)
        limit: Maximum number of conversations to return
        offset: Number of conversations to skip

    Returns:
        dict: Conversations list and count
    """
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)

    # Build query
    query = {}
    if status_filter:
        query["status"] = status_filter

    # Get total count
    total_count = conversations.count_documents(query)

    # Get conversations
    cursor = conversations.find(query).sort("updated_at", -1).skip(offset).limit(limit)

    conversations_list = []
    for conv in cursor:
        conversations_list.append({
            "id": str(conv["_id"]),
            "user_id": conv["user_id"],
            "user_name": conv["user_name"],
            "user_email": conv["user_email"],
            "status": conv["status"],
            "unread_count": conv.get("unread_admin_count", 0),
            "last_message": conv.get("last_message"),
            "last_message_time": conv["last_message_time"].isoformat() if conv.get("last_message_time") else None,
            "created_at": conv["created_at"].isoformat(),
            "updated_at": conv["updated_at"].isoformat()
        })

    return {
        "conversations": conversations_list,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.get("/chat/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Get detailed conversation with all messages

    Args:
        conversation_id: Conversation ID
        current_admin: Current authenticated admin

    Returns:
        dict: Conversation details with messages
    """
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)
    messages = get_collection(CHAT_MESSAGES_COLLECTION)

    # Get conversation
    try:
        conversation = conversations.find_one({"_id": ObjectId(conversation_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get all messages
    message_list = list(messages.find(
        {"conversation_id": conversation_id}
    ).sort("created_at", 1))

    # Mark user messages as read by admin
    messages.update_many(
        {
            "conversation_id": conversation_id,
            "sender_type": "user",
            "is_read": False
        },
        {"$set": {"is_read": True}}
    )

    # Reset unread count for admin
    conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {"$set": {"unread_admin_count": 0}}
    )

    return {
        "id": str(conversation["_id"]),
        "user_id": conversation["user_id"],
        "user_name": conversation["user_name"],
        "user_email": conversation["user_email"],
        "status": conversation["status"],
        "created_at": conversation["created_at"].isoformat(),
        "updated_at": conversation["updated_at"].isoformat(),
        "messages": [
            {
                "id": str(msg["_id"]),
                "conversation_id": msg["conversation_id"],
                "sender_id": msg["sender_id"],
                "sender_type": msg["sender_type"],
                "sender_name": msg["sender_name"],
                "message": msg["message"],
                "is_read": msg["is_read"],
                "created_at": msg["created_at"].isoformat()
            }
            for msg in message_list
        ]
    }


class AdminMessageReply(BaseModel):
    """Schema for admin message reply"""
    message: str = Field(..., min_length=1, max_length=2000)


@router.post("/chat/conversations/{conversation_id}/reply")
async def reply_to_conversation(
    conversation_id: str,
    reply_data: AdminMessageReply,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Send a reply to a conversation

    Args:
        conversation_id: Conversation ID
        reply_data: Reply message data
        current_admin: Current authenticated admin

    Returns:
        dict: Created message
    """
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)
    messages_col = get_collection(CHAT_MESSAGES_COLLECTION)

    # Get conversation
    try:
        conversation = conversations.find_one({"_id": ObjectId(conversation_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Get the assigned agent name for this conversation (shown to user)
    # This ensures all admin replies show the same random name to the user
    assigned_agent_name = conversation.get("assigned_agent_name", "Support Team")

    # Create message
    new_message = {
        "conversation_id": conversation_id,
        "sender_id": current_admin["user_id"],
        "sender_type": "admin",
        "sender_name": assigned_agent_name,  # Use the assigned agent name
        "message": reply_data.message,
        "is_read": False,
        "created_at": datetime.utcnow()
    }

    result = messages_col.insert_one(new_message)
    new_message["_id"] = result.inserted_id

    # Update conversation
    conversations.update_one(
        {"_id": ObjectId(conversation_id)},
        {
            "$set": {
                "last_message": reply_data.message[:100],
                "last_message_time": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "status": "active"  # Reopen if closed
            },
            "$inc": {"unread_user_count": 1}
        }
    )

    return {
        "id": str(new_message["_id"]),
        "conversation_id": new_message["conversation_id"],
        "sender_id": new_message["sender_id"],
        "sender_type": new_message["sender_type"],
        "sender_name": new_message["sender_name"],
        "message": new_message["message"],
        "is_read": new_message["is_read"],
        "created_at": new_message["created_at"].isoformat()
    }


@router.put("/chat/conversations/{conversation_id}/close")
async def close_conversation(
    conversation_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Close a conversation

    Args:
        conversation_id: Conversation ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)

    try:
        result = conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "status": "closed",
                    "updated_at": datetime.utcnow()
                }
            }
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return {"message": "Conversation closed successfully"}


@router.post("/chat/conversations/{conversation_id}/mark-read")
async def mark_conversation_read(
    conversation_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Mark a conversation as read by admin

    Args:
        conversation_id: Conversation ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)
    messages = get_collection(CHAT_MESSAGES_COLLECTION)

    try:
        # Mark user messages as read by admin
        messages.update_many(
            {
                "conversation_id": conversation_id,
                "sender_type": "user",
                "is_read": False
            },
            {"$set": {"is_read": True}}
        )

        # Reset unread count for admin
        result = conversations.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"unread_admin_count": 0}}
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation ID"
        )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return {"message": "Conversation marked as read"}


@router.get("/chat/unread-count")
async def get_admin_unread_count(current_admin: dict = Depends(get_current_admin)):
    """
    Get total count of unread messages across all conversations

    Args:
        current_admin: Current authenticated admin

    Returns:
        dict: Unread count
    """
    conversations = get_collection(CHAT_CONVERSATIONS_COLLECTION)

    pipeline = [
        {"$match": {"status": "active"}},
        {"$group": {"_id": None, "total": {"$sum": "$unread_admin_count"}}}
    ]

    result = list(conversations.aggregate(pipeline))
    total_unread = result[0]["total"] if result else 0

    return {"unread_count": total_unread}


# ============================================================
# NOTIFICATIONS MANAGEMENT
# ============================================================

@router.post("/notifications")
async def create_notification(
    notification_data: NotificationCreate,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Create a notification (broadcast or targeted)

    Args:
        notification_data: Notification data
        current_admin: Current authenticated admin

    Returns:
        dict: Created notification
    """
    notifications = get_collection(NOTIFICATIONS_COLLECTION)

    # Validate target user if specific
    if notification_data.target_type == "specific":
        if not notification_data.target_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="target_user_id is required for specific notifications"
            )

        # Verify user exists
        users = get_collection(USERS_COLLECTION)
        try:
            user = users.find_one({"_id": ObjectId(notification_data.target_user_id)})
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target user not found"
                )
        except:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID"
            )

    # Create notification document
    notification_dict = {
        "title": notification_data.title,
        "message": notification_data.message,
        "notification_type": notification_data.notification_type,
        "target_type": notification_data.target_type,
        "target_user_id": notification_data.target_user_id,
        "is_dismissed": False,
        "created_by": current_admin["user_id"],
        "created_at": datetime.utcnow()
    }

    # Insert notification
    result = notifications.insert_one(notification_dict)
    notification_dict["_id"] = result.inserted_id

    return {
        "id": str(notification_dict["_id"]),
        "title": notification_dict["title"],
        "message": notification_dict["message"],
        "notification_type": notification_dict["notification_type"],
        "target_type": notification_dict["target_type"],
        "target_user_id": notification_dict["target_user_id"],
        "created_at": notification_dict["created_at"].isoformat(),
        "message": f"Notification created successfully and sent to {'all users' if notification_data.target_type == 'all' else '1 user'}"
    }


@router.get("/notifications")
async def get_all_notifications(
    current_admin: dict = Depends(get_current_admin),
    limit: int = 50,
    offset: int = 0
):
    """
    Get all notifications (admin only)

    Args:
        current_admin: Current authenticated admin
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip

    Returns:
        dict: Notifications list and count
    """
    notifications = get_collection(NOTIFICATIONS_COLLECTION)

    # Get total count
    total_count = notifications.count_documents({})

    # Get notifications
    cursor = notifications.find().sort("created_at", -1).skip(offset).limit(limit)

    notifications_list = []
    for notif in cursor:
        notifications_list.append({
            "id": str(notif["_id"]),
            "title": notif["title"],
            "message": notif["message"],
            "notification_type": notif["notification_type"],
            "target_type": notif["target_type"],
            "target_user_id": notif.get("target_user_id"),
            "created_by": notif["created_by"],
            "created_at": notif["created_at"].isoformat()
        })

    return {
        "notifications": notifications_list,
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """
    Delete a notification

    Args:
        notification_id: Notification ID
        current_admin: Current authenticated admin

    Returns:
        dict: Success message
    """
    notifications = get_collection(NOTIFICATIONS_COLLECTION)

    try:
        result = notifications.delete_one({"_id": ObjectId(notification_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification ID"
        )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return {"message": "Notification deleted successfully"}
