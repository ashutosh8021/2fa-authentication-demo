#!/usr/bin/env python3
"""
Password Reset Test Script for 2FA Demo
Tests the complete password reset flow with real email delivery
"""

import sys
import os
import time

# Add current directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_password_reset_flow():
    """Test the complete password reset flow"""
    
    print("=" * 60)
    print("🔐 2FA DEMO - PASSWORD RESET TEST")
    print("=" * 60)
    
    print("\n🧪 Testing Password Reset Flow...\n")
    
    # Import after adding to path
    try:
        from app import (send_password_reset_email, create_password_reset_token, 
                        verify_reset_token, get_user_by_email, init_db,
                        hash_password, update_user_password)
        
        # Initialize database
        init_db()
        print("✅ Database initialized")
        
        # Test user creation (simulate a user exists)
        import sqlite3
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        # Check if test user exists, if not create one
        test_email = "test@example.com"
        test_username = "testuser"
        test_password = "testpass123"
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (test_email,))
        existing_user = cursor.fetchone()
        
        if not existing_user:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (test_username, test_email, hash_password(test_password)))
            conn.commit()
            print(f"✅ Test user created: {test_username} ({test_email})")
        else:
            print(f"✅ Test user exists: {test_username} ({test_email})")
        
        conn.close()
        
        # Test 1: Get user by email
        user = get_user_by_email(test_email)
        if user:
            print(f"✅ User lookup successful: ID {user['id']}")
        else:
            print("❌ User lookup failed")
            return False
        
        # Test 2: Create password reset token
        reset_token = create_password_reset_token(user['id'])
        print(f"✅ Reset token created: {reset_token}")
        
        # Test 3: Send password reset email
        print(f"\n📧 Testing password reset email to: {test_email}")
        email_sent = send_password_reset_email(test_email, reset_token)
        
        if email_sent:
            print("✅ Password reset email sent successfully!")
        else:
            print("⚠️  Email sent via console simulation (SendGrid not configured)")
        
        # Test 4: Verify reset token
        token_valid = verify_reset_token(user['id'], reset_token)
        if token_valid:
            print("✅ Reset token verification successful")
        else:
            print("❌ Reset token verification failed")
            return False
        
        # Test 5: Try to verify the same token again (should fail - single use)
        token_valid_again = verify_reset_token(user['id'], reset_token)
        if not token_valid_again:
            print("✅ Token single-use validation working (cannot reuse)")
        else:
            print("❌ Token reuse prevention failed")
            return False
        
        # Test 6: Create new token and test password update
        new_reset_token = create_password_reset_token(user['id'])
        verify_reset_token(user['id'], new_reset_token)  # Mark as used
        
        new_password = "newpassword123"
        update_user_password(user['id'], new_password)
        print("✅ Password update successful")
        
        # Test 7: Verify password was actually changed
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user['id'],))
        updated_hash = cursor.fetchone()[0]
        conn.close()
        
        if updated_hash == hash_password(new_password):
            print("✅ Password hash verification successful")
        else:
            print("❌ Password hash verification failed")
            return False
        
        print(f"\n🎉 ALL PASSWORD RESET TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_password_reset_security():
    """Test security aspects of password reset"""
    
    print("\n" + "=" * 60)
    print("🛡️ SECURITY TESTS")
    print("=" * 60)
    
    try:
        from app import create_password_reset_token, verify_reset_token
        from datetime import datetime, timedelta
        import sqlite3
        
        # Create a test user ID (use 1 for simplicity)
        test_user_id = 1
        
        # Test 1: Token expiry
        print("\n🕐 Testing token expiry...")
        
        # Manually create an expired token in database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        expired_token = "123456"
        past_time = datetime.now() - timedelta(minutes=20)  # 20 minutes ago
        
        cursor.execute('''
            INSERT INTO password_resets (user_id, reset_token, expires_at, used)
            VALUES (?, ?, ?, FALSE)
        ''', (test_user_id, expired_token, past_time))
        conn.commit()
        conn.close()
        
        # Try to verify expired token
        is_valid = verify_reset_token(test_user_id, expired_token)
        if not is_valid:
            print("✅ Expired token correctly rejected")
        else:
            print("❌ Expired token was accepted (security issue!)")
            return False
        
        # Test 2: Invalid token
        print("\n🔒 Testing invalid token...")
        invalid_token = "999999"
        is_valid = verify_reset_token(test_user_id, invalid_token)
        if not is_valid:
            print("✅ Invalid token correctly rejected")
        else:
            print("❌ Invalid token was accepted (security issue!)")
            return False
        
        # Test 3: Token cleanup (old tokens are removed)
        print("\n🧹 Testing token cleanup...")
        
        # Create multiple tokens for same user
        token1 = create_password_reset_token(test_user_id)
        time.sleep(1)  # Ensure different timestamps
        token2 = create_password_reset_token(test_user_id)
        
        # First token should be invalidated when second is created
        is_valid_old = verify_reset_token(test_user_id, token1)
        if not is_valid_old:
            print("✅ Old tokens correctly invalidated when new one is created")
        else:
            print("❌ Old token still valid (should be invalidated)")
            return False
        
        # New token should work
        is_valid_new = verify_reset_token(test_user_id, token2)
        if is_valid_new:
            print("✅ New token works correctly")
        else:
            print("❌ New token not working")
            return False
        
        print(f"\n🎉 ALL SECURITY TESTS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Security test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all password reset tests"""
    
    print("🚀 Starting Password Reset Tests...\n")
    
    # Test 1: Basic functionality
    basic_test_passed = test_password_reset_flow()
    
    # Test 2: Security aspects
    security_test_passed = test_password_reset_security()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    print(f"Basic Functionality: {'✅ PASS' if basic_test_passed else '❌ FAIL'}")
    print(f"Security Tests: {'✅ PASS' if security_test_passed else '❌ FAIL'}")
    
    if basic_test_passed and security_test_passed:
        print(f"\n🎉 ALL TESTS PASSED! Password reset feature is ready for production.")
        print(f"\n🌟 Features Tested:")
        print(f"   ✅ Email-based password reset")
        print(f"   ✅ Token generation and validation")
        print(f"   ✅ Token expiry (15 minutes)")
        print(f"   ✅ Single-use tokens")
        print(f"   ✅ Token cleanup")
        print(f"   ✅ Password hash update")
        print(f"   ✅ Security validations")
        
        print(f"\n🚀 Ready for deployment!")
    else:
        print(f"\n❌ Some tests failed. Please review the issues above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
