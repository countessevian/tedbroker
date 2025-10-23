from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from bson import ObjectId
from typing import Optional

from app.schemas import UserRegister, UserLogin, Token, UserResponse, PasswordChange
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.database import get_collection, USERS_COLLECTION
from app.twofa_service import twofa_service
from app.email_service import email_service
from app.login_history import login_history_service
from app.security_alerts import security_alerts_service
from app.rate_limiter import limiter, get_rate_limit
from app.referrals_service import referrals_service
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# Pydantic models for 2FA
class TwoFAVerify(BaseModel):
    email: str
    code: str


class TwoFAResponse(BaseModel):
    message: str
    requires_2fa: bool = False


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


@router.post("/register")
@limiter.limit(get_rate_limit("register"))
async def register(request: Request, user_data: UserRegister):
    """Register a new user and send 2FA verification code"""
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
        "wallet_balance": 0.0,  # New users start with zero balance
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    # Insert user into database
    result = users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id

    # Generate unique referral code for the new user
    try:
        referral_code = referrals_service.create_referral_link(str(user_dict["_id"]))
        print(f"Generated referral code for user {user_dict['username']}: {referral_code}")
    except Exception as e:
        print(f"Failed to generate referral code: {e}")

    # Generate 2FA code for email verification
    code = twofa_service.create_2fa_session(
        email=user_dict["email"],
        user_id=str(user_dict["_id"])
    )

    # Send 2FA code via email
    email_sent = email_service.send_2fa_code(
        to_email=user_dict["email"],
        code=code,
        username=user_dict["full_name"]
    )

    if not email_sent:
        # If SendGrid is not configured, log the code for testing
        print(f"2FA Code for {user_dict['email']}: {code}")

    # Return response indicating 2FA is required
    return {
        "message": "Registration successful. Please verify your email with the code sent to you.",
        "requires_2fa": True,
        "email": user_dict["email"],
        "user_id": str(user_dict["_id"])
    }


@router.post("/login")
@limiter.limit(get_rate_limit("login"))
async def login(request: Request, user_credentials: UserLogin):
    """Login user - sends 2FA code via email with security tracking"""
    # Get user from database
    user = get_user_by_email(user_credentials.email)

    if not user:
        # Record failed login attempt
        login_history_service.record_login_attempt(
            email=user_credentials.email,
            user_id=None,
            request=request,
            success=False,
            failure_reason="User not found"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(user_credentials.password, user["hashed_password"]):
        # Record failed login attempt
        login_history_service.record_login_attempt(
            email=user["email"],
            user_id=str(user["_id"]),
            request=request,
            success=False,
            failure_reason="Incorrect password"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("is_active", True):
        login_history_service.record_login_attempt(
            email=user["email"],
            user_id=str(user["_id"]),
            request=request,
            success=False,
            failure_reason="Account inactive"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Check for suspicious activity
    suspicious_activity = login_history_service.check_suspicious_activity(
        email=user["email"],
        request=request
    )

    # Send security alert if suspicious
    if suspicious_activity.get("is_suspicious"):
        ip_address = login_history_service.get_ip_address(request)
        device_info = login_history_service.get_device_info(request)
        location = login_history_service.get_location_from_ip(ip_address)
        username = user.get("full_name", user.get("username", "User"))

        # Send alert email (non-blocking)
        try:
            security_alerts_service.send_suspicious_login_alert(
                email=user["email"],
                username=username,
                suspicious_activity=suspicious_activity,
                ip_address=ip_address,
                device_info=device_info,
                location=location
            )
        except Exception as e:
            print(f"Failed to send security alert: {e}")

    # Generate 2FA code
    code = twofa_service.create_2fa_session(
        email=user["email"],
        user_id=str(user["_id"])
    )

    # Send 2FA code via email
    username = user.get("full_name", user.get("username", "User"))
    email_sent = email_service.send_2fa_code(
        to_email=user["email"],
        code=code,
        username=username
    )

    if not email_sent:
        # If SendGrid is not configured, log the code for testing
        print(f"2FA Code for {user['email']}: {code}")

    return {
        "message": "Verification code sent to your email",
        "requires_2fa": True,
        "email": user["email"],
        "security_alert": suspicious_activity.get("is_suspicious", False)
    }


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


class UpdateProfile(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None


@router.put("/update-profile", response_model=UserResponse)
async def update_profile(
    profile_data: UpdateProfile,
    current_user: dict = Depends(get_current_user_token)
):
    """Update user profile information"""
    users = get_collection(USERS_COLLECTION)

    # Get user from database
    user = get_user_by_id(current_user["user_id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prepare update data
    update_data = {"updated_at": datetime.utcnow()}

    if profile_data.full_name is not None:
        update_data["full_name"] = profile_data.full_name

    if profile_data.phone is not None:
        update_data["phone"] = profile_data.phone

    if profile_data.gender is not None:
        if profile_data.gender and profile_data.gender not in ['Male', 'Female', 'Others', '']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender must be Male, Female, or Others"
            )
        update_data["gender"] = profile_data.gender if profile_data.gender else None

    if profile_data.country is not None:
        update_data["country"] = profile_data.country

    # Update user
    users.update_one(
        {"_id": ObjectId(current_user["user_id"])},
        {"$set": update_data}
    )

    # Fetch updated user
    updated_user = get_user_by_id(current_user["user_id"])

    return UserResponse(
        id=str(updated_user["_id"]),
        email=updated_user["email"],
        username=updated_user["username"],
        full_name=updated_user.get("full_name"),
        phone=updated_user.get("phone"),
        gender=updated_user.get("gender"),
        country=updated_user.get("country"),
        account_types=updated_user.get("account_types", []),
        wallet_balance=updated_user.get("wallet_balance", 0.0),
        is_active=updated_user.get("is_active", True),
        is_verified=updated_user.get("is_verified", False),
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"]
    )


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


@router.post("/verify-2fa", response_model=Token)
@limiter.limit(get_rate_limit("verify_2fa"))
async def verify_2fa(request: Request, verification_data: TwoFAVerify):
    """Verify 2FA code and return access token with login history tracking"""
    # Verify the code
    result = twofa_service.verify_code(
        email=verification_data.email,
        code=verification_data.code
    )

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )

    # Get user
    user = get_user_by_email(verification_data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Mark user as verified if not already verified
    users = get_collection(USERS_COLLECTION)
    if not user.get("is_verified", False):
        users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "is_verified": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        print(f"User {user['email']} marked as verified")

    # Record successful login
    login_history_service.record_login_attempt(
        email=user["email"],
        user_id=str(user["_id"]),
        request=request,
        success=True
    )

    # Clean up 2FA session
    twofa_service.delete_session(verification_data.email)

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": str(user["_id"])},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/resend-2fa")
@limiter.limit(get_rate_limit("resend_2fa"))
async def resend_2fa(request: Request, email_data: dict):
    """Resend 2FA verification code"""
    email = email_data.get("email")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )

    # Get user
    user = get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new 2FA code
    code = twofa_service.create_2fa_session(
        email=user["email"],
        user_id=str(user["_id"])
    )

    # Send code via email
    username = user.get("full_name", user.get("username", "User"))
    email_sent = email_service.send_2fa_code(
        to_email=user["email"],
        code=code,
        username=username
    )

    if not email_sent:
        print(f"2FA Code for {user['email']}: {code}")

    return {
        "message": "New verification code sent to your email"
    }


@router.get("/login-history")
async def get_login_history(
    current_user: dict = Depends(get_current_user_token),
    limit: int = 50,
    offset: int = 0
):
    """Get login history for current user"""
    history = login_history_service.get_user_login_history(
        user_id=current_user["user_id"],
        limit=limit,
        offset=offset
    )

    return {
        "history": history,
        "count": len(history)
    }


@router.get("/login-statistics")
async def get_login_statistics(
    current_user: dict = Depends(get_current_user_token),
    days: int = 30
):
    """Get login statistics for current user"""
    stats = login_history_service.get_login_statistics(
        user_id=current_user["user_id"],
        days=days
    )

    return stats
