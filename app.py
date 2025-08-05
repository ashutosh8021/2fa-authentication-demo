from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime, timedelta

# Try to import email configuration
try:
    from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD
    EMAIL_CONFIGURED = True
except ImportError:
    # Default values if config.py doesn't exist
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    SENDER_EMAIL = "your-email@gmail.com"
    SENDER_PASSWORD = "your-app-password"
    EMAIL_CONFIGURED = False

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
    
    conn.commit()
    conn.close()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp_code):
    """
    Send OTP via email using SMTP.
    Falls back to console simulation if email sending fails.
    """
    
    # Check if email is properly configured
    if not EMAIL_CONFIGURED or SENDER_EMAIL == "your-email@gmail.com":
        print(f"\n⚠️  EMAIL NOT CONFIGURED")
        print(f"📧 To enable real email sending:")
        print(f"   1. Copy config_template.py to config.py")
        print(f"   2. Update config.py with your email settings")
        print(f"   3. For Gmail: Enable 2FA and generate App Password")
        
        # Fallback to console simulation
        print(f"\n=== EMAIL SIMULATION ===")
        print(f"To: {email}")
        print(f"Subject: Your 2FA Code")
        print(f"Body: Your verification code is: {otp_code}")
        print(f"This code expires in 5 minutes.")
        print(f"========================\n")
        return False
    
    # Try to send real email
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = "🔐 Your 2FA Verification Code"
        
        # Create HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">🔐 2FA Verification</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Your Verification Code</h2>
                <div style="background: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                    <h1 style="font-size: 2.5em; color: #667eea; letter-spacing: 5px; margin: 0;">{otp_code}</h1>
                </div>
                <p style="color: #666; font-size: 16px;">
                    Enter this 6-digit code to complete your login. This code will expire in <strong>5 minutes</strong>.
                </p>
                <p style="color: #999; font-size: 14px;">
                    If you didn't request this code, please ignore this email.
                </p>
            </div>
            <div style="background: #333; padding: 15px; text-align: center;">
                <p style="color: #999; margin: 0; font-size: 12px;">2FA Demo Application</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Connect and send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, email, text)
        server.quit()
        
        print(f"\n✅ EMAIL SENT SUCCESSFULLY to {email}")
        print(f"📧 OTP Code: {otp_code}")
        print(f"⏰ Expires in 5 minutes\n")
        return True
        
    except Exception as e:
        print(f"\n❌ EMAIL SENDING FAILED: {e}")
        print(f"📧 Falling back to console simulation...")
        
        # Fallback to console simulation
        print(f"\n=== EMAIL SIMULATION ===")
        print(f"To: {email}")
        print(f"Subject: Your 2FA Code")
        print(f"Body: Your verification code is: {otp_code}")
        print(f"This code expires in 5 minutes.")
        print(f"========================\n")
        return False

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash, email FROM users WHERE username = ?', (username,))
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
        username = request.form['username']
        password = request.form['password']
        
        user = verify_user(username, password)
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
            flash('Invalid username or password!')
    
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
