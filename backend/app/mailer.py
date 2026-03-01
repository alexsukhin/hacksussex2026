import smtplib
from email.message import EmailMessage
from typing import Optional

class EmailNotifier:
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        use_tls: bool = True,):

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send(self, to_email: str, subject: str, body: str):
        print("Connecting to SMTP...")
        msg = EmailMessage()
        msg["From"] = self.username
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            print("Logging in...")
            server.login(self.username, self.password)
            print("Sending message...")
            server.send_message(msg)
            print("SMTP send complete.")