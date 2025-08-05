# 2FA Demo Web Application

A complete demonstration of Two-Factor Authentication (2FA) using Flask, featuring username/password login plus email OTP verification.

![2FA Demo](https://img.shields.io/badge/Demo-2FA%20Authentication-success)
![Flask](https://img.shields.io/badge/Flask-2.3.3-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

## 🎯 Project Overview

This project demonstrates a practical implementation of Two-Factor Authentication (2FA) to address the security vulnerability of password-only authentication systems. The application adds an extra layer of security by requiring both password verification and email-based OTP confirmation.

## ✨ Features

- 🔐 **Username/Password Authentication** (First Factor)
- 📧 **Email OTP Verification** (Second Factor)
- ⏰ **Time-limited OTP Codes** (5-minute expiry)
- 🔒 **Single-use OTP Codes**
- 💾 **SQLite Database** for user storage
- 🎨 **Modern Web Interface**
- 🛡️ **Secure Session Management**
- ✉️ **Real SMTP Email Integration** (with console fallback)

## 🔄 How It Works

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Registration  │    │   Login Step 1  │    │   Login Step 2  │
│                 │    │                 │    │                 │
│ Username + Email│───▶│Username+Password│───▶│   OTP Verify    │
│   + Password    │    │   Validation    │    │   Email Code    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐             │
│   Dashboard     │◄───│  Session Start  │◄────────────┘
│   Protected     │    │   2FA Complete  │
│    Content      │    │                 │
└─────────────────┘    └─────────────────┘
```

### Authentication Flow:
1. **Registration**: Users create an account with username, email, and password
2. **Login Step 1**: User enters username and password → System validates credentials
3. **OTP Generation**: System generates a 6-digit OTP and sends it to user's email
4. **Login Step 2**: User enters the OTP code within 5 minutes
5. **Access Granted**: User gains access to the protected dashboard with active session

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd 2fa_demo
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Email (Optional)**:
   ```bash
   copy config_template.py config.py
   # Edit config.py with your email settings
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Access the Application**:
   Open your browser and go to: `http://localhost:5000`

## Usage

### Creating an Account
1. Click "Sign up here" on the home page
2. Enter username, email, and password
3. Click "Create Account"

### Logging In
1. Enter your username and password
2. **For Real Email**: Check your email inbox for the OTP code
3. **For Demo Mode**: Check the **console output** for the OTP code (simulated email)
4. Enter the 6-digit OTP code
5. Access your secure dashboard

## 🔧 Technical Implementation

### Architecture
- **Frontend**: HTML5, CSS3, JavaScript (responsive design)
- **Backend**: Flask (Python web framework)
- **Database**: SQLite (with users and OTPs tables)
- **Security**: SHA-256 password hashing, session management
- **Email**: SMTP integration with HTML templates

### Key Security Features
- ✅ **Password Hashing**: SHA-256 encryption for stored passwords
- ✅ **OTP Validation**: Time-based expiry (5 minutes) and single-use codes
- ✅ **Session Management**: Secure authentication state tracking
- ✅ **Input Validation**: Form validation and SQL injection prevention
- ✅ **Email Security**: SMTP TLS encryption for email delivery

## 📊 Database Schema

### Users Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `username` | TEXT | Unique username |
| `email` | TEXT | User's email address |
| `password_hash` | TEXT | SHA-256 hashed password |
| `created_at` | TIMESTAMP | Account creation time |

### OTPs Table
| Field | Type | Description |
|-------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `user_id` | INTEGER | Foreign key to users table |
| `otp_code` | TEXT | 6-digit verification code |
| `created_at` | TIMESTAMP | OTP creation time |
| `expires_at` | TIMESTAMP | OTP expiration time |
| `used` | BOOLEAN | Single-use flag |

## 📁 Project Structure

```
2fa_demo/
├── 📄 app.py                    # Main Flask application (259 lines)
├── 📄 requirements.txt          # Python dependencies
├── 📄 config_template.py        # Email configuration template
├── 📄 EMAIL_SETUP.md           # Email setup instructions
├── 📄 users.db                 # SQLite database (auto-created)
├── 📄 .gitignore               # Git ignore rules
├── 📂 templates/               # HTML templates
│   ├── 📄 base.html            # Base template with styling
│   ├── 📄 index.html           # Home page
│   ├── 📄 register.html        # Registration form
│   ├── 📄 login.html           # Login form
│   ├── 📄 verify_otp.html      # OTP verification form
│   └── 📄 dashboard.html       # Protected dashboard
└── 📄 README.md               # Project documentation
```

## 🎓 Educational Value & Learning Outcomes

This project demonstrates practical implementation of:

### Security Concepts
- **Multi-Factor Authentication (MFA)** principles and implementation
- **OTP (One-Time Password)** generation and validation
- **Session Management** and secure authentication state
- **Password Security** with proper hashing techniques

### Web Development Skills
- **Flask Framework** for web application development
- **Database Integration** with SQLite and SQL operations
- **Email Integration** using SMTP protocols
- **Frontend Development** with responsive HTML/CSS design

### Software Engineering Practices
- **Project Structure** and code organization
- **Error Handling** and user feedback systems
- **Configuration Management** for different environments
- **Documentation** and setup instructions

## 🎯 Project Objectives Achieved

✅ **Primary Goal**: Demonstrate 2FA implementation to enhance password security  
✅ **Technical Goal**: Build a minimal yet functional web application  
✅ **Educational Goal**: Teach students practical implementation of 2FA  
✅ **Security Goal**: Show real-world authentication security patterns  

## 🔮 Future Enhancements

- 📱 **SMS OTP**: Alternative to email-based verification
- 🔐 **TOTP Support**: Time-based OTP using authenticator apps
- 🛡️ **Rate Limiting**: Prevent brute force attacks
- 📊 **Admin Dashboard**: User management and analytics
- 🔗 **API Integration**: RESTful API for mobile apps
- 🎨 **Enhanced UI**: Modern JavaScript frameworks integration

## 🚨 Production Considerations

⚠️ **Important**: This is a demo application. For production use:

- Use environment variables for sensitive configuration
- Implement rate limiting for OTP requests
- Add CSRF protection and input sanitization
- Use stronger password hashing (bcrypt/scrypt)
- Implement proper logging and monitoring
- Use production-grade database (PostgreSQL/MySQL)
- Add SSL/TLS encryption and security headers
- Implement account lockout and suspicious activity detection

## 📄 License

This project is created for educational purposes and demonstration of 2FA concepts.

---

## 🤝 Contributing

This is an educational demo project. Feel free to fork and enhance for learning purposes!

**Created by**: ASHUTOSH KUMAR  
**Course**: Computer Science/Software Engineering  
**Date**: August 2025
