# Page View Notification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Smartsupp mobile notifications for every page visit with rate limiting (5 per hour per IP)

**Architecture:** Frontend JavaScript captures page loads and sends to backend endpoint. Backend applies rate limiting and sends notifications via existing Smartsupp service.

**Tech Stack:** FastAPI, Python, JavaScript, Smartsupp REST API

---

## File Structure

| File | Purpose |
|------|---------|
| `app/routes/pageview.py` | New endpoint for receiving page view events |
| `app/smartsupp_service.py` | Add `send_pageview_alert()` method |
| `public/copytradingbroker.io/assets/js/chat-events.js` | Add page view tracking code |
| `main.py` | Register new pageview router |

---

### Task 1: Add pageview alert method to Smartsupp service

**Files:**
- Modify: `app/smartsupp_service.py:136-138`

- [ ] **Step 1: Add send_pageview_alert method**

Add the following method to the `SmartsuppService` class, before the closing of the class definition (before line 138):

```python
    def send_pageview_alert(
        self,
        page: str,
        ip_address: str,
        device_info: Dict,
        location: Dict,
        timestamp: Optional[datetime] = None
    ):
        self._ensure_initialized()

        if not self._conversation_id:
            print("Warning: Smartsupp conversation not available, skipping pageview alert")
            return

        ts = (timestamp or datetime.utcnow()).strftime("%Y-%m-%d %H:%M UTC")
        country = location.get("country", "Unknown")
        city = location.get("city", "")
        loc_str = f"{city}, {country}" if city else country
        browser = device_info.get("browser", "Unknown")
        os_str = device_info.get("os", "Unknown")

        message = (
            f"Page Visit \u2014 Ted Broker\n"
            f"Page: {page}\n"
            f"Time: {ts}\n"
            f"IP: {ip_address}\n"
            f"Location: {loc_str}\n"
            f"Browser: {browser} / {os_str}"
        )

        try:
            with httpx.Client(base_url=SMARTSUPP_BASE, headers=HEADERS, timeout=10) as client:
                resp = client.post(
                    f"/conversations/{self._conversation_id}/messages",
                    json={
                        "type": "message",
                        "sub_type": "contact",
                        "contact_id": self._contact_id,
                        "content": {
                            "type": "text",
                            "text": message
                        }
                    }
                )
                if resp.status_code not in (200, 201):
                    print(f"Failed to send Smartsupp pageview alert: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Error sending Smartsupp pageview alert: {e}")
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile app/smartsupp_service.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add app/smartsupp_service.py
git commit -m "feat: add send_pageview_alert method to Smartsupp service"
```

---

### Task 2: Create pageview route with rate limiting

**Files:**
- Create: `app/routes/pageview.py`

- [ ] **Step 1: Create the pageview route file**

Create `app/routes/pageview.py` with the following content:

```python
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
```

- [ ] **Step 2: Verify syntax**

Run: `python -m py_compile app/routes/pageview.py`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add app/routes/pageview.py
git commit -m "feat: add pageview endpoint with rate limiting"
```

---

### Task 3: Register pageview router in main.py

**Files:**
- Modify: `main.py:11` (import line)
- Modify: `main.py:69` (include_router)

- [ ] **Step 1: Add pageview to imports**

In `main.py`, line 11, add `pageview` to the imports from `app.routes`:

Change:
```python
from app.routes import auth, traders, plans, etf_plans, defi_plans, options_plans, wallet, referrals, admin, deposits, investments, news, crypto_wallets, withdrawals, chat, onboarding, notifications, language
```

To:
```python
from app.routes import auth, traders, plans, etf_plans, defi_plans, options_plans, wallet, referrals, admin, deposits, investments, news, crypto_wallets, withdrawals, chat, onboarding, notifications, language, pageview
```

- [ ] **Step 2: Include pageview router**

In `main.py`, after line 69 (after `app.include_router(language.router)`), add:

```python
# Include pageview routes
app.include_router(pageview.router)
```

- [ ] **Step 3: Verify syntax**

Run: `python -m py_compile main.py`
Expected: No output (success)

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: register pageview router in main app"
```

---

### Task 4: Add page view tracking to chat-events.js

**Files:**
- Modify: `public/copytradingbroker.io/assets/js/chat-events.js:76`

- [ ] **Step 1: Add page view tracking code**

At the end of `chat-events.js` (after line 76), add the following code:

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
    }).catch(() => {}); // Silent failure - non-blocking
  }
  
  // Send on page load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendPageView);
  } else {
    sendPageView();
  }
})();
```

- [ ] **Step 2: Verify JavaScript syntax**

Run: `node -c public/copytradingbroker.io/assets/js/chat-events.js`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add public/copytradingbroker.io/assets/js/chat-events.js
git commit -m "feat: add page view tracking to chat-events.js"
```

---

### Task 5: Test the integration

**Files:**
- Test: Manual testing

- [ ] **Step 1: Start the development server**

Run: `python main.py`
Expected: Server starts on port 8000

- [ ] **Step 2: Visit a page in browser**

Open browser and navigate to `http://localhost:8000/`
Expected: Page loads normally

- [ ] **Step 3: Check server logs**

Check terminal output for any errors
Expected: No errors related to pageview endpoint

- [ ] **Step 4: Verify Smartsupp notification**

Check Smartsupp mobile app for notification
Expected: "Page Visit — Ted Broker" notification with page URL, time, IP, location, browser

- [ ] **Step 5: Test rate limiting**

Refresh the page 6 times quickly (within 1 minute)
Expected: First 5 requests return `{"status":"ok"}`, 6th returns `{"status":"rate_limited"}`

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: complete page view notification system"
```

---

## Summary

After completing all tasks:

1. **Frontend** (`chat-events.js`): Sends page view events on every page load
2. **Backend** (`pageview.py`): Receives events, applies rate limiting (5/hour/IP), sends notifications
3. **Smartsupp** (`smartsupp_service.py`): Sends "Page Visit" notifications to mobile app
4. **Rate Limiting**: In-memory storage, 5 notifications per hour per IP address

The system reuses existing patterns from the login alert implementation and requires no changes to HTML files (chat-events.js is already included in all 24 pages).