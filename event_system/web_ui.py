from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_wtf.csrf import CSRFProtect
from . import auth, events, registrations, attendance, reports, email_utils, config, students, db
from .forms import LoginForm, RegistrationForm, StudentForm, EventForm, EventRegistrationForm, CancelRegistrationForm, AttendanceForm, EmailForm
import datetime
import os
import atexit

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)
csrf = CSRFProtect(app)

# --- App Lifecycle Management ---
# Initialize the database connection pool when the app starts
db.init_pool()

# Register a function to close the pool when the app exits
atexit.register(db.close_pool)
# --- End Lifecycle Management ---

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        result = auth.create_web_user(username, password)

        if "Success" in result:
            flash(result, 'success')
            return redirect(url_for('login'))
        else:
            flash(result, 'danger')
            return redirect(url_for('register'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_data = auth.login(username, password)
        if user_data:
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            session['role'] = user_data['role']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/students', methods=['GET', 'POST'])
def students_page():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    form = StudentForm()
    if form.validate_on_submit():
        student_id = form.student_id.data
        name = form.name.data
        email = form.email.data
        course = form.course.data
        year = form.year.data
        
        result = students.add_student(student_id, name, email, course, year)
        
        if "Success" in result:
            flash(result, 'success')
        else:
            flash(result, 'danger')
        
        return redirect(url_for('students_page'))

    all_students = students.get_all_students()
    return render_template('students.html', students=all_students, role=session.get('role'), form=form)

@app.route('/events', methods=['GET', 'POST'])
def events_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    form = EventForm()
    if form.validate_on_submit():
        if session.get('role') != 'admin':
            flash('You are not authorized to create events.', 'danger')
            return redirect(url_for('events_page'))
        
        event_name = form.event_name.data
        event_date = form.event_date.data
        event_time = form.event_time.data
        venue = form.venue.data
        total_slots = form.total_slots.data
        
        result = events.create_event(event_name, event_date, event_time, venue, total_slots)
        
        if "Success" in result:
            flash(result, 'success')
        else:
            flash(result, 'danger')
        
        return redirect(url_for('events_page'))

    all_events = events.get_all_events()
    return render_template('events.html', events=all_events, role=session.get('role'), form=form)

@app.route('/registrations', methods=['GET', 'POST'])
def registrations_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    form = EventRegistrationForm()
    if form.validate_on_submit():
        if session.get('role') != 'admin':
            flash('You are not authorized to register students.', 'danger')
            return redirect(url_for('registrations_page'))

        event_id = form.event_id.data
        student_id = form.student_id.data

        result = registrations.register_student_for_event(event_id, student_id)

        if "Success" in result:
            flash(result, 'success')
        elif "Info" in result:
            flash(result, 'info')
        else:
            flash(result, 'danger')
        
        return redirect(url_for('registrations_page', event_id=event_id))

    all_events = events.get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    registered_students = []
    if selected_event_id and session.get('role') == 'admin':
        registered_students = registrations.get_registered_students(selected_event_id)

    return render_template('registrations.html', events=all_events, registered_students=registered_students, selected_event_id=selected_event_id, role=session.get('role'), form=form)

@app.route('/cancel_registration', methods=['POST'])
def cancel_registration():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    form = CancelRegistrationForm()
    if form.validate_on_submit():
        event_id = form.event_id.data
        student_id = form.student_id.data

        result = registrations.cancel_registration(event_id, student_id)

        if "Success" in result:
            flash(result, 'success')
        else:
            flash(result, 'danger')

        return redirect(url_for('registrations_page', event_id=event_id))
    return redirect(url_for('registrations_page')) # Redirect if form not valid or GET request

@app.route('/attendance', methods=['GET', 'POST'])
def attendance_page():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    form = AttendanceForm()
    if form.validate_on_submit():
        event_id = form.event_id.data
        student_id = form.student_id.data
        status = form.status.data

        result = attendance.mark_attendance(event_id, student_id, status)

        if "Success" in result:
            flash(result, 'success')
        else:
            flash(result, 'danger')
        
        return redirect(url_for('attendance_page', event_id=event_id))

    all_events = events.get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    attendance_list = []
    if selected_event_id:
        attendance_list = attendance.get_event_attendance(selected_event_id)

    return render_template('attendance.html', events=all_events, attendance_list=attendance_list, selected_event_id=selected_event_id, role=session.get('role'), form=form)

@app.route('/reports', methods=['GET'])
def reports_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    all_events = events.get_all_events()
    selected_event_id = request.args.get('event_id', type=int)
    stats = None
    if selected_event_id:
        stats = reports.get_event_statistics(selected_event_id)

    return render_template('reports.html', events=all_events, stats=stats, selected_event_id=selected_event_id)

@app.route('/reports/export/<int:event_id>')
def export_csv(event_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    path = reports.export_attendance_to_csv(event_id)
    if path:
        return send_file(path, as_attachment=True)
    else:
        flash('Could not export the report.', 'danger')
        return redirect(url_for('reports_page'))

@app.route('/emails', methods=['GET', 'POST'])
def emails_page():
    if 'username' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    all_events = events.get_all_events()
    form = EmailForm(events=all_events)
    if form.validate_on_submit():
        event_id = form.event_id.data
        subject = form.subject.data
        body = form.body.data
        
        event_details = events.get_event_details(event_id)
        if not event_details:
            flash("Error: Could not retrieve event details.", 'danger')
            return redirect(url_for('emails_page'))

        _, event_name, _, _, _, _ = event_details

        if form.send_test.data: # Check if send test button was clicked
            recipient = config.EMAIL_CONFIG.get("sender_email")
            if not recipient or recipient == "your_email@example.com":
                flash("Please configure 'sender_email' in config.py for testing.", 'danger')
                return redirect(url_for('emails_page'))
            
            email_utils.send_email(recipient, f"TEST: {subject}", body)
            flash(f"Test email sent to {recipient}", 'success')
        else:
            registered_students_data = registrations.get_registered_students(event_id)
            if not registered_students_data:
                flash("No students are registered for this event.", 'warning')
                return redirect(url_for('emails_page'))

            recipients = [student[2] for student in registered_students_data if student[2]]
            if not recipients:
                flash("No valid email addresses found for registered students.", 'warning')
                return redirect(url_for('emails_page'))
            
            email_utils.send_emails_in_background(recipients, subject, body)
            flash(f"Emails are being sent to {len(recipients)} recipients in the background.", 'info')

        return redirect(url_for('emails_page'))

    return render_template('emails.html', form=form)
