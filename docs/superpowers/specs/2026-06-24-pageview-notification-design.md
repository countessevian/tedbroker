# Page View Notification Design

## Overview

Extend Smartsupp integration to send mobile notifications for every page visit (with rate limiting) in addition to existing login alerts. Notifications include page URL, IP, location, browser, and timestamp.

## Requirements

1. **Trigger**: Any page load on any of the 24 HTML pages
2. **Notification Content**: Page URL, timestamp, IP address, geolocation, browser/OS
3. **Rate Limiting**: 5 notifications per hour per IP address
4. **Deduplication**: None - every page view triggers notification (subject to rate limit)
5. **Delivery**: Mobile push via Smartsupp conversation (same as login alerts)

## Architecture

### Components

1. **Frontend Page View Tracker** (in `chat-events.js`)
   - Captures page load events
   - Sends POST to `/api/pageview` with page, timestamp, userAgent

2. **Backend Page View Endpoint** (new route)
   - Receives page view events
   - Extracts IP and geolocation
   - Applies rate limiting (in-memory)
   - Calls Smartsupp service

3. **Smartsupp Service Extension**
   - New `send_pageview_alert()` method
   - Reuses existing conversation and message pattern

### Data Flow

```
Page Load → chat-events.js → POST /api/pageview → FastAPI endpoint
    → Extract IP/location → Rate limit check → SmartsuppService.send_pageview_alert()
    → Smartsupp API → Mobile push notification
```

## Implementation Details

### Frontend (chat-events.js)

Add page view tracking after existing Smartsupp widget hiding code:

```javascript
// Page View Tracking
(function() {
  function sendPageView() {
    fetch('/api/pageview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        page: window.location.pathname,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent
      })
    }).catch(() => {});
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendPageView);
  } else {
    sendPageView();
  }
})();
```

### Backend (app/routes/pageview.py)

New FastAPI router:

```python
from fastapi import APIRouter, Request
from pydantic import BaseModel
from collections import defaultdict
import time

router = APIRouter()

rate_limit_store = defaultdict(list)
RATE_LIMIT = 5
RATE_WINDOW = 3600

class PageViewEvent(BaseModel):
    page: str
    timestamp: str
    userAgent: str

@router.post("/api/pageview")
async def receive_pageview(event: PageViewEvent, request: Request):
    ip = request.client.host
    if "x-forwarded-for" in request.headers:
        ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    
    now = time.time()
    rate_limit_store[ip] = [t for t in rate_limit_store[ip] if now - t < RATE_WINDOW]
    
    if len(rate_limit_store[ip]) >= RATE_LIMIT:
        return {"status": "rate_limited"}
    
    rate_limit_store[ip].append(now)
    
    from app.login_history import get_location_from_ip, get_device_info
    location = await get_location_from_ip(ip)
    device_info = get_device_info(event.userAgent)
    
    from app.smartsupp_service import smartsupp_service
    await smartsupp_service.send_pageview_alert(
        page=event.page,
        ip=ip,
        location=location,
        browser=device_info
    )
    
    return {"status": "ok"}
```

### Smartsupp Service (app/smartsupp_service.py)

Add method to existing `SmartsuppService` class:

```python
async def send_pageview_alert(self, page: str, ip: str, location: dict, browser: dict):
    """Send page visit notification to Smartsupp conversation."""
    try:
        conversation = await self._get_or_create_conversation()
        if not conversation:
            return
        
        message = (
            f"Page Visit -- Ted Broker\n"
            f"Page: {page}\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"IP: {ip}\n"
            f"Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}\n"
            f"Browser: {browser.get('browser', 'Unknown')} / {browser.get('os', 'Unknown')}"
        )
        
        await self._send_message(conversation['id'], message)
        
    except Exception as e:
        logger.error(f"Failed to send pageview alert: {e}")
```

## Files to Modify

1. **`public/copytradingbroker.io/assets/js/chat-events.js`** - Add page view tracking code
2. **`app/routes/pageview.py`** (new) - Backend endpoint for page view events
3. **`app/smartsupp_service.py`** - Add `send_pageview_alert()` method
4. **`main.py`** - Register new pageview router

## Rate Limiting

- **Storage**: In-memory (Python dict)
- **Limit**: 5 notifications per hour per IP
- **Window**: Rolling 1-hour window
- **Behavior**: Returns `{"status": "rate_limited"}` when exceeded, no notification sent

## Error Handling

- Frontend: Silent failure (`.catch(() => {})`)
- Backend: Graceful failure (logs errors, returns 200)
- Smartsupp: Non-blocking (catches exceptions, logs errors)

## Testing

1. **Unit Tests**: Rate limiting logic, message formatting
2. **Integration Tests**: Endpoint receives valid events, triggers notifications
3. **Manual Testing**: Visit pages, verify notifications appear in Smartsupp mobile app

## Success Criteria

1. Page loads trigger mobile notifications via Smartsupp
2. Notifications include all required information (page, IP, location, browser, time)
3. Rate limiting prevents spam (max 5 per hour per IP)
4. No impact on page load performance
5. Graceful failure if Smartsupp service is unavailable