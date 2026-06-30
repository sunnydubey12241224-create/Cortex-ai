import streamlit as st
import datetime

from agents.email_agent import EmailAgent
from agents.calendar_agent import CalendarAgent
from agents.reminder_agent import ReminderAgent

# Init agents
email = EmailAgent()
calendar = CalendarAgent()
reminder = ReminderAgent()

st.set_page_config(page_title="AI Dashboard", layout="wide")

st.title("📊 AI Daily Planner Dashboard")

# =============================
# 📅 TODAY INFO
# =============================
today = datetime.datetime.now().strftime("%A, %d %B %Y")
st.subheader(f"📅 {today}")

col1, col2 = st.columns(2)

# =============================
# 📧 EMAIL SECTION
# =============================
with col1:
    st.subheader("📧 Latest Email Summary")

    if st.button("Refresh Emails"):
        summary = email.execute()
        st.session_state["email_summary"] = summary

    st.write(st.session_state.get("email_summary", "Click refresh"))

# =============================
# 📅 CALENDAR SECTION
# =============================
with col2:
    st.subheader("📅 Today's Meetings")

    if st.button("Refresh Meetings"):
        meetings = calendar.get_events_today()
        st.session_state["meetings"] = meetings

    st.write(st.session_state.get("meetings", "Click refresh"))

# =============================
# 🔔 REMINDERS
# =============================
st.subheader("🔔 Active Reminders")

triggered = reminder.check_reminders()

if triggered:
    for msg, t in triggered:
        st.success(f"{msg}")
else:
    st.info("No active reminders")

# =============================
# 🤖 AI SUMMARY
# =============================
st.subheader("🤖 AI Daily Summary")

if st.button("Generate Summary"):

    email_data = st.session_state.get("email_summary", "")
    meeting_data = st.session_state.get("meetings", "")

    summary = f"""
Today's Overview:

Emails:
{email_data}

Meetings:
{meeting_data}

Give a short smart summary.
"""

    from llm_engine import generate
    ai_summary = generate(summary)

    st.session_state["ai_summary"] = ai_summary

st.write(st.session_state.get("ai_summary", "Click generate"))

# =============================
# AUTO REFRESH OPTION
# =============================
if st.checkbox("Auto Refresh (10s)"):
    import time
    time.sleep(10)
    st.rerun()