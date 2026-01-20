# create_user.py
# A utility script to add a new user with a hashed password to the database.

import getpass
from event_system import db, auth
import oracledb # Import the oracledb library to catch specific exceptions

def create_user():
    """
    Prompts for user details, hashes the password, and inserts the new user
    into the database.
    """
    print("--- Create a New User ---")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    role = input("Enter role (admin/volunteer): ").lower()

    if not all([username, password, role]):
        print("Username, password, and role are required.")
        return

    if role not in ['admin', 'volunteer']:
        print("Invalid role. Please choose 'admin' or 'volunteer'.")
        return

    # Hash the password
    hashed_password = auth.hash_password(password)

    conn = db.get_connection()
    if not conn:
        print("Database connection failed.")
        return

    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO USERS (username, password, role)
        VALUES (:username, :password, :role)
        """
        cursor.execute(query, {
            'username': username,
            'password': hashed_password,
            'role': role
        })
        conn.commit()
        print(f"Successfully created user: {username} with role: {role}")
    except oracledb.IntegrityError as e:
        error_obj, = e.args
        # Check if the error is a unique constraint violation for the username
        if "UK_USERNAME" in error_obj.message:
            print(f"Error: Username '{username}' already exists.")
        else:
            print(f"An integrity error occurred: {e}")
        conn.rollback()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    db.init_pool()  # Initialize the pool
    create_user()
    db.close_pool() # Close the pool
