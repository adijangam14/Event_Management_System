# config.py
# Database and email configuration details.
#
# This file retrieves sensitive information (like passwords and API keys) from
# environment variables. This is a security best practice that avoids hard-coding
# credentials directly into the source code.
#
# To run this application, you must set the following environment variables before
# launching it:
#
# For the Database (Oracle):
#   - DB_USER: Your Oracle database username.
#   - DB_PASSWORD: Your Oracle database password.
#   - DB_DSN: The connection string for your Oracle database (e.g., 'localhost:1521/XEPDB1').
#
# For Email Notifications (SMTP):
#   - SMTP_SERVER: The address of your SMTP server (e.g., 'smtp.gmail.com').
#   - SMTP_PORT: The port for the SMTP server (e.g., 587 for TLS).
#   - SMTP_USERNAME: Your email account username.
#   - SMTP_PASSWORD: Your email account password or an app-specific password.
#   - SENDER_EMAIL: The email address that will appear as the sender.
#
# You can set these variables directly in your shell, or use a `.env` file
# with a library like `python-dotenv` for easier management during development.

import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists.
# This is useful for development environments.
load_dotenv()

# --- Database Configuration ---
# Retrieves Oracle database credentials from environment variables.
DB_CONFIG = {
    'user': os.environ.get('DB_USER', 'default_user'),
    'password': os.environ.get('DB_PASSWORD', 'default_password'),
    'dsn': os.environ.get('DB_DSN', 'localhost:1521/XEPDB1')
}

# --- Email Configuration ---
# Retrieves SMTP server details from environment variables for sending emails.
EMAIL_CONFIG = {
    'smtp_server': os.environ.get('SMTP_SERVER', 'smtp.example.com'),
    'smtp_port': int(os.environ.get('SMTP_PORT', 587)),
    'smtp_username': os.environ.get('SMTP_USERNAME', 'user@example.com'),
    'smtp_password': os.environ.get('SMTP_PASSWORD', 'password'),
    'sender_email': os.environ.get('SENDER_EMAIL', 'noreply@example.com')
}

# --- Validation and Feedback ---
# Provides a simple check to see if default values are being used, which might
# indicate that the environment variables have not been set. This is helpful
# for new users setting up the project.

if DB_CONFIG['user'] == 'default_user' or EMAIL_CONFIG['smtp_server'] == 'smtp.example.com':
    print("---")
    print("WARNING: Using default configuration values.")
    print("The application may not connect to the database or send emails correctly until you set the required environment variables.")
    print("Please see the instructions in `event_system/config.py` for more details.")
    print("---\n")
