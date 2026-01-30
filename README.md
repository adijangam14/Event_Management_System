# College Event Registration and Attendance Management System

This project is a desktop and web application for managing event registrations and attendance, built with Python and an Oracle database. It provides a graphical user interface using Tkinter and a web interface using Flask.

## 🔹 Features

*   **Event Management**: Admins can create, view, and manage events, including setting capacity limits.
*   **Student Registration**: Admins can register students for events, with automatic capacity enforcement.
*   **Attendance Marking**: Admins and volunteers can mark student attendance. Attendance can only be marked on or after the event date to ensure accuracy.
*   **Email Notifications**: Admins can send customized email notifications to all registered attendees of an event. Emails are sent asynchronously to prevent UI blocking, ensuring a smooth user experience.
*   **Secure Password Storage**: User passwords are securely hashed using `bcrypt`, a strong and widely-used password-hashing function.
*   **Role-Based Access Control**:
    *   **Admin**: Full access to all features, including creating events, registering students, marking attendance, viewing reports, and sending email notifications.
    *   **Volunteer**: Limited access to view events, mark attendance, and view reports. Volunteers can self-register.
*   **Reporting and Analytics**:
    *   View real-time attendance statistics for any event.
    *   Generate and view graphical reports of event attendance.
*   **CSV Export**: Export event attendance lists to a CSV file for easy data sharing and analysis.
*   **Dual Interface**: The application can be run as a desktop application (using Tkinter) or as a web application (using Flask), providing flexibility for different user needs.
*   **Automated Installer**: A shell script (`installer.sh`) is included to automate the setup process on Linux and macOS.

## 🔹 Tech Stack

*   **Backend**: Python 3
*   **Database**: Oracle
*   **UI**:
    *   Desktop: Tkinter (built-in Python GUI library)
    *   Web: Flask
*   **Database Driver**: `python-oracledb`
*   **Password Hashing**: `bcrypt`
*   **Email Validation**: `email_validator`
*   **Web Forms**: `Flask-WTF`

## 🔹 Setup and Installation

### Prerequisites

1.  **Python 3**: Make sure you have Python 3 installed.
2.  **Oracle Database**: You need access to an Oracle Database instance.
3.  **Oracle Instant Client**: The `python-oracledb` driver may require the Oracle Instant Client libraries. Follow the driver's installation instructions for your OS.

### Automated Installation (Linux/macOS)

For Linux and macOS users, an installer script is provided to automate the setup process.

1.  **Run the installer script:**
    ```bash
    bash installer.sh
    ```
    The script will:
    *   Check for Python 3.
    *   Create a virtual environment.
    *   Install all required dependencies.
    *   Prompt you to enter your database and email credentials and create the `.env` file.

2.  **Set up the Database Schema:**
    *   After the script completes, you still need to set up the database schema. Connect to your Oracle database using a SQL client (like SQL*Plus or DBeaver).
    *   Run the script `event_system/database_setup.sql` to create all the required tables, sequences, and constraints.

### Manual Installation

1.  **Clone the repository or download the source code.**

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required Python libraries:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the Application:**
    *   Create a `.env` file in the root directory of the project.
    *   Add the following environment variables to the `.env` file with your credentials:
        ```
        DB_USER=your_username
        DB_PASSWORD=your_password
        DB_DSN=your_host:your_port/your_service_name
        SMTP_SERVER=your.smtp.server.com
        SMTP_PORT=587
        SMTP_USERNAME=your_email@example.com
        SMTP_PASSWORD=your_email_password
        SENDER_EMAIL=your_email@example.com
        ```

5.  **Set up the Database Schema:**
    *   Connect to your Oracle database using a SQL client.
    *   Run the script `event_system/database_setup.sql` to create the database schema.

6.  **Insert Sample Data (Optional):**
    *   To test the application with some pre-populated data, run the `event_system/sample_data.sql` script in your SQL client.
    *   This script will create sample users, students, and an event.

---

## 🔹 How to Run the Application

First, ensure you have activated the virtual environment:
```bash
source venv/bin/activate
```

### Running the Desktop Application

Use the `--ui` flag to launch the Tkinter desktop application.

```bash
python -m event_system --ui
```

### Running the Web Application

Use the `--web` flag to launch the Flask web application.

```bash
python -m event_system --web
```
The application will be available at `http://127.0.0.1:5000` in your web browser.

## 🔹 Usage

### Creating a New User

*   **Admin Users**: You can create new admin users with a securely hashed password by running the `create_user.py` script:
    ```bash
    python -m event_system.create_user
    ```
    You will be prompted to enter a username, password, and the role 'admin'.

*   **Volunteer Users**: Volunteers can self-register through either the web interface or the desktop application by navigating to the "Register" page/screen.

### Logging In

Once the application is running, you can log in with a registered username and password. The interface will adapt based on the user's role (Admin or Volunteer).

### Sample Credentials

If you used the `sample_data.sql` script, you can log in with the following credentials:

*   **Admin User:**
    *   Username: `admin1`
    *   Password: `admin123`
*   **Volunteer User:**
    *   Username: `volunteer1`
    *   Password: `vol123`
*   **Another Volunteer User:**
    *   Username: `volunteer2`
    *   Password: `vol456`