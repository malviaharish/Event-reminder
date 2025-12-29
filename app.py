import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ===================== CONFIG ===================== #

EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

TWILIO_SID = "ACxxxxxxxxxxxxxxxx"
TWILIO_AUTH = "xxxxxxxxxxxxxxxx"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"

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

# ===================== WHATSAPP ===================== #

def send_whatsapp(to_number, message):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    client.messages.create(
        body=message,
        from_=TWILIO_WHATSAPP_FROM,
        to=f"whatsapp:{to_number}"
    )

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
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': TIMEZONE,
        },
    }

    service.events().insert(calendarId='primary', body=event).execute()

# ===================== DATA ===================== #

def load_events():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, parse_dates=["event_datetime"])
    return pd.DataFrame(columns=[
        "event", "event_datetime", "email", "whatsapp", "notified"
    ])

def save_events(df):
    df.to_csv(DATA_FILE, index=False)

# ===================== NOTIFICATION ===================== #

def notify_event(index, row):
    message = f"⏰ Reminder:\n{row['event']}\n🕒 {row['event_datetime']}"

    if pd.notna(row["email"]):
        send_email(row["email"], "Event Reminder", message)

    if pd.notna(row["whatsapp"]):
        send_whatsapp(row["whatsapp"], message)

    df = load_events()
    df.at[index, "notified"] = True
    save_events(df)

# ===================== SCHEDULER ===================== #

scheduler = BackgroundScheduler()
scheduler.start()

def schedule_events():
    df = load_events()
    for i, row in df.iterrows():
        if not row["notified"] and row["event_datetime"] > datetime.now():
            scheduler.add_job(
                notify_event,
                'date',
                run_date=row["event_datetime"],
                args=[i, row],
                replace_existing=True
            )

schedule_events()

# ===================== STREAMLIT UI ===================== #

st.title("📅 Smart Event Reminder App")

st.subheader("➕ Add New Event")

event = st.text_input("Event Title")
date = st.date_input("Event Date")
time_input = st.time_input("Event Time")

email = st.text_input("Email (optional)")
whatsapp = st.text_input("WhatsApp Number (optional, +91XXXXXXXXXX)")
add_calendar = st.checkbox("Add to Google Calendar")

if st.button("Add Event"):
    event_datetime = datetime.combine(date, time_input)
    end_datetime = event_datetime + timedelta(minutes=30)

    if add_calendar:
        add_to_google_calendar(event, event_datetime, end_datetime)

    df = load_events()
    df = pd.concat([df, pd.DataFrame([{
        "event": event,
        "event_datetime": event_datetime,
        "email": email if email else None,
        "whatsapp": whatsapp if whatsapp else None,
        "notified": False
    }])], ignore_index=True)

    save_events(df)
    schedule_events()
    st.success("✅ Event added successfully")

st.subheader("📋 Upcoming Events")
st.dataframe(load_events())

st.info("⚠️ Keep the app running for reminders to work")
