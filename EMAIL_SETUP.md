# How to Enable Real Email Sending in 2FA Demo

## Current Status
Your 2FA demo is currently using **console simulation** - OTP codes are printed to the terminal instead of being sent via email.

## To Enable Real Email Sending:

### Option 1: Gmail Setup (Recommended)

1. **Copy the configuration template:**
   ```bash
   copy config_template.py config.py
   ```

2. **Enable 2-Factor Authentication on your Google Account:**
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

3. **Generate an App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Generate a 16-character app password
   - **Important**: Use this App Password, NOT your regular Gmail password

4. **Update config.py with your settings:**
   ```python
   SMTP_SERVER = "smtp.gmail.com"
   SMTP_PORT = 587
   SENDER_EMAIL = "youremail@gmail.com"        # Your Gmail address
   SENDER_PASSWORD = "abcd efgh ijkl mnop"     # Your 16-character App Password
   ```

### Option 2: Other Email Providers

**Outlook/Hotmail:**
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
SENDER_EMAIL = "youremail@outlook.com"
SENDER_PASSWORD = "your-password"
```

**Yahoo Mail:**
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
SENDER_EMAIL = "youremail@yahoo.com"
SENDER_PASSWORD = "your-app-password"  # Yahoo also requires App Passwords
```

### Option 3: For Testing Only - Check Console

If you don't want to set up real email sending right now, you can:

1. **Find the OTP in the terminal/console output** where you started the Flask app
2. Look for messages like:
   ```
   === EMAIL SIMULATION ===
   To: user@example.com
   Subject: Your 2FA Code
   Body: Your verification code is: 123456
   ========================
   ```

## Security Notes

- ✅ **Never commit config.py to version control** (it contains sensitive credentials)
- ✅ **Use App Passwords, not regular passwords** for Gmail/Yahoo
- ✅ **The config.py file is already in .gitignore**
- ⚠️ **For production use environment variables** instead of config files

## Testing Your Setup

1. Save your config.py file
2. Restart the Flask application
3. Try logging in - you should see "✅ EMAIL SENT SUCCESSFULLY" in the console
4. Check your email inbox for the OTP code

## Troubleshooting

**Common Issues:**
- **"Authentication failed"**: Using regular password instead of App Password
- **"Less secure app access"**: Enable 2FA and use App Passwords instead
- **"Connection refused"**: Check SMTP server and port settings
- **"Timeout"**: Check your firewall/antivirus settings

**Still having issues?**
The app will automatically fall back to console simulation and show the OTP in the terminal.
