# students.py
# Handles student creation and listing.

from . import db
from . import auth
import re
import oracledb

def add_student(current_user_role, student_id, name, email, course, year):
    """
    Adds a new student to the database after validating inputs.
    This action is restricted to admin users and handles race conditions.
    """
    if current_user_role != 'admin':
        return "Error: Administrative privileges required."

    # --- Input Validation ---
    if not all([student_id, name, email]):
        return "Error: Student ID, Name, and Email are required."
    
    # Basic email format validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Error: Invalid email format."
        
    try:
        year_int = int(year)
        if year_int <= 0:
            return "Error: Year must be a positive number."
    except (ValueError, TypeError):
        return "Error: Year must be a valid number."

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO STUDENTS (student_id, name, email, course, year)
                VALUES (:student_id, :name, :email, :course, :year)
                """
                cursor.execute(query, {
                    'student_id': student_id,
                    'name': name,
                    'email': email,
                    'course': course,
                    'year': year_int
                })
                conn.commit()
                return "Success: Student added successfully."
    except oracledb.IntegrityError as e:
        error_obj, = e.args
        # Assuming the student_id is the primary key (PK) and email has a unique constraint (UK_EMAIL)
        if "PK_STUDENTS" in error_obj.message:
            return f"Error: Student with ID '{student_id}' already exists."
        elif "UK_STUDENT_EMAIL" in error_obj.message: # Adjusted constraint name for likely convention
            return f"Error: A student with the email '{email}' already exists."
        else:
            return f"A database integrity error occurred: {e}"
    except oracledb.DatabaseError as e:
        return f"A database error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def get_all_students():
    """
    Retrieves a list of all students from the database.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT student_id, name, email, course, year FROM STUDENTS ORDER BY name"
                cursor.execute(query)
                return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching students: {e}")
        return []

def get_student_by_id(student_id):
    """
    Retrieves a single student's details from the database.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT student_id, name, email, course, year FROM STUDENTS WHERE student_id = :student_id"
                cursor.execute(query, {'student_id': student_id})
                return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching student: {e}")
        return None

def update_student(current_user_role, student_id, name, email, course, year):
    """
    Updates a student's details in the database.
    """
    if current_user_role != 'admin':
        return "Error: Administrative privileges required."

    if not all([student_id, name, email]):
        return "Error: Student ID, Name, and Email are required."

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return "Error: Invalid email format."
        
    try:
        year_int = int(year)
        if year_int <= 0:
            return "Error: Year must be a positive number."
    except (ValueError, TypeError):
        return "Error: Year must be a valid number."

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                UPDATE STUDENTS
                SET name = :name, email = :email, course = :course, year = :year
                WHERE student_id = :student_id
                """
                cursor.execute(query, {
                    'name': name,
                    'email': email,
                    'course': course,
                    'year': year_int,
                    'student_id': student_id
                })
                conn.commit()
                if cursor.rowcount == 0:
                    return "Error: Student not found."
                return "Success: Student updated successfully."
    except oracledb.IntegrityError as e:
        error_obj, = e.args
        if "UK_STUDENT_EMAIL" in error_obj.message:
            return f"Error: A student with the email '{email}' already exists."
        else:
            return f"A database integrity error occurred: {e}"
    except oracledb.DatabaseError as e:
        return f"A database error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def delete_student(current_user_role, student_id):
    """
    Deletes a student from the database.
    """
    if current_user_role != 'admin':
        return "Error: Administrative privileges required."

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "DELETE FROM STUDENTS WHERE student_id = :student_id"
                cursor.execute(query, {'student_id': student_id})
                conn.commit()
                if cursor.rowcount == 0:
                    return "Error: Student not found."
                return "Success: Student deleted successfully."
    except oracledb.DatabaseError as e:
        return f"A database error occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


# Example usage (for testing purposes)
if __name__ == '__main__':
    import random

    def test_admin_can_add_student():
        print("\n--- Testing Student Addition (as Admin) ---")
        # Use a random ID and email to avoid constraint violations on re-runs
        student_id = f"TEST{random.randint(1000, 9999)}"
        email = f"test.{random.randint(1000, 9999)}@example.com"
        result = add_student(
            'admin', student_id, 'Test Student', email, 'Computer Science', '2024'
        )
        print(result)
        assert "Success" in result
        print("Test passed: Admin was able to add a student.")

    def test_volunteer_cannot_add_student():
        print("\n--- Testing Student Addition (as Volunteer) ---")
        result = add_student(
            'volunteer', 'VTEST99', 'Volunteer Test', 'vtest99@example.com', 'Biology', '2023'
        )
        print(result)
        assert "Error: Administrative privileges required." in result
        print("Test passed: Volunteer was correctly prevented from adding a student.")

    # Execute the tests
    db.init_pool()
    test_admin_can_add_student()
    test_volunteer_cannot_add_student()
    db.close_pool()
