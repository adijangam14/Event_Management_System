# attendance.py
# Handles marking and viewing of student attendance for events.

from . import db
import datetime

def mark_attendance(event_id, student_id, attended_status='Y'):
    """
    Marks or updates a student's attendance for a given event using a MERGE statement
    to prevent race conditions.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # --- Check 1: Event Date vs. Current Date ---
                cursor.execute("SELECT event_date FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
                result = cursor.fetchone()
                if not result:
                    return "Error: Event not found."
                
                event_date = result[0]
                current_date = datetime.date.today()
                if isinstance(event_date, datetime.datetime):
                    event_date = event_date.date()
                if event_date > current_date:
                    return f"Error: Attendance can only be marked on or after the event date ({event_date.strftime('%Y-%m-%d')})."

                # --- Check 2: Student Registration ---
                cursor.execute(
                    "SELECT reg_id FROM REGISTRATIONS WHERE event_id = :event_id AND student_id = :student_id",
                    {'event_id': event_id, 'student_id': student_id}
                )
                if not cursor.fetchone():
                    return "Error: Cannot mark attendance for a student who is not registered for this event."

                # --- Upsert Operation using MERGE ---
                merge_query = """
                MERGE INTO ATTENDANCE a
                USING (SELECT :event_id AS event_id, :student_id AS student_id FROM dual) s
                ON (a.event_id = s.event_id AND a.student_id = s.student_id)
                WHEN MATCHED THEN
                    UPDATE SET a.attended = :status
                WHEN NOT MATCHED THEN
                    INSERT (event_id, student_id, attended)
                    VALUES (:event_id, :student_id, :status)
                """
                cursor.execute(merge_query, {
                    'event_id': event_id,
                    'student_id': student_id,
                    'status': attended_status
                })
                
                conn.commit()
                return "Success: Attendance record saved successfully."

    except Exception as e:
        print(f"Error marking attendance: {e}")
        return f"An unexpected error occurred: {e}"

def get_event_attendance(event_id):
    """
    Retrieves the attendance status for all registered students for an event.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT
                    s.student_id,
                    s.name,
                    NVL(a.attended, 'N') AS attendance_status
                FROM REGISTRATIONS r
                JOIN STUDENTS s ON r.student_id = s.student_id
                LEFT JOIN ATTENDANCE a ON r.event_id = a.event_id AND r.student_id = a.student_id
                WHERE r.event_id = :event_id
                ORDER BY s.name
                """
                cursor.execute(query, {'event_id': event_id})
                return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching event attendance: {e}")
        return []

# Example usage (for testing purposes)
if __name__ == '__main__':
    # ASSUMPTIONS FOR TESTING:
    # 1. An event exists with ID=1, and its date is in the past.
    #    (e.g., UPDATE EVENTS SET event_date = '01-JAN-24' WHERE event_id = 1;)
    # 2. Another event exists with ID=2, and its date is in the future.
    #    (e.g., from events.py test, or create one with a future date)
    # 3. Students 'S001' (Alice) and 'S002' (Bob) are registered for event 1.
    #    (e.g., from registrations.py test)

    PAST_EVENT_ID = 1
    FUTURE_EVENT_ID = 2

    print(f"--- Testing Attendance for Past Event (ID: {PAST_EVENT_ID}) ---")
    
    # Test 1: Mark attendance for a registered student
    print("\n1. Marking attendance for Alice (S001)...")
    result = mark_attendance(PAST_EVENT_ID, 'S001', 'Y')
    print(f"   Result: {result}")

    # Test 2: Update attendance for the same student
    print("\n2. Updating attendance for Alice (S001) to 'N'...")
    result = mark_attendance(PAST_EVENT_ID, 'S001', 'N')
    print(f"   Result: {result}")

    # Test 3: Mark attendance for an unregistered student
    print("\n3. Attempting to mark attendance for unregistered Charlie (S003)...")
    result = mark_attendance(PAST_EVENT_ID, 'S003', 'Y')
    print(f"   Result: {result}")

    print(f"\n--- Testing Attendance for Future Event (ID: {FUTURE_EVENT_ID}) ---")

    # Test 4: Attempt to mark attendance for a future event
    print("\n4. Attempting to mark attendance for future event...")
    result = mark_attendance(FUTURE_EVENT_ID, 'S001', 'Y') # Assuming S001 is registered
    print(f"   Result: {result}")

    # Test 5: Fetching attendance list
    print(f"\n--- Fetching attendance for event {PAST_EVENT_ID} ---")
    attendance_list = get_event_attendance(PAST_EVENT_ID)
    if attendance_list:
        print("   Attendance List:")
        for student in attendance_list:
            print(f"   - {student}")
    else:
        print("   No attendance records found or an error occurred.")

