"""
Referral System Service
Handles referral link generation, tracking, and bonus crediting
"""

from datetime import datetime
from typing import Dict, List, Optional
import secrets
import string
from bson import ObjectId

from app.database import get_collection, USERS_COLLECTION

# Collection for storing referrals
REFERRALS_COLLECTION = "referrals"

# Global configuration - Base referral bonus amount
BASE_REFERRAL_BONUS = 50.0  # $50 bonus for each successful referral


class ReferralsService:
    """Service for managing referral system"""

    @staticmethod
    def generate_referral_code(length: int = 8) -> str:
        """
        Generate a unique referral code

        Args:
            length: Length of the referral code

        Returns:
            str: Unique referral code
        """
        characters = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def create_referral_link(user_id: str) -> str:
        """
        Create or get referral link for a user

        Args:
            user_id: User ID

        Returns:
            str: Referral code
        """
        users = get_collection(USERS_COLLECTION)
        user = users.find_one({"_id": ObjectId(user_id)})

        if not user:
            raise ValueError("User not found")

        # Check if user already has a referral code
        if user.get("referral_code"):
            return user["referral_code"]

        # Generate unique referral code
        referral_code = ReferralsService.generate_referral_code()

        # Ensure uniqueness
        while users.find_one({"referral_code": referral_code}):
            referral_code = ReferralsService.generate_referral_code()

        # Update user with referral code
        users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "referral_code": referral_code,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return referral_code

    @staticmethod
    def get_referral_link(user_id: str, base_url: str = "https://tedbrokers.com") -> str:
        """
        Get full referral link for a user

        Args:
            user_id: User ID
            base_url: Base URL for the platform

        Returns:
            str: Full referral link
        """
        referral_code = ReferralsService.create_referral_link(user_id)
        return f"{base_url}/register?ref={referral_code}"

    @staticmethod
    def submit_referral(referral_code: str, referred_user_id: str) -> Dict:
        """
        Submit a referral and credit the referrer's wallet

        Args:
            referral_code: Referral code from the link
            referred_user_id: ID of the user who used the referral link

        Returns:
            dict: Result with success status and details
        """
        users = get_collection(USERS_COLLECTION)
        referrals = get_collection(REFERRALS_COLLECTION)

        # Find the referrer by referral code
        referrer = users.find_one({"referral_code": referral_code})

        if not referrer:
            return {
                "success": False,
                "error": "Invalid referral code"
            }

        referrer_id = str(referrer["_id"])

        # Check if user is trying to refer themselves
        if referrer_id == referred_user_id:
            return {
                "success": False,
                "error": "You cannot use your own referral link"
            }

        # Check if this user has already been referred
        existing_referral = referrals.find_one({"referred_user_id": referred_user_id})

        if existing_referral:
            return {
                "success": False,
                "error": "You have already been referred by someone"
            }

        # Create referral record
        referral_record = {
            "referrer_id": referrer_id,
            "referred_user_id": referred_user_id,
            "referral_code": referral_code,
            "bonus_amount": BASE_REFERRAL_BONUS,
            "status": "completed",
            "created_at": datetime.utcnow()
        }

        referrals.insert_one(referral_record)

        # Credit referrer's wallet with bonus
        users.update_one(
            {"_id": ObjectId(referrer_id)},
            {
                "$inc": {"wallet_balance": BASE_REFERRAL_BONUS},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        # Mark the referred user as having used a referral
        users.update_one(
            {"_id": ObjectId(referred_user_id)},
            {
                "$set": {
                    "referred_by": referrer_id,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return {
            "success": True,
            "referrer_id": referrer_id,
            "bonus_amount": BASE_REFERRAL_BONUS,
            "message": f"Referral bonus of ${BASE_REFERRAL_BONUS} credited to referrer's wallet"
        }

    @staticmethod
    def get_user_referrals(user_id: str) -> Dict:
        """
        Get referral statistics for a user

        Args:
            user_id: User ID

        Returns:
            dict: Referral statistics including count, earnings, and list of referred users
        """
        users = get_collection(USERS_COLLECTION)
        referrals = get_collection(REFERRALS_COLLECTION)

        # Get all referrals made by this user
        user_referrals = list(referrals.find({"referrer_id": user_id}))

        total_referrals = len(user_referrals)
        total_earnings = sum(ref.get("bonus_amount", 0) for ref in user_referrals)

        # Get details of referred users
        referred_users_list = []
        for referral in user_referrals:
            referred_user = users.find_one({"_id": ObjectId(referral["referred_user_id"])})
            if referred_user:
                referred_users_list.append({
                    "username": referred_user.get("username", "Unknown"),
                    "email": referred_user.get("email", "Unknown"),
                    "full_name": referred_user.get("full_name", "Unknown"),
                    "joined_date": referral.get("created_at"),
                    "bonus_earned": referral.get("bonus_amount", 0),
                    "status": referral.get("status", "completed")
                })

        # Count active referrals (users who are still active)
        active_referrals = 0
        for referral in user_referrals:
            referred_user = users.find_one({"_id": ObjectId(referral["referred_user_id"])})
            if referred_user and referred_user.get("is_active", False):
                active_referrals += 1

        return {
            "total_referrals": total_referrals,
            "total_earnings": total_earnings,
            "active_referrals": active_referrals,
            "base_bonus_amount": BASE_REFERRAL_BONUS,
            "referred_users": referred_users_list
        }

    @staticmethod
    def get_referral_code_by_user_id(user_id: str) -> Optional[str]:
        """
        Get referral code for a user

        Args:
            user_id: User ID

        Returns:
            str or None: Referral code if exists
        """
        users = get_collection(USERS_COLLECTION)
        user = users.find_one({"_id": ObjectId(user_id)})

        if user and user.get("referral_code"):
            return user["referral_code"]

        return None


# Create singleton instance
referrals_service = ReferralsService()
