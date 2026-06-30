import speech_recognition as sr
import pyttsx3
import threading

# Initialize engine
engine = pyttsx3.init()
engine_lock = threading.Lock()

# ===============================
# 🔊 VOICE CONFIGURATION
# ===============================
def set_voice(style="default", rate=180, volume=1.0):
    voices = engine.getProperty('voices')

    # Select voice
    if style == "female" and len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    else:
        engine.setProperty('voice', voices[0].id)

    # Set properties
    engine.setProperty('rate', rate)      # Speed
    engine.setProperty('volume', volume)  # Volume (0.0 to 1.0)


# ===============================
# 🔊 SPEAK FUNCTION
# ===============================
def speak(text):
    if not text:
        return

    def run():
        with engine_lock:
            engine.say(text)
            engine.runAndWait()

    t = threading.Thread(target=run)
    t.start()


# ===============================
# 🛑 STOP SPEAKING
# ===============================
def stop_speaking():
    with engine_lock:
        engine.stop()


# ===============================
# 🎤 LISTEN FUNCTION
# ===============================
def listen(timeout=5, phrase_time_limit=10):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            print("🎤 Listening...")

            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=1)

            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        print("🧠 Processing...")

        text = recognizer.recognize_google(audio)
        print("You said:", text)

        return text

    except sr.WaitTimeoutError:
        print("⏱ No speech detected")
        return ""

    except sr.UnknownValueError:
        print("🤷 Could not understand audio")
        return ""

    except sr.RequestError:
        print("❌ Speech service error")
        return ""

    except Exception as e:
        print("⚠ Error:", e)
        return ""