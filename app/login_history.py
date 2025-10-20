"""
Login History Tracking System
Tracks all login attempts and provides security analytics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from fastapi import Request
import user_agents
from app.database import get_collection

# Collection for storing login history
LOGIN_HISTORY_COLLECTION = "login_history"


class LoginHistoryService:
    """Service for tracking and analyzing login history"""

    @staticmethod
    def get_device_info(request: Request) -> Dict:
        """Extract device and browser information from request"""
        user_agent_string = request.headers.get("User-Agent", "Unknown")
        ua = user_agents.parse(user_agent_string)

        return {
            "browser": f"{ua.browser.family} {ua.browser.version_string}",
            "os": f"{ua.os.family} {ua.os.version_string}",
            "device": ua.device.family,
            "is_mobile": ua.is_mobile,
            "is_tablet": ua.is_tablet,
            "is_pc": ua.is_pc,
            "user_agent": user_agent_string
        }

    @staticmethod
    def get_ip_address(request: Request) -> str:
        """Get real IP address from request"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "Unknown"

    @staticmethod
    def get_location_from_ip(ip_address: str) -> Dict:
        """
        Get approximate location from IP address
        Note: This is a placeholder. In production, use a service like ipapi.co or ipstack.com
        """
        # TODO: Implement IP geolocation service
        return {
            "country": "Unknown",
            "city": "Unknown",
            "region": "Unknown"
        }

    @staticmethod
    def record_login_attempt(
        email: str,
        user_id: Optional[str],
        request: Request,
        success: bool,
        failure_reason: Optional[str] = None
    ) -> str:
        """
        Record a login attempt

        Args:
            email: User's email
            user_id: User ID if login successful
            request: FastAPI request object
            success: Whether login was successful
            failure_reason: Reason for failure (if applicable)

        Returns:
            str: Login attempt ID
        """
        collection = get_collection(LOGIN_HISTORY_COLLECTION)

        ip_address = LoginHistoryService.get_ip_address(request)
        device_info = LoginHistoryService.get_device_info(request)
        location = LoginHistoryService.get_location_from_ip(ip_address)

        login_record = {
            "email": email,
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "failure_reason": failure_reason,
            "timestamp": datetime.utcnow(),
            "device_info": device_info,
            "location": location
        }

        result = collection.insert_one(login_record)
        return str(result.inserted_id)

    @staticmethod
    def get_user_login_history(
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """
        Get login history for a specific user

        Args:
            user_id: User ID
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of login records
        """
        collection = get_collection(LOGIN_HISTORY_COLLECTION)

        cursor = collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).skip(offset).limit(limit)

        records = []
        for record in cursor:
            record["_id"] = str(record["_id"])
            records.append(record)

        return records

    @staticmethod
    def get_failed_attempts(
        email: str,
        minutes: int = 15
    ) -> int:
        """
        Get number of failed login attempts for an email in the last X minutes

        Args:
            email: User's email
            minutes: Time window in minutes

        Returns:
            int: Number of failed attempts
        """
        collection = get_collection(LOGIN_HISTORY_COLLECTION)

        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)

        count = collection.count_documents({
            "email": email,
            "success": False,
            "timestamp": {"$gte": time_threshold}
        })

        return count

    @staticmethod
    def check_suspicious_activity(email: str, request: Request) -> Dict:
        """
        Check for suspicious login activity

        Returns:
            dict: Analysis results with flags for suspicious activity
        """
        collection = get_collection(LOGIN_HISTORY_COLLECTION)

        ip_address = LoginHistoryService.get_ip_address(request)
        current_time = datetime.utcnow()

        # Check last successful login
        last_success = collection.find_one(
            {"email": email, "success": True},
            sort=[("timestamp", -1)]
        )

        suspicious_flags = {
            "is_suspicious": False,
            "reasons": [],
            "risk_level": "low"  # low, medium, high
        }

        if last_success:
            # Check if login from different location
            if last_success.get("ip_address") != ip_address:
                # Check if locations are significantly different
                last_location = last_success.get("location", {})
                current_location = LoginHistoryService.get_location_from_ip(ip_address)

                if (last_location.get("country") != current_location.get("country") and
                    last_location.get("country") != "Unknown"):
                    suspicious_flags["reasons"].append("Login from different country")
                    suspicious_flags["risk_level"] = "medium"

            # Check time since last login (very quick succession might be suspicious)
            time_diff = (current_time - last_success["timestamp"]).total_seconds() / 60
            if time_diff < 1:  # Less than 1 minute
                suspicious_flags["reasons"].append("Multiple rapid login attempts")
                suspicious_flags["risk_level"] = "medium"

        # Check for recent failed attempts
        failed_count = LoginHistoryService.get_failed_attempts(email, minutes=15)
        if failed_count >= 3:
            suspicious_flags["reasons"].append(f"{failed_count} failed attempts in last 15 minutes")
            suspicious_flags["risk_level"] = "high"

        # Check for login attempts from multiple IPs in short time
        recent_ips = collection.distinct(
            "ip_address",
            {
                "email": email,
                "timestamp": {"$gte": current_time - timedelta(minutes=30)}
            }
        )
        if len(recent_ips) >= 3:
            suspicious_flags["reasons"].append(f"Login attempts from {len(recent_ips)} different IPs in 30 minutes")
            suspicious_flags["risk_level"] = "high"

        suspicious_flags["is_suspicious"] = len(suspicious_flags["reasons"]) > 0

        return suspicious_flags

    @staticmethod
    def get_login_statistics(user_id: str, days: int = 30) -> Dict:
        """
        Get login statistics for a user

        Args:
            user_id: User ID
            days: Number of days to analyze

        Returns:
            dict: Statistics
        """
        collection = get_collection(LOGIN_HISTORY_COLLECTION)

        time_threshold = datetime.utcnow() - timedelta(days=days)

        # Get all login attempts in time period
        attempts = list(collection.find({
            "user_id": user_id,
            "timestamp": {"$gte": time_threshold}
        }))

        total_attempts = len(attempts)
        successful_logins = sum(1 for a in attempts if a["success"])
        failed_logins = total_attempts - successful_logins

        # Get unique IPs and devices
        unique_ips = set(a["ip_address"] for a in attempts)
        unique_devices = set(a["device_info"].get("device", "Unknown") for a in attempts)

        # Get most recent login
        recent_login = None
        if attempts:
            recent_login = max(attempts, key=lambda x: x["timestamp"])

        return {
            "total_attempts": total_attempts,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "unique_ips": len(unique_ips),
            "unique_devices": len(unique_devices),
            "most_recent_login": recent_login.get("timestamp") if recent_login else None,
            "most_recent_ip": recent_login.get("ip_address") if recent_login else None
        }


# Create singleton instance
login_history_service = LoginHistoryService()
