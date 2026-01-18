# Email Configuration Guide

The password reset feature can send emails. Here's how to set it up:

## Option 1: Gmail (Recommended for Testing)

### Step 1: Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Enable 2-Factor Authentication

### Step 2: Create App-Specific Password
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Windows Computer" (or your device)
3. Google will generate a 16-character password
4. Copy this password

### Step 3: Update Email Configuration
Open `epet-backend/app/email.py` and update:

```python
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # For SSL
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-app-specific-password"  # 16-char password from step 2
```

### Step 4: Enable SMTP Email Sending
Uncomment this line in the `forgot_password()` function in `app/routes/users.py`:

```python
# Change from:
# await send_password_reset_email(request.email, reset_token="sample-token")

# To:
await send_smtp_email(to_email=request.email, subject="PawStore - Password Reset", html_body=html_body)
```

## Option 2: Using Environment Variables (Recommended for Production)

Create a `.env` file in `epet-backend/`:

```
EMAIL_PROVIDER=gmail
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password
EMAIL_FROM_NAME=PawStore
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
```

Then update `app/email.py` to read from environment variables.

## Testing Without Email

Currently, the system logs password reset links to the console/logs. 
- Check the server logs when user clicks "Forgot Password"
- You'll see a message like: "Reset link: http://localhost:5173/reset-password?email=..."
- Copy this link to test the reset functionality

## Email Providers

### Gmail
- SMTP: smtp.gmail.com
- Port: 465 (SSL) or 587 (TLS)
- Requires app-specific password

### Outlook
- SMTP: smtp-mail.outlook.com
- Port: 587 (TLS)
- Password: Your Outlook password

### SendGrid (Best for Production)
- Install: `pip install sendgrid`
- Get API key from sendgrid.com
- Update email module to use SendGrid API

### AWS SES
- Install: `pip install boto3`
- Configure AWS credentials
- More robust and scalable

## Next Steps

1. Test with console logs first (current setup)
2. When ready, uncomment `send_smtp_email()` line
3. Update with your email credentials
4. Test the complete flow
