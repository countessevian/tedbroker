"""
Two-Factor Authentication Service
Handles 2FA code generation, storage, and verification
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict
from app.database import get_collection

# Collection for storing 2FA codes
TWOFA_COLLECTION = "twofa_codes"


class TwoFAService:
    """Service for managing 2FA codes"""

    @staticmethod
    def generate_code(length: int = 6) -> str:
        """
        Generate a random verification code

        Args:
            length: Length of the code (default: 6)

        Returns:
            str: Random numeric code
        """
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def create_2fa_session(email: str, user_id: str) -> str:
        """
        Create a new 2FA session and generate code

        Args:
            email: User's email address
            user_id: User's ID

        Returns:
            str: Generated verification code
        """
        collection = get_collection(TWOFA_COLLECTION)

        # Generate 6-digit code
        code = TwoFAService.generate_code()

        # Delete any existing codes for this email
        collection.delete_many({"email": email})

        # Store the code with expiration
        expiry_time = datetime.utcnow() + timedelta(minutes=10)

        session_data = {
            "email": email,
            "user_id": user_id,
            "code": code,
            "created_at": datetime.utcnow(),
            "expires_at": expiry_time,
            "attempts": 0,
            "verified": False
        }

        collection.insert_one(session_data)

        return code

    @staticmethod
    def verify_code(email: str, code: str) -> Dict[str, any]:
        """
        Verify a 2FA code

        Args:
            email: User's email address
            code: Code to verify

        Returns:
            dict: Result containing success status and message
        """
        collection = get_collection(TWOFA_COLLECTION)

        # Find the session
        session = collection.find_one({
            "email": email,
            "verified": False
        })

        if not session:
            return {
                "success": False,
                "error": "No verification code found. Please request a new code."
            }

        # Check if code has expired
        if datetime.utcnow() > session["expires_at"]:
            collection.delete_one({"_id": session["_id"]})
            return {
                "success": False,
                "error": "Verification code has expired. Please request a new code."
            }

        # Check if too many attempts
        if session["attempts"] >= 5:
            collection.delete_one({"_id": session["_id"]})
            return {
                "success": False,
                "error": "Too many failed attempts. Please request a new code."
            }

        # Increment attempts
        collection.update_one(
            {"_id": session["_id"]},
            {"$inc": {"attempts": 1}}
        )

        # Verify the code
        if session["code"] != code:
            return {
                "success": False,
                "error": "Invalid verification code. Please try again."
            }

        # Mark as verified
        collection.update_one(
            {"_id": session["_id"]},
            {"$set": {"verified": True}}
        )

        return {
            "success": True,
            "user_id": session["user_id"],
            "message": "Verification successful"
        }

    @staticmethod
    def cleanup_expired_codes():
        """
        Remove expired 2FA codes from database
        This can be called periodically to clean up old codes
        """
        collection = get_collection(TWOFA_COLLECTION)
        collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })

    @staticmethod
    def get_session(email: str) -> Optional[Dict]:
        """
        Get active 2FA session for an email

        Args:
            email: User's email address

        Returns:
            dict or None: Session data if found
        """
        collection = get_collection(TWOFA_COLLECTION)
        return collection.find_one({
            "email": email,
            "verified": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })

    @staticmethod
    def delete_session(email: str):
        """
        Delete 2FA session for an email

        Args:
            email: User's email address
        """
        collection = get_collection(TWOFA_COLLECTION)
        collection.delete_many({"email": email})


# Create singleton instance
twofa_service = TwoFAService()
