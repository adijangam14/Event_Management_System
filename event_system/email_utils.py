import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import threading
import logging

# Configure logging for the module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from .config import EMAIL_CONFIG

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG["sender_email"]
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Create a default SSL context
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls(context=context)  # Secure the connection
            server.login(EMAIL_CONFIG["smtp_username"], EMAIL_CONFIG["smtp_password"])
            server.send_message(msg)
        logging.info(f"Email sent successfully to {to_email} for subject: {subject}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Failed to send email to {to_email} - Authentication Error: {e}. Check SMTP username/password.")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logging.error(f"Failed to send email to {to_email} - Server Disconnected: {e}. Check SMTP server/port.")
        return False
    except smtplib.SMTPException as e:
        logging.error(f"Failed to send email to {to_email} - SMTP Error: {e}")
        return False
    except Exception as e:
        logging.error(f"Failed to send email to {to_email} - General Error: {e}", exc_info=True)
        return False

def create_event_notification_email_body(event_name, event_date, event_time, event_location, custom_message=""):
    """
    Creates the body of an event notification email.
    """
    body = f"""
Dear Attendee,

This is a notification regarding the upcoming event: **{event_name}**.

Date: {event_date}
Time: {event_time}
Location: {event_location}

{custom_message}

We look forward to seeing you there!

Best regards,
The Event Management Team
"""
    return body.strip() # Remove leading/trailing whitespace

def send_emails_in_background(recipients, subject, body, completion_callback=None):
    """
    Sends multiple emails in a separate thread to avoid blocking the main UI thread.

    Args:
        recipients (list): A list of email addresses to send the email to.
        subject (str): The subject of the email.
        body (str): The body content of the email.
        completion_callback (callable, optional): A function to call after all emails
                                                   have been attempted to send.
                                                   It will receive a dictionary with
                                                   'success_count' and 'fail_count'.
    """
    def _send_emails_task():
        success_count = 0
        fail_count = 0
        for recipient in recipients:
            if send_email(recipient, subject, body):
                success_count += 1
            else:
                fail_count += 1
        if completion_callback:
            completion_callback({'success_count': success_count, 'fail_count': fail_count})

    # Start the email sending in a new thread
    thread = threading.Thread(target=_send_emails_task)
    thread.daemon = True # Allow the main program to exit even if thread is running
    thread.start()

if __name__ == "__main__":
    # Example usage (for testing purposes)
    # Replace with actual recipient and SMTP details
    recipient = "test@example.com"
    email_subject = "Test Event Notification"
    email_body = "This is a test email for your event notification system."
    # For actual testing, you'd need to set up EMAIL_CONFIG with valid credentials
    # logging.info("Example usage placeholder. Configure EMAIL_CONFIG and uncomment send_email to test.")
    # If running this directly, ensure EMAIL_CONFIG is properly set up or
    # temporary values are provided for testing.
    # For a real test, you'd need a working SMTP server and credentials.
    # send_email(recipient, email_subject, email_body)
    pass