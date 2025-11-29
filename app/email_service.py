"""
Email Service using SendGrid
Handles sending emails for 2FA verification codes
"""

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from typing import Optional


class EmailService:
    """Service for sending emails via SendGrid"""

    def __init__(self):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@tedbrokers.com")
        self.from_name = os.getenv("SENDGRID_FROM_NAME", "TED Brokers")

        if not self.api_key:
            print("WARNING: SENDGRID_API_KEY not configured. Email sending will be disabled.")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None
    ) -> bool:
        """
        Send an email via SendGrid

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            plain_content: Plain text content (optional)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.api_key:
            print(f"⚠️  SendGrid API key not configured!")
            print(f"Email would have been sent to {to_email}: {subject}")
            return False

        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", plain_content or ""),
                html_content=Content("text/html", html_content)
            )

            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)

            if response.status_code in [200, 201, 202]:
                print(f"✓ Email sent successfully to {to_email}")
                print(f"  Subject: {subject}")
                print(f"  Status: {response.status_code}")
                return True
            else:
                print(f"✗ Email sending failed to {to_email}")
                print(f"  Status: {response.status_code}")
                print(f"  Response: {response.body}")
                return False
        except Exception as e:
            print(f"✗ Error sending email to {to_email}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def send_2fa_code(self, to_email: str, code: str, username: str = "User") -> bool:
        """
        Send 2FA verification code email

        Args:
            to_email: Recipient email address
            code: 6-digit verification code
            username: User's name or username

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "Your TED Brokers Verification Code"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
                .logo {{
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #2D3748;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #4A5568;
                    margin-bottom: 30px;
                    font-size: 15px;
                }}
                .code-container {{
                    background: #f7fafc;
                    border: 2px solid #D32F2F;
                    border-radius: 8px;
                    padding: 25px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code-label {{
                    color: #718096;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 10px;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #D32F2F;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 4px;
                }}
                .warning-text {{
                    color: #856404;
                    font-size: 14px;
                    margin: 0;
                }}
                .expiry {{
                    text-align: center;
                    color: #718096;
                    font-size: 14px;
                    margin-top: 20px;
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
                    <h1 class="logo">TED Brokers</h1>
                </div>

                <div class="content">
                    <p class="greeting">Hello {username},</p>

                    <p class="message">
                        We received a request to sign in to your TED Brokers account. To complete your login,
                        please use the verification code below:
                    </p>

                    <div class="code-container">
                        <div class="code-label">Verification Code</div>
                        <div class="code">{code}</div>
                    </div>

                    <p class="expiry">
                        This code will expire in <strong>10 minutes</strong>.
                    </p>

                    <div class="warning">
                        <p class="warning-text">
                            <strong>Security Notice:</strong> If you didn't request this code, please ignore this email
                            and ensure your account is secure.
                        </p>
                    </div>

                    <p class="message">
                        For your security, never share this code with anyone. TED Brokers will never ask you
                        for your verification code.
                    </p>
                </div>

                <div class="footer">
                    <p>© 2025 TED Brokers. All rights reserved.</p>
                    <p>
                        Need help? Contact us at
                        <a href="mailto:support@tedbrokers.com" class="footer-link">support@tedbrokers.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Hello {username},

        We received a request to sign in to your TED Brokers account.

        Your verification code is: {code}

        This code will expire in 10 minutes.

        If you didn't request this code, please ignore this email and ensure your account is secure.

        For your security, never share this code with anyone.

        Best regards,
        TED Brokers Team
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_password_reset_code(self, to_email: str, code: str, username: str = "User") -> bool:
        """
        Send password reset verification code email

        Args:
            to_email: Recipient email address
            code: 6-digit verification code
            username: User's name or username

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        subject = "Password Reset - TED Brokers"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
                .logo {{
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #2D3748;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #4A5568;
                    margin-bottom: 30px;
                    font-size: 15px;
                }}
                .code-container {{
                    background: #f7fafc;
                    border: 2px solid #D32F2F;
                    border-radius: 8px;
                    padding: 25px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code-label {{
                    color: #718096;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 10px;
                }}
                .code {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #D32F2F;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 4px;
                }}
                .warning-text {{
                    color: #856404;
                    font-size: 14px;
                    margin: 0;
                }}
                .expiry {{
                    text-align: center;
                    color: #718096;
                    font-size: 14px;
                    margin-top: 20px;
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
                    <h1 class="logo">TED Brokers</h1>
                </div>

                <div class="content">
                    <p class="greeting">Hello {username},</p>

                    <p class="message">
                        We received a request to reset your password. To proceed with resetting your password,
                        please use the verification code below:
                    </p>

                    <div class="code-container">
                        <div class="code-label">Password Reset Code</div>
                        <div class="code">{code}</div>
                    </div>

                    <p class="expiry">
                        This code will expire in <strong>10 minutes</strong>.
                    </p>

                    <div class="warning">
                        <p class="warning-text">
                            <strong>Security Notice:</strong> If you didn't request a password reset, please ignore
                            this email and ensure your account is secure. Your password will not be changed unless
                            you complete the reset process.
                        </p>
                    </div>

                    <p class="message">
                        For your security, never share this code with anyone. TED Brokers will never ask you
                        for your verification code.
                    </p>
                </div>

                <div class="footer">
                    <p>© 2025 TED Brokers. All rights reserved.</p>
                    <p>
                        Need help? Contact us at
                        <a href="mailto:support@tedbrokers.com" class="footer-link">support@tedbrokers.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Hello {username},

        We received a request to reset your password for your TED Brokers account.

        Your password reset verification code is: {code}

        This code will expire in 10 minutes.

        If you didn't request a password reset, please ignore this email and ensure your account is secure.

        For your security, never share this code with anyone.

        Best regards,
        TED Brokers Team
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_login_notification(self, to_email: str, username: str, ip_address: str, device_info: str, location: str = "Unknown") -> bool:
        """
        Send login notification email

        Args:
            to_email: Recipient email address
            username: User's name or username
            ip_address: IP address of the login
            device_info: Device information
            location: Geographic location

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        from datetime import datetime

        login_time = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
        subject = "New Login to Your TED Brokers Account"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
                .logo {{
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #2D3748;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #4A5568;
                    margin-bottom: 20px;
                    font-size: 15px;
                }}
                .details-box {{
                    background: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    font-weight: 600;
                    color: #718096;
                }}
                .detail-value {{
                    color: #2D3748;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 4px;
                }}
                .warning-text {{
                    color: #856404;
                    font-size: 14px;
                    margin: 0;
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
                    <h1 class="logo">TED Brokers</h1>
                </div>

                <div class="content">
                    <p class="greeting">Hello {username},</p>

                    <p class="message">
                        We detected a new login to your TED Brokers account. Here are the details:
                    </p>

                    <div class="details-box">
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span class="detail-value">{login_time}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">IP Address:</span>
                            <span class="detail-value">{ip_address}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Device:</span>
                            <span class="detail-value">{device_info}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Location:</span>
                            <span class="detail-value">{location}</span>
                        </div>
                    </div>

                    <div class="warning">
                        <p class="warning-text">
                            <strong>Security Notice:</strong> If you did not perform this login, please secure
                            your account immediately by changing your password and enabling two-factor authentication.
                        </p>
                    </div>

                    <p class="message">
                        For your security, we recommend enabling two-factor authentication if you haven't already.
                    </p>
                </div>

                <div class="footer">
                    <p>&copy; 2025 TED Brokers. All rights reserved.</p>
                    <p>
                        Need help? Contact us at
                        <a href="mailto:support@tedbrokers.com" class="footer-link">support@tedbrokers.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Hello {username},

        We detected a new login to your TED Brokers account.

        Login Details:
        - Time: {login_time}
        - IP Address: {ip_address}
        - Device: {device_info}
        - Location: {location}

        If you did not perform this login, please secure your account immediately by changing your password.

        Best regards,
        TED Brokers Team
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_deposit_notification(self, to_email: str, username: str, amount: float, payment_method: str) -> bool:
        """
        Send deposit approval notification email

        Args:
            to_email: Recipient email address
            username: User's name or username
            amount: Deposit amount
            payment_method: Payment method used

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        from datetime import datetime

        approval_time = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
        subject = "Deposit Approved - TED Brokers"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
                .logo {{
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #2D3748;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #4A5568;
                    margin-bottom: 20px;
                    font-size: 15px;
                }}
                .success-box {{
                    background: #d4edda;
                    border: 2px solid #28a745;
                    border-radius: 8px;
                    padding: 25px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .success-icon {{
                    color: #28a745;
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .amount {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #28a745;
                    margin: 15px 0;
                }}
                .details-box {{
                    background: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    font-weight: 600;
                    color: #718096;
                }}
                .detail-value {{
                    color: #2D3748;
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
                    <h1 class="logo">TED Brokers</h1>
                </div>

                <div class="content">
                    <p class="greeting">Hello {username},</p>

                    <p class="message">
                        Great news! Your deposit has been successfully approved and credited to your account.
                    </p>

                    <div class="success-box">
                        <div class="success-icon">✓</div>
                        <div style="color: #28a745; font-size: 18px; font-weight: 600;">Deposit Approved</div>
                        <div class="amount">${amount:.2f}</div>
                    </div>

                    <div class="details-box">
                        <div class="detail-row">
                            <span class="detail-label">Amount:</span>
                            <span class="detail-value">${amount:.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Payment Method:</span>
                            <span class="detail-value">{payment_method}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Approved:</span>
                            <span class="detail-value">{approval_time}</span>
                        </div>
                    </div>

                    <p class="message">
                        Your funds are now available in your wallet and ready to use for trading.
                    </p>
                </div>

                <div class="footer">
                    <p>&copy; 2025 TED Brokers. All rights reserved.</p>
                    <p>
                        Need help? Contact us at
                        <a href="mailto:support@tedbrokers.com" class="footer-link">support@tedbrokers.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Hello {username},

        Great news! Your deposit has been successfully approved and credited to your account.

        Deposit Details:
        - Amount: ${amount:.2f}
        - Payment Method: {payment_method}
        - Approved: {approval_time}

        Your funds are now available in your wallet and ready to use for trading.

        Best regards,
        TED Brokers Team
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_withdrawal_notification(self, to_email: str, username: str, amount: float, withdrawal_method: str, account_details: dict) -> bool:
        """
        Send withdrawal approval notification email

        Args:
            to_email: Recipient email address
            username: User's name or username
            amount: Withdrawal amount
            withdrawal_method: Withdrawal method (bank or crypto)
            account_details: Account details dictionary

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        from datetime import datetime

        approval_time = datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
        subject = "Withdrawal Processed - TED Brokers"

        # Format account details based on withdrawal method
        account_info = ""
        if withdrawal_method == "bank":
            account_info = f"""
                        <div class="detail-row">
                            <span class="detail-label">Bank Name:</span>
                            <span class="detail-value">{account_details.get('bank_name', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Account Number:</span>
                            <span class="detail-value">***{account_details.get('account_number', '')[-4:]}</span>
                        </div>
            """
            account_plain = f"Bank: {account_details.get('bank_name', 'N/A')}, Account: ***{account_details.get('account_number', '')[-4:]}"
        else:
            wallet_address = account_details.get('wallet_address', '')
            masked_address = f"{wallet_address[:6]}...{wallet_address[-4:]}" if len(wallet_address) > 10 else wallet_address
            account_info = f"""
                        <div class="detail-row">
                            <span class="detail-label">Currency:</span>
                            <span class="detail-value">{account_details.get('currency', 'N/A')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Wallet Address:</span>
                            <span class="detail-value">{masked_address}</span>
                        </div>
            """
            account_plain = f"Currency: {account_details.get('currency', 'N/A')}, Wallet: {masked_address}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
                .logo {{
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    margin: 0;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #2D3748;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #4A5568;
                    margin-bottom: 20px;
                    font-size: 15px;
                }}
                .success-box {{
                    background: #cfe2ff;
                    border: 2px solid #0d6efd;
                    border-radius: 8px;
                    padding: 25px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .success-icon {{
                    color: #0d6efd;
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .amount {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #0d6efd;
                    margin: 15px 0;
                }}
                .details-box {{
                    background: #f7fafc;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                .detail-label {{
                    font-weight: 600;
                    color: #718096;
                }}
                .detail-value {{
                    color: #2D3748;
                }}
                .info-box {{
                    background: #d1ecf1;
                    border-left: 4px solid #17a2b8;
                    padding: 15px;
                    margin: 25px 0;
                    border-radius: 4px;
                }}
                .info-text {{
                    color: #0c5460;
                    font-size: 14px;
                    margin: 0;
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
                    <h1 class="logo">TED Brokers</h1>
                </div>

                <div class="content">
                    <p class="greeting">Hello {username},</p>

                    <p class="message">
                        Your withdrawal request has been approved and is being processed.
                    </p>

                    <div class="success-box">
                        <div class="success-icon">✓</div>
                        <div style="color: #0d6efd; font-size: 18px; font-weight: 600;">Withdrawal Approved</div>
                        <div class="amount">${amount:.2f}</div>
                    </div>

                    <div class="details-box">
                        <div class="detail-row">
                            <span class="detail-label">Amount:</span>
                            <span class="detail-value">${amount:.2f}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Method:</span>
                            <span class="detail-value">{withdrawal_method.title()}</span>
                        </div>
{account_info}
                        <div class="detail-row">
                            <span class="detail-label">Processed:</span>
                            <span class="detail-value">{approval_time}</span>
                        </div>
                    </div>

                    <div class="info-box">
                        <p class="info-text">
                            <strong>Processing Time:</strong> Your funds will be transferred within 2-5 business days
                            depending on your financial institution.
                        </p>
                    </div>

                    <p class="message">
                        You will receive a confirmation once the transfer is complete. If you have any questions,
                        please don't hesitate to contact our support team.
                    </p>
                </div>

                <div class="footer">
                    <p>&copy; 2025 TED Brokers. All rights reserved.</p>
                    <p>
                        Need help? Contact us at
                        <a href="mailto:support@tedbrokers.com" class="footer-link">support@tedbrokers.com</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Hello {username},

        Your withdrawal request has been approved and is being processed.

        Withdrawal Details:
        - Amount: ${amount:.2f}
        - Method: {withdrawal_method.title()}
        - {account_plain}
        - Processed: {approval_time}

        Your funds will be transferred within 2-5 business days depending on your financial institution.

        Best regards,
        TED Brokers Team
        """

        return self.send_email(to_email, subject, html_content, plain_content)


# Create a singleton instance
email_service = EmailService()
