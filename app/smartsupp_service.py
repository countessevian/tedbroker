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
                conv_id = items[0].get("id")
                if not conv_id:
                    return None
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


smartsupp_service = SmartsuppService()
