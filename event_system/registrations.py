# registrations.py
# Handles student registrations for events, including capacity checks.

from . import db
from . import auth
import datetime

def register_student_for_event(current_user_role, event_id, student_id):
    """
    Registers a student for a specific event, handling all business rules
    within a single database transaction.
    """
    if current_user_role not in ['admin', 'volunteer']:
        return "Error: You do not have the required permissions to perform this action."

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

def cancel_registration(current_user_role, event_id, student_id):
    """
    Cancels a student's registration for an event and deletes any associated
    attendance records.
    """
    if current_user_role not in ['admin', 'volunteer']:
        return "Error: You do not have the required permissions to perform this action."
        
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

if __name__ == '__main__':
    # Note: These tests require a student 'S001' and an event with ID 1 to exist.
    # They also require a user with role 'unauthorized' to not exist for a valid test.
    
    def setup_test_data():
        """A basic function to ensure some data exists for testing."""
        print("--- Setting up test data ---")
        try:
            with db.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Ensure event 1 exists
                    cursor.execute("SELECT * FROM events WHERE event_id=1")
                    if not cursor.fetchone():
                         cursor.execute("INSERT INTO events (event_id, event_name, event_date, venue, total_slots) VALUES (1, 'Test Event', sysdate, 'Test Venue', 5)")
                    # Ensure student S001 exists
                    cursor.execute("SELECT * FROM students WHERE student_id='S001'")
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO students (student_id, name, email, course, year) VALUES ('S001', 'Test Student', 'test@test.com', 'CS', 2024)")
                    # Clean up previous registration for S001 in event 1
                    cursor.execute("DELETE FROM registrations WHERE event_id=1 AND student_id='S001'")
                    conn.commit()
        except Exception as e:
            print(f"Test data setup failed: {e}")


    def test_registration_permissions():
        print("\n--- Testing Registration Permissions ---")
        # Admin can register
        result_admin = register_student_for_event('admin', 1, 'S001')
        print(f"Admin registration result: {result_admin}")
        assert "Success" in result_admin
        # Volunteer can register
        result_volunteer = register_student_for_event('volunteer', 1, 'S001')
        print(f"Volunteer registration result: {result_volunteer}")
        assert "Info: Student is already registered" in result_volunteer # Already registered by admin
        # Unauthorized role cannot register
        result_unauthorized = register_student_for_event('unauthorized_role', 1, 'S001')
        print(f"Unauthorized registration result: {result_unauthorized}")
        assert "Error: You do not have the required permissions" in result_unauthorized
        print("Registration permission tests passed.")

    def test_cancellation_permissions():
        print("\n--- Testing Cancellation Permissions ---")
        # Volunteer can cancel
        result_volunteer = cancel_registration('volunteer', 1, 'S001')
        print(f"Volunteer cancellation result: {result_volunteer}")
        assert "Success" in result_volunteer
        # Re-register for the next test
        register_student_for_event('admin', 1, 'S001')
        # Unauthorized role cannot cancel
        result_unauthorized = cancel_registration('unauthorized_role', 1, 'S001')
        print(f"Unauthorized cancellation result: {result_unauthorized}")
        assert "Error: You do not have the required permissions" in result_unauthorized
        # Admin can cancel
        result_admin = cancel_registration('admin', 1, 'S001')
        print(f"Admin cancellation result: {result_admin}")
        assert "Success" in result_admin
        print("Cancellation permission tests passed.")

    # Execute tests
    db.init_pool()
    setup_test_data()
    test_registration_permissions()
    test_cancellation_permissions()
    db.close_pool()
