# auth.py
# Handles user authentication and role-based access.

import bcrypt
from . import db
import oracledb

def hash_password(plain_text_password):
    """Hashes a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_text_password, hashed_password):
    """Verifies a plain-text password against a hashed password."""
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_web_user(username, password):
    """
    Creates a new user with the 'volunteer' role.
    """
    if not all([username, password]):
        return "Error: Username and password are required."

    hashed_password = hash_password(password)
    role = 'volunteer' # All web-registered users are volunteers

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
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
                return "Success: User created successfully. Please login."
    except oracledb.IntegrityError as e:
        error_obj, = e.args
        if "UK_USERNAME" in error_obj.message:
            return f"Error: Username '{username}' already exists."
        else:
            return f"A database integrity error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def login(username, password):
    """
    Validates user credentials against the USERS table using hashed passwords.
    If successful, it returns the user's details.
    
    Args:
        username (str): The user's username.
        password (str): The user's plain-text password.

    Returns:
        dict: A dictionary with user_id, username, and role if successful.
        None: If login fails.
    """
    conn = db.get_connection()
    if not conn:
        return None  # Database connection failed

    try:
        with conn.cursor() as cursor:
            # Fetch the hashed password from the database, making username check case-insensitive
            query = "SELECT user_id, username, password, role FROM USERS WHERE LOWER(username) = LOWER(:username)"
            cursor.execute(query, {'username': username})
            result = cursor.fetchone()

            if result:
                user_id, db_username, hashed_password_from_db, role = result
                # Verify the provided password against the stored hash
                if verify_password(password, hashed_password_from_db):
                    # Return the actual username from the DB for consistent casing
                    user_data = {
                        'user_id': user_id,
                        'username': db_username,
                        'role': role
                    }
                    print(f"Login successful for user: {db_username}, Role: {role}")
                    return user_data

            # If user not found or password doesn't match
            print("Invalid username or password.")
            return None
    except Exception as e:
        print(f"An error occurred during login: {e}")
        return None
    finally:
        if conn:
            conn.close() # Release the connection back to the pool


# Example usage (for testing purposes)
if __name__ == '__main__':
    # This assumes you have a user in your USERS table with a hashed password.
    # To test, you can use the create_user.py script to add a new admin.
    
    # Test successful login
    print("--- Testing Successful Login ---")
    # Replace 'admin123' with the password you used in create_user.py
    user_data = login('admin1', 'admin123')
    if user_data:
        print(f"Logged in with role: {user_data['role']}")
        print(f"Is admin? {user_data['role'] == 'admin'}")
        print("Current session:", user_data)
    else:
        print("Login failed. Make sure you have a user 'admin1' with a hashed password in the USERS table.")

    print("\n--- Testing Failed Login ---")
    user_data = login('admin1', 'wrongpassword')
    if not user_data:
        print("Failed login test passed.")

