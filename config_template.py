# Email Configuration for 2FA Demo
# Copy this file to config.py and update with your settings

# Gmail SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"  # Your Gmail address
SENDER_PASSWORD = "your-app-password"   # Your Gmail App Password (not regular password)

# Other SMTP providers:
# 
# Outlook/Hotmail:
# SMTP_SERVER = "smtp-mail.outlook.com"
# SMTP_PORT = 587
#
# Yahoo:
# SMTP_SERVER = "smtp.mail.yahoo.com" 
# SMTP_PORT = 587
#
# Custom SMTP:
# SMTP_SERVER = "your-smtp-server.com"
# SMTP_PORT = 587 (or 465 for SSL)

# Security Note: 
# For Gmail, you need to:
# 1. Enable 2-Factor Authentication on your Google account
# 2. Generate an "App Password" (not your regular Gmail password)
# 3. Use the App Password in SENDER_PASSWORD above
