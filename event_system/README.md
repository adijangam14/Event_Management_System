# College Event Registration and Attendance Management System

This project is a desktop application for managing event registrations and attendance, built with Python and an Oracle database. It provides a graphical user interface using Tkinter and role-based access for administrators and volunteers.

## 🔹 Features

*   **Event Management**: Admins can create and manage events, including setting capacity limits.
*   **Student Registration**: Admins can register students for events, with automatic capacity enforcement.
*   **Attendance Marking**: Admins and volunteers can mark student attendance, but only on or after the event date.
*   **Email Notifications**: Admins can send customized email notifications to all registered attendees of an event. Emails are sent asynchronously to prevent UI blocking.
*   **Secure Password Storage**: User passwords are securely hashed using `bcrypt`.
*   **Role-Based Access**:
    *   **Admin**: Full access to create events, register students, mark attendance, view reports, and send email notifications.
    *   **Volunteer**: Limited access to mark attendance and view reports.
*   **Reporting**: View real-time attendance statistics for any event.
*   **CSV Export**: Export event attendance lists to a CSV file.

## 🔹 Tech Stack

*   **Backend**: Python 3
*   **Database**: Oracle
*   **UI**: Tkinter (built-in Python GUI library)
*   **Database Driver**: `python-oracledb`
*   **Password Hashing**: `bcrypt`

## 🔹 Project Structure

The application is organized into the following modules:

```
event_system/
│
├── db.py              # Oracle connection handling
├── auth.py            # Login & role validation (with password hashing)
├── events.py          # Event creation & listing
├── registrations.py  # Student registrations + capacity check
├── attendance.py     # Attendance marking + date validation
├── reports.py        # Statistics + CSV export
├── email_utils.py     # Email sending utilities
├── create_user.py     # Utility script to create new users (NEW)
├── ui.py              # Tkinter UI screens
├── __main__.py          # Application entry point
├── config.py          # Database and Email credentials (DO NOT COMMIT)
├── database_setup.sql # Oracle SQL scripts for table creation
└── sample_data.sql    # SQL scripts to insert sample data
```

---

## 🔹 Setup and Installation

### Prerequisites

1.  **Python 3**: Make sure you have Python 3 installed.
2.  **Oracle Database**: You need access to an Oracle Database instance.
3.  **Oracle Instant Client**: The `python-oracledb` driver may require the Oracle Instant Client libraries. Follow the driver's installation instructions for your OS.

### Installation Steps

1.  **Clone the repository or download the source code.**

2.  **Install the required Python libraries:**
    The main dependencies are the Oracle database driver and the `bcrypt` library for password hashing.

    ```bash
    pip install python-oracledb bcrypt
    ```

3.  **Configure the Application:**
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

4.  **Set up the Database Schema:**
    *   Connect to your Oracle database using a SQL client (like SQL*Plus or DBeaver).
    *   Run the script `event_system/database_setup.sql` to create all the required tables, sequences, and constraints.
    *   **Note**: The script now includes an `email` column in the `STUDENTS` table, which is required for the email notification feature.

5.  **Insert Sample Data (Optional):**
    *   To test the application with some pre-populated data, run the `event_system/sample_data.sql` script in your SQL client.
    *   This script will create sample users with hashed passwords, students, and an event. **Make sure to add email addresses to the sample student data.**

---

## 🔹 How to Run the Application

Navigate to the parent directory (the one containing the `event_system` folder) and run the application as a Python module. This is important because it allows the relative imports within the package to work correctly.

```bash
python -m event_system
```

The application window should appear, starting with the login screen.

### Creating a New User

You can create new users (admin or volunteer) with a securely hashed password by running the `create_user.py` script:

```bash
python -m event_system.create_user
```

You will be prompted to enter a username, password, and role.

### Sample Credentials

If you used the `sample_data.sql` script, you can log in with the following credentials:

*   **Admin User:**
    *   Username: `admin1`
    *   Password: `admin123`
*   **Volunteer User:**
    *   Username: `volunteer1`
    *   Password: `volunteer123`
