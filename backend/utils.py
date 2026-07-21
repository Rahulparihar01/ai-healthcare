import qrcode
import os
import random

def generate_health_id() -> str:
    """Generates a 14-digit unique health ID similar to the ABHA format XX-XXXX-XXXX-XXXX"""
    p1 = str(random.randint(10, 99))
    p2 = str(random.randint(1000, 9999))
    p3 = str(random.randint(1000, 9999))
    p4 = str(random.randint(1000, 9999))
    return f"{p1}-{p2}-{p3}-{p4}"

def generate_qr_code(health_id: str) -> str:
    """Generates a QR code for the given health ID and saves it locally. Returns the file path."""
    qr_dir = os.path.join(os.path.dirname(__file__), "public", "qrcodes")
    os.makedirs(qr_dir, exist_ok=True)
    
    file_path = os.path.join(qr_dir, f"{health_id}.png")
    
    # URL that the doctor would scan
    url_to_encode = f"https://healthid.ai/p/{health_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url_to_encode)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_path)
    
    # Return relative path for web access
    return f"/public/qrcodes/{health_id}.png"

def send_email_otp(email: str, otp: str):
    """
    Sends an OTP via email. 
    In production, this would use a real SMTP server or API (like AWS SES or SendGrid).
    For local development, it simulates the process.
    """
    import smtplib
    from email.mime.text import MIMEText
    
    SMTP_SERVER = os.environ.get("SMTP_SERVER")
    SMTP_PORT = os.environ.get("SMTP_PORT")
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASS = os.environ.get("SMTP_PASS")
    
    # If no SMTP credentials are provided, just print it to the console for testing
    if not SMTP_SERVER or not SMTP_USER:
        print(f"--- MOCK EMAIL ---")
        print(f"To: {email}")
        print(f"Subject: Your HealthID AI Verification Code")
        print(f"Body: Your OTP code is {otp}")
        print(f"------------------")
        return True

    msg = MIMEText(f"Your OTP code is {otp}. It will expire in 10 minutes.")
    msg['Subject'] = 'Your HealthID AI Verification Code'
    msg['From'] = SMTP_USER
    msg['To'] = email

    print(f"=====================================")
    print(f"🚀 MOCK/DEBUG OTP: {otp}")
    print(f"📧 Sending to: {email}")
    print(f"=====================================")

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
