import streamlit as st
from datetime import datetime, timedelta
from ics import Calendar, Event
import io

st.title("⏰ Multi-Event Reminder (.ics) Creator")

# Input fields
title = st.text_input("Event Title", "")
description = st.text_area("Event Description", "")
num_events = st.number_input("Number of events", min_value=1, value=1)
dates = []
start_times = []
end_times = []

for i in range(num_events):
    st.markdown(f"**Event {i+1}**")
    d = st.date_input(f"Date for Event {i+1}", datetime.now().date(), key=f"date{i}")
    stime = st.time_input(f"Start Time for Event {i+1}", datetime.now().time(), key=f"stime{i}")
    etime = st.time_input(f"End Time for Event {i+1}", (datetime.now() + timedelta(hours=1)).time(), key=f"etime{i}")
    dates.append(d)
    start_times.append(stime)
    end_times.append(etime)

if st.button("➕ Create .ics File for All Events"):
    if not title:
        st.warning("Please enter an event title.")
    else:
        # Create calendar
        c = Calendar()
        for i in range(num_events):
            e = Event()
            e.name = title
            e.begin = datetime.combine(dates[i], start_times[i])
            e.end = datetime.combine(dates[i], end_times[i])
            e.description = description
            c.events.add(e)

        # Save to in-memory file
        ics_file = io.StringIO(str(c))
        st.download_button(
            label="⬇️ Download Multi-Event .ics File",
            data=ics_file.getvalue(),
            file_name=f"{title.replace(' ', '_')}_events.ics",
            mime="text/calendar"
        )
        st.success("✅ Multi-event .ics file created! Click download to add all events to Google Calendar.")
