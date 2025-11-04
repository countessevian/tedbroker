"""
Rate Limiting Middleware
Protects against brute force attacks and API abuse
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Callable


def get_real_ip(request: Request) -> str:
    """
    Get real IP address from request, considering proxies

    Checks headers in order:
    1. X-Forwarded-For (from proxies)
    2. X-Real-IP (from nginx)
    3. Direct remote address
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take first IP if multiple proxies
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fallback to direct connection
    return get_remote_address(request)


# Create limiter instance with custom key function
limiter = Limiter(
    key_func=get_real_ip,
    default_limits=["1000/hour"],  # Global default: 1000 requests per hour
    storage_uri="memory://",  # Use in-memory storage (can be changed to Redis for production)
    strategy="fixed-window"
)

# Custom rate limits for different endpoints
RATE_LIMITS = {
    # Authentication endpoints
    "login": "5/minute",           # 5 login attempts per minute
    "register": "3/minute",         # 3 registration attempts per minute
    "verify_2fa": "10/minute",      # 10 2FA verification attempts per minute
    "resend_2fa": "3/minute",       # 3 resend code attempts per minute
    "forgot_password": "3/minute",  # 3 forgot password attempts per minute
    "reset_password": "5/minute",   # 5 password reset attempts per minute

    # Sensitive operations
    "change_password": "3/minute",
    "delete_account": "1/minute",

    # General API
    "general": "100/minute"
}


def get_rate_limit(endpoint: str) -> str:
    """Get rate limit for specific endpoint"""
    return RATE_LIMITS.get(endpoint, RATE_LIMITS["general"])
