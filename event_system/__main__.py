# main.py
# Main entry point for the Event Registration and Attendance System.

import argparse
from .ui import EventSystemUI
from .web_ui import app as web_app
from . import db

def main():
    """
    Initializes and runs the selected application interface.
    """
    parser = argparse.ArgumentParser(description="Event Registration and Attendance System")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--ui", action="store_true", help="Run the Tkinter desktop UI")
    group.add_argument("--web", action="store_true", help="Run the Flask web UI")

    args = parser.parse_args()

    if args.web:
        print("Starting the Event Management System Web UI...")
        # Note: For production, use a proper WSGI server instead of app.run()
        web_app.run(debug=True)
    else:
        print("Starting the Event Management System Desktop UI...")
        app = EventSystemUI()
        app.mainloop()

if __name__ == "__main__":
    main()
