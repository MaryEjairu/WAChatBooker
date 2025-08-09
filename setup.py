#!/usr/bin/env python3
"""
Setup script for WhatsApp Appointment Booking Bot
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Error installing packages. Please install manually:")
        print("pip install -r requirements.txt")
        return False
    return True

def check_environment():
    """Check if environment variables are set"""
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN", 
        "TWILIO_PHONE_NUMBER"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables before running the bot.")
        print("You can create a .env file or export them in your shell.")
        return False
    
    print("✅ All environment variables are set!")
    return True

def create_database():
    """Initialize the database"""
    print("Initializing database...")
    try:
        from app import app, db
        with app.app_context():
            db.create_all()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 WhatsApp Appointment Booking Bot Setup")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 2: Check environment variables
    if not check_environment():
        print("\n📝 To set environment variables:")
        print("export TWILIO_ACCOUNT_SID='your_account_sid'")
        print("export TWILIO_AUTH_TOKEN='your_auth_token'")
        print("export TWILIO_PHONE_NUMBER='whatsapp:+1234567890'")
        sys.exit(1)
    
    # Step 3: Initialize database
    if not create_database():
        sys.exit(1)
    
    print("\n🎉 Setup complete!")
    print("\nTo start the bot:")
    print("python main.py")
    print("\nOr with gunicorn:")
    print("gunicorn --bind 0.0.0.0:5000 --reload main:app")
    print("\nDon't forget to configure your Twilio webhook URL!")

if __name__ == "__main__":
    main()