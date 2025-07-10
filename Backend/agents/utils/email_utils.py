from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv
load_dotenv()

def send_confirmation_email(to_email, patient_name, doctor_name, date, time, calendar_link=None):
    print( "________---------______", to_email)
    message = Mail(
        from_email='mehtasanjeev@gmail.com',
        to_emails=to_email,
        subject='Appointment Confirmation',
        html_content=f"""
        <p>Dear {patient_name},</p>
        <p>Your appointment with Dr. {doctor_name} is confirmed.</p>
        <ul>
            <li><strong>Date:</strong> {date}</li>
            <li><strong>Time:</strong> {time}</li>
        </ul>
        {f'<p><strong>Calendar:</strong> <a href="{calendar_link}">{calendar_link}</a></p>' if calendar_link else ''}
        <p>Regards,<br>Health Assistant Bot</p>
        """
    )

    try:
        sg = SendGridAPIClient(os.getenv("SEND_GRID_API"))
        response = sg.send(message)
        print(f"Email sent to {to_email}, status code: {response.status_code}")
    except Exception as e:
        print("SendGrid email error:", e)
