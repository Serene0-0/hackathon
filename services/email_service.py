import os
import smtplib
from email.message import EmailMessage

class EmailService:
    def __init__(self):
        self.host = os.getenv("SMTP_HOST", "127.0.0.1")
        self.port = int(os.getenv("SMTP_PORT", "1025"))
        self.from_email = os.getenv("MAIL_FROM", "no-reply@lumenary.local")

    def send_email(self, to_email: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        # Mailpit/Mailhog typically no auth, plain SMTP
        with smtplib.SMTP(self.host, self.port) as smtp:
            smtp.send_message(msg)
