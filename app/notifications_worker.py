from celery import shared_task
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

@shared_task(name="notifications.send_email_notification")
def send_email_notification(to_email: str, subject: str, body: str):
    """
    Background task to send an email notification.
    Falls back to console print if SMTP credentials are missing.
    """
    if not SMTP_SERVER or not SMTP_USER or not SMTP_PASS:
        print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {body}")
        return {"status": "mocked", "message": "Email printed to console"}
        
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return {"status": "success", "message": f"Email sent to {to_email}"}
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return {"status": "error", "message": str(e)}

@shared_task(name="notifications.send_sms_notification")
def send_sms_notification(phone_number: str, message: str):
    """
    Background task to send an SMS notification.
    Twilio integration is scaffolded here, falls back to console.
    """
    # TWILIO_SID = os.getenv("TWILIO_SID")
    # TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    
    # if TWILIO_SID and TWILIO_AUTH_TOKEN:
    #     from twilio.rest import Client
    #     client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    #     client.messages.create(body=message, from_="+1234567890", to=phone_number)
    
    print(f"[MOCK SMS] To: {phone_number} | Message: {message}")
    return {"status": "mocked", "message": "SMS printed to console"}
