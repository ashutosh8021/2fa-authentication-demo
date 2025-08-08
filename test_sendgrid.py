#!/usr/bin/env python3
"""
SendGrid Email Test Script for 2FA Demo
Tests the email configuration and sends a test OTP email
"""

import sys
import os

# Add current directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_sendgrid_config():
    """Test if SendGrid is properly configured"""
    
    print("🧪 Testing SendGrid Configuration...\n")
    
    # Try to import configuration
    try:
        from config import SENDGRID_API_KEY, SENDER_EMAIL, SENDER_NAME
        print("✅ Config file imported successfully")
        
        # Check if values are configured
        if SENDGRID_API_KEY == "your-sendgrid-api-key-here":
            print("❌ SENDGRID_API_KEY not configured")
            print("   Please update config.py with your SendGrid API key")
            return False
        else:
            print(f"✅ API Key configured (starts with: {SENDGRID_API_KEY[:10]}...)")
        
        if SENDER_EMAIL == "your-verified-sender@yourdomain.com":
            print("❌ SENDER_EMAIL not configured")
            print("   Please update config.py with your verified sender email")
            return False
        else:
            print(f"✅ Sender email: {SENDER_EMAIL}")
        
        print(f"✅ Sender name: {SENDER_NAME}")
        return True
        
    except ImportError as e:
        print("❌ Config file not found or incomplete")
        print("   Please copy config_sendgrid.py to config.py and update it")
        print(f"   Error: {e}")
        return False

def test_sendgrid_connection():
    """Test SendGrid API connection"""
    
    print("\n🔌 Testing SendGrid API Connection...\n")
    
    try:
        from sendgrid import SendGridAPIClient
        from config import SENDGRID_API_KEY
        
        # Create SendGrid client
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        
        # Test API key with a simple API call
        response = sg.client.user.email.get()
        
        if response.status_code == 200:
            print("✅ SendGrid API connection successful")
            print(f"📊 Response status: {response.status_code}")
            return True
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ SendGrid API connection failed: {str(e)}")
        
        if "Unauthorized" in str(e):
            print("   → Check your API key is correct")
            print("   → Ensure API key has Mail Send permissions")
        elif "sendgrid" in str(e).lower():
            print("   → Install SendGrid: pip install sendgrid")
        
        return False

def send_test_email():
    """Send a test OTP email"""
    
    print("\n📧 Sending Test OTP Email...\n")
    
    # Get test email from user
    test_email = input("Enter your email to receive test OTP: ").strip()
    
    if not test_email or '@' not in test_email:
        print("❌ Invalid email address")
        return False
    
    try:
        # Import the send function from main app
        from app import send_otp_email
        
        # Generate test OTP
        test_otp = "123456"
        
        # Send test email
        success = send_otp_email(test_email, test_otp)
        
        if success:
            print("\n🎉 Test email sent successfully!")
            print("📧 Check your inbox (and spam folder)")
            print(f"🔐 Test OTP was: {test_otp}")
            return True
        else:
            print("\n❌ Test email failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Error sending test email: {str(e)}")
        return False

def main():
    """Run all tests"""
    
    print("=" * 60)
    print("🧪 2FA DEMO - SENDGRID EMAIL TEST")
    print("=" * 60)
    
    # Test 1: Configuration
    config_ok = test_sendgrid_config()
    
    if not config_ok:
        print("\n❌ Configuration test failed. Please fix configuration first.")
        print("\nSetup steps:")
        print("1. Copy config_sendgrid.py to config.py")
        print("2. Update config.py with your SendGrid API key")
        print("3. Update config.py with your verified sender email")
        print("4. Run this test again")
        return
    
    # Test 2: API Connection
    connection_ok = test_sendgrid_connection()
    
    if not connection_ok:
        print("\n❌ API connection test failed.")
        print("Please check your API key and try again.")
        return
    
    # Test 3: Send Test Email
    print("\n" + "=" * 60)
    print("🎯 Ready to send test email!")
    print("=" * 60)
    
    send_test = input("\nSend test OTP email? (y/n): ").strip().lower()
    
    if send_test == 'y':
        email_ok = send_test_email()
        
        if email_ok:
            print("\n🎉 ALL TESTS PASSED!")
            print("Your 2FA demo is ready for real email delivery!")
        else:
            print("\n❌ Email test failed.")
    else:
        print("\n✅ Configuration tests passed!")
        print("Run 'python app.py' to start your 2FA demo")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
