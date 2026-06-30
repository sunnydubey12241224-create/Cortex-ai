import streamlit as st
import datetime

# Agents
from agents.planner_agent import PlannerAgent
from agents.memory_agent import MemoryAgent
from agents.alarm_agent import AlarmAgent
from agents.email_agent import EmailAgent
from agents.conversation_agent import ConversationAgent
from agents.email_monitor import EmailMonitor
from agents.calendar_agent import CalendarAgent
from agents.reminder_agent import ReminderAgent
from agents.auto_planner import AutoPlanner

# Voice
from voice import listen, speak, set_voice

# Initialize agents
planner = PlannerAgent()
memory = MemoryAgent()
alarm = AlarmAgent()
email = EmailAgent()
conversation = ConversationAgent()
monitor = EmailMonitor()
calendar = CalendarAgent()
reminder = ReminderAgent()
auto_planner = AutoPlanner()

# UI config
st.set_page_config(page_title="Cortex AI", layout="wide")

# ===============================
# 🧠 HEADER
# ===============================
st.title("Cortex AI Assistant")
st.caption("Your intelligent personal AI system 🚀")

# ===============================
# 🎯 TABS
# ===============================
tab1, tab2, tab3 = st.tabs(["🤖 Chat", "📊 Dashboard", "⚙️ Settings"])

# ===============================
# ⚙️ SETTINGS TAB
# ===============================
with tab3:
    st.header("⚙️ Settings")

    st.subheader("🎤 Voice Control")

    if "voice_enabled" not in st.session_state:
        st.session_state.voice_enabled = True

    if "voice_input" not in st.session_state:
        st.session_state.voice_input = False

    st.session_state.voice_enabled = st.checkbox(
        "🔊 Enable Voice Output", value=st.session_state.voice_enabled
    )

    st.session_state.voice_input = st.checkbox(
        "🎤 Enable Voice Input", value=st.session_state.voice_input
    )

    style = st.selectbox("Voice Style", ["default", "female"])
    speed = st.slider("Speech Speed", 100, 250, 180)
    volume = st.slider("Volume", 0.0, 1.0, 1.0)

    set_voice(style, speed, volume)

# ===============================
# 🤖 CHAT TAB
# ===============================
with tab1:

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 🔔 Email notification
    notif = monitor.check_new_email()
    if notif:
        st.toast(notif)

    # 🔔 Reminder check
    triggered = reminder.check_reminders()
    for msg, t in triggered:
        st.toast(f"🔔 {msg}")
        if st.session_state.voice_enabled:
            speak(msg)

    # 🎤 Input
    if st.session_state.voice_input and st.button("🎤 Speak"):
        user_input = listen()
    else:
        user_input = st.chat_input("Ask Cortex anything...")

    # Show history
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.write(m["content"])

    if user_input:

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        try:
            plan = planner.plan(user_input)

            # ⏰ Alarm
            if plan["task"] == "set_alarm":
                response = alarm.execute(user_input)

            # 📧 Email
            elif plan["task"] == "summarize_email":
                response = email.execute()

            elif plan["task"] == "reply_email":
                response = email.generate_reply()

            elif plan["task"] == "multi_email_summary":
                response = email.summarize_multiple(3)

            # 📅 Calendar
            elif plan["task"] == "calendar":
                response = calendar.get_events_today()

            elif plan["task"] == "smart_schedule":
                response = calendar.smart_schedule()

            # 🔔 FIXED REMINDER (IMPORTANT 🔥)
            elif plan["task"] == "reminder":
                response = reminder.add_reminder_from_text(user_input)

            # 🧠 Memory
            elif plan["task"] == "store_memory":
                response = memory.store(user_input)

            elif plan["task"] == "recall_memory":
                response = memory.recall(user_input)

            # 💬 Default
            else:
                response = conversation.respond(user_input)

        except Exception as e:
            response = f"⚠ Error: {str(e)}"

        with st.chat_message("assistant"):
            st.write(response)

        if st.session_state.voice_enabled:
            speak(response)

        st.session_state.messages.append({"role": "assistant", "content": response})

# ===============================
# 📊 DASHBOARD TAB
# ===============================
with tab2:

    st.header("📊 Cortex Daily Planner")

    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    st.subheader(f"📅 {today}")

    col1, col2 = st.columns(2)

    # 📧 EMAILS
    with col1:
        st.subheader("📧 Email Summary")

        if st.button("Refresh Emails"):
            st.session_state["email_summary"] = email.execute()

        st.write(st.session_state.get("email_summary", "Click refresh"))

    # 📅 MEETINGS
    with col2:
        st.subheader("📅 Meetings")

        if st.button("Refresh Meetings"):
            st.session_state["meetings"] = calendar.get_events_today()

        st.write(st.session_state.get("meetings", "Click refresh"))

    # 🔔 REMINDERS
    st.subheader("🔔 Active Reminders")

    active = reminder.reminders

    if active:
        for msg, t in active:
            st.success(f"{msg} at {t.strftime('%H:%M')}")
    else:
        st.info("No reminders")

    # 🧠 AI AUTO PLANNER
    st.subheader("🧠 AI Auto Planner")

    if st.button("Generate Full Day Plan"):

        emails = email.execute()
        meetings = calendar.get_events_today()

        plan = auto_planner.generate_plan(emails, meetings)

        st.session_state["day_plan"] = plan

    st.write(st.session_state.get("day_plan", "Click to generate your plan"))