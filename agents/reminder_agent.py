import datetime
import re

class ReminderAgent:

    def __init__(self):
        self.reminders = []

    def parse_time(self, text):
        text = text.lower()

        # Match formats like 9, 09:00, 9:30 am
        match = re.search(r'(\d{1,2})(:(\d{2}))?\s*(am|pm)?', text)

        if not match:
            return None

        hour = int(match.group(1))
        minute = int(match.group(3)) if match.group(3) else 0
        am_pm = match.group(4)

        if am_pm == "pm" and hour != 12:
            hour += 12
        elif am_pm == "am" and hour == 12:
            hour = 0

        now = datetime.datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # If time already passed → schedule next day
        if target <= now:
            target += datetime.timedelta(days=1)

        return target

    def add_reminder_from_text(self, text):
        target_time = self.parse_time(text)

        if not target_time:
            return "⚠ Could not understand time"

        message = "Reminder!"
        self.reminders.append((message, target_time))

        return f"🔔 Reminder set for {target_time.strftime('%H:%M')}"

    def check_reminders(self):
        now = datetime.datetime.now()
        triggered = []

        for r in self.reminders:
            msg, t = r
            if now >= t:
                triggered.append(r)

        for r in triggered:
            self.reminders.remove(r)

        return triggered