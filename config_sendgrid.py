# SendGrid Email Configuration for 2FA Demo
# Copy this file to config.py and update with your SendGrid settings

# SendGrid Configuration
SENDGRID_API_KEY = "your-sendgrid-api-key-here"  # Your SendGrid API key
SENDER_EMAIL = "your-verified-sender@yourdomain.com"  # Must be verified in SendGrid
SENDER_NAME = "2FA Demo App"  # Display name for sender

# Email Templates
EMAIL_TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2FA Verification Code</title>
</head>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f4f4f4;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 28px;">🔐 2FA Verification</h1>
        <p style="color: #e8e8e8; margin: 10px 0 0 0;">Secure Authentication Code</p>
    </div>
    
    <div style="background: white; padding: 40px; margin: 0;">
        <h2 style="color: #333; text-align: center; margin: 0 0 20px 0;">Your Verification Code</h2>
        
        <div style="background: #f8f9ff; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; border: 2px solid #667eea;">
            <h1 style="font-size: 3em; color: #667eea; letter-spacing: 8px; margin: 0; font-weight: bold;">{otp_code}</h1>
        </div>
        
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
            <p style="color: #856404; margin: 0; text-align: center;">
                ⏰ This code will expire in <strong>5 minutes</strong>
            </p>
        </div>
        
        <p style="color: #666; font-size: 16px; line-height: 1.6; text-align: center;">
            Enter this 6-digit code in your browser to complete your login.
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <p style="color: #999; font-size: 14px; margin: 0;">
                If you didn't request this code, please ignore this email.
            </p>
        </div>
    </div>
    
    <div style="background: #333; padding: 20px; text-align: center;">
        <p style="color: #999; margin: 0; font-size: 12px;">
            🛡️ 2FA Demo Application - Secure Authentication System
        </p>
        <p style="color: #666; margin: 5px 0 0 0; font-size: 11px;">
            This is an automated message, please do not reply.
        </p>
    </div>
</body>
</html>
"""

EMAIL_TEMPLATE_TEXT = """
🔐 2FA VERIFICATION CODE

Your verification code is: {otp_code}

This code will expire in 5 minutes.

Enter this code in your browser to complete your login.

If you didn't request this code, please ignore this email.

---
2FA Demo Application
Secure Authentication System
"""

# Security Notes for SendGrid:
# 1. Get your API key from https://app.sendgrid.com/settings/api_keys
# 2. Verify your sender email in SendGrid dashboard
# 3. For production, use domain authentication
# 4. Store API key as environment variable for security

# Environment Variable Option:
# You can also set SENDGRID_API_KEY as an environment variable:
# export SENDGRID_API_KEY="your-api-key"
# Then use: import os; SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
