from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, DateField, TimeField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, NumberRange, Optional
from datetime import date

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class StudentForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    course = StringField('Course')
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Student')

class EventForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_date = DateField('Event Date', format='%Y-%m-%d', validators=[DataRequired()])
    event_time = StringField('Event Time', validators=[DataRequired()])
    venue = StringField('Venue', validators=[DataRequired()])
    total_slots = IntegerField('Total Slots', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Create Event')

class EventRegistrationForm(FlaskForm): # Renamed to avoid conflict with top-level RegistrationForm
    event_id = IntegerField('Event ID', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Register')

class CancelRegistrationForm(FlaskForm):
    event_id = IntegerField('Event ID', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Cancel Registration')

class AttendanceForm(FlaskForm):
    event_id = IntegerField('Event ID', validators=[DataRequired()])
    student_id = StringField('Student ID', validators=[DataRequired()])
    status = StringField('Status', validators=[DataRequired()]) # 'Y' or 'N'
    submit_present = SubmitField('Mark Present')
    submit_absent = SubmitField('Mark Absent')

class EmailForm(FlaskForm):
    event_id = SelectField('Event', coerce=int, validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    body = StringField('Body', validators=[DataRequired()])
    send_emails = SubmitField('Send Emails')
    send_test = SubmitField('Send Test Email')

    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.event_id.choices = [(event[0], event[1]) for event in kwargs.get('events', [])]
