# Smartsupp Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate Smartsupp for invisible visitor tracking and login push notifications.

**Architecture:** A hidden Smartsupp JS widget on all pages handles visitor tracking (mobile push). A new Python service (`smartsupp_service.py`) creates a persistent "Login Alert" conversation and sends login details as messages via the Smartsupp v2 REST API, triggering mobile push notifications.

**Tech Stack:** Smartsupp v2 REST API, Python (httpx), FastAPI, vanilla JS

**Files:**
- Create: `app/smartsupp_service.py`
- Modify: `app/routes/auth.py`
- Modify: `public/copytradingbroker.io/assets/js/chat-events.js`
- Modify: `.env.example`
- Modify: `.env`

---

### Task 1: Add Smartsupp widget to chat-events.js

**Files:**
- Modify: `public/copytradingbroker.io/assets/js/chat-events.js`

- [ ] **Step 1: Add Smartsupp loader script and hide widget**

Append to the end of `chat-events.js`:

```javascript
// Smartsupp — hidden visitor tracking
(function(w,d,s,o,f,js,fjs){
  w['Smartsupp']=o; w[o]=w[o]||function(){(w[o].q=w[o].q||[]).push(arguments)};
  js=d.createElement(s); fjs=d.getElementsByTagName(s)[0];
  js.id=o; js.src=f; js.async=1; fjs.parentNode.insertBefore(js,fjs);
})(window,document,'script','smartsupp','https://www.smartsuppchat.com/loader.js?key=046eb16e4fcdd1c4985f1a6f93910d3484a02f05');

smartsupp('widget', 'hide');
```

- [ ] **Step 2: Verify widget loads invisibly**

Run: `python3 -c "
import re
with open('public/copytradingbroker.io/assets/js/chat-events.js') as f:
    content = f.read()
assert 'smartsuppchat.com/loader.js' in content, 'Smartsupp loader not found'
assert \"smartsupp('widget', 'hide')\" in content, 'Widget hide call not found'
print('OK: Smartsupp widget embed found')
"`


### Task 2: Create smartsupp_service.py

**Files:**
- Create: `app/smartsupp_service.py`

- [ ] **Step 1: Create the service file**

Write `app/smartsupp_service.py`:

```python
import os
import httpx
from typing import Optional, Dict
from datetime import datetime

SMARTSUPP_API_KEY = os.getenv("SMARTSUPP_API_KEY", "")
SMARTSUPP_BASE = "https://api.smartsupp.com/v2"
SMARTSUPP_ALERT_EMAIL = os.getenv("SMARTSUPP_ALERT_EMAIL", "login-alerts@tedbroker.com")
ALERT_CONVERSATION_EXT_ID = "tedbroker-login-alerts"

HEADERS = {
    "Authorization": f"Bearer {SMARTSUPP_API_KEY}",
    "Content-Type": "application/json"
}


class SmartsuppService:
    def __init__(self):
        self._contact_id: Optional[str] = None
        self._conversation_id: Optional[str] = None
        self._initialized = False

    def _ensure_initialized(self):
        if not self._initialized:
            self._initialize()
            self._initialized = True

    def _initialize(self):
        if not SMARTSUPP_API_KEY:
            print("Warning: SMARTSUPP_API_KEY not set, Smartsupp notifications disabled")
            return

        try:
            with httpx.Client(base_url=SMARTSUPP_BASE, headers=HEADERS, timeout=10) as client:
                self._contact_id = self._find_or_create_contact(client)
                if self._contact_id:
                    self._conversation_id = self._find_or_create_conversation(client)
        except Exception as e:
            print(f"Error initializing Smartsupp: {e}")

    def _find_or_create_contact(self, client: httpx.Client) -> Optional[str]:
        resp = client.get("/contacts/find", params={"email": SMARTSUPP_ALERT_EMAIL})
        if resp.status_code == 200:
            data = resp.json()
            if data.get("id"):
                return data["id"]

        resp = client.post("/contacts", json={"email": SMARTSUPP_ALERT_EMAIL, "name": "Login Alert"})
        if resp.status_code in (200, 201):
            return resp.json().get("id")

        print(f"Failed to create Smartsupp contact: {resp.status_code} {resp.text}")
        return None

    def _find_or_create_conversation(self, client: httpx.Client) -> Optional[str]:
        resp = client.post("/conversations/search", json={
            "size": 5,
            "query": [{"field": "ext_id", "value": ALERT_CONVERSATION_EXT_ID}],
            "sort": [{"created_at": "desc"}]
        })
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            if items:
                conv_id = items[0]["id"]
                status = items[0].get("status")
                if status in ("closed", "finished"):
                    reopen = client.patch(f"/conversations/{conv_id}/open")
                    if reopen.status_code not in (200, 201):
                        conv_id = None
                if conv_id:
                    return conv_id

        resp = client.post("/conversations", json={
            "contact_id": self._contact_id,
            "ext_id": ALERT_CONVERSATION_EXT_ID,
            "text": "Login Alert conversation started"
        })
        if resp.status_code in (200, 201):
            return resp.json().get("id")

        print(f"Failed to create Smartsupp conversation: {resp.status_code} {resp.text}")
        return None

    def send_login_alert(
        self,
        email: str,
        username: str,
        ip_address: str,
        device_info: Dict,
        location: Dict,
        timestamp: Optional[datetime] = None
    ):
        self._ensure_initialized()

        if not self._conversation_id:
            print("Warning: Smartsupp conversation not available, skipping login alert")
            return

        ts = (timestamp or datetime.utcnow()).strftime("%Y-%m-%d %H:%M UTC")
        country = location.get("country", "Unknown")
        city = location.get("city", "")
        loc_str = f"{city}, {country}" if city else country
        browser = device_info.get("browser", "Unknown")
        os_str = device_info.get("os", "Unknown")

        message = (
            f"New Login \u2014 Ted Broker\n"
            f"User: {email}\n"
            f"Time: {ts}\n"
            f"IP: {ip_address}\n"
            f"Location: {loc_str}\n"
            f"Device: {browser} / {os_str}"
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
                    print(f"Failed to send Smartsupp login alert: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Error sending Smartsupp login alert: {e}")


smartsupp_service = SmartsuppService()
```

- [ ] **Step 2: Verify the service file**

Run: `python3 -c "
import ast
with open('app/smartsupp_service.py') as f:
    ast.parse(f.read())
print('OK: smartsupp_service.py parses successfully')
"`


### Task 3: Hook into login flow (no 2FA)

**Files:**
- Modify: `app/routes/auth.py`

- [ ] **Step 1: Add import**

Add the import after line 28:
```python
from app.smartsupp_service import smartsupp_service
```

- [ ] **Step 2: Add Smartsupp call after successful login (no 2FA branch)**

After the email notification try/except at lines 219-228, add:
```python
        # Send Smartsupp login alert
        try:
            smartsupp_service.send_login_alert(
                email=user["email"],
                username=username,
                ip_address=ip_address,
                device_info=device_info,
                location=location
            )
        except Exception as e:
            print(f"Failed to send Smartsupp login alert: {e}")
```


### Task 4: Hook into login flow (with 2FA)

**Files:**
- Modify: `app/routes/auth.py`

- [ ] **Step 1: Add Smartsupp call after 2FA verification**

After the email notification try/except at lines 553-554 in `verify_2fa`, add:
```python
    # Send Smartsupp login alert
    try:
        smartsupp_service.send_login_alert(
            email=user["email"],
            username=username,
            ip_address=ip_address,
            device_info=device_info,
            location=location
        )
    except Exception as e:
        print(f"Failed to send Smartsupp login alert: {e}")
```


### Task 5: Add environment configuration

**Files:**
- Modify: `.env.example`
- Modify: `.env`

- [ ] **Step 1: Add to `.env.example`**

Append to the end of `.env.example`:
```
# Smartsupp Integration
SMARTSUPP_API_KEY=your-smartsupp-api-key
SMARTSUPP_ALERT_EMAIL=login-alerts@tedbroker.com
```

- [ ] **Step 2: Add to `.env`**

Append to the end of `.env`:
```
# Smartsupp Integration
SMARTSUPP_API_KEY=046eb16e4fcdd1c4985f1a6f93910d3484a02f05
SMARTSUPP_ALERT_EMAIL=login-alerts@tedbroker.com
```


### Task 6: Create simple end-to-end test

**Files:**
- Create: `test_smartsupp_service.py`

- [ ] **Step 1: Write test**

```python
"""Tests for Smartsupp integration service"""
from app.smartsupp_service import SmartsuppService


def test_send_login_alert_graceful_failure():
    """Should not crash when API key is missing"""
    service = SmartsuppService()
    try:
        service.send_login_alert(
            email="test@example.com",
            username="Test User",
            ip_address="192.168.1.1",
            device_info={"browser": "Chrome 120", "os": "Windows 10", "device": "PC"},
            location={"country": "Nigeria", "city": "Lagos"}
        )
    except Exception:
        assert False, "send_login_alert should not raise when not initialized"
```

- [ ] **Step 2: Run test**

Run: `python3 -m pytest test_smartsupp_service.py -v`
Expected: PASS (1 passed)
