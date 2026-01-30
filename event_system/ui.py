import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from ttkthemes import ThemedTk
from . import auth, events, registrations, attendance, reports, email_utils, students, db, config
import datetime
import os

class EventSystemUI(ThemedTk):
    """
    Main application window that manages different frames (screens).
    """
    def __init__(self):
        super().__init__(theme=config.DESKTOP_THEME)

        # --- Database Pool Management ---
        try:
            db.init_pool()
        except Exception as e:
            messagebox.showerror("Fatal Error", f"Failed to connect to the database: {e}\nThe application will now close.")
            self.destroy()
            return

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # --- End Pool Management ---

        self.title("Event Registration and Attendance System")
        self.geometry("900x700")

        # --- Style Configuration ---
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 13))
        self.style.configure("TButton", font=("Helvetica", 13), padding=10)
        self.style.configure("TEntry", font=("Helvetica", 13), padding=5)
        self.style.configure("TLabelFrame.Label", font=("Helvetica", 15, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 19, "bold"))

        # Container for all frames
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.current_user = None
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
        frame = FrameClass(self.container, self, user=self.current_user)
        frame.grid(row=0, column=0, sticky="nsew")

    def show_login_screen(self):
        self.current_user = None
        self.show_frame(LoginScreen)

    def show_dashboard(self, user_data):
        """Shows the dashboard after a successful login."""
        self.current_user = user_data
        self.show_frame(DashboardScreen)
    def show_volunteer_registration_screen(self):
        self.show_frame(VolunteerRegistrationScreen)

class LoginScreen(ttk.Frame):
    """
    The login screen for users to enter their credentials.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller

        # Main frame to center the content
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.grid(row=0, column=0)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(form_frame, text="Login", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(form_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        self.username_entry.focus_set()

        login_button = ttk.Button(form_frame, text="Login", command=self.handle_login, style="Accent.TButton")
        login_button.grid(row=3, column=0, columnspan=2, pady=20)

        register_button = ttk.Button(form_frame, text="Register as Volunteer", command=self.controller.show_volunteer_registration_screen)
        register_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.message_label = ttk.Label(form_frame, text="", foreground="red")
        self.message_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        self.controller.bind('<Return>', lambda event: self.handle_login())

    def handle_login(self):
        """
        Handles the login button click event.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.message_label.config(text="Username and password are required.")
            return

        user_data = auth.login(username, password)

        if user_data:
            self.controller.unbind('<Return>')
            self.controller.show_dashboard(user_data)
        else:
            self.message_label.config(text="Invalid username or password.")

class VolunteerRegistrationScreen(ttk.Frame):
    """
    Screen for volunteers to register for an account.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller

        # Main frame to center the content
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Form frame
        form_frame = ttk.Frame(main_frame)
        form_frame.grid(row=0, column=0)

        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(form_frame, text="Volunteer Registration", style="Header.TLabel").grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(form_frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.username_entry = ttk.Entry(form_frame, width=30)
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)

        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.password_entry = ttk.Entry(form_frame, show="*", width=30)
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        self.username_entry.focus_set()

        register_button = ttk.Button(form_frame, text="Register", command=self.handle_registration, style="Accent.TButton")
        register_button.grid(row=3, column=0, columnspan=2, pady=20)

        back_button = ttk.Button(form_frame, text="Back to Login", command=self.controller.show_login_screen)
        back_button.grid(row=4, column=0, columnspan=2, pady=10)

        self.message_label = ttk.Label(form_frame, text="", foreground="red")
        self.message_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        self.controller.bind('<Return>', lambda event: self.handle_registration())

    def handle_registration(self):
        """
        Handles the registration button click event.
        """
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            self.message_label.config(text="Username and password are required.")
            return

        result = auth.create_web_user(username, password)

        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.controller.show_login_screen()
        else:
            self.message_label.config(text=result)

class DashboardScreen(ttk.Frame):
    """
    The main dashboard shown after a successful login.
    """
    def __init__(self, parent, controller, user):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        if not self.user:
            messagebox.showerror("Error", "No user data found. Please log in again.")
            controller.show_login_screen()
            return

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Welcome labels frame
        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, pady=(20, 10))

        ttk.Label(header_frame, text=f"Welcome, {self.user['username']}!", style="Header.TLabel").pack()
        ttk.Label(header_frame, text=f"Your Role: {self.user['role'].capitalize()}", font=("Arial", 14)).pack()

        # Button frame
        button_frame = ttk.Frame(self)
        button_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        
        button_frame.grid_columnconfigure((0, 1), weight=1)

        row = 0
        if self.user['role'] == 'admin':
            ttk.Button(button_frame, text="Manage Events", command=lambda: controller.show_frame(EventManagementScreen)).grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            ttk.Button(button_frame, text="Register Students", command=lambda: controller.show_frame(RegistrationScreen)).grid(row=row, column=1, padx=10, pady=10, sticky="nsew")
            row += 1
            ttk.Button(button_frame, text="Manage Students", command=lambda: controller.show_frame(StudentManagementScreen)).grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
            ttk.Button(button_frame, text="Send Event Notifications", command=lambda: controller.show_frame(EmailNotificationScreen)).grid(row=row, column=1, padx=10, pady=10, sticky="nsew")
            row += 1

        # Shared buttons
        ttk.Button(button_frame, text="Mark Attendance", command=lambda: controller.show_frame(AttendanceScreen)).grid(row=row, column=0, padx=10, pady=10, sticky="nsew")
        ttk.Button(button_frame, text="View Reports", command=lambda: controller.show_frame(ReportsScreen)).grid(row=row, column=1, padx=10, pady=10, sticky="nsew")
        
        # Logout button frame
        logout_frame = ttk.Frame(self)
        logout_frame.grid(row=2, column=0, pady=(10, 20))

        logout_button = ttk.Button(logout_frame, text="Logout", command=self.handle_logout)
        logout_button.pack()

    def handle_logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.controller.show_login_screen()

class StudentManagementScreen(ttk.Frame):
    """
    Screen for creating and viewing students.
    """
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        ttk.Label(self, text="Student Management", style="Header.TLabel").pack(pady=10, padx=10)

        form_frame = ttk.LabelFrame(self, text="Add New Student")
        form_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(form_frame, text="Student ID:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.student_id_entry = ttk.Entry(form_frame, width=40)
        self.student_id_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Course:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.course_entry = ttk.Entry(form_frame)
        self.course_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Year:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.year_entry = ttk.Entry(form_frame)
        self.year_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        
        create_button = ttk.Button(form_frame, text="Add Student", command=self.handle_add_student, style="Accent.TButton")
        create_button.grid(row=5, column=0, columnspan=2, pady=10)

        list_frame = ttk.LabelFrame(self, text="All Students")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill="x", padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill="x", expand=True, side="left")
        self.search_entry.bind("<KeyRelease>", self.filter_students)

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
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        refresh_button = ttk.Button(button_frame, text="Refresh List", command=self.populate_students_list)
        refresh_button.grid(row=0, column=0, padx=5)
        
        
        back_button = ttk.Button(button_frame, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.grid(row=0, column=1, padx=5)

        edit_button = ttk.Button(button_frame, text="Edit Student", command=self.handle_edit_student)
        edit_button.grid(row=0, column=2, padx=5)

        delete_button = ttk.Button(button_frame, text="Delete Student", command=self.handle_delete_student)
        delete_button.grid(row=0, column=3, padx=5)

        self.populate_students_list()

    def handle_add_student(self):
        student_id = self.student_id_entry.get()
        name = self.name_entry.get()
        email = self.email_entry.get()
        course = self.course_entry.get()
        year_str = self.year_entry.get()

        if not year_str.isdigit():
            messagebox.showerror("Input Error", "Year must be a number.")
            return
        
        year = int(year_str)

        result = students.add_student(self.user['role'], student_id, name, email, course, year)
        
        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.clear_form()
            self.populate_students_list()
        else:
            messagebox.showerror("Error", result)

    def handle_edit_student(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a student to edit.")
            return

        student_details = self.tree.item(selected_item)
        student_id = student_details['values'][0]
        
        edit_window = EditStudentWindow(self, self.controller, self.user, student_id)
        edit_window.grab_set()

    def handle_delete_student(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a student to delete.")
            return

        student_details = self.tree.item(selected_item)
        student_id = student_details['values'][0]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student {student_id}?"):
            result = students.delete_student(self.user['role'], student_id)
            if "Success" in result:
                messagebox.showinfo("Success", result)
                self.populate_students_list()
            else:
                messagebox.showerror("Error", result)

    def populate_students_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.all_students = students.get_all_students()
        for student in self.all_students:
            self.tree.insert("", "end", values=student)

    def filter_students(self, event):
        filter_term = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())

        for student in self.all_students:
            if filter_term in student[1].lower():
                self.tree.insert("", "end", values=student)

    def clear_form(self):
        self.student_id_entry.delete(0, 'end')
        self.name_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.course_entry.delete(0, 'end')
        self.year_entry.delete(0, 'end')

class EditStudentWindow(tk.Toplevel):
    def __init__(self, parent, controller, user, student_id):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.user = user
        self.student_id = student_id

        self.title(f"Edit Student {student_id}")
        self.geometry("400x300")

        student_data = students.get_student_by_id(student_id)
        if not student_data:
            messagebox.showerror("Error", "Student not found.", parent=self)
            self.destroy()
            return

        form_frame = ttk.Frame(self, padding=10)
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        self.name_entry.insert(0, student_data[1])

        ttk.Label(form_frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=1, column=1, sticky="ew", pady=5)
        self.email_entry.insert(0, student_data[2])

        ttk.Label(form_frame, text="Course:").grid(row=2, column=0, sticky="w", pady=5)
        self.course_entry = ttk.Entry(form_frame)
        self.course_entry.grid(row=2, column=1, sticky="ew", pady=5)
        self.course_entry.insert(0, student_data[3])

        ttk.Label(form_frame, text="Year:").grid(row=3, column=0, sticky="w", pady=5)
        self.year_entry = ttk.Entry(form_frame)
        self.year_entry.grid(row=3, column=1, sticky="ew", pady=5)
        self.year_entry.insert(0, student_data[4])

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        update_button = ttk.Button(button_frame, text="Update", command=self.handle_update)
        update_button.pack(side="left", padx=5)

        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=5)

    def handle_update(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        course = self.course_entry.get()
        year_str = self.year_entry.get()

        if not year_str.isdigit():
            messagebox.showerror("Input Error", "Year must be a number.", parent=self)
            return
        
        year = int(year_str)

        result = students.update_student(self.user['role'], self.student_id, name, email, course, year)
        
        if "Success" in result:
            messagebox.showinfo("Success", result, parent=self)
            self.parent.populate_students_list()
            self.destroy()
        else:
            messagebox.showerror("Error", result, parent=self)



class EventManagementScreen(ttk.Frame):
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user

        ttk.Label(self, text="Event Management", style="Header.TLabel").pack(pady=10, padx=10)

        form_frame = ttk.LabelFrame(self, text="Create New Event")
        form_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(form_frame, text="Event Name:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.event_name_entry = ttk.Entry(form_frame, width=40)
        self.event_name_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.event_date_entry = ttk.Entry(form_frame)
        self.event_date_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Time (HH:MM AM/PM):").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.event_time_entry = ttk.Entry(form_frame)
        self.event_time_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Venue:").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.venue_entry = ttk.Entry(form_frame)
        self.venue_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=5)

        ttk.Label(form_frame, text="Total Slots:").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.total_slots_entry = ttk.Entry(form_frame)
        self.total_slots_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=5)
        
        create_button = ttk.Button(form_frame, text="Create Event", command=self.handle_create_event, style="Accent.TButton")
        create_button.grid(row=5, column=0, columnspan=2, pady=10)

        list_frame = ttk.LabelFrame(self, text="All Events")
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
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        refresh_button = ttk.Button(button_frame, text="Refresh List", command=self.populate_events_list)
        refresh_button.grid(row=0, column=0, padx=5)
        
        back_button = ttk.Button(button_frame, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.grid(row=0, column=1, padx=5)

        self.populate_events_list()

    def handle_create_event(self):
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

        try:
            datetime.datetime.strptime(time_str, "%I:%M %p")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid time format. Please use HH:MM AM/PM.")
            return

        if not slots_str.isdigit():
            messagebox.showerror("Input Error", "Total slots must be a number.")
            return
        
        slots = int(slots_str)

        result = events.create_event(self.user['role'], name, event_date, time_str, venue, slots)
        
        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.clear_form()
            self.populate_events_list()
        else:
            messagebox.showerror("Error", result)

    def populate_events_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        all_events = events.get_all_events()
        for event in all_events:
            event_id, name, date, time, venue, slots = event
            formatted_date = date.strftime("%Y-%m-%d")
            self.tree.insert("", "end", values=(event_id, name, formatted_date, time, venue, slots))

    def clear_form(self):
        self.event_name_entry.delete(0, 'end')
        self.event_date_entry.delete(0, 'end')
        self.event_time_entry.delete(0, 'end')
        self.venue_entry.delete(0, 'end')
        self.total_slots_entry.delete(0, 'end')


class EmailNotificationScreen(ttk.Frame):
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()
        self.event_map = {}

        ttk.Label(self, text="Send Event Notifications", style="Header.TLabel").pack(pady=10, padx=10)

        event_frame = ttk.LabelFrame(self, text="Select Event")
        event_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40, font=("Arial", 12))
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        message_frame = ttk.LabelFrame(self, text="Custom Message (Optional)")
        message_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.message_text = tk.Text(message_frame, height=10, width=70, font=("Arial", 12))
        self.message_text.pack(pady=5, padx=5, fill="both", expand=True)
        
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=20)

        send_button = ttk.Button(action_frame, text="Send Notifications", command=self.handle_send_emails, style="Accent.TButton")
        send_button.pack(side="left", padx=10)

        send_test_button = ttk.Button(action_frame, text="Send Test Email", command=self.handle_send_test_email)
        send_test_button.pack(side="left", padx=10)
        
        back_button = ttk.Button(action_frame, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(side="left", padx=10)

    def populate_event_dropdown(self):
        all_events = events.get_all_events()
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def handle_event_selection(self, event_arg):
        pass

    def _email_completion_callback(self, results):
        success_count = results.get('success_count', 0)
        fail_count = results.get('fail_count', 0)
        messagebox.showinfo("Email Sending Complete", 
                            f"Email sending process finished:\n"
                            f"Successfully sent: {success_count}\n"
                            f"Failed to send: {fail_count}")

    def handle_send_emails(self):
        selection = self.selected_event_id.get()
        if not selection:
            messagebox.showerror("Error", "Please select an event.")
            return

        event_id = self.event_map.get(selection)
        if not event_id:
            messagebox.showerror("Error", "Invalid event selected.")
            return

        event_details = events.get_event_details(event_id)
        if not event_details:
            messagebox.showerror("Error", "Could not retrieve event details.")
            return
        
        _, event_name, event_date, event_time, venue, _ = event_details
        
        registered_students_data = registrations.get_registered_students(event_id)
        if not registered_students_data:
            messagebox.showwarning("No Recipients", "No students are registered for this event.")
            return

        recipients = [student[2] for student in registered_students_data if student[2]]
        if not recipients:
            messagebox.showwarning("No Recipients", "No valid email addresses found for registered students.")
            return

        custom_message = self.message_text.get("1.0", tk.END).strip()
        email_body = email_utils.create_event_notification_email_body(
            event_name,
            event_date.strftime("%Y-%m-%d"),
            event_time,
            venue,
            custom_message
        )
        
        email_subject = f"Notification: {event_name}"

        confirm = messagebox.askyesno("Confirm Send", 
                                      f"Are you sure you want to send notifications to {len(recipients)} students for '{event_name}'?")
        if not confirm:
            return

        messagebox.showinfo("Sending Emails", "Emails are being sent in the background. You will be notified upon completion.")
        email_utils.send_emails_in_background(recipients, email_subject, email_body, self._email_completion_callback)

    def handle_send_test_email(self):
        current_user_email = email_utils.EMAIL_CONFIG.get("sender_email")
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
        email_utils.send_emails_in_background([current_user_email], email_subject, email_body, self._email_completion_callback)


class RegistrationScreen(ttk.Frame):
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()
        self.event_map = {}

        ttk.Label(self, text="Student Registration", style="Header.TLabel").pack(pady=10)

        event_frame = ttk.LabelFrame(self, text="Select Event")
        event_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40, font=("Arial", 12))
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        reg_form_frame = ttk.LabelFrame(self, text="Register a Student")
        reg_form_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(reg_form_frame, text="Student ID:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.student_id_entry = ttk.Entry(reg_form_frame, width=30)
        self.student_id_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        register_button = ttk.Button(reg_form_frame, text="Register Student", command=self.handle_register, style="Accent.TButton")
        register_button.grid(row=1, column=0, columnspan=2, pady=10)

        cancel_button = ttk.Button(reg_form_frame, text="Cancel Registration", command=self.handle_cancel_registration)
        cancel_button.grid(row=2, column=0, columnspan=2, pady=10)

        list_frame = ttk.LabelFrame(self, text="Registered Students for Selected Event")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill="x", expand=True, side="left")
        self.search_entry.bind("<KeyRelease>", self.filter_students)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Reg Date"), show='headings')
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Reg Date", text="Registration Date")
        self.tree.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        back_button = ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(pady=20)

    def populate_event_dropdown(self):
        all_events = events.get_all_events()
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def handle_event_selection(self, event_arg):
        self.populate_registered_students()

    def populate_registered_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selection = self.selected_event_id.get()
        if not selection:
            return
            
        event_id = self.event_map.get(selection)
        if event_id:
            self.students = registrations.get_registered_students(event_id)
            for student in self.students:
                student_id, name, email, reg_date = student
                formatted_date = reg_date.strftime("%Y-%m-%d %H:%M")
                self.tree.insert("", "end", values=(student_id, name, formatted_date))

    def filter_students(self, event):
        filter_term = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())

        for student in self.students:
            if filter_term in student[1].lower():
                student_id, name, email, reg_date = student
                formatted_date = reg_date.strftime("%Y-%m-%d %H:%M")
                self.tree.insert("", "end", values=(student_id, name, formatted_date))


    def handle_register(self):
        student_id = self.student_id_entry.get()
        selection = self.selected_event_id.get()

        if not student_id or not selection:
            messagebox.showerror("Input Error", "Please select an event and enter a student ID.")
            return
        
        event_id = self.event_map.get(selection)
        if not event_id:
            messagebox.showerror("Input Error", "Invalid event selected.")
            return

        result = registrations.register_student_for_event(self.user['role'], event_id, student_id)
        
        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.student_id_entry.delete(0, 'end')
            self.populate_registered_students()
        elif "Info" in result:
            messagebox.showinfo("Info", result)
        else:
            messagebox.showerror("Error", result)

    def handle_cancel_registration(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a student from the list to cancel their registration.")
            return

        student_details = self.tree.item(selected_item)
        student_id = student_details['values'][0]
        
        selection = self.selected_event_id.get()
        event_id = self.event_map.get(selection)

        if not event_id:
            messagebox.showerror("Error", "No event selected.")
            return

        result = registrations.cancel_registration(self.user['role'], event_id, student_id)

        if "Success" in result:
            messagebox.showinfo("Success", result)
            self.populate_registered_students()
        else:
            messagebox.showerror("Error", result)


class AttendanceScreen(ttk.Frame):
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()
        self.event_map = {}

        ttk.Label(self, text="Mark Attendance", style="Header.TLabel").pack(pady=10)

        event_frame = ttk.LabelFrame(self, text="Select Event")
        event_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40, font=("Arial", 12))
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        list_frame = ttk.LabelFrame(self, text="Mark Student Attendance")
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(fill="x", expand=True, side="left")
        self.search_entry.bind("<KeyRelease>", self.filter_students)

        self.tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Status"), show='headings')
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Student Name")
        self.tree.heading("Status", text="Attended (Y/N)")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=10)

        mark_yes_button = ttk.Button(action_frame, text="Mark as Attended (Y)", command=lambda: self.handle_mark_attendance('Y'), style="Accent.TButton")
        mark_yes_button.pack(side="left", padx=10)

        mark_no_button = ttk.Button(action_frame, text="Mark as Not Attended (N)", command=lambda: self.handle_mark_attendance('N'))
        mark_no_button.pack(side="left", padx=10)
        
        back_button = ttk.Button(self, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(pady=20)

    def populate_event_dropdown(self):
        all_events = events.get_all_events()
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def handle_event_selection(self, event_arg):
        self.populate_attendance_list()

    def populate_attendance_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selection = self.selected_event_id.get()
        if not selection:
            return
            
        event_id = self.event_map.get(selection)
        if event_id:
            self.students = attendance.get_event_attendance(event_id)
            for student in self.students:
                self.tree.insert("", "end", values=student)

    def filter_students(self, event):
        filter_term = self.search_entry.get().lower()
        self.tree.delete(*self.tree.get_children())

        for student in self.students:
            if filter_term in student[1].lower():
                self.tree.insert("", "end", values=student)

    def handle_mark_attendance(self, status):
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
            self.populate_attendance_list()
        else:
            messagebox.showerror("Error", result)


class ReportsScreen(ttk.Frame):
    def __init__(self, parent, controller, user=None):
        super().__init__(parent)
        self.controller = controller
        self.user = user
        self.selected_event_id = tk.StringVar()
        self.event_map = {}
        self.chart_window = None # To hold the chart window reference

        ttk.Label(self, text="Reports and Export", style="Header.TLabel").pack(pady=10)

        event_frame = ttk.LabelFrame(self, text="Select Event")
        event_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(event_frame, text="Choose Event:").pack(side="left", padx=5)
        self.event_menu = ttk.Combobox(event_frame, textvariable=self.selected_event_id, width=40, font=("Arial", 12))
        self.event_menu.pack(side="left", padx=5)
        self.event_menu.bind("<<ComboboxSelected>>", self.handle_event_selection)
        
        self.populate_event_dropdown()

        stats_frame = ttk.LabelFrame(self, text="Event Statistics")
        stats_frame.pack(pady=10, padx=10, fill="x")

        self.registered_label = ttk.Label(stats_frame, text="Total Registered: -")
        self.registered_label.pack(anchor="w", pady=5, padx=5)
        
        self.attended_label = ttk.Label(stats_frame, text="Total Attended: -")
        self.attended_label.pack(anchor="w", pady=5, padx=5)

        self.percentage_label = ttk.Label(stats_frame, text="Attendance Percentage: -")
        self.percentage_label.pack(anchor="w", pady=5, padx=5)

        action_frame = ttk.Frame(self)
        action_frame.pack(pady=20)

        view_chart_button = ttk.Button(action_frame, text="View Attendance Chart", command=self.handle_view_chart)
        view_chart_button.pack(side="left", padx=10)

        export_button = ttk.Button(action_frame, text="Export Attendance to CSV", command=self.handle_export_csv, style="Accent.TButton")
        export_button.pack(side="left", padx=10)
        
        refresh_button = ttk.Button(action_frame, text="Refresh Stats", command=self.display_statistics)
        refresh_button.pack(side="left", padx=10)
        
        back_button = ttk.Button(action_frame, text="Back to Dashboard", command=lambda: controller.show_dashboard(self.user))
        back_button.pack(side="left", padx=10)

    def handle_event_selection(self, event_arg):
        self.display_statistics()

    def populate_event_dropdown(self):
        all_events = events.get_all_events()
        self.event_map = {f"{event[0]}: {event[1]}": event[0] for event in all_events}
        self.event_menu['values'] = list(self.event_map.keys())

    def display_statistics(self):
        selected_event = self.selected_event_id.get()
        if not selected_event:
            self.registered_label.config(text="Total Registered: -")
            self.attended_label.config(text="Total Attended: -")
            self.percentage_label.config(text="Attendance Percentage: -")
            return

        event_id = self.event_map.get(selected_event)
        if event_id:
            statistics = reports.get_event_statistics(event_id)
            if statistics:
                self.registered_label.config(text=f"Total Registered: {statistics['registered']}")
                self.attended_label.config(text=f"Total Attended: {statistics['attended']}")
                self.percentage_label.config(text=f"Attendance Percentage: {statistics['percentage']:.2f}%")
            else:
                self.registered_label.config(text="Total Registered: N/A")
                self.attended_label.config(text="Total Attended: N/A")
                self.percentage_label.config(text="Attendance Percentage: N/A")
        else:
            messagebox.showerror("Error", "Invalid event selected.")

    def handle_view_chart(self):
        from PIL import Image, ImageTk

        selected_event = self.selected_event_id.get()
        if not selected_event:
            messagebox.showerror("Selection Error", "Please select an event to view its chart.")
            return

        event_id = self.event_map.get(selected_event)
        if event_id:
            # The chart path is relative to the static folder, e.g., 'static/chart.png'
            # We need the full path to open it with PIL.
            relative_chart_path = reports.generate_attendance_chart(event_id)
            
            if not relative_chart_path:
                messagebox.showinfo("No Data", "Not enough data to generate a chart for this event.")
                return

            full_chart_path = os.path.join("event_system", relative_chart_path)

            if self.chart_window and self.chart_window.winfo_exists():
                self.chart_window.destroy()

            self.chart_window = tk.Toplevel(self.controller)
            self.chart_window.title("Attendance Chart")

            try:
                img = Image.open(full_chart_path)
                photo = ImageTk.PhotoImage(img)
                
                chart_label = ttk.Label(self.chart_window, image=photo)
                chart_label.image = photo # Keep a reference to avoid garbage collection
                chart_label.pack(pady=10, padx=10)
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not display chart: {e}")
                self.chart_window.destroy()
            finally:
                # Clean up the temporary file after displaying it
                if os.path.exists(full_chart_path):
                    os.remove(full_chart_path)
        else:
            messagebox.showerror("Error", "Invalid event selected.")

    def handle_export_csv(self):
        selected_event = self.selected_event_id.get()
        if not selected_event:
            messagebox.showerror("Selection Error", "Please select an event to export its report.")
            return

        event_id = self.event_map.get(selected_event)
        if event_id:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save Attendance Report As"
            )
            if file_path:
                result = reports.export_attendance_to_csv(event_id, file_path)
                if result and "Success" in result:
                    messagebox.showinfo("Export Successful", result)
                elif result and "Info" in result:
                    messagebox.showinfo("Export Information", result)
                else:
                    messagebox.showerror("Export Error", result if result else "Failed to export attendance data.")
        else:
            messagebox.showerror("Error", "Invalid event selected.")