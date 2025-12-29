import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_ADDRESS = "clinicalaffairs@zohomail.in"
EMAIL_PASSWORD = "YOUR_ZOHO_APP_PASSWORD"

SMTP_SERVER = "smtp.zoho.in"
SMTP_PORT = 587

def send_html_email(to_email, subject, html_body):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
