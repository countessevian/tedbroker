from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Optional

from app.auth import get_current_user_token
from app.referrals_service import referrals_service, BASE_REFERRAL_BONUS

router = APIRouter(prefix="/api/referrals", tags=["Referrals"])


class ReferralSubmission(BaseModel):
    """Schema for submitting a referral code"""
    referral_code: str


@router.get("/my-link")
async def get_my_referral_link(current_user: dict = Depends(get_current_user_token)):
    """
    Get the current user's referral link

    Returns:
        dict: Referral link and code
    """
    try:
        referral_link = referrals_service.get_referral_link(
            user_id=current_user["user_id"],
            base_url="https://tedbrokers.com"
        )

        referral_code = referrals_service.get_referral_code_by_user_id(
            user_id=current_user["user_id"]
        )

        return {
            "referral_link": referral_link,
            "referral_code": referral_code,
            "base_bonus": BASE_REFERRAL_BONUS
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate referral link: {str(e)}"
        )


@router.get("/my-statistics")
async def get_my_referral_statistics(current_user: dict = Depends(get_current_user_token)):
    """
    Get referral statistics for the current user

    Returns:
        dict: Total referrals, earnings, and list of referred users
    """
    try:
        stats = referrals_service.get_user_referrals(user_id=current_user["user_id"])
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch referral statistics: {str(e)}"
        )


@router.post("/submit")
async def submit_referral_code(
    referral_data: ReferralSubmission,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Submit a referral code (used by new users)

    Args:
        referral_data: Contains the referral code
        current_user: Current authenticated user

    Returns:
        dict: Success message and bonus amount
    """
    try:
        result = referrals_service.submit_referral(
            referral_code=referral_data.referral_code,
            referred_user_id=current_user["user_id"]
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )

        return {
            "success": True,
            "message": result["message"],
            "bonus_amount": result["bonus_amount"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit referral: {str(e)}"
        )


@router.post("/skip")
async def skip_referral(current_user: dict = Depends(get_current_user_token)):
    """
    Mark that user has skipped the referral code submission

    Args:
        current_user: Current authenticated user

    Returns:
        dict: Success message
    """
    try:
        result = referrals_service.mark_referral_skipped(user_id=current_user["user_id"])

        return {
            "success": True,
            "message": "Referral modal skipped successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to skip referral: {str(e)}"
        )


@router.get("/config")
async def get_referral_config():
    """
    Get referral system configuration (public endpoint)

    Returns:
        dict: Configuration including base bonus amount
    """
    return {
        "base_referral_bonus": BASE_REFERRAL_BONUS,
        "currency": "USD"
    }
