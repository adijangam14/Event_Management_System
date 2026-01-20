import tkinter as tk
from tkinter import messagebox, ttk
from . import auth, events, registrations, attendance, reports, email_utils, students
import datetime

class EventSystemUI(tk.Tk):
    """
    Main application window that manages different frames (screens).
    """
    def __init__(self):
        super().__init__()

        # --- Database Pool Management ---
        # Initialize the connection pool at the start of the application
        try:
            db.init_pool()
        except Exception as e:
            # If the pool fails, the app can't run. Show an error and exit.
            messagebox.showerror("Fatal Error", f"Failed to connect to the database: {e}\nThe application will now close.")
            self.destroy()
            return

        # Register the cleanup function to be called when the window is closed
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # --- End Pool Management ---

        self.title("Event Registration and Attendance System")
        self.geometry("800x600")

        # Container for all frames
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.current_user = None  # To hold the logged-in user's data
        self.show_login_screen()

    def on_closing(self):
        """
        Handles the window closing event to ensure the connection pool is closed.
        """
        print("Closing application and connection pool.")
        db.close_pool()
        self.destroy()

    def show_frame(self, FrameClass):
        """Destroys the current frame and shows the new one."""
        for widget in self.container.winfo_children():
            widget.destroy()
        # Pass the current_user to every frame
        frame = FrameClass(self.container, self, user=self.current_user)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_login_screen(self):
        self.current_user = None # Clear user on logout
        self.show_frame(LoginScreen)

    def show_dashboard(self, user_data):
        """Shows the dashboard after a successful login."""
        self.current_user = user_data
        self.show_frame(DashboardScreen)

class LoginScreen(tk.Frame):
    """
    The login screen for users to enter their credentials.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Login", font=("Arial", 16)).pack(pady=20)

        tk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = tk.Entry(self)
        self.username_entry.pack(pady=5)

        tk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        # Set focus to username entry
        self.username_entry.focus_set()

        login_button = tk.Button(self, text="Login", command=self.handle_login)
        login_button.pack(pady=20)

        self.message_label = tk.Label(self, text="", fg="red")
        self.message_label.pack(pady=5)
        
        # Allow pressing Enter to log in
        self.controller.bind('<Return>', lambda event: self.handle_login())

    def handle_login(self):
        """
        Handles the login button click event.
        Authenticates the user and switches to the dashboard on success.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.message_label.config(text="Username and password are required.")
            return

        user_data = auth.login(username, password)

        if user_data:
            # Unbind the Enter key event from login screen
            self.controller.unbind('<Return>')
            self.controller.show_dashboard(user_data)
        else:
            self.message_label.config(text="Invalid username or password.")

class DashboardScreen(tk.Frame):
    """
    The main dashboard shown after a successful login.
    This will contain navigation to other parts of the application.
    """
    def __init__(self, parent, controller, user):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        if not self.user:
            # If for some reason the user is not set, go back to login
            messagebox.showerror("Error", "No user data found. Please log in again.")
            controller.show_login_screen()
            return

        tk.Label(self, text=f"Welcome, {self.user['username']}!", font=("Arial", 18)).pack(pady=20)
        tk.Label(self, text=f"Your Role: {self.user['role'].capitalize()}", font=("Arial", 12)).pack(pady=10)

        # --- Navigation Buttons ---
        # These buttons will lead to different functionalities.
        # We will implement the frames for these later.

        if self.user['role'] == 'admin':
            btn_event = tk.Button(self, text="Manage Events", command=lambda: controller.show_frame(EventManagementScreen))
            btn_event.pack(pady=10)

            btn_register = tk.Button(self, text="Register Students", command=lambda: controller.show_frame(RegistrationScreen))
            btn_register.pack(pady=10)

            btn_students = tk.Button(self, text="Manage Students", command=lambda: controller.show_frame(StudentManagementScreen))
            btn_students.pack(pady=10)

            btn_email = tk.Button(self, text="Send Event Notifications", command=lambda: controller.show_frame(EmailNotificationScreen))
            btn_email.pack(pady=10)


        # Both admins and volunteers can mark attendance and view reports
        btn_attend = tk.Button(self, text="Mark Attendance", command=lambda: controller.show_frame(AttendanceScreen))
        btn_attend.pack(pady=10)
        
        btn_reports = tk.Button(self, text="View Reports", command=lambda: controller.show_frame(ReportsScreen))
        btn_reports.pack(pady=10)

        # --- Logout Button ---
        logout_button = tk.Button(self, text="Logout", command=self.handle_logout)
        logout_button.pack(pady=40)

    def handle_logout(self):
        self.controller.show_login_screen()

class StudentManagementScreen(tk.Frame):
    """
    Screen for creating and viewing students.
    Accessible only to admin users.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        # --- Title ---
        tk.Label(self, text="Student Management", font=("Arial", 16)).pack(pady=10, padx=10)

        # --- Create Student Form ---
        form_frame = tk.LabelFrame(self, text="Add New Student", padx=10, pady=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky="w", pady=2)
        self.student_id_entry = tk.Entry(form_frame, width=40)
        self.student_id_entry.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=2)
        self.email_entry = tk.Entry(form_frame)
        self.email_entry.grid(row=2, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Course:").grid(row=3, column=0, sticky="w", pady=2)
        self.course_entry = tk.Entry(form_frame)
        self.course_entry.grid(row=3, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Year:").grid(row=4, column=0, sticky="w", pady=2)
        self.year_entry = tk.Entry(form_frame)
        self.year_entry.grid(row=4, column=1, sticky="ew", pady=2)
        
        create_button = tk.Button(form_frame, text="Add Student", command=self.handle_add_student)
        create_button.grid(row=5, column=0, columnspan=2, pady=10)

        # --- Student List ---
        list_frame = tk.LabelFrame(self, text="All Students", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Email", "Course", "Year"), show='headings')
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Course", text="Course")
        self.tree.heading("Year", text="Year")

        self.tree.column("ID", width=100)
        self.tree.column("Name", width=150)
        self.tree.column("Email", width=200)
        self.tree.column("Course", width=100)
        self.tree.column("Year", width=50)

        self.tree.pack(fill="both", expand=True, side="left")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        refresh_button = tk.Button(self, text="Refresh List", command=self.populate_students_list)
        refresh_button.pack(pady=5)
        
        back_button = tk.Button(self, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(pady=10)

        self.populate_students_list()

    def handle_add_student(self):
        """
        Gathers data from the form and calls the backend function to create a student.
        """
        student_id = self.student_id_entry.get()
        name = self.name_entry.get()
        email = self.email_entry.get()
        course = self.course_entry.get()
        year_str = self.year_entry.get()

        # The validation is now handled in the students.py file.
        result = students.add_student(student_id, name, email, course, year_str)
        
        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.clear_form()
            self.populate_students_list()
        else:
            messagebox.showerror("Error", result)

    def populate_students_list(self):
        """
        Fetches all students from the database and populates the treeview.
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch and insert new items
        all_students = students.get_all_students()
        for student in all_students:
            self.tree.insert("", "end", values=student)

    def clear_form(self):
        """Clears the entry fields after successful submission."""
        self.student_id_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.course_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')

# --- Placeholder Frames for other screens ---
# We will implement these properly in the next steps.

class EventManagementScreen(tk.Frame):
    """
    Screen for creating and viewing events.
    Accessible only to admin users.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        # --- Title ---
        tk.Label(self, text="Event Management", font=("Arial", 16)).pack(pady=10, padx=10)

        # --- Create Event Form ---
        form_frame = tk.LabelFrame(self, text="Create New Event", padx=10, pady=10)
        form_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(form_frame, text="Event Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.event_name_entry = tk.Entry(form_frame, width=40)
        self.event_name_entry.grid(row=0, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=2)
        self.event_date_entry = tk.Entry(form_frame)
        self.event_date_entry.grid(row=1, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Time (HH:MM AM/PM):").grid(row=2, column=0, sticky="w", pady=2)
        self.event_time_entry = tk.Entry(form_frame)
        self.event_time_entry.grid(row=2, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Venue:").grid(row=3, column=0, sticky="w", pady=2)
        self.venue_entry = tk.Entry(form_frame)
        self.venue_entry.grid(row=3, column=1, sticky="ew", pady=2)

        tk.Label(form_frame, text="Total Slots:").grid(row=4, column=0, sticky="w", pady=2)
        self.total_slots_entry = tk.Entry(form_frame)
        self.total_slots_entry.grid(row=4, column=1, sticky="ew", pady=2)
        
        create_button = tk.Button(form_frame, text="Create Event", command=self.handle_create_event)
        create_button.grid(row=5, column=0, columnspan=2, pady=10)

        # --- Event List ---
        list_frame = tk.LabelFrame(self, text="All Events", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Date", "Time", "Venue", "Slots"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Event Name")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Venue", text="Venue")
        self.tree.heading("Slots", text="Total Slots")

        self.tree.column("ID", width=50)
        self.tree.column("Name", width=200)
        self.tree.column("Date", width=100)
        self.tree.column("Time", width=80)
        self.tree.column("Venue", width=150)
        self.tree.column("Slots", width=80)

        self.tree.pack(fill="both", expand=True, side="left")
        
        # Add a scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        refresh_button = tk.Button(self, text="Refresh List", command=self.populate_events_list)
        refresh_button.pack(pady=5)
        
        back_button = tk.Button(self, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(pady=10)

        self.populate_events_list()

    def handle_create_event(self):
        """
        Gathers data from the form and calls the backend function to create an event.
        """
        name = self.event_name_entry.get()
        date_str = self.event_date_entry.get()
        time_str = self.event_time_entry.get()
        venue = self.venue_entry.get()
        slots_str = self.total_slots_entry.get()

        try:
            event_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
            return

        result = events.create_event(name, event_date, time_str, venue, slots_str)
        
        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.clear_form()
            self.populate_events_list()
        else:
            messagebox.showerror("Error", result)

    def populate_events_list(self):
        """
        Fetches all events from the database and populates the treeview.
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Fetch and insert new items
        all_events = events.get_all_events()
        for event in all_events:
            # Format date for display
            event_id, name, date, time, venue, slots = event
            formatted_date = date.strftime("%Y-%m-%d")
            self.tree.insert("", "end", values=(event_id, name, formatted_date, time, venue, slots))

    def clear_form(self):
        """Clears the entry fields after successful submission."""
        self.event_name_entry.delete(0, 'end')
        self.event_date_entry.delete(0, 'end')
        self.event_time_entry.delete(0, 'end')
        self.venue_entry.delete(0, 'end')
        self.total_slots_entry.delete(0, 'end')


class EmailNotificationScreen(tk.Frame):
    """
    Screen for composing and sending email notifications to registered students of an event.
    Accessible only to admin users.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()
        self.event_map = {} # To store event name to ID mapping

        tk.Label(self, text="Send Event Notifications", font=("Arial", 16)).pack(pady=10, padx=10)

        # --- Event Selection ---
        event_frame = tk.LabelFrame(self, text="Select Event", padx=10, pady=10)
        event_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40)
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        # --- Custom Message ---
        message_frame = tk.LabelFrame(self, text="Custom Message (Optional)", padx=10, pady=10)
        message_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.message_text = tk.Text(message_frame, height=10, width=70)
        self.message_text.pack(pady=5, padx=5, fill="both", expand=True)
        
        # --- Action Buttons ---
        action_frame = tk.Frame(self)
        action_frame.pack(pady=20)

        send_button = tk.Button(action_frame, text="Send Notifications", command=self.handle_send_emails)
        send_button.pack(side="left", padx=10)

        # New: Send Test Email Button
        send_test_button = tk.Button(action_frame, text="Send Test Email", command=self.handle_send_test_email)
        send_test_button.pack(side="left", padx=10)
        
        back_button = tk.Button(action_frame, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(side="left", padx=10)

    def populate_event_dropdown(self):
        """Fetches events and populates the dropdown menu."""
        all_events = events.get_all_events()
        # We want to display "ID: Name" but the value should just be the ID.
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def handle_event_selection(self, event_arg): # Renamed event to event_arg to avoid conflict
        """Called when an event is selected from the dropdown."""
        # This can be used to update a preview, or just ensure a valid selection
        pass

    def _email_completion_callback(self, results):
        """Callback function executed after emails are sent in background."""
        success_count = results.get('success_count', 0)
        fail_count = results.get('fail_count', 0)
        messagebox.showinfo("Email Sending Complete", 
                            f"Email sending process finished:\n"
                            f"Successfully sent: {success_count}\n"
                            f"Failed to send: {fail_count}")

    def handle_send_emails(self):
        """Handles the sending of emails to registered students."""
        selection = self.selected_event_id.get()
        if not selection:
            messagebox.showerror("Error", "Please select an event.")
            return

        event_id = self.event_map.get(selection)
        if not event_id:
            messagebox.showerror("Error", "Invalid event selected.")
            return

        # 1. Retrieve Event Details
        event_details = events.get_event_details(event_id)
        if not event_details:
            messagebox.showerror("Error", "Could not retrieve event details.")
            return
        
        # event_details tuple: (event_id, event_name, event_date, event_time, venue, total_slots)
        _, event_name, event_date, event_time, venue, _ = event_details
        
        # 2. Get registered students (recipients)
        registered_students_data = registrations.get_registered_students(event_id)
        if not registered_students_data:
            messagebox.showwarning("No Recipients", "No students are registered for this event.")
            return

        recipients = [student[2] for student in registered_students_data if student[2]] # student[2] is email
        if not recipients:
            messagebox.showwarning("No Recipients", "No valid email addresses found for registered students.")
            return

        # 3. Construct email body
        custom_message = self.message_text.get("1.0", tk.END).strip()
        email_body = email_utils.create_event_notification_email_body(
            event_name,
            event_date.strftime("%Y-%m-%d"),
            event_time,
            venue,
            custom_message
        )
        
        email_subject = f"Notification: {event_name}"

        # Confirm before sending to all
        confirm = messagebox.askyesno("Confirm Send", 
                                      f"Are you sure you want to send notifications to {len(recipients)} students for '{event_name}'?")
        if not confirm:
            return

        # 4. Initiate asynchronous email sending
        messagebox.showinfo("Sending Emails", "Emails are being sent in the background. You will be notified upon completion.")
        # Ensure that self.controller is correctly passed if it has methods to update the UI from another thread safely.
        # For simple messageboxes, Tkinter handles threading reasonably well.
        email_utils.send_emails_in_background(recipients, email_subject, email_body, self._email_completion_callback)

    def handle_send_test_email(self):
        """Handles sending a test email to the current admin user."""
        current_user_email = email_utils.EMAIL_CONFIG.get("sender_email") # Use sender email as test recipient
        if not current_user_email or current_user_email == "your_email@example.com":
            messagebox.showerror("Configuration Error", "Please configure 'sender_email' in config.py for testing.")
            return

        selection = self.selected_event_id.get()
        if not selection:
            messagebox.showerror("Error", "Please select an event to send a test email for.")
            return

        event_id = self.event_map.get(selection)
        if not event_id:
            messagebox.showerror("Error", "Invalid event selected.")
            return

        event_details = events.get_event_details(event_id)
        if not event_details:
            messagebox.showerror("Error", "Could not retrieve event details for test email.")
            return
        
        _, event_name, event_date, event_time, venue, _ = event_details
        custom_message = self.message_text.get("1.0", tk.END).strip()
        email_body = email_utils.create_event_notification_email_body(
            event_name,
            event_date.strftime("%Y-%m-%d"),
            event_time, 
            venue,
            f"THIS IS A TEST EMAIL.\n\n{custom_message}"
        )
        email_subject = f"TEST: Notification: {event_name}"

        messagebox.showinfo("Sending Test Email", "Sending a test email in the background.")
        # Using a lambda to pass the test recipient as a list for send_emails_in_background
        email_utils.send_emails_in_background([current_user_email], email_subject, email_body, self._email_completion_callback)



class RegistrationScreen(tk.Frame):
    """
    Screen for registering students for an event.
    Accessible only to admin users.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()

        tk.Label(self, text="Student Registration", font=("Arial", 16)).pack(pady=10)

        # --- Event Selection ---
        event_frame = tk.LabelFrame(self, text="Select Event", padx=10, pady=10)
        event_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40)
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        # --- Registration Form ---
        reg_form_frame = tk.LabelFrame(self, text="Register a Student", padx=10, pady=10)
        reg_form_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(reg_form_frame, text="Student ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.student_id_entry = tk.Entry(reg_form_frame, width=30)
        self.student_id_entry.grid(row=0, column=1, sticky="w", pady=5)

        register_button = tk.Button(reg_form_frame, text="Register Student", command=self.handle_register)
        register_button.grid(row=1, column=0, columnspan=2, pady=10)

        # --- Registered Students List ---
        list_frame = tk.LabelFrame(self, text="Registered Students for Selected Event", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Reg Date"), show='headings')
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Reg Date", text="Registration Date")
        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        back_button = tk.Button(self, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(pady=20)

    def populate_event_dropdown(self):
        """Fetches events and populates the dropdown menu."""
        all_events = events.get_all_events()
        # We want to display "ID: Name" but the value should just be the ID.
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def handle_event_selection(self, event_arg):
        """Updates the registered students list when an event is selected."""
        self.populate_registered_students()

    def populate_registered_students(self):
        """Populates the treeview with students registered for the selected event."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        selection = self.selected_event_id.get()
        if not selection:
            return
            
        event_id = self.event_map.get(selection)
        if event_id:
            registered_students = registrations.get_registered_students(event_id)
            for student in registered_students:
                student_id, name, email, reg_date = student
                formatted_date = reg_date.strftime("%Y-%m-%d %H:%M")
                self.tree.insert("", "end", values=(student_id, name, formatted_date))

    def handle_register(self):
        """Handles the registration of a student."""
        student_id = self.student_id_entry.get()
        selection = self.selected_event_id.get()

        if not student_id or not selection:
            messagebox.showerror("Input Error", "Please select an event and enter a student ID.")
            return
        
        event_id = self.event_map.get(selection)
        if not event_id:
            messagebox.showerror("Input Error", "Invalid event selected.")
            return

        result = registrations.register_student_for_event(event_id, student_id)
        
        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.student_id_entry.delete(0, 'end')
            self.populate_registered_students()
        elif "Info" in result:
            messagebox.showinfo("Info", result)
        else:
            messagebox.showerror("Error", result)


class AttendanceScreen(tk.Frame):
    """
    Screen for marking student attendance for an event.
    Accessible to both admins and volunteers.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()

        tk.Label(self, text="Mark Attendance", font=("Arial", 16)).pack(pady=10)

        # --- Event Selection ---
        event_frame = tk.LabelFrame(self, text="Select Event", padx=10, pady=10)
        event_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40)
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        # --- Attendance List and Actions ---
        list_frame = tk.LabelFrame(self, text="Mark Student Attendance", padx=10, pady=10)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Status"), show='headings')
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Status", text="Attended (Y/N)")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # --- Action Buttons ---
        action_frame = tk.Frame(self)
        action_frame.pack(pady=10)

        mark_yes_button = tk.Button(action_frame, text="Mark as Attended (Y)", command=lambda: self.handle_mark_attendance('Y'))
        mark_yes_button.pack(side="left", padx=10)

        mark_no_button = tk.Button(action_frame, text="Mark as Not Attended (N)", command=lambda: self.handle_mark_attendance('N'))
        mark_no_button.pack(side="left", padx=10)
        
        back_button = tk.Button(self, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(pady=20)

    def populate_event_dropdown(self):
        """Fetches events and populates the dropdown menu."""
        all_events = events.get_all_events()
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def handle_event_selection(self, event_arg):
        self.populate_attendance_list()

    def populate_attendance_list(self):
        """Populates the treeview with attendance data for the selected event."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        selection = self.selected_event_id.get()
        if not selection:
            return
            
        event_id = self.event_map.get(selection)
        if event_id:
            attendance_list = attendance.get_event_attendance(event_id)
            for student in attendance_list:
                self.tree.insert("", "end", values=student)

    def handle_mark_attendance(self, status):
        """
        Marks the selected student's attendance with the given status.
        """
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a student from the list.")
            return

        student_details = self.tree.item(selected_item)
        student_id = student_details['values'][0]
        
        selection = self.selected_event_id.get()
        event_id = self.event_map.get(selection)

        if not event_id:
            messagebox.showerror("Error", "No event selected.")
            return

        result = attendance.mark_attendance(event_id, student_id, status)

        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.populate_attendance_list()  # Refresh the list
        else:
            messagebox.showerror("Error", result)


class ReportsScreen(tk.Frame):
    """
    Screen for viewing event statistics and exporting attendance reports.
    Accessible to both admins and volunteers.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()

        tk.Label(self, text="Reports and Export", font=("Arial", 16)).pack(pady=10)

        # --- Event Selection ---
        event_frame = tk.LabelFrame(self, text="Select Event", padx=10, pady=10)
        event_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40)
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        # --- Statistics Display ---
        stats_frame = tk.LabelFrame(self, text="Event Statistics", padx=10, pady=10)
        stats_frame.pack(pady=10, padx=10, fill="x")

        self.registered_label = tk.Label(stats_frame, text="Total Registered: -", font=("Arial", 12))
        self.registered_label.pack(anchor="w", pady=2)
        
        self.attended_label = tk.Label(stats_frame, text="Total Attended: -", font=("Arial", 12))
        self.attended_label.pack(anchor="w", pady=2)

        self.percentage_label = tk.Label(stats_frame, text="Attendance Percentage: -", font=("Arial", 12))
        self.percentage_label.pack(anchor="w", pady=2)

        # --- Actions ---
        action_frame = tk.Frame(self)
        action_frame.pack(pady=20)

        export_button = tk.Button(action_frame, text="Export Attendance to CSV", command=self.handle_export_csv)
        export_button.pack(side="left", padx=10)
        
        refresh_button = tk.Button(action_frame, text="Refresh Stats", command=self.display_statistics)
        refresh_button.pack(side="left", padx=10)
