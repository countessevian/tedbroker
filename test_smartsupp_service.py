"""Test Smartsupp service graceful failure (no API key required)"""

import os
import sys

# Ensure API key is not set for this test
if "SMARTSUPP_API_KEY" in os.environ:
    del os.environ["SMARTSUPP_API_KEY"]

sys.path.insert(0, os.path.dirname(__file__))

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
        print("PASS: send_login_alert did not raise when not initialized")
    except Exception as e:
        print(f"FAIL: send_login_alert raised: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_send_login_alert_graceful_failure()
