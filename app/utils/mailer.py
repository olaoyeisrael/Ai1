import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv(override=True)

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html'))
        print("1")
    

        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        # print(EMAIL_PORT)
        server.starttls()
    
        server.login(EMAIL_USER, EMAIL_PASS)

        print("3")
        server.send_message(msg)
        # with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
        #     server.login(EMAIL_USER, EMAIL_PASS)
        #     server.send_message(msg)

        print(f"[MAILER] Email sent to {to_email}")

    except Exception as e:
        print(f"[MAILER ERROR] Failed to send email: {e}")


