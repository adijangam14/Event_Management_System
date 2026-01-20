#!/bin/bash

# Installer script for the College Event Registration and Attendance Management System

# --- Functions ---

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print a separator line
print_separator() {
    echo "------------------------------------------------------------"
}

# --- Start of Script ---

echo "Starting the installer for the Event Management System..."
print_separator

# --- 1. Check for Python 3 ---

echo "Checking for Python 3..."
if command_exists python3; then
    echo "Python 3 found."
else
    echo "Error: Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi
print_separator

# --- 2. Create a Virtual Environment ---

echo "Creating a Python virtual environment..."
if python3 -m venv venv; then
    echo "Virtual environment created successfully in the 'venv' directory."
else
    echo "Error: Failed to create a virtual environment."
    echo "Please ensure that the 'venv' module is installed for Python 3."
    echo "On Debian/Ubuntu, you can run: sudo apt-get install python3-venv"
    exit 1
fi
print_separator

# --- 3. Install Dependencies in the Virtual Environment ---

echo "Installing required Python libraries into the virtual environment..."
# Activate the virtual environment for this script's context
source venv/bin/activate

# Upgrade pip to the latest version
echo "Upgrading pip..."
if python3 -m pip install --upgrade pip; then
    echo "pip upgraded successfully."
else
    echo "Warning: Failed to upgrade pip. Continuing with the existing version."
fi

if python3 -m pip install -r requirements.txt; then
    echo "Dependencies installed successfully."
else
    echo "Error: Failed to install dependencies. Please check your internet connection and try again."
    # Deactivate on failure
    deactivate
    exit 1
fi
print_separator

# --- 4. Create .env file ---

echo "Now, let's create the .env file with your credentials."
echo "Please provide the following information:"

read -p "Enter your Oracle database username: " DB_USER
read -sp "Enter your Oracle database password: " DB_PASSWORD
echo
read -p "Enter your Oracle database connection string (e.g., localhost:1521/XEPDB1): " DB_DSN
read -p "Enter your SMTP server address (e.g., smtp.gmail.com): " SMTP_SERVER
read -p "Enter your SMTP server port (e.g., 587): " SMTP_PORT
read -p "Enter your SMTP username (your email address): " SMTP_USERNAME
read -sp "Enter your SMTP password: " SMTP_PASSWORD
echo
read -p "Enter your sender email address: " SENDER_EMAIL

# Create the .env file
cat > .env << EOL
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_DSN=${DB_DSN}
SMTP_SERVER=${SMTP_SERVER}
SMTP_PORT=${SMTP_PORT}
SMTP_USERNAME=${SMTP_USERNAME}
SMTP_PASSWORD=${SMTP_PASSWORD}
SENDER_EMAIL=${SENDER_EMAIL}
EOL

echo ".env file created successfully."
print_separator

# --- 5. Set up the database ---

echo "The next step is to set up the database schema."
echo "You need to run the 'event_system/database_setup.sql' script in your Oracle database."
read -p "Do you want to see the contents of the SQL script now? (y/n): " show_sql
if [[ "$show_sql" == "y" || "$show_sql" == "Y" ]]; then
    print_separator
    cat event_system/database_setup.sql
    print_separator
fi
echo "Please run the SQL script in your database before running the application."
print_separator

# --- 6. Provide instructions ---

echo "Installation complete!"
echo
echo "IMPORTANT: Before running the application, you must activate the virtual environment."
echo "Run the following command:"
echo "source venv/bin/activate"
echo
echo "Once the virtual environment is activated, you can run the application in two ways:"
echo
echo "1. Desktop Application (Tkinter):"
echo "   Run the following command from the project root directory:"
echo "   python3 -m event_system"
echo
echo "2. Web Application (Flask):"
echo "   Run the following command from the project root directory:"
echo "   python3 event_system/web_ui.py"
echo "   Then, open your web browser and go to http://127.0.0.1:5000"
echo
echo "To create a new user, run:"
echo "python3 -m event_system.create_user"
echo
echo "When you are finished, you can deactivate the virtual environment by running:"
echo "deactivate"
echo

# Deactivate the virtual environment at the end of the script
deactivate

exit 0
