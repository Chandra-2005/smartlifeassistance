
#voice_recognition.py
import speech_recognition as sr
import pvporcupine
import pyaudio
import numpy as np

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

        try:
            query = recognizer.recognize_google(audio)
            print(f"Recognized: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            return None