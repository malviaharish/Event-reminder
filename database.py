import sqlite3
from datetime import datetime

DB_NAME = "reminders.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT,
        event_datetime TEXT,
        reminder_datetime TEXT,
        email TEXT,
        notified INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

def add_reminder(event, event_dt, reminder_dt, email):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    INSERT INTO reminders (event, event_datetime, reminder_datetime, email)
    VALUES (?, ?, ?, ?)
    """, (event, event_dt, reminder_dt, email))

    conn.commit()
    conn.close()

def get_pending_reminders(now):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM reminders
    WHERE notified = 0 AND reminder_datetime <= ?
    """, (now,))

    rows = c.fetchall()
    conn.close()
    return rows

def mark_notified(reminder_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    UPDATE reminders SET notified = 1 WHERE id = ?
    """, (reminder_id,))

    conn.commit()
    conn.close()

def get_all():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reminders ORDER BY reminder_datetime")
    rows = c.fetchall()
    conn.close()
    return rows
