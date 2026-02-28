'''
email is RainMakerEmailNotifier@gmail.com
password is Zq'*^Q&1055?

GMAIL APP PASSWORD is      ielp ubim yidw iqif
'''

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
        msg = EmailMessage()
        msg["From"] = self.username or "or"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            if self.username and self.password:
                server.login(self.username, self.password)
            server.send_message(msg)