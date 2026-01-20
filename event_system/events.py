# events.py
# Handles event creation and listing.

from . import db
from . import auth
import datetime

def create_event(event_name, event_date, event_time, venue, total_slots):
    """
    Creates a new event and saves it to the database.
    This action is restricted to admin users.
    """
    if not all([event_name, event_date, event_time, venue, total_slots]):
        return "Error: All fields are required."
    
    try:
        slots = int(total_slots)
        if slots <= 0:
            return "Error: Total slots must be a positive number."
    except (ValueError, TypeError):
        return "Error: Total slots must be a valid number."

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO EVENTS (event_name, event_date, event_time, venue, total_slots)
                VALUES (:event_name, :event_date, :event_time, :venue, :total_slots)
                """
                cursor.execute(query, {
                    'event_name': event_name,
                    'event_date': event_date,
                    'event_time': event_time,
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
    # --- Test Case 1: Create event as an Admin ---
    # To test this, we first need to log in as an admin.
    print("--- Logging in as admin to test event creation ---")
    auth.login('admin', 'adminpass')
    
    if auth.is_admin():
        print("\n--- Testing Event Creation (as Admin) ---")
        # Creating a sample event
        event_created = create_event(
            'Annual Tech Symposium',
            datetime.date(2024, 10, 25),
            '10:00 AM',
            'Main Auditorium',
            150
        )
        if event_created:
            print("Event creation test passed.")
        else:
            print("Event creation test failed.")
    else:
        print("Could not test event creation because admin login failed.")
        print("Ensure you have an 'admin' user with password 'adminpass'.")

    # --- Test Case 2: Attempt to create event as a non-admin ---
    auth.logout() # Log out admin
    print("\n--- Logging in as volunteer to test event creation restriction ---")
    # This assumes a 'volunteer' user exists, e.g.,
    # INSERT INTO USERS (user_id, username, password, role) 
    # VALUES ('volunteer01', 'volunteer', 'volunteerpass', 'volunteer');
    auth.login('volunteer', 'volunteerpass')

    if not auth.is_admin() and auth.get_current_role() == 'volunteer':
        print("\n--- Testing Event Creation (as Volunteer) ---")
        event_created = create_event(
            'Unauthorized Event',
            datetime.date(2024, 11, 15),
            '10:00 AM',
            'Secret Location',
            50
        )
        if not event_created:
            print("Test passed: Volunteer was correctly prevented from creating an event.")
        else:
            print("Test failed: Volunteer was able to create an event.")
    auth.logout()


    # --- Test Case 3: Fetch all events ---
    print("\n--- Testing Fetching All Events ---")
    all_events = get_all_events()
    if all_events:
        print("Successfully fetched events:")
        for event in all_events:
            print(event)
    else:
        print("No events found or an error occurred. If you just created an event, there might be an issue.")

