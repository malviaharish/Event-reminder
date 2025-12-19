import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

# Example events
events = [
    {"name": "Submit report", "date": "2025-12-20", "email": "your_email@gmail.com"}
]

# Check events
today = datetime.now().date()
for event in events:
    event_date = datetime.strptime(event["date"], "%Y-%m-%d").date()
    if event_date == today + timedelta(days=1):  # remind 1 day before
        msg = MIMEText(f"Reminder: {event['name']} is scheduled for {event['date']}")
        msg['Subject'] = "Event Reminder"
        msg['From'] = "your_email@gmail.com"
        msg['To'] = event["email"]

        # Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("malviaharish@gmail.com", "Krishnaram1$")
            server.send_message(msg)

        print(f"Reminder sent for {event['name']}")
