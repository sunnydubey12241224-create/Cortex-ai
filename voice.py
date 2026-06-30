import os
import speech_recognition as sr

# Cloud detection
IS_WINDOWS = os.name == "nt"

engine = None

if IS_WINDOWS:
    try:
        import pyttsx3
        engine = pyttsx3.init()
    except Exception:
        engine = None


def speak(text):
    """Speak only on Windows."""
    if engine is None:
        return

    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        pass


def listen():
    """Voice input only on Windows."""
    if not IS_WINDOWS:
        return ""

    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio)
    except Exception:
        return ""


def set_voice(style="default", speed=180, volume=1.0):
    """Configure voice engine on Windows."""
    if engine is None:
        return

    try:
        engine.setProperty("rate", speed)
        engine.setProperty("volume", volume)

        voices = engine.getProperty("voices")

        if style == "female" and len(voices) > 1:
            engine.setProperty("voice", voices[1].id)
        elif len(voices) > 0:
            engine.setProperty("voice", voices[0].id)

    except Exception:
        pass