import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import secrets
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Gmail SMTP configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Gmail credentials
SENDER_EMAIL = "pawstore0.help@gmail.com"
SENDER_PASSWORD = "nqjugmajtvujckzk"
SENDER_NAME = "PawStore"

# DEBUG: Print credentials on startup
import sys
print(f"[EMAIL DEBUG] Sender Email: {SENDER_EMAIL}", file=sys.stderr)
print(f"[EMAIL DEBUG] SMTP Server: {SMTP_SERVER}:{SMTP_PORT}", file=sys.stderr)

# Store reset tokens temporarily (in production, use database)
reset_tokens = {}


def generate_reset_token():
    """Generate a secure reset token"""
    return secrets.token_urlsafe(32)


def create_reset_token(email: str):
    """Create and store reset token for email"""
    token = generate_reset_token()
    # Store token with 24-hour expiration
    reset_tokens[email] = {
        "token": token,
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    return token


def verify_reset_token(email: str, token: str) -> bool:
    """Verify if reset token is valid"""
    if email not in reset_tokens:
        return False
    
    token_data = reset_tokens[email]
    if token_data["token"] != token:
        return False
    
    if datetime.utcnow() > token_data["expires_at"]:
        del reset_tokens[email]
        return False
    
    return True


async def send_password_reset_email(to_email: str) -> bool:
    """
    Send password reset email to user with reset link
    """
    try:
        # Generate reset token
        reset_token = create_reset_token(to_email)
        
        # Create reset link
        reset_link = f"http://localhost:8080/reset-password?email={to_email}&token={reset_token}"
        
        subject = "PawStore - Password Reset Request"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <h2 style="color: #FF8C42; margin-bottom: 20px;">🐾 Password Reset Request</h2>
                    
                    <p style="color: #333; font-size: 14px; margin-bottom: 15px;">
                        Hello,
                    </p>
                    
                    <p style="color: #333; font-size: 14px; margin-bottom: 20px;">
                        We received a request to reset your password for your PawStore account. 
                        If you didn't make this request, please ignore this email.
                    </p>
                    
                    <p style="color: #333; font-size: 14px; margin-bottom: 20px;">
                        To reset your password, click the button below:
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #FF8C42; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 12px; margin: 30px 0; padding: 15px; background-color: #f9f9f9; border-left: 4px solid #FF8C42;">
                        <strong>Link expires in:</strong> 24 hours<br>
                        Token: {reset_token[:10]}...
                    </p>
                    
                    <p style="color: #999; font-size: 12px;">
                        If the button doesn't work, copy and paste this link in your browser:<br>
                        <small style="word-break: break-all;">{reset_link}</small>
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 11px; margin: 0;">
                        This is an automated email from PawStore. Please do not reply to this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # Send email
        success = await send_smtp_email(to_email, subject, html_body)
        
        if success:
            logger.info(f"Password reset email sent to {to_email}")
            logger.info(f"Reset link: {reset_link}")
        else:
            logger.error(f"Failed to send password reset email to {to_email}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error in send_password_reset_email: {str(e)}")
        return False


async def send_smtp_email(to_email: str, subject: str, html_body: str) -> bool:
    """
    Send email via Gmail SMTP
    
    Setup Instructions:
    1. Enable 2FA on your Google account: https://myaccount.google.com/security
    2. Generate app password: https://myaccount.google.com/apppasswords
    3. Update SENDER_EMAIL and SENDER_PASSWORD in this file
    """
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
        message["To"] = to_email
        
        # Attach HTML content
        part = MIMEText(html_body, "html")
        message.attach(part)
        
        # Send email via Gmail SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Secure connection
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())
        
        logger.info(f"✓ Email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed. Check email credentials: {str(e)}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"❌ SMTP error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        return False

