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


# Create a singleton instance
email_service = EmailService()
