import time
from datetime import datetime
from database import init_db, get_pending_reminders, mark_notified
from emailer import send_html_email

init_db()

def load_template(event, event_time):
    with open("templates/reminder.html") as f:
        html = f.read()
    return html.replace("{{EVENT}}", event)\
               .replace("{{EVENT_TIME}}", event_time)

print("✅ Reminder worker started")

while True:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reminders = get_pending_reminders(now)

    for r in reminders:
        reminder_id, event, event_dt, reminder_dt, email, _ = r

        html = load_template(event, event_dt)

        try:
            send_html_email(
                email,
                "⏰ Event Reminder",
                html
            )
            mark_notified(reminder_id)
            print(f"📧 Sent reminder for: {event}")
        except Exception as e:
            print("❌ Email failed:", e)

    time.sleep(60)
