import os
from app.mailer import EmailNotifier
from app.telegraphMailer import sendUpdate

notifier = EmailNotifier(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    username="greenfieldemailnotifier@gmail.com",
    password="byycpptmgzexpyxb",
    use_tls=True,
)

def send_alert(to_email: str, subject: str, body: str):
    try:
        notifier.send(to_email, subject, body)
        print(f"Email sent: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

    sendUpdate()