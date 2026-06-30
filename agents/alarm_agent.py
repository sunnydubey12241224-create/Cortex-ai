import datetime
import time
import threading

try:
    import winsound
    SOUND = "beep"
except:
    SOUND = "print"


class AlarmAgent:

    def set_alarm(self, hour, minute):

        def run_alarm():
            while True:
                now = datetime.datetime.now()

                if now.hour == hour and now.minute == minute:
                    for _ in range(5):
                        if SOUND == "beep":
                            winsound.Beep(1000, 500)
                        else:
                            print("⏰ ALARM RINGING!")
                        time.sleep(1)
                    break

                time.sleep(5)

        threading.Thread(target=run_alarm).start()
        return f"⏰ Alarm set for {hour}:{minute}"

    def execute(self, text):
        try:
            time_str = text.split("at")[1].strip()
            hour, minute = map(int, time_str.split(":"))
            return self.set_alarm(hour, minute)
        except:
            return "⚠ Use format: set alarm at HH:MM"