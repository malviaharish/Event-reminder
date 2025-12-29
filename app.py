import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ===================== CONFIG ===================== #

EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

DATA_FILE = "events.csv"
TIMEZONE = "Asia/Kolkata"
SCOPES = ['https://www.googleapis.com/auth/calendar']

# ===================== EMAIL ===================== #

def send_email(to_email, subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

# ===================== GOOGLE CALENDAR ===================== #

def get_calendar_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

def add_to_google_calendar(title, start_dt, end_dt):
    service = get_calendar_service()
    event = {
        'summary': title,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': TIMEZONE},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': TIMEZONE},
    }
    service.events().insert(calendarId='primary', body=event).execute()

# ===================== DATA ===================== #

def load_events():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["event_datetime", "reminder_datetime"])
    return pd.DataFrame(columns=[
        "event", "event_datetime", "reminder_datetime",
        "email", "add_to_calendar", "notified"
    ])

def save_events(df):
    df.to_csv(DATA_FILE, index=False)

# ===================== NOTIFICATION ===================== #

def notify_event(index, row):
    message = (
        f"⏰ Reminder\n\n"
        f"Event: {row['event']}\n"
        f"Event Time: {row['event_datetime']}"
    )

    if pd.notna(row["email"]):
        send_email(row["email"], "Event Reminder", message)

    df = load_events()
    df.at[index, "notified"] = True
    save_events(df)

# ===================== SCHEDULER ===================== #

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_events():
    df = load_events()
    for i, row in df.iterrows():
        if not row["notified"] and row["reminder_datetime"] > datetime.now():
            scheduler.add_job(
                notify_event,
                'date',
                run_date=row["reminder_datetime"],
                args=[i, row],
                replace_existing=True
            )

schedule_events()

# ===================== STREAMLIT UI ===================== #

st.title("📅 Smart Event Reminder App (Multiple Reminders)")

# ---------- MANUAL ENTRY ---------- #
st.subheader("➕ Add Event Manually")

event = st.text_input("Event Title")
event_date = st.date_input("Event Date")
event_time = st.time_input("Event Time")
email = st.text_input("Email (optional)")
add_calendar = st.checkbox("Add to Google Calendar")

st.markdown("### 🔔 Reminder Options")
rem_1h = st.checkbox("1 hour before")
rem_1d = st.checkbox("1 day before")
custom_reminders = st.text_area(
    "Custom reminder datetimes (comma separated, YYYY-MM-DD HH:MM)",
    placeholder="2025-01-19 10:00, 2025-01-20 09:30"
)

if st.button("Add Event"):
    event_datetime = datetime.combine(event_date, event_time)
    reminders = []

    if rem_1h:
        reminders.append(event_datetime - timedelta(hours=1))
    if rem_1d:
        reminders.append(event_datetime - timedelta(days=1))
    if custom_reminders.strip():
        for dt in custom_reminders.split(","):
            reminders.append(pd.to_datetime(dt.strip()))

    df = load_events()

    for rdt in reminders:
        df = pd.concat([df, pd.DataFrame([{
            "event": event,
            "event_datetime": event_datetime,
            "reminder_datetime": rdt,
            "email": email if email else None,
            "add_to_calendar": "yes" if add_calendar else "no",
            "notified": False
        }])], ignore_index=True)

    save_events(df)

    if add_calendar:
        add_to_google_calendar(event, event_datetime, event_datetime + timedelta(minutes=30))

    schedule_events()
    st.success("✅ Event with multiple reminders added")

# ---------- EXCEL UPLOAD ---------- #
st.subheader("📤 Upload Events via Excel")

uploaded_file = st.file_uploader("Upload Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    excel_df = pd.read_excel(uploaded_file)

    required = {"event", "event_datetime", "reminder_datetimes", "email", "add_to_calendar"}
    if not required.issubset(excel_df.columns):
        st.error("❌ Excel missing required columns")
    else:
        df = load_events()

        for _, row in excel_df.iterrows():
            event_dt = pd.to_datetime(row["event_datetime"])
            reminders = str(row["reminder_datetimes"]).split(",")

            for r in reminders:
                df = pd.concat([df, pd.DataFrame([{
                    "event": row["event"],
                    "event_datetime": event_dt,
                    "reminder_datetime": pd.to_datetime(r.strip()),
                    "email": row["email"],
                    "add_to_calendar": row["add_to_calendar"],
                    "notified": False
                }])], ignore_index=True)

            if str(row["add_to_calendar"]).lower() == "yes":
                add_to_google_calendar(
                    row["event"],
                    event_dt,
                    event_dt + timedelta(minutes=30)
                )

        save_events(df)
        schedule_events()
        st.success("✅ Excel events with multiple reminders scheduled")

# ---------- VIEW ---------- #
st.subheader("📋 Scheduled Reminders")
st.dataframe(load_events())

st.info("⚠️ Keep the app running for reminders to work")
