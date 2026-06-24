from fastapi import APIRouter, Request
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict
import time

from app.login_history import LoginHistoryService
from app.smartsupp_service import smartsupp_service

router = APIRouter()

# In-memory rate limiter: {ip: [timestamp, timestamp, ...]}
rate_limit_store = defaultdict(list)
RATE_LIMIT = 5  # max notifications per hour
RATE_WINDOW = 3600  # 1 hour in seconds


class PageViewEvent(BaseModel):
    page: str
    timestamp: str
    userAgent: str


@router.post("/api/pageview")
async def receive_pageview(event: PageViewEvent, request: Request):
    # Get client IP
    ip = LoginHistoryService.get_ip_address(request)
    
    # Rate limiting check
    now = time.time()
    # Clean old entries outside the window
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < RATE_WINDOW]
    
    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return {"status": "rate_limited"}
    
    # Add current timestamp
    rate_limit_store[ip].append(now)
    
    # Extract device info from user agent string
    import user_agents
    ua = user_agents.parse(event.userAgent)
    device_info = {
        "browser": f"{ua.browser.family} {ua.browser.version_string}",
        "os": f"{ua.os.family} {ua.os.version_string}",
        "device": ua.device.family
    }
    
    # Get location from IP
    location = LoginHistoryService.get_location_from_ip(ip)
    
    # Parse timestamp from frontend
    try:
        ts = datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
    except ValueError:
        ts = datetime.utcnow()
    
    # Send Smartsupp notification
    smartsupp_service.send_pageview_alert(
        page=event.page,
        ip_address=ip,
        device_info=device_info,
        location=location,
        timestamp=ts
    )
    
    return {"status": "ok"}
