"""
IP-Based Security Alerts Service
Sends email alerts for suspicious login activity
"""

from datetime import datetime
from typing import Dict
from app.email_service import email_service


class SecurityAlertsService:
    """Service for sending security alerts to users"""

    @staticmethod
    def send_suspicious_login_alert(
        email: str,
        username: str,
        suspicious_activity: Dict,
        ip_address: str,
        device_info: Dict,
        location: Dict
    ) -> bool:
        """
        Send security alert email for suspicious login activity

        Args:
            email: User's email address
            username: User's username or full name
            suspicious_activity: Dict with suspicious activity flags
            ip_address: IP address of login attempt
            device_info: Device and browser information
            location: Location information

        Returns:
            bool: True if email sent successfully
        """
        if not suspicious_activity.get("is_suspicious"):
            return False

        risk_level = suspicious_activity.get("risk_level", "low")
        reasons = suspicious_activity.get("reasons", [])

        # Determine risk color
        risk_colors = {
            "low": "#FFA726",
            "medium": "#FF7043",
            "high": "#E53935"
        }
        risk_color = risk_colors.get(risk_level, "#FFA726")

        subject = f"Security Alert: Suspicious Login Attempt Detected"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: {risk_color};
                    padding: 30px;
                    text-align: center;
                }}
                .header-icon {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .header h1 {{
                    color: white;
                    font-size: 24px;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .alert-box {{
                    background: #fff3cd;
                    border-left: 4px solid {risk_color};
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 4px;
                }}
                .alert-title {{
                    font-weight: bold;
                    color: #856404;
                    margin-bottom: 10px;
                }}
                .alert-reasons {{
                    list-style: none;
                    padding: 0;
                    margin: 10px 0 0 0;
                }}
                .alert-reasons li {{
                    padding: 5px 0;
                    color: #856404;
                }}
                .alert-reasons li:before {{
                    content: "⚠ ";
                    margin-right: 5px;
                }}
                .info-section {{
                    background: #f8f9fa;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 25px 0;
                }}
                .info-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #dee2e6;
                }}
                .info-row:last-child {{
                    border-bottom: none;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #495057;
                }}
                .info-value {{
                    color: #6c757d;
                    text-align: right;
                }}
                .action-buttons {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 5px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                }}
                .btn-primary {{
                    background: #D32F2F;
                    color: white;
                }}
                .btn-secondary {{
                    background: #6c757d;
                    color: white;
                }}
                .footer {{
                    background: #2D3748;
                    padding: 25px;
                    text-align: center;
                    color: #A0AEC0;
                    font-size: 13px;
                }}
                .footer-link {{
                    color: #D32F2F;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="header-icon">🔒</div>
                    <h1>Security Alert</h1>
                </div>

                <div class="content">
                    <p>Hello {username},</p>

                    <p>
                        We detected suspicious activity on your TED Brokers account. Someone tried to log in with
                        credentials that matched your account, but the login attempt was flagged for the following reasons:
                    </p>

                    <div class="alert-box">
                        <div class="alert-title">Risk Level: {risk_level.upper()}</div>
                        <ul class="alert-reasons">
                            {"".join(f"<li>{reason}</li>" for reason in reasons)}
                        </ul>
                    </div>

                    <h3>Login Attempt Details</h3>
                    <div class="info-section">
                        <div class="info-row">
                            <span class="info-label">Time:</span>
                            <span class="info-value">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">IP Address:</span>
                            <span class="info-value">{ip_address}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Location:</span>
                            <span class="info-value">{location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Device:</span>
                            <span class="info-value">{device_info.get('device', 'Unknown')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Browser:</span>
                            <span class="info-value">{device_info.get('browser', 'Unknown')}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Operating System:</span>
                            <span class="info-value">{device_info.get('os', 'Unknown')}</span>
                        </div>
                    </div>

                    <h3>What should you do?</h3>
                    <p>
                        <strong>If this was you:</strong><br>
                        No action is required. The login attempt was automatically flagged due to security parameters,
                        but you can proceed with verification.
                    </p>

                    <p>
                        <strong>If this wasn't you:</strong><br>
                        Please secure your account immediately:
                    </p>

                    <div class="action-buttons">
                        <a href="https://tedbrokers.com/change-password" class="btn btn-primary">
                            Change Password
                        </a>
                        <a href="https://tedbrokers.com/security" class="btn btn-secondary">
                            View Security Settings
                        </a>
                    </div>

                    <p style="color: #6c757d; font-size: 14px; margin-top: 30px;">
                        For your security, we recommend:
                        <ul style="color: #6c757d; font-size: 14px;">
                            <li>Using a strong, unique password</li>
                            <li>Enabling 2-factor authentication (already enabled)</li>
                            <li>Not sharing your login credentials</li>
                            <li>Being cautious of phishing attempts</li>
                        </ul>
                    </p>
                </div>

                <div class="footer">
                    <p>© 2025 TED Brokers. All rights reserved.</p>
                    <p>
                        Need help? Contact us at
                        <a href="mailto:security@tedbrokers.com" class="footer-link">security@tedbrokers.com</a>
                    </p>
                    <p style="margin-top: 15px; font-size: 12px;">
                        This is an automated security alert. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Security Alert - Suspicious Login Attempt

        Hello {username},

        We detected suspicious activity on your TED Brokers account.

        Risk Level: {risk_level.upper()}

        Reasons:
        {chr(10).join(f"- {reason}" for reason in reasons)}

        Login Attempt Details:
        - Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        - IP Address: {ip_address}
        - Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}
        - Device: {device_info.get('device', 'Unknown')}
        - Browser: {device_info.get('browser', 'Unknown')}
        - OS: {device_info.get('os', 'Unknown')}

        If this wasn't you, please:
        1. Change your password immediately
        2. Review your security settings
        3. Contact support if needed

        TED Brokers Security Team
        security@tedbrokers.com
        """

        return email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            plain_content=plain_content
        )

    @staticmethod
    def send_successful_login_notification(
        email: str,
        username: str,
        ip_address: str,
        device_info: Dict,
        location: Dict
    ) -> bool:
        """
        Send notification for successful login from new location/device

        Args:
            email: User's email address
            username: User's username or full name
            ip_address: IP address
            device_info: Device information
            location: Location information

        Returns:
            bool: True if email sent successfully
        """
        subject = "New Login to Your TED Brokers Account"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #D32F2F 0%, #B71C1C 100%);
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    color: white;
                    font-size: 24px;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .info-box {{
                    background: #f8f9fa;
                    border-radius: 6px;
                    padding: 20px;
                    margin: 25px 0;
                }}
                .footer {{
                    background: #2D3748;
                    padding: 25px;
                    text-align: center;
                    color: #A0AEC0;
                    font-size: 13px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✓ Successful Login</h1>
                </div>

                <div class="content">
                    <p>Hello {username},</p>

                    <p>Your TED Brokers account was successfully accessed.</p>

                    <div class="info-box">
                        <strong>Login Details:</strong><br>
                        Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}<br>
                        IP: {ip_address}<br>
                        Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}<br>
                        Device: {device_info.get('device', 'Unknown')}<br>
                        Browser: {device_info.get('browser', 'Unknown')}
                    </div>

                    <p>
                        If this wasn't you, please secure your account immediately by changing your password.
                    </p>
                </div>

                <div class="footer">
                    <p>© 2025 TED Brokers. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Successful Login to Your TED Brokers Account

        Hello {username},

        Your account was successfully accessed.

        Login Details:
        - Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}
        - IP Address: {ip_address}
        - Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}
        - Device: {device_info.get('device', 'Unknown')}
        - Browser: {device_info.get('browser', 'Unknown')}

        If this wasn't you, please secure your account immediately.

        TED Brokers Team
        """

        return email_service.send_email(
            to_email=email,
            subject=subject,
            html_content=html_content,
            plain_content=plain_content
        )


# Create singleton instance
security_alerts_service = SecurityAlertsService()
