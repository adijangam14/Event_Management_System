# events.py
# Handles event creation and listing.

from . import db
import datetime

def create_event(current_user_role, event_name, event_date, event_time, venue, total_slots):
    """
    Creates a new event and saves it to the database.
    This action is restricted to admin users.
    """
    if current_user_role != 'admin':
        return "Error: Administrative privileges required."

    if not all([event_name, event_date, event_time, venue, total_slots]):
        return "Error: All fields are required."
    
    try:
        slots = int(total_slots)
        if slots <= 0:
            return "Error: Total slots must be a positive number."
    except (ValueError, TypeError):
        return "Error: Total slots must be a valid number."

    try:
        # Validate and format event_date
        if isinstance(event_date, datetime.date):
            formatted_date = event_date.strftime('%Y-%m-%d')
        else:
            try:
                formatted_date = datetime.datetime.strptime(str(event_date), '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                return "Error: Invalid date format. Please use YYYY-MM-DD."

        # Validate and format event_time
        try:
            # Try parsing with AM/PM
            dt_time = datetime.datetime.strptime(str(event_time), '%I:%M %p')
        except ValueError:
            try:
                # Try parsing with 24-hour format
                dt_time = datetime.datetime.strptime(str(event_time), '%H:%M')
            except ValueError:
                return "Error: Invalid time format. Please use HH:MM AM/PM or HH:MM."
        
        formatted_time = dt_time.strftime('%I:%M %p')

        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO EVENTS (event_name, event_date, event_time, venue, total_slots)
                VALUES (:event_name, TO_DATE(:event_date, 'YYYY-MM-DD'), :event_time, :venue, :total_slots)
                """
                cursor.execute(query, {
                    'event_name': event_name,
                    'event_date': formatted_date,
                    'event_time': formatted_time,
                    'venue': venue,
                    'total_slots': slots
                })
                conn.commit()
                print(f"Successfully created event: {event_name}")
                return "Success: Event created successfully."
    except Exception as e:
        print(f"Error creating event: {e}")
        # Rollback is handled by the connection pool/transaction manager if an error occurs
        return f"An unexpected error occurred: {e}"

def get_all_events():
    """
    Retrieves a list of all events from the database.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT event_id, event_name, event_date, event_time, venue, total_slots FROM EVENTS ORDER BY event_date DESC"
                cursor.execute(query)
                return cursor.fetchall()
    except Exception as e:
        print(f"Error fetching events: {e}")
        return []

def get_event_details(event_id):
    """
    Retrieves details for a single event from the database.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT event_id, event_name, event_date, event_time, venue, total_slots FROM EVENTS WHERE event_id = :event_id"
                cursor.execute(query, {'event_id': event_id})
                return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching event details for event_id {event_id}: {e}")
        return None


# Example usage (for testing purposes)
if __name__ == '__main__':
    def test_admin_can_create_event():
        print("\n--- Testing Event Creation (as Admin) ---")
        result = create_event(
            'admin',  # Pass the role directly
            'Annual Tech Symposium',
            datetime.date(2024, 10, 25),
            '10:00 AM',
            'Main Auditorium',
            150
        )
        print(result)
        assert "Success" in result
        print("Test passed: Admin was able to create an event.")

    def test_volunteer_cannot_create_event():
        print("\n--- Testing Event Creation (as Volunteer) ---")
        result = create_event(
            'volunteer',  # Pass the role directly
            'Unauthorized Event',
            datetime.date(2024, 11, 15),
            '10:00 AM',
            'Secret Location',
            50
        )
        print(result)
        assert "Error: Administrative privileges required." in result
        print("Test passed: Volunteer was correctly prevented from creating an event.")

    def test_get_all_events():
        print("\n--- Testing Fetching All Events ---")
        all_events = get_all_events()
        if all_events:
            print("Successfully fetched events:")
            for event in all_events:
                print(event)
        else:
            print("No events found or an error occurred.")

    # Execute the tests
    db.init_pool()
    test_admin_can_create_event()
    test_volunteer_cannot_create_event()
    test_get_all_events()
    db.close_pool()