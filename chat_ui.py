import os
import datetime
import streamlit as st

# ===============================
# Agents
# ===============================
from agents.planner_agent import PlannerAgent
from agents.memory_agent import MemoryAgent
from agents.alarm_agent import AlarmAgent
from agents.email_agent import EmailAgent
from agents.conversation_agent import ConversationAgent
from agents.email_monitor import EmailMonitor
from agents.calendar_agent import CalendarAgent
from agents.reminder_agent import ReminderAgent
from agents.auto_planner import AutoPlanner

# ===============================
# Voice
# ===============================
from voice import listen, speak, set_voice

# ===============================
# Streamlit Config
# ===============================
st.set_page_config(
    page_title="Cortex AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ===============================
# Cloud Detection
# ===============================
IS_WINDOWS = os.name == "nt"

# ===============================
# Initialize Agents
# ===============================
planner = PlannerAgent()
memory = MemoryAgent()
alarm = AlarmAgent()
email = EmailAgent()
conversation = ConversationAgent()
monitor = EmailMonitor()
calendar = CalendarAgent()
reminder = ReminderAgent()
auto_planner = AutoPlanner()

# ===============================
# Session State
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = IS_WINDOWS

if "voice_input" not in st.session_state:
    st.session_state.voice_input = False

if "email_summary" not in st.session_state:
    st.session_state.email_summary = "Click Refresh"

if "meetings" not in st.session_state:
    st.session_state.meetings = "Click Refresh"

if "day_plan" not in st.session_state:
    st.session_state.day_plan = "Click Generate"

# ===============================
# Header
# ===============================
st.title("🤖 Cortex AI Assistant")
st.caption("Your Intelligent Personal AI Assistant")

if not IS_WINDOWS:
    st.info("☁ Running on Cloud Mode (Voice features disabled).")

# ===============================
# Tabs
# ===============================
tab_chat, tab_dashboard, tab_settings = st.tabs(
    [
        "🤖 Chat",
        "📊 Dashboard",
        "⚙ Settings"
    ]
)

# ===========================================================
# SETTINGS TAB
# ===========================================================
with tab_settings:

    st.header("⚙ Settings")

    st.subheader("🎤 Voice Settings")

    st.session_state.voice_enabled = st.checkbox(
        "Enable Voice Output",
        value=st.session_state.voice_enabled,
        disabled=not IS_WINDOWS
    )

    st.session_state.voice_input = st.checkbox(
        "Enable Voice Input",
        value=st.session_state.voice_input,
        disabled=not IS_WINDOWS
    )

    voice_style = st.selectbox(
        "Voice Style",
        [
            "default",
            "female"
        ],
        disabled=not IS_WINDOWS
    )

    speech_speed = st.slider(
        "Speech Speed",
        100,
        250,
        180,
        disabled=not IS_WINDOWS
    )

    speech_volume = st.slider(
        "Volume",
        0.0,
        1.0,
        1.0,
        disabled=not IS_WINDOWS
    )

    if IS_WINDOWS:
        try:
            set_voice(
                voice_style,
                speech_speed,
                speech_volume
            )
        except Exception as e:
            st.warning(f"Voice engine unavailable: {e}")

    st.divider()

    st.subheader("ℹ System Information")

    st.write("Platform:", os.name)
    st.write("Current Date:", datetime.datetime.now())

    st.success("Settings saved successfully.")
# ===========================================================
# CHAT TAB
# ===========================================================
with tab_chat:

    st.header("💬 Chat with Cortex AI")

    # -------------------------------------------------------
    # Email Notifications
    # -------------------------------------------------------
    try:
        notification = monitor.check_new_email()

        if notification:
            st.toast(notification)

            if IS_WINDOWS and st.session_state.voice_enabled:
                try:
                    speak(notification)
                except Exception:
                    pass

    except Exception as e:
        st.warning(f"Email Monitor: {e}")

    # -------------------------------------------------------
    # Reminder Notifications
    # -------------------------------------------------------
    try:
        reminders = reminder.check_reminders()

        for message, reminder_time in reminders:

            st.toast(f"🔔 {message}")

            if IS_WINDOWS and st.session_state.voice_enabled:
                try:
                    speak(message)
                except Exception:
                    pass

    except Exception as e:
        st.warning(f"Reminder Error: {e}")

    # -------------------------------------------------------
    # Display Chat History
    # -------------------------------------------------------
    for chat in st.session_state.messages:

        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    # -------------------------------------------------------
    # Voice Input
    # -------------------------------------------------------
    voice_text = None

    if (
        IS_WINDOWS
        and st.session_state.voice_input
        and st.button("🎤 Speak")
    ):
        try:
            voice_text = listen()
        except Exception as e:
            st.error(f"Voice Error: {e}")

    # -------------------------------------------------------
    # Text Input
    # -------------------------------------------------------
    typed_text = st.chat_input("Ask Cortex anything...")

    user_input = voice_text if voice_text else typed_text

    # -------------------------------------------------------
    # Main Conversation
    # -------------------------------------------------------
    if user_input:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input
            }
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.spinner("🧠 Cortex is thinking..."):

            try:

                plan = planner.plan(user_input)

                task = plan.get("task", "conversation")

                # ===========================================
                # Alarm
                # ===========================================
                if task == "set_alarm":

                    response = alarm.execute(user_input)

                # ===========================================
                # Email Summary
                # ===========================================
                elif task == "summarize_email":

                    response = email.execute()

                # ===========================================
                # Email Reply
                # ===========================================
                elif task == "reply_email":

                    response = email.generate_reply()

                # ===========================================
                # Multiple Email Summary
                # ===========================================
                elif task == "multi_email_summary":

                    response = email.summarize_multiple(3)

                # ===========================================
                # Calendar
                # ===========================================
                elif task == "calendar":

                    response = calendar.get_events_today()

                # ===========================================
                # Smart Schedule
                # ===========================================
                elif task == "smart_schedule":

                    response = calendar.smart_schedule()

                # ===========================================
                # Reminder
                # ===========================================
                elif task == "reminder":

                    response = reminder.add_reminder_from_text(
                        user_input
                    )

                # ===========================================
                # Memory Store
                # ===========================================
                elif task == "store_memory":

                    response = memory.store(user_input)

                # ===========================================
                # Memory Recall
                # ===========================================
                elif task == "recall_memory":

                    response = memory.recall(user_input)

                # ===========================================
                # Planner
                # ===========================================
                elif task == "planner":

                    response = planner.generate_day_plan(user_input)

                # ===========================================
                # Auto Planner
                # ===========================================
                elif task == "auto_planner":

                    emails = email.execute()

                    meetings = calendar.get_events_today()

                    response = auto_planner.generate_plan(
                        emails,
                        meetings
                    )

                # ===========================================
                # Default Conversation
                # ===========================================
                else:

                    response = conversation.respond(user_input)

            except Exception as e:

                response = f"⚠️ {str(e)}"

        # ---------------------------------------------------
        # Assistant Response
        # ---------------------------------------------------
        with st.chat_message("assistant"):

            st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        # ---------------------------------------------------
        # Voice Output
        # ---------------------------------------------------
        if (
            IS_WINDOWS
            and st.session_state.voice_enabled
        ):
            try:
                speak(response)
            except Exception:
                pass
# ===========================================================
# DASHBOARD TAB
# ===========================================================
with tab_dashboard:

    st.header("📊 Cortex AI Dashboard")

    today = datetime.datetime.now().strftime("%A, %d %B %Y")
    current_time = datetime.datetime.now().strftime("%I:%M %p")

    st.markdown(f"### 📅 {today}")
    st.caption(f"🕒 Current Time : {current_time}")

    st.divider()

    # =======================================================
    # QUICK STATS
    # =======================================================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "💬 Chats",
            len(st.session_state.messages)
        )

    with c2:
        st.metric(
            "📧 Emails",
            "Ready"
        )

    with c3:
        st.metric(
            "📅 Calendar",
            "Connected"
        )

    with c4:
        st.metric(
            "🔔 Reminders",
            len(reminder.reminders)
        )

    st.divider()

    # =======================================================
    # EMAIL & CALENDAR
    # =======================================================
    left, right = st.columns(2)

    with left:

        st.subheader("📧 Email Summary")

        if st.button(
            "🔄 Refresh Emails",
            use_container_width=True
        ):

            with st.spinner("Loading Emails..."):

                try:

                    st.session_state.email_summary = email.execute()

                except Exception as e:

                    st.session_state.email_summary = str(e)

        st.info(
            st.session_state.email_summary
        )

    with right:

        st.subheader("📅 Today's Meetings")

        if st.button(
            "🔄 Refresh Meetings",
            use_container_width=True
        ):

            with st.spinner("Loading Calendar..."):

                try:

                    st.session_state.meetings = (
                        calendar.get_events_today()
                    )

                except Exception as e:

                    st.session_state.meetings = str(e)

        st.info(
            st.session_state.meetings
        )

    st.divider()

    # =======================================================
    # REMINDERS
    # =======================================================
    st.subheader("🔔 Active Reminders")

    if reminder.reminders:

        for msg, reminder_time in reminder.reminders:

            st.success(
                f"🕒 {reminder_time.strftime('%H:%M')}  •  {msg}"
            )

    else:

        st.info("No Active Reminders")

    st.divider()

    # =======================================================
    # AI AUTO PLANNER
    # =======================================================
    st.subheader("🧠 AI Auto Planner")

    if st.button(
        "🚀 Generate Smart Daily Plan",
        use_container_width=True
    ):

        with st.spinner("Generating your personalized plan..."):

            try:

                emails = email.execute()

                meetings = calendar.get_events_today()

                plan = auto_planner.generate_plan(
                    emails,
                    meetings
                )

                st.session_state.day_plan = plan

            except Exception as e:

                st.session_state.day_plan = str(e)

    st.markdown(
        st.session_state.day_plan
    )

    st.divider()

    # =======================================================
    # CHAT HISTORY
    # =======================================================
    with st.expander("💬 Conversation History"):

        if st.session_state.messages:

            for msg in st.session_state.messages:

                role = (
                    "🧑 You"
                    if msg["role"] == "user"
                    else "🤖 Cortex"
                )

                st.markdown(
                    f"**{role}:** {msg['content']}"
                )

        else:

            st.info("No conversation yet.")

    st.divider()

    # =======================================================
    # MEMORY
    # =======================================================
    st.subheader("🧠 Memory")

    if st.button(
        "Show Stored Memory",
        use_container_width=True
    ):

        try:

            memories = memory.recall("all")

            st.success(memories)

        except Exception as e:

            st.error(e)

    st.divider()

    # =======================================================
    # FOOTER
    # =======================================================
    st.markdown("---")

    st.caption(
        "🤖 Cortex AI Assistant | Powered by OpenAI | "
        "Planner • Email • Calendar • Memory • Voice"
    )