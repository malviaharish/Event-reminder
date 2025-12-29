import streamlit as st
from datetime import datetime, timedelta
import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ===================== CONFIG ===================== #
SCOPES = ['https://www.googleapis.com/auth/calendar']  # Full access to manage calendar
CREDENTIALS_FILE = 'credentials.json'  # Downloaded from Google Cloud Console

# ===================== AUTHENTICATION ===================== #
def get_calendar_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('calendar', 'v3', credentials=creds)
    return service

# ===================== ADD EVENT FUNCTION ===================== #
def create_event(service, title, description, start_datetime, end_datetime):
    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'Asia/Kolkata',
        },
    }
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink')

# ===================== STREAMLIT UI ===================== #
st.set_page_config(page_title="Google Calendar Reminder", page_icon="⏰", layout="centered")
st.title("⏰ Google Calendar Reminder App")
st.write("Add reminders/events to your Google Calendar directly from this app.")

# Input fields
title = st.text_input("Event Title", "")
description = st.text_area("Event Description", "")
date = st.date_input("Event Date", datetime.now().date())
start_time = st.time_input("Start Time", datetime.now().time())
end_time = st.time_input("End Time", (datetime.now() + timedelta(hours=1)).time())

add_event = st.button("➕ Add to Google Calendar")

# Run when button clicked
if add_event:
    if not title:
        st.warning("Please enter an event title.")
    else:
        service = get_calendar_service()
        start_dt = datetime.combine(date, start_time).isoformat()
        end_dt = datetime.combine(date, end_time).isoformat()
        try:
            event_link = create_event(service, title, description, start_dt, end_dt)
            st.success("✅ Event added successfully!")
            st.markdown(f"[Open in Google Calendar]({event_link})")
        except Exception as e:
            st.error(f"Error adding event: {e}")

st.info("ℹ️ First time you run this app, a browser window will open for Google login and authorization.")
