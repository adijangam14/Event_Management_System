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

# --- Web Theme Configuration ---
# A list of available Bootswatch themes:
# cerulean, cosmo, cyborg, darkly, flatly, journal, litera, lumen, lux, materia, minty,
# morph, pulse, quartz, sandstone, simplex, sketchy, slate, solar, spacelab, superhero,
# united, vapor, yeti, zephyr
WEB_THEME = 'vapor'

# --- Desktop Theme Configuration ---
# A list of available ttk themes:
# arc, black, blue, breeze, clearlooks, elegance, equilux, itft1, kroc,
# radiance, scidblue, smalt
DESKTOP_THEME = 'blue'

if DB_CONFIG['user'] == 'default_user' or EMAIL_CONFIG['smtp_server'] == 'smtp.example.com':
    print("---")
    print("WARNING: Using default configuration values.")
    print("The application may not connect to the database or send emails correctly until you set the required environment variables.")
    print("Please see the instructions in `event_system/config.py` for more details.")
    print("---\n")
