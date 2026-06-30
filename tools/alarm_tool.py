import schedule
import threading
import time
from voice import speak

def set_alarm(time_str):

    def job():
        speak("Alarm ringing!")

    schedule.every().day.at(time_str).do(job)

    def run():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

    return f"Alarm set for {time_str}"