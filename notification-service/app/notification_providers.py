import aiosmtplib
from email.message import EmailMessage
from twilio.rest import Client
from .settings import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

async def send_email(to_email: str, subject: str, body: str) -> bool:
    message = EmailMessage()
    message["From"] = SMTP_USERNAME
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True
        )
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

def send_sms(to_number: str, message: str) -> bool:
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        print(f"SMS sent to {to_number}: SID {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {to_number}: {e}")
        return False
