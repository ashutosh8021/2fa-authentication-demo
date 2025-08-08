from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import random
import string
import os
from datetime import datetime, timedelta

# SendGrid imports
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Try to import SendGrid configuration
try:
    from config import SENDGRID_API_KEY, SENDER_EMAIL, SENDER_NAME, EMAIL_TEMPLATE_HTML, EMAIL_TEMPLATE_TEXT
    EMAIL_CONFIGURED = True
    print("✅ SendGrid configuration loaded successfully")
except ImportError:
    # Default values if config.py doesn't exist
    SENDGRID_API_KEY = "your-sendgrid-api-key-here"
    SENDER_EMAIL = "your-verified-sender@yourdomain.com"
    SENDER_NAME = "2FA Demo App"
    EMAIL_TEMPLATE_HTML = None
    EMAIL_TEMPLATE_TEXT = None
    EMAIL_CONFIGURED = False
    print("⚠️  SendGrid configuration not found. Copy config_sendgrid.py to config.py and update it.")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create OTP table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create password reset tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reset_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp_code):
    """
    Send OTP via email using SendGrid API.
    Falls back to console simulation if SendGrid is not configured.
    """
    
    # Check if SendGrid is properly configured
    if not EMAIL_CONFIGURED or SENDGRID_API_KEY == "your-sendgrid-api-key-here":
        print(f"\n⚠️  SENDGRID NOT CONFIGURED")
        print(f"📧 To enable real email sending:")
        print(f"   1. Copy config_sendgrid.py to config.py")
        print(f"   2. Update config.py with your SendGrid API key")
        print(f"   3. Verify your sender email in SendGrid dashboard")
        print(f"   4. Get your API key from: https://app.sendgrid.com/settings/api_keys")
        
        # Fallback to console simulation
        print(f"\n=== EMAIL SIMULATION (SendGrid not configured) ===")
        print(f"To: {email}")
        print(f"Subject: 🔐 Your 2FA Verification Code")
        print(f"Body: Your verification code is: {otp_code}")
        print(f"This code expires in 5 minutes.")
        print(f"====================================================\n")
        return False
    
    # Try to send real email via SendGrid
    try:
        # Create the email message
        message = Mail(
            from_email=(SENDER_EMAIL, SENDER_NAME),
            to_emails=email,
            subject="🔐 Your 2FA Verification Code",
            html_content=EMAIL_TEMPLATE_HTML.format(otp_code=otp_code),
            plain_text_content=EMAIL_TEMPLATE_TEXT.format(otp_code=otp_code)
        )
        
        # Send email via SendGrid
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Check if email was sent successfully
        if response.status_code in [200, 201, 202]:
            print(f"\n✅ EMAIL SENT SUCCESSFULLY via SendGrid")
            print(f"📧 To: {email}")
            print(f"🔐 OTP Code: {otp_code}")
            print(f"⏰ Expires in 5 minutes")
            print(f"📊 SendGrid Status: {response.status_code}\n")
            return True
        else:
            print(f"\n⚠️  SendGrid returned status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"\n❌ SENDGRID EMAIL FAILED: {str(e)}")
        print(f"📧 Falling back to console simulation...")
        
        # Fallback to console simulation
        print(f"\n=== EMAIL SIMULATION (SendGrid failed) ===")
        print(f"To: {email}")
        print(f"Subject: 🔐 Your 2FA Verification Code") 
        print(f"Body: Your verification code is: {otp_code}")
        print(f"This code expires in 5 minutes.")
        print(f"Error: {str(e)}")
        print(f"==========================================\n")
        return False

def verify_user(username_or_email, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check if the input is username or email
    cursor.execute('SELECT id, password_hash, email FROM users WHERE username = ? OR email = ?', 
                   (username_or_email, username_or_email))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[1] == hash_password(password):
        return {'id': user[0], 'email': user[2]}
    return None

def create_otp(user_id):
    otp_code = generate_otp()
    expires_at = datetime.now() + timedelta(minutes=5)
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Remove any existing unused OTPs for this user
    cursor.execute('DELETE FROM otps WHERE user_id = ? AND used = FALSE', (user_id,))
    
    # Create new OTP
    cursor.execute('''
        INSERT INTO otps (user_id, otp_code, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, otp_code, expires_at))
    
    conn.commit()
    conn.close()
    
    return otp_code

def verify_otp_code(user_id, otp_code):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id FROM otps 
        WHERE user_id = ? AND otp_code = ? AND used = FALSE AND expires_at > ?
    ''', (user_id, otp_code, datetime.now()))
    
    otp_record = cursor.fetchone()
    
    if otp_record:
        # Mark OTP as used
        cursor.execute('UPDATE otps SET used = TRUE WHERE id = ?', (otp_record[0],))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def send_password_reset_email(email, reset_token):
    """
    Send password reset token via email using SendGrid API.
    """
    
    # Check if SendGrid is properly configured
    if not EMAIL_CONFIGURED or SENDGRID_API_KEY == "your-sendgrid-api-key-here":
        print(f"\n⚠️  SENDGRID NOT CONFIGURED")
        print(f"📧 Password reset email simulation...")
        
        # Fallback to console simulation
        print(f"\n=== PASSWORD RESET EMAIL SIMULATION ===")
        print(f"To: {email}")
        print(f"Subject: 🔐 Password Reset Code")
        print(f"Body: Your password reset code is: {reset_token}")
        print(f"This code expires in 15 minutes.")
        print(f"======================================\n")
        return False
    
    # Try to send real email via SendGrid
    try:
        # Create HTML email template for password reset
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset Code</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f4f4f4;">
            <div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">🔐 Password Reset</h1>
                <p style="color: #ffebee; margin: 10px 0 0 0;">Reset Your Account Password</p>
            </div>
            
            <div style="background: white; padding: 40px; margin: 0;">
                <h2 style="color: #333; text-align: center; margin: 0 0 20px 0;">Your Reset Code</h2>
                
                <div style="background: #ffebee; padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0; border: 2px solid #e74c3c;">
                    <h1 style="font-size: 3em; color: #e74c3c; letter-spacing: 8px; margin: 0; font-weight: bold;">{reset_token}</h1>
                </div>
                
                <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="color: #856404; margin: 0; text-align: center;">
                        ⏰ This code will expire in <strong>15 minutes</strong>
                    </p>
                </div>
                
                <p style="color: #666; font-size: 16px; line-height: 1.6; text-align: center;">
                    Enter this 6-digit code on the password reset page to create a new password.
                </p>
                
                <div style="background: #ffebee; border-radius: 5px; padding: 15px; margin: 20px 0;">
                    <p style="color: #c0392b; margin: 0; text-align: center; font-size: 14px;">
                        <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email.
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
        
        text_content = f"""
🔐 PASSWORD RESET CODE

Your password reset code is: {reset_token}

This code will expire in 15 minutes.

Enter this code on the password reset page to create a new password.

⚠️ Security Notice: If you didn't request this password reset, please ignore this email.

---
2FA Demo Application
Secure Authentication System
        """
        
        # Create the email message
        message = Mail(
            from_email=(SENDER_EMAIL, SENDER_NAME),
            to_emails=email,
            subject="🔐 Password Reset Code",
            html_content=html_content,
            plain_text_content=text_content
        )
        
        # Send email via SendGrid
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)
        
        # Check if email was sent successfully
        if response.status_code in [200, 201, 202]:
            print(f"\n✅ PASSWORD RESET EMAIL SENT via SendGrid")
            print(f"📧 To: {email}")
            print(f"🔐 Reset Code: {reset_token}")
            print(f"⏰ Expires in 15 minutes")
            print(f"📊 SendGrid Status: {response.status_code}\n")
            return True
        else:
            print(f"\n⚠️  SendGrid returned status {response.status_code}")
            return False
        
    except Exception as e:
        print(f"\n❌ SENDGRID PASSWORD RESET EMAIL FAILED: {str(e)}")
        print(f"📧 Falling back to console simulation...")
        
        # Fallback to console simulation
        print(f"\n=== PASSWORD RESET EMAIL SIMULATION ===")
        print(f"To: {email}")
        print(f"Subject: 🔐 Password Reset Code") 
        print(f"Body: Your password reset code is: {reset_token}")
        print(f"This code expires in 15 minutes.")
        print(f"Error: {str(e)}")
        print(f"=====================================\n")
        return False

def create_password_reset_token(user_id):
    reset_token = generate_otp()  # Same 6-digit format
    expires_at = datetime.now() + timedelta(minutes=15)  # 15 minutes for password reset
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Remove any existing unused reset tokens for this user
    cursor.execute('DELETE FROM password_resets WHERE user_id = ? AND used = FALSE', (user_id,))
    
    # Create new reset token
    cursor.execute('''
        INSERT INTO password_resets (user_id, reset_token, expires_at)
        VALUES (?, ?, ?)
    ''', (user_id, reset_token, expires_at))
    
    conn.commit()
    conn.close()
    
    return reset_token

def verify_reset_token(user_id, reset_token):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id FROM password_resets 
        WHERE user_id = ? AND reset_token = ? AND used = FALSE AND expires_at > ?
    ''', (user_id, reset_token, datetime.now()))
    
    token_record = cursor.fetchone()
    
    if token_record:
        # Mark token as used
        cursor.execute('UPDATE password_resets SET used = TRUE WHERE id = ?', (token_record[0],))
        conn.commit()
        conn.close()
        return True
    
    conn.close()
    return False

def update_user_password(user_id, new_password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    password_hash = hash_password(new_password)
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, email FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {'id': user[0], 'username': user[1], 'email': user[2]}
    return None

# Routes
@app.route('/')
def home():
    if 'user_id' in session and session.get('authenticated'):
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if not username or not email or not password:
            flash('All fields are required!')
            return render_template('register.html')
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, hash_password(password)))
            conn.commit()
            flash('Registration successful! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']  # Form field still named 'username' but accepts both
        password = request.form['password']
        
        user = verify_user(username_or_email, password)
        if user:
            # Store user info in session but don't mark as fully authenticated yet
            session['user_id'] = user['id']
            session['user_email'] = user['email']
            session['authenticated'] = False
            
            # Generate and send OTP
            otp_code = create_otp(user['id'])
            send_otp_email(user['email'], otp_code)
            
            flash('Please check your email for the verification code.')
            return redirect(url_for('verify_otp'))
        else:
            flash('Invalid username/email or password!')
    
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        otp_code = request.form['otp_code']
        
        if verify_otp_code(session['user_id'], otp_code):
            session['authenticated'] = True
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid or expired verification code!')
    
    return render_template('verify_otp.html')

@app.route('/resend-otp')
def resend_otp():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    otp_code = create_otp(session['user_id'])
    send_otp_email(session['user_email'], otp_code)
    flash('New verification code sent to your email.')
    return redirect(url_for('verify_otp'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or not session.get('authenticated'):
        flash('Please login first.')
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, email FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    return render_template('dashboard.html', username=user[0], email=user[1])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('home'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        user = get_user_by_email(email)
        
        if user:
            # Create reset token and send email
            reset_token = create_password_reset_token(user['id'])
            send_password_reset_email(email, reset_token)
            
            # Store user info in session for reset process
            session['reset_user_id'] = user['id']
            session['reset_email'] = email
            
            flash('Password reset code sent to your email!')
            return redirect(url_for('verify_reset'))
        else:
            flash('No account found with this email address.')
    
    return render_template('forgot_password.html')

@app.route('/verify-reset', methods=['GET', 'POST'])
def verify_reset():
    if 'reset_user_id' not in session:
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        reset_token = request.form['reset_token']
        
        if verify_reset_token(session['reset_user_id'], reset_token):
            # Token is valid, proceed to password reset
            session['reset_token_verified'] = True
            return redirect(url_for('reset_password'))
        else:
            flash('Invalid or expired reset code!')
    
    return render_template('verify_reset.html', email=session.get('reset_email'))

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if 'reset_user_id' not in session or not session.get('reset_token_verified'):
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match!')
        elif len(new_password) < 6:
            flash('Password must be at least 6 characters long!')
        else:
            # Update password
            update_user_password(session['reset_user_id'], new_password)
            
            # Clear reset session data
            session.pop('reset_user_id', None)
            session.pop('reset_email', None)
            session.pop('reset_token_verified', None)
            
            flash('Password reset successful! You can now login with your new password.')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/resend-reset')
def resend_reset():
    if 'reset_user_id' not in session:
        return redirect(url_for('forgot_password'))
    
    reset_token = create_password_reset_token(session['reset_user_id'])
    send_password_reset_email(session['reset_email'], reset_token)
    flash('New password reset code sent to your email.')
    return redirect(url_for('verify_reset'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
