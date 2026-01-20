# students.py
# Handles student creation and listing.

from . import db

import re
from . import db
import oracledb

def add_student(student_id, name, email, course, year):
    """
    Adds a new student to the database after validating inputs.
    This action is restricted to admin users.
    """
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
                # Check for existing student ID
                cursor.execute("SELECT student_id FROM STUDENTS WHERE student_id = :1", [student_id])
                if cursor.fetchone():
                    return "Error: Student with this ID already exists."
                
                # Check for existing email
                cursor.execute("SELECT email FROM STUDENTS WHERE email = :1", [email])
                if cursor.fetchone():
                    return "Error: A student with this email already exists."

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
