from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Optional
from bson import ObjectId
from datetime import datetime

from app.database import get_collection, USERS_COLLECTION
from app.auth import get_current_user_token

router = APIRouter(prefix="/api/language", tags=["language"])

# Top 10 most spoken languages in the world with their language codes and country flags
SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "flag": "🇺🇸", "country_code": "US"},
    "zh": {"name": "中文 (Chinese)", "flag": "🇨🇳", "country_code": "CN"},
    "hi": {"name": "हिन्दी (Hindi)", "flag": "🇮🇳", "country_code": "IN"},
    "es": {"name": "Español (Spanish)", "flag": "🇪🇸", "country_code": "ES"},
    "fr": {"name": "Français (French)", "flag": "🇫🇷", "country_code": "FR"},
    "ar": {"name": "العربية (Arabic)", "flag": "🇸🇦", "country_code": "SA"},
    "bn": {"name": "বাংলা (Bengali)", "flag": "🇧🇩", "country_code": "BD"},
    "ru": {"name": "Русский (Russian)", "flag": "🇷🇺", "country_code": "RU"},
    "pt": {"name": "Português (Portuguese)", "flag": "🇵🇹", "country_code": "PT"},
    "de": {"name": "Deutsch (German)", "flag": "🇩🇪", "country_code": "DE"}
}

# Map country codes to language codes (for IP-based detection)
COUNTRY_TO_LANGUAGE = {
    "US": "en", "GB": "en", "CA": "en", "AU": "en", "NZ": "en", "IE": "en",
    "CN": "zh", "TW": "zh", "HK": "zh", "SG": "zh",
    "IN": "hi",
    "ES": "es", "MX": "es", "AR": "es", "CO": "es", "PE": "es", "VE": "es", "CL": "es",
    "FR": "fr", "BE": "fr", "CH": "fr", "LU": "fr",
    "SA": "ar", "AE": "ar", "EG": "ar", "IQ": "ar", "JO": "ar", "KW": "ar", "LB": "ar",
    "BD": "bn",
    "RU": "ru", "BY": "ru", "KZ": "ru",
    "PT": "pt", "BR": "pt", "AO": "pt", "MZ": "pt",
    "DE": "de", "AT": "de"
}


def get_location_from_ip(ip_address: str) -> Dict:
    """
    Get country code from IP address using ipapi.co
    Reuses the logic from login_history.py
    """
    # Skip local/private IPs
    if ip_address in ["Unknown", "127.0.0.1", "localhost"] or ip_address.startswith("192.168.") or ip_address.startswith("10."):
        return {"country_code": "US"}  # Default to US for local IPs

    try:
        import requests
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)

        if response.status_code == 200:
            data = response.json()
            return {
                "country_code": data.get("country_code", "US"),
                "country": data.get("country_name", "Unknown"),
                "city": data.get("city", "Unknown")
            }
    except Exception as e:
        print(f"Error getting location from IP {ip_address}: {str(e)}")

    return {"country_code": "US"}  # Default to US on error


def get_ip_address(request: Request) -> str:
    """Extract the real IP address from request headers"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    return request.client.host if request.client else "Unknown"


@router.get("/supported")
async def get_supported_languages():
    """
    Get list of all supported languages with flags
    """
    return {
        "languages": SUPPORTED_LANGUAGES,
        "default": "en"
    }


@router.get("/detect")
async def detect_language(request: Request):
    """
    Detect language based on user's IP address
    Returns suggested language code based on their location
    """
    ip_address = get_ip_address(request)
    location = get_location_from_ip(ip_address)
    country_code = location.get("country_code", "US")

    # Map country to language
    detected_language = COUNTRY_TO_LANGUAGE.get(country_code, "en")

    return {
        "detected_language": detected_language,
        "country_code": country_code,
        "country": location.get("country", "Unknown"),
        "language_info": SUPPORTED_LANGUAGES.get(detected_language, SUPPORTED_LANGUAGES["en"]),
        "ip_address": ip_address
    }


@router.get("/preference")
async def get_user_language_preference(current_user: dict = Depends(get_current_user_token)):
    """
    Get authenticated user's saved language preference
    """
    users = get_collection(USERS_COLLECTION)
    user_id = current_user["user_id"]

    user = users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    preferred_language = user.get("preferred_language", "en")

    return {
        "preferred_language": preferred_language,
        "language_info": SUPPORTED_LANGUAGES.get(preferred_language, SUPPORTED_LANGUAGES["en"])
    }


@router.put("/preference")
async def set_user_language_preference(
    language_data: dict,
    current_user: dict = Depends(get_current_user_token)
):
    """
    Save user's language preference
    """
    users = get_collection(USERS_COLLECTION)
    user_id = current_user["user_id"]

    language_code = language_data.get("language")

    if not language_code:
        raise HTTPException(status_code=400, detail="language field is required")

    if language_code not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language_code}")

    # Update user's language preference
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "preferred_language": language_code,
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "message": "Language preference updated successfully",
        "preferred_language": language_code,
        "language_info": SUPPORTED_LANGUAGES[language_code]
    }
