# reports.py
# Generates statistics and handles CSV exports for event attendance.

import csv
import os
from . import db

def get_event_statistics(event_id):
    """
    Calculates attendance statistics for a specific event.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if event exists
                cursor.execute("SELECT event_name FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
                event_name_tuple = cursor.fetchone()
                if not event_name_tuple:
                    print(f"No event found with ID: {event_id}")
                    return None
                
                event_name = event_name_tuple[0]

                # Get total registered students
                cursor.execute("SELECT COUNT(*) FROM REGISTRATIONS WHERE event_id = :event_id", {'event_id': event_id})
                total_registered = cursor.fetchone()[0]

                # Get total attended students
                cursor.execute(
                    "SELECT COUNT(*) FROM ATTENDANCE WHERE event_id = :event_id AND attended = 'Y'",
                    {'event_id': event_id}
                )
                total_attended = cursor.fetchone()[0]

                # Calculate attendance percentage
                percentage = (total_attended / total_registered) * 100 if total_registered > 0 else 0

                return {
                    'event_name': event_name,
                    'registered': total_registered,
                    'attended': total_attended,
                    'percentage': round(percentage, 2)
                }
    except Exception as e:
        print(f"Error calculating statistics for event {event_id}: {e}")
        return None

def generate_attendance_chart(event_id):
    """
    Generates a bar chart for event attendance and saves it to a temporary file.
    """
    stats = get_event_statistics(event_id)
    if not stats or stats['registered'] == 0:
        return None

    try:
        import matplotlib
        matplotlib.use('Agg') # Use non-interactive backend
        import matplotlib.pyplot as plt
        import tempfile

        labels = ['Registered', 'Attended']
        values = [stats['registered'], stats['attended']]

        fig, ax = plt.subplots()
        bars = ax.bar(labels, values, color=['skyblue', 'lightgreen'])
        
        ax.set_ylabel('Number of Students')
        ax.set_title(f'Attendance for: {stats["event_name"]}')
        ax.set_ylim(0, max(values) * 1.1) # Add some space at the top

        # Add number labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom')

        # Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir='./event_system/static') as tmpfile:
            chart_path = tmpfile.name
            plt.savefig(chart_path)
            plt.close(fig) # Close the figure to free up memory
        
        # Return a web-accessible path
        return os.path.join('static', os.path.basename(chart_path))
        
    except Exception as e:
        print(f"Error generating attendance chart: {e}")
        return None

def sanitize_for_csv(value):
    """
    Sanitizes a value to prevent CSV injection.
    If the value starts with '=', '+', '-', or '@', it prepends a single quote.
    """
    if isinstance(value, str) and value.startswith(('=', '+', '-', '@')):
        return "'" + value
    return value

def export_attendance_to_csv(event_id, full_file_path):
    """
    Exports the attendance list for an event to a CSV file.
    Expects `full_file_path` to be the complete path including filename.
    """
    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if event exists
                cursor.execute("SELECT event_name FROM EVENTS WHERE event_id = :event_id", {'event_id': event_id})
                if not cursor.fetchone():
                    return "Error: Event not found."

                # Fetch the attendance data
                query = """
                SELECT s.student_id, s.name, NVL(a.attended, 'N') AS attendance_status
                FROM REGISTRATIONS r
                JOIN STUDENTS s ON r.student_id = s.student_id
                LEFT JOIN ATTENDANCE a ON r.event_id = a.event_id AND r.student_id = a.student_id
                WHERE r.event_id = :event_id
                ORDER BY s.name
                """
                cursor.execute(query, {'event_id': event_id})
                attendance_data = cursor.fetchall()
                
                if not attendance_data:
                    return "Info: No registrations found for this event. Nothing to export."

        # Sanitize data and write to the specified full_file_path
        with open(full_file_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Student ID', 'Student Name', 'Attendance Status (Y/N)'])
            # Sanitize each cell before writing
            sanitized_data = [[sanitize_for_csv(cell) for cell in row] for row in attendance_data]
            csv_writer.writerows(sanitized_data)
        
        return f"Success: Attendance data exported to {os.path.abspath(full_file_path)}"

    except Exception as e:
        print(f"Error exporting attendance to CSV for event {event_id}: {e}")
        return f"Error: Failed to export attendance data. Reason: {e}"
