# registrations.py
# Handles student registrations for events, including capacity checks.

from . import db
import datetime

def register_student_for_event(event_id, student_id):
    """
    Registers a student for a specific event, handling all business rules
    within a single database transaction.
    """
    try:
        with db.get_connection() as conn:
            # Using a transaction context manager ensures atomicity.
            # It will automatically commit if the block succeeds, or rollback if it fails.
            with conn.cursor() as cursor:
                # --- Check 1: Event Capacity and Existence (with row lock) ---
                cursor.execute("SELECT total_slots FROM EVENTS WHERE event_id = :event_id FOR UPDATE", {'event_id': event_id})
                event_result = cursor.fetchone()
                if not event_result:
                    return "Error: Event not found."
                total_slots = event_result[0]

                # --- Check 2: Student Existence ---
                cursor.execute("SELECT name FROM STUDENTS WHERE student_id = :student_id", {'student_id': student_id})
                if not cursor.fetchone():
                    return "Error: Student not found."

                # --- Check 3: Already Registered ---
                cursor.execute(
                    "SELECT reg_id FROM REGISTRATIONS WHERE event_id = :event_id AND student_id = :student_id",
                    {'event_id': event_id, 'student_id': student_id}
                )
                if cursor.fetchone():
                    return "Info: Student is already registered for this event."

                # --- Check 4: Capacity Check ---
                cursor.execute("SELECT COUNT(*) FROM REGISTRATIONS WHERE event_id = :event_id", {'event_id': event_id})
                registered_count = cursor.fetchone()[0]
                
                if registered_count >= total_slots:
                    return "Error: Event is full. Cannot register."

                # --- If all checks pass, proceed with registration ---
                insert_query = """
                INSERT INTO REGISTRATIONS (event_id, student_id, reg_date)
                VALUES (:event_id, :student_id, :reg_date)
                """
                cursor.execute(insert_query, {
                    'event_id': event_id,
                    'student_id': student_id,
                    'reg_date': datetime.datetime.now()
                })
                
                conn.commit()
                return "Success: Student registered successfully."

    except Exception as e:
        print(f"Error during registration: {e}")
        # The transaction is automatically rolled back by the 'with' statement on exception
        return f"An unexpected error occurred: {e}"

def get_registered_students(event_id):
    """
    Retrieves a list of students registered for a given event.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT s.student_id, s.name, s.email, r.reg_date
                FROM STUDENTS s
                JOIN REGISTRATIONS r ON s.student_id = r.student_id
                WHERE r.event_id = :event_id
                ORDER BY s.name
                """
                cursor.execute(query, {'event_id': event_id})
                return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching registered students: {e}")
        return []

def cancel_registration(event_id, student_id):
    """
    Cancels a student's registration for an event and deletes any associated
    attendance records.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # First, delete any attendance records for this registration
                cursor.execute(
                    "DELETE FROM ATTENDANCE WHERE event_id = :1 AND student_id = :2",
                    [event_id, student_id]
                )
                
                # Then, delete the registration itself
                cursor.execute(
                    "DELETE FROM REGISTRATIONS WHERE event_id = :1 AND student_id = :2",
                    [event_id, student_id]
                )
                
                conn.commit()
                return "Success: Registration canceled successfully."
    except Exception as e:
        print(f"Error canceling registration: {e}")
        return f"An unexpected error occurred: {e}"
