import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import init_db, add_reminder, get_all
import sqlite3

DB_NAME = "reminders.db"

# ===================== DB INIT ===================== #
init_db()

def delete_reminder(reminder_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()

# ===================== UI ===================== #

st.set_page_config(page_title="Smart Event Reminder", layout="wide")
st.title("📅 Smart Event Reminder System")

# ---------- ADD EVENT ---------- #
st.subheader("➕ Add Event")

col1, col2, col3 = st.columns(3)
with col1:
    event = st.text_input("Event Title")
with col2:
    event_date = st.date_input("Event Date")
with col3:
    event_time = st.time_input("Event Time")

email = st.text_input("📧 Email for Reminder")

st.markdown("### 🔔 Reminder Options")
c1, c2, c3 = st.columns(3)

with c1:
    rem_1h = st.checkbox("1 hour before")
with c2:
    rem_1d = st.checkbox("1 day before")
with c3:
    rem_1w = st.checkbox("1 week before")

custom_reminders = st.text_area(
    "Custom reminder times (YYYY-MM-DD HH:MM, comma separated)",
    placeholder="2025-01-19 10:00, 2025-01-20 09:30"
)

if st.button("✅ Add Event"):
    if not event or not email:
        st.error("Event title and email are required")
    else:
        event_dt = datetime.combine(event_date, event_time)

        reminders = []
        if rem_1h:
            reminders.append(event_dt - timedelta(hours=1))
        if rem_1d:
            reminders.append(event_dt - timedelta(days=1))
        if rem_1w:
            reminders.append(event_dt - timedelta(weeks=1))

        if custom_reminders.strip():
            try:
                reminders.extend([
                    datetime.strptime(x.strip(), "%Y-%m-%d %H:%M")
                    for x in custom_reminders.split(",")
                ])
            except ValueError:
                st.error("❌ Invalid custom datetime format")
                st.stop()

        for r in reminders:
            add_reminder(
                event,
                event_dt.strftime("%Y-%m-%d %H:%M:%S"),
                r.strftime("%Y-%m-%d %H:%M:%S"),
                email
            )

        st.success("🎉 Event and reminders added")

# ---------- VIEW / EDIT ---------- #
st.subheader("📋 Scheduled Reminders")

rows = get_all()
df = pd.DataFrame(
    rows,
    columns=["ID", "Event", "Event Time", "Reminder Time", "Email", "Notified"]
)

st.dataframe(df, use_container_width=True)

st.markdown("### 🗑️ Delete Reminder")

delete_id = st.number_input(
    "Enter Reminder ID to delete",
    min_value=1,
    step=1
)

if st.button("❌ Delete Reminder"):
    delete_reminder(delete_id)
    st.success("Reminder deleted")

st.info("ℹ️ Reminders are sent by background worker (worker.py)")
