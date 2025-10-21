"""
Admin Service
Handles admin user management and authentication
"""

from datetime import datetime
from typing import Optional, Dict
from bson import ObjectId

from app.database import get_collection
from app.auth import get_password_hash, verify_password

# Collection for admin users
ADMINS_COLLECTION = "admins"


class AdminService:
    """Service for managing admin users"""

    @staticmethod
    def check_admin_exists() -> bool:
        """
        Check if any admin exists in the system

        Returns:
            bool: True if at least one admin exists
        """
        admins = get_collection(ADMINS_COLLECTION)
        return admins.count_documents({}) > 0

    @staticmethod
    def create_admin(username: str, email: str, password: str, full_name: str) -> Dict:
        """
        Create a new admin user (only if no admin exists)

        Args:
            username: Admin username
            email: Admin email
            password: Plain text password
            full_name: Admin full name

        Returns:
            dict: Created admin data

        Raises:
            ValueError: If admin already exists
        """
        admins = get_collection(ADMINS_COLLECTION)

        # Check if admin already exists
        if AdminService.check_admin_exists():
            raise ValueError("Admin already exists. Only one admin can be registered.")

        # Check for duplicate username or email
        if admins.find_one({"username": username}):
            raise ValueError("Username already taken")

        if admins.find_one({"email": email}):
            raise ValueError("Email already registered")

        # Create admin document
        admin_dict = {
            "username": username,
            "email": email,
            "hashed_password": get_password_hash(password),
            "full_name": full_name,
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": None
        }

        # Insert admin into database
        result = admins.insert_one(admin_dict)
        admin_dict["_id"] = result.inserted_id

        return {
            "id": str(admin_dict["_id"]),
            "username": admin_dict["username"],
            "email": admin_dict["email"],
            "full_name": admin_dict["full_name"],
            "role": admin_dict["role"],
            "created_at": admin_dict["created_at"]
        }

    @staticmethod
    def authenticate_admin(username: str, password: str) -> Optional[Dict]:
        """
        Authenticate an admin user

        Args:
            username: Admin username
            password: Plain text password

        Returns:
            dict: Admin data if authenticated, None otherwise
        """
        admins = get_collection(ADMINS_COLLECTION)
        admin = admins.find_one({"username": username})

        if not admin:
            return None

        if not verify_password(password, admin["hashed_password"]):
            return None

        if not admin.get("is_active", False):
            return None

        # Update last login
        admins.update_one(
            {"_id": admin["_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )

        return {
            "id": str(admin["_id"]),
            "username": admin["username"],
            "email": admin["email"],
            "full_name": admin["full_name"],
            "role": admin["role"],
            "last_login": datetime.utcnow()
        }

    @staticmethod
    def get_admin_by_id(admin_id: str) -> Optional[Dict]:
        """
        Get admin by ID

        Args:
            admin_id: Admin ID

        Returns:
            dict: Admin data if found, None otherwise
        """
        admins = get_collection(ADMINS_COLLECTION)
        try:
            admin = admins.find_one({"_id": ObjectId(admin_id)})
            if admin:
                return {
                    "id": str(admin["_id"]),
                    "username": admin["username"],
                    "email": admin["email"],
                    "full_name": admin["full_name"],
                    "role": admin["role"],
                    "is_active": admin.get("is_active", True),
                    "created_at": admin["created_at"],
                    "last_login": admin.get("last_login")
                }
            return None
        except:
            return None

    @staticmethod
    def verify_admin_token(admin_id: str) -> bool:
        """
        Verify that an admin exists and is active

        Args:
            admin_id: Admin ID from JWT token

        Returns:
            bool: True if admin is valid and active
        """
        admin = AdminService.get_admin_by_id(admin_id)
        return admin is not None and admin.get("is_active", False)


# Create singleton instance
admin_service = AdminService()
