import streamlit as st
from datetime import datetime, timedelta
from database import init_db, add_reminder, get_all

init_db()

st.title("📅 Smart Event Reminder (SQLite + Worker)")

event = st.text_input("Event Title")
event_date = st.date_input("Event Date")
event_time = st.time_input("Event Time")
email = st.text_input("Email")

st.markdown("### 🔔 Reminder Options")
one_hour = st.checkbox("1 hour before")
one_day = st.checkbox("1 day before")
custom = st.text_area(
    "Custom reminder times (YYYY-MM-DD HH:MM, comma separated)"
)

if st.button("Add Event"):
    event_dt = datetime.combine(event_date, event_time)

    reminders = []
    if one_hour:
        reminders.append(event_dt - timedelta(hours=1))
    if one_day:
        reminders.append(event_dt - timedelta(days=1))
    if custom.strip():
        reminders.extend([
            datetime.strptime(x.strip(), "%Y-%m-%d %H:%M")
            for x in custom.split(",")
        ])

    for r in reminders:
        add_reminder(
            event,
            event_dt.strftime("%Y-%m-%d %H:%M:%S"),
            r.strftime("%Y-%m-%d %H:%M:%S"),
            email
        )

    st.success("✅ Event added with reminders")

st.subheader("📋 Scheduled Reminders")
data = get_all()
st.dataframe(data, use_container_width=True)
