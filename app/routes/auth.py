from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from bson import ObjectId

from app.schemas import UserRegister, UserLogin, Token, UserResponse, PasswordChange
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.database import get_collection, USERS_COLLECTION

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def get_user_by_email(email: str):
    """Get user by email from database"""
    users = get_collection(USERS_COLLECTION)
    return users.find_one({"email": email})


def get_user_by_username(username: str):
    """Get user by username from database"""
    users = get_collection(USERS_COLLECTION)
    return users.find_one({"username": username})


def get_user_by_id(user_id: str):
    """Get user by ID from database"""
    users = get_collection(USERS_COLLECTION)
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except:
        return None


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register a new user"""
    print(f"DEBUG: Received registration data: {user_data.model_dump()}")
    users = get_collection(USERS_COLLECTION)

    # Check if user already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user document
    user_dict = {
        "email": user_data.email,
        "username": user_data.username,
        "hashed_password": get_password_hash(user_data.password),
        "full_name": user_data.full_name,
        "phone": user_data.phone,
        "gender": user_data.gender,
        "country": user_data.country,
        "account_types": user_data.account_types if user_data.account_types else [],
        "wallet_balance": 5000.0,  # Give new users $5000 starting balance for testing
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert user into database
    result = users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id

    # Return user response
    return UserResponse(
        id=str(user_dict["_id"]),
        email=user_dict["email"],
        username=user_dict["username"],
        full_name=user_dict["full_name"],
        phone=user_dict["phone"],
        gender=user_dict["gender"],
        country=user_dict["country"],
        account_types=user_dict["account_types"],
        wallet_balance=user_dict["wallet_balance"],
        is_active=user_dict["is_active"],
        is_verified=user_dict["is_verified"],
        created_at=user_dict["created_at"],
        updated_at=user_dict["updated_at"]
    )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return access token"""
    # Get user from database
    user = get_user_by_email(user_credentials.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": str(user["_id"])},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login (for Swagger UI)"""
    # Get user from database (username field contains email)
    user = get_user_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": str(user["_id"])},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict = Depends(get_current_user_token)):
    """Get current authenticated user"""
    user = get_user_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        username=user["username"],
        full_name=user.get("full_name"),
        phone=user.get("phone"),
        gender=user.get("gender"),
        country=user.get("country"),
        account_types=user.get("account_types", []),
        wallet_balance=user.get("wallet_balance", 0.0),
        is_active=user.get("is_active", True),
        is_verified=user.get("is_verified", False),
        created_at=user["created_at"],
        updated_at=user["updated_at"]
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user_token)
):
    """Change user password"""
    users = get_collection(USERS_COLLECTION)

    # Get user from database
    user = get_user_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify old password
    if not verify_password(password_data.old_password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    # Update password
    users.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {
            "$set": {
                "hashed_password": get_password_hash(password_data.new_password),
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Password changed successfully"}


@router.delete("/delete-account")
async def delete_account(current_user: dict = Depends(get_current_user_token)):
    """Delete user account"""
    users = get_collection(USERS_COLLECTION)

    # Delete user
    result = users.delete_one({"_id": ObjectId(current_user["user_id"])})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"message": "Account deleted successfully"}
